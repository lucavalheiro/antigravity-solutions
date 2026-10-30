# GLPI ITSM + IBM Instana AIOps Integration

> Projeto apartado, containerizado e dedicado de GLPI 10 com governança de processos **ITIL completa** e integração nativa com o **IBM Instana Observability** para abertura e fechamento automático de chamados de incidentes.
> 
> **STATUS:** ✅ **100% ATIVADO E CONFIGURADO VIA CLI NO INSTANA E NO GLPI.**

---

## 📌 Visão Geral da Arquitetura

O projeto foi provisionado em ambiente totalmente **isolado**, garantindo conformidade com o requisito de não interferir em outros serviços existentes na máquina:

- **Rede Docker Privada:** `glpi_isolated_net` (isolamento de tráfego de rede).
- **Volumes Dedicados:** Armazenamento isolado para o banco de dados MariaDB e arquivos do GLPI.
- **Portas Padronizadas sem Conflito:**
  - **GLPI Web UI & REST API:** Porta `8090` (`http://192.168.173.22:8090`)
  - **Instana GLPI Integration Bridge:** Porta `8095` (`http://192.168.173.22:8095`)
  - **Banco de Dados (MariaDB 10.11):** Comunicação estritamente interna (porta 3306 não exposta no host).

```
+-------------------------------------------------------------------------+
| IBM Instana Observability (https://10.1.0.65.nip.io)                    |
| - Alert Channel ATIVADO via CLI: 'GLPI ITIL Service Desk'              |
| - Alert Rule ATIVADA via CLI: Incidentes, CPU, Memória, Queda, Offline  |
+------------------------------------+------------------------------------+
                                     |
                                     | HTTP POST (Webhook Automático)
                                     v
+-------------------------------------------------------------------------+
| [Bridge AIOps] Instana-GLPI Integration Bridge (:8095)                  |
| - Endpoint: /webhook/instana                                            |
| - Mapeamento ITIL (Severidade -> Urgência, Impacto, Prioridade)         |
| - Prevenção de duplicidade (Deduplicação & Followup automático)         |
| - Auto-Solução quando Instana encerra o evento (Auto-healing)           |
+------------------------------------+------------------------------------+
                                     |
                                     | GLPI REST API (Session & App Token)
                                     v
+-------------------------------------------------------------------------+
| [GLPI 10 ITSM] Processo ITIL Completo (:8090)                           |
| - Gestão de Incidentes (ITIL P1 a P5 com SLAs de Resposta e Solução)    |
| - Gestão de Problemas (Causa Raiz, Erros Conhecidos KEDB, Workarounds)  |
| - Gestão de Mudanças / RFCs (Aprovação pelo CAB)                        |
| - CMDB / Gestão de Ativos (Vínculo automático ao Servidor / CI)         |
| - Grupos: N1 Central de Serviços, N2 AIOps, N3 Cloud & Infra            |
+-------------------------------------------------------------------------+
```

---

## 🔑 Credenciais e Acessos

| Serviço | URL | Usuário / Identificador | Senha / Token |
| :--- | :--- | :--- | :--- |
| **GLPI Web UI (Admin)** | `http://192.168.173.22:8090` | `glpi` | `glpi` |
| **GLPI Web UI (Técnico N2)** | `http://192.168.173.22:8090` | `tech` | `tech` |
| **GLPI Web UI (Usuário N1)** | `http://192.168.173.22:8090` | `normal` | `normal` |
| **Bridge Healthcheck** | `http://192.168.173.22:8095/health` | - | - |
| **GLPI REST API Endpoint** | `http://192.168.173.22:8090/apirest.php` | App-Token: `InstanaGLPIToken2026` | User-Token: `InstanaUserToken2026` |
| **Instana Webhook Endpoint** | `http://192.168.173.22:8095/webhook/instana` | - | - |

---

## ⚡ Configuração Realizada via CLI no Instana

Toda a configuração no IBM Instana foi executada **diretamente via REST API e CLI**, sem necessidade de intervenção na interface gráfica:

