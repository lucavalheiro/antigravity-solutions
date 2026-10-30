# Instana Turbo & Portal Sommelier IBM

Ambiente unificado de observabilidade, automação de infraestrutura e gestão de incidentes ITIL com IBM Instana, IBM Turbonomic, Watsonx e GLPI Service Desk.

## 🌟 Módulos da Solução

### 1. Portal Sommelier de Soluções IBM (`projeto-sommelier/`)
Interface web responsiva com apresentação interativa das tecnologias:
- **IBM Instana:** APM e observabilidade full-stack em tempo real.
- **IBM Turbonomic:** Otimização de recursos e custos com Application Resource Management (ARM).
- **IBM Watsonx:** Inteligência artificial generativa e governança.
- **GLPI Service Desk & ERPNext:** Integração corporativa e gestão de ativos.
- **IBM Quantum:** Computação quântica aplicada aos negócios.

### 2. GLPI ITIL Bridge (`glpi-itil/`)
Automação de incidentes entre IBM Instana e GLPI:
- Recebe webhooks de alertas do IBM Instana.
- Abre e atualiza chamados no GLPI com enriquecimento de dados ITIL e criticidade.
- `bridge/`: Serviço em Python (FastAPI/requests) com Dockerfile e `docker-compose.yml`.
- `setup_itil.sql`: Script de provisionamento das categorias, grupos e prioridades ITIL no GLPI.
- Scripts de teste e validação de alertas (`test_alert.ps1`, `test_alert.sh`).

### 3. Automação e Utilitários
- `server_sommelier.py`: Servidor HTTP local para servir os portais e dashboards.
- `deploy_html.py`: Script para publicação e deploy automático dos assets HTML no servidor web remoto.
- `update_watsonx_logo.py`: Padronização de identidade visual e logomarcas Watsonx.

## 🚀 Como Executar o GLPI ITIL Bridge

```bash
cd glpi-itil
docker-compose up -d
```