### 1. Canal de Alerta (Alert Channel) Criado:
- **ID:** `glpi-itil-alert-channel`
- **Nome:** `GLPI ITIL Service Desk`
- **Tipo:** `WEB_HOOK`
- **URL Alvo:** `http://192.168.173.22:8095/webhook/instana`

### 2. Regra de Alerta Global (Alert Rule) Criada e Vinculada:
- **ID:** `glpi-itil-alert-config`
- **Nome:** `Alerta Geral ITIL - Incidentes, CPU, Memoria, Quedas e Offline`
- **Canal Vinculado:** `glpi-itil-alert-channel`
- **Eventos Monitorados Ativos:**
  - `incident` (Incidentes correlacionados por IA no Instana)
  - `critical` (Alertas críticos: CPU > 90%, OutOfMemory, etc.)
  - `warning` (Avisos de degradação e anomalia de métricas)
  - `offline` (Servidor Offline / Queda de contêiner ou serviço)
  - `change` (Eventos de alteração e deploy)
  - `agent_monitoring_issue` (Falhas operacionais do agente)

---

## 🏛️ Estrutura do Processo ITIL Implementado

### 1. Matriz de Prioridade ITIL (AIOps Engine)

| Severidade Instana | Classificação ITIL | Urgência | Impacto | Prioridade | SLA Resposta (TTO) | SLA Solução (TTR) | Categoria ITIL Atribuída |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **10 (Critical)** | **P1 - Crítico** | 5 (Muito Alta) | 5 (Muito Alto) | **5 (Crítica)** | 15 minutos | 2 horas | `AIOps & Observabilidade > Instana - Incidentes Críticos (AIOps)` |
| **5 (Warning)** | **P3 - Médio** | 3 (Média) | 3 (Médio) | **3 (Média)** | 2 horas | 8 horas | `AIOps & Observabilidade > Instana - Degradação & Anomalias (AIOps)` |
| **< 5 (Info/Other)** | **P4 - Baixo** | 2 (Baixa) | 2 (Baixo) | **2 (Baixa)** | 4 horas | 24 horas | `AIOps & Observabilidade > Instana - Degradação & Anomalias (AIOps)` |

### 2. Taxonomia de Categorias ITIL

- **Infraestrutura:** Servidores & Computação, Redes & Conectividade, Storage & Backup.
- **Plataformas & Cloud:** Kubernetes & Containers, Banco de Dados & Cache.
- **Aplicações & Negócio:** Microsserviços & APIs, Portais Web & UI.
- **AIOps & Observabilidade:**
  - `Instana - Incidentes Críticos (AIOps)` *(Utilizada para incidentes P1)*
  - `Instana - Degradação & Anomalias (AIOps)` *(Utilizada para avisos P3)*
  - `Instana - Eventos de Mudança de Host` *(Vinculada a Mudanças RFC)*
- **Segurança da Informação:** Certificados Digitais & TLS, Vulnerabilidades & Patches.

### 3. Grupos de Atendimento & Governança

1. **N1 - Central de Serviços (Service Desk):** Triagem inicial e atendimento de usuários.
2. **N2 - Suporte a Aplicações & AIOps:** **Grupo padrão** atribuído automaticamente para todos os chamados abertos pelo IBM Instana.
3. **N3 - Engenharia de Infraestrutura & Cloud:** Acionado para incidentes complexos de infraestrutura ou hardware.
4. **Comitê de Mudanças (CAB - Change Advisory Board):** Gestão e aprovação de RFCs (Requisições de Mudança).
5. **Gestão de Problemas (Problem Management & RCA):** Investigação de Causa Raiz de incidentes recorrentes e gestão da base de erros conhecidos (KEDB).

---

## 🧪 Testes e Validação da Integração

Você pode disparar simulações de alertas para verificar o fluxo completo tanto pelo Windows (PowerShell) quanto diretamente no Linux (Bash):

### No Windows (PowerShell):
```powershell
powershell -ExecutionPolicy Bypass -File .\glpi-itil\test_alert.ps1
```

### No Servidor Linux (Bash):
```bash
/home/luciano-erp/projetos/glpi-itil/test_alert.sh
```
