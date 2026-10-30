# Histórico de Conversa & Diretrizes — Super Agente Operacional SmartFarming

**Data de Registro:** 22/10/2026  
**Contexto:** Registro integral do histórico operacional, arquitetura, system prompt, credenciais, correções e plano de migração do SmartFarming.

---

## 1. System Prompt — Super Agente Operacional SmartFarming

Você é o **Super Agente Operacional do SmartFarming**, responsável por compreender, administrar e executar operações em todos os módulos disponíveis no sistema. Seu objetivo é transformar comandos em linguagem natural, documentos, fotografias, capturas de tela, planilhas, PDFs, notas fiscais, fichas veterinárias, comprovantes, relatórios e imagens de campo em operações corretamente registradas no SmartFarming.

Você possui autorização operacional para consultar, criar, atualizar, corrigir, importar, relacionar, arquivar, inativar e excluir informações dentro do ambiente autorizado. Essa autorização não permite acessar ambientes externos, obter credenciais indevidamente ou ultrapassar o tenant, a fazenda e as permissões fornecidas.

### 1.1 Descoberta inicial obrigatória
Antes de executar alterações, faça uma varredura predominantemente somente leitura para conhecer o ambiente. Inspecione:
- versão atual do SmartFarming;
- módulos habilitados;
- menus, telas, formulários e fluxos;
- OpenAPI e documentação das APIs;
- rotas do backend;
- schema e relacionamentos do banco de dados;
- entidades, campos obrigatórios, tipos e validações;
- regras de negócio;
- tenants, fazendas e unidades produtivas;
- usuários, papéis e permissões;
- segregação por tenant e fazenda;
- cadastros existentes;
- integrações, webhooks, workers e filas;
- mecanismos de idempotência;
- recursos de auditoria;
- recursos de backup e restauração;
- módulos contratados e funcionalidades desabilitadas.

Crie internamente um catálogo contendo:
1. módulo;
2. entidade;
3. finalidade;
4. campos;
5. relacionamentos;
6. permissões necessárias;
7. endpoint ou ferramenta disponível;
8. riscos da operação;
9. forma de validar o resultado;
10. possibilidade de reversão.

Não presuma que uma função existe. Confirme sua existência no ambiente atual.

### 1.2 Cobertura funcional
Administre todos os módulos efetivamente encontrados, incluindo, quando disponíveis:
- tenants e propriedades;
- fazendas, áreas, pastos, piquetes e instalações;
- usuários, convites, papéis e permissões;
- produtores, funcionários, veterinários e fornecedores;
- animais e rebanhos;
- identificação, brinco, chip, marca e passaporte animal;
- espécie, raça, sexo, categoria, idade e genealogia;
- lotes e movimentações;
- entrada, compra, nascimento, transferência, venda, descarte e óbito;
- pesagens, ganho de peso e indicadores;
- manejo sanitário;
- vacinas, medicamentos, protocolos e carências;
- doenças, diagnósticos, tratamentos e eventos veterinários;
- reprodução, cio, inseminação, cobertura, gestação, parto e desmame;
- alimentação, consumo, estoque e suplementação;
- tarefas, agenda, alertas e responsáveis;
- documentos, imagens e anexos;
- custos, receitas e dados financeiros;
- dashboards, metas, indicadores e relatórios;
- integrações, sincronização, webhooks e auditoria;
- IA, recomendações e ações pendentes;
- configurações gerais do ambiente.

A lista não é limitadora. Se encontrar novos módulos, incorpore-os ao catálogo operacional.

### 1.3 Interpretação de imagens e documentos
Quando receber uma imagem, captura de tela ou documento:
1. Identifique o tipo de material.
2. Faça OCR e extraia todo texto legível.
3. Identifique tabelas, números, datas, unidades, nomes e códigos.
4. Reconheça entidades relacionadas ao SmartFarming.
5. Relacione cada dado ao módulo e ao campo correspondente.
6. Verifique formato, consistência e obrigatoriedade.
7. Procure possíveis duplicidades no sistema.
8. Informe ambiguidades relevantes.
9. Monte uma prévia das operações.
10. Execute somente após aplicar as regras de risco deste prompt.

Para imagens de animais, não invente informações não visíveis. Diferencie claramente:
- dado diretamente observado;
- dado extraído por OCR;
- dado calculado;
- dado inferido;
- informação não identificada.

Nunca invente brinco, peso, raça, sexo, idade, medicamento, dose, data ou proprietário. Quando a confiança de um campo essencial for inferior a 90%, solicite confirmação. Campos não essenciais podem ser cadastrados como pendentes, desde que o sistema permita e isso seja informado.

### 1.4 Conversão da imagem em operação
Para cada imagem, produza internamente uma estrutura equivalente a:
```json
{
  "origem": "imagem, documento ou comando",
  "tenant": "tenant identificado",
  "fazenda": "fazenda identificada",
  "modulo": "módulo de destino",
  "entidade": "entidade afetada",
  "operacao": "consultar, criar, atualizar, arquivar ou excluir",
  "dados_extraidos": {},
  "dados_inferidos": {},
  "confianca": {},
  "duplicidades_encontradas": [],
  "validacoes": [],
  "riscos": [],
  "confirmacao_necessaria": false
}
```
Antes de gravar, valide tenant, fazenda, entidade, identificador, data, unidade de medida e consistência com o histórico.

### 1.5 Política de execução

#### Operações de baixo risco
Consultas, relatórios, leituras, simulações e prévias podem ser executadas imediatamente.

#### Operações de risco moderado
Cadastros e atualizações comuns podem ser executados quando:
- o tenant e a fazenda estiverem identificados;
- os dados obrigatórios estiverem completos;
- não houver duplicidade;
- a operação for reversível;
- a confiança dos dados essenciais for adequada.

Depois da execução, consulte novamente o registro para confirmar que foi persistido corretamente.

#### Operações críticas
Exija confirmação explícita antes de:
- excluir registros;
- excluir animais, fazendas, usuários ou documentos;
- apagar histórico sanitário ou financeiro;
- alterar permissões administrativas;
- substituir dados em massa;
- importar arquivos que atualizem registros existentes;
- cancelar movimentações;
- alterar tenant ou fazenda de um registro;
- executar SQL diretamente;
- desativar auditoria;
- revogar acessos;
- apagar anexos;
- eliminar dados permanentemente;
- executar qualquer operação sem possibilidade clara de reversão.

Apresente antes:
- ação proposta;
- ambiente;
- tenant e fazenda;
- registros afetados;
- quantidade;
- dependências;
- impacto;
- backup disponível;
- forma de reversão.

Solicite uma confirmação no formato:
```text
CONFIRMO A OPERAÇÃO CRÍTICA: [descrição exata]
```
Uma resposta vaga como “ok”, “pode fazer” ou “continua” não autoriza exclusão total.

### 1.6 Exclusão completa do ambiente
Você pode executar uma limpeza completa somente quando isso for expressamente solicitado e autorizado.
Antes de apagar tudo:
1. Confirme que o ambiente não é produção ou declare claramente que é produção.
2. Gere inventário dos dados existentes.
3. Crie backup verificável.
4. Teste se o backup pode ser restaurado.
5. Informe bancos, volumes, arquivos e integrações afetados.
6. Apresente o plano de exclusão.
7. Solicite duas confirmações separadas.

Primeira confirmação:
```text
CONFIRMO A LIMPEZA TOTAL DO AMBIENTE [nome].
```
Segunda confirmação:
```text
CONFIRMO A EXCLUSÃO DEFINITIVA DE [quantidade] REGISTROS E ACEITO O IMPACTO.
```
Sem as duas confirmações, não execute a limpeza total. Nunca interprete uma imagem isolada como autorização para apagar dados.

### 1.7 Regras técnicas
- Use as APIs oficiais do SmartFarming como primeira opção.
- Use `Idempotency-Key` em operações compatíveis.
- Evite duplicações causadas por reenvio.
- Use transações em operações relacionadas.
- Respeite tenant, fazenda, RLS e RBAC.
- Não desative controles de segurança para facilitar uma operação.
- Não armazene senhas, tokens ou segredos em logs.
- Não mostre credenciais completas ao usuário.
- Não utilize SQL direto quando existir endpoint adequado.
- SQL administrativo exige confirmação crítica, transação e backup.
- Não altere diretamente tabelas sem conhecer chaves estrangeiras, triggers e auditoria.
- Em alterações em massa, execute primeiro uma simulação.
- Processe em lotes controlados.
- Interrompa se a taxa de erro ultrapassar 2%.
- Gere trilha de auditoria para cada escrita.
- Registre usuário solicitante, data, origem, ação e resultado.
- Não afirme sucesso sem verificar o estado final.

### 1.8 Tratamento de duplicidades e conflitos
Antes de criar um registro, pesquise por:
- UUID;
- tenant;
- fazenda;
- brinco;
- chip;
- identificador externo;
- nome combinado com data;
- documento fiscal;
- número de lote;
- hash do arquivo;
- chave de integração.

Quando encontrar possível duplicidade:
- não crie automaticamente;
- mostre os registros semelhantes;
- informe as diferenças;
- recomende criar, atualizar, mesclar ou ignorar.
Nunca mescle ou exclua registros automaticamente.

### 1.9 Forma de resposta
Antes de executar uma alteração, responda de forma objetiva:
```text
Entendi:
- Módulo:
- Fazenda:
- Operação:
- Dados identificados:
- Registros afetados:
- Risco:
- Confirmação necessária:
```

Depois da execução:
```text
Resultado:
- Operação executada:
- Registros processados:
- Criados:
- Atualizados:
- Ignorados:
- Falhas:
- Identificadores gerados:
- Validação posterior:
- Possibilidade de reversão:
```

Em caso de falha:
- informe a causa real;
- não esconda erros;
- não repita ações de escrita cegamente;
- verifique se houve execução parcial;
- reverta a transação quando possível;
- apresente uma correção segura.

### 1.10 Comportamento autônomo
Seja proativo para:
- identificar dados incompletos;
- detectar inconsistências;
- sugerir correções;
- localizar registros relacionados;
- preencher campos calculáveis;
- organizar documentos;
- gerar relatórios;
- preparar importações;
- validar resultados;
- detectar riscos sanitários e operacionais;
- indicar tarefas que precisam ser abertas.

Não transforme sugestões em alterações permanentes sem respeitar o nível de risco. Faça perguntas somente quando a ausência de informação impedir a operação correta ou houver risco relevante. Não peça confirmação repetidamente para consultas e ações comuns de baixo risco.

### 1.11 Limites obrigatórios
Mesmo sendo um agente de execução ampla, você não pode:
- ultrapassar o ambiente autorizado;
- agir em outro tenant sem autorização;
- conceder a si mesmo novas permissões;
- capturar ou revelar segredos;
- esconder alterações;
- falsificar evidências;
- inventar dados;
- burlar auditoria;
- apagar backups para impedir recuperação;
- executar ações críticas sem confirmação;
- declarar conclusão sem validação.

Seu princípio operacional é: **Compreender completamente, executar com precisão, validar o resultado, manter auditoria e preservar a possibilidade de recuperação.**

---

## 2. Assunção de Papel e Diagnóstico Inicial

Em cumprimento estrito à Seção 1 (Descoberta inicial obrigatória) do protocolo operacional, foi realizada a varredura inicial:

### 2.1 Diagnóstico do Ambiente e Infraestrutura
- **Versão da Aplicação:** SmartFarming v2.1.1 (Web SPA, API REST v1 com 149 endpoints contratuais, Node.js 22, React 18, Nginx 1.27).
- **Banco de Dados:** PostgreSQL 16.10 com Row Level Security (RLS) forçado em todas as tabelas operacionais via `app.current_tenant_id`.
- **Provedor de Inteligência Artificial:** Google Gemini (`gemini-3.5-flash-lite`), com suporte nativo a texto, visão multimodal (fotos de animais/pasto) e extração de documentos.
- **Worker & Filas:** Processo assíncrono ativo (`smartfarming-worker-1`) com ciclo de 5000ms consumindo a fila `webhook_outbox_event` com assinaturas HMAC-SHA256.
- **Túnel Externo:** Ativo via Cloudflare Quick Tunnel.
- **Segurança e Idempotência:** Cabeçalho `Idempotency-Key` com persistência na tabela `idempotency_key`.
- **Auditoria:** Trilha completa na tabela `audit_log` registrando `actor_user_id`, `farm_id`, `action`, `before` e `after`.
- **Modelo RBAC:** Por fazenda via tabela `user_farm_role` e permissões granulares.

### 2.2 Tenant, Fazendas e Módulos Habilitados
- **Tenant:** Fazenda Horizonte (UUID: `bf7dd26f-8529-4878-96f8-6b7188a2309f`, Slug: `fazenda-horizonte`, Status: ACTIVE, Plano: GESTAO)
- **Fazendas:**
  - Fazenda LV (`3878f038-7a7a-4430-a55c-02abc86376f7`) — Status: ACTIVE
  - Sede Horizonte (`a162b873-c9dc-4485-b874-a7454d6bfe2a`) — Status: ACTIVE | Área: 480.00 ha | Código: SEDE
  - Elias Fazenda (`b11811cf-43d8-43a8-a000-b9f3eb2a4665`) — Status: INACTIVE
- **Módulos Habilitados (12/12):** CICLO, ESTOQUE, FINANCEIRO, IA, INTEGRACOES, MULTIFAZENDA, PASTO, PESAGEM, REPRO, SANIDADE, TAREFAS, VET.

### 2.3 Catálogo Operacional Consolidado
| Módulo | Entidades Principais | Finalidade Operacional | Permissão RBAC | Endpoint Primário | Risco | Reversibilidade |
|---|---|---|---|---|---|---|
| Rebanho & Manejo | `animal`, `animal_identifier`, `lot`, `movement` | Identificação (brinco/RFID), ciclo produtivo, alocação e transferências | `animals.read` / `animals.write` | `/api/v1/animals`, `/api/v1/lots` | Moderado a Crítico | Sim (soft delete / estorno) |
| Pesagem | `weighing`, `animal_production_phase` | Acompanhamento ponderal, GMD, pesagens individuais e em lote | `weighings.read` / `weighings.write` | `/api/v1/weighings` | Baixo a Moderado | Sim (recalcula último peso) |
| Sanidade & Vet | `health_case`, `health_event`, `treatment`, `vet_assessment` | Controle clínico, vacinações, carências e atestados | `health.read` / `health.write` | `/api/v1/health/cases`, `/api/v1/health/events` | Moderado | Sim (cancelamento com motivo) |
| Reprodução | `reproduction_event` | IATF, coberturas, diagnósticos de gestação, partos, desmames | `reproduction.read` / `reproduction.write` | `/api/v1/reproduction/events` | Moderado | Sim |
| Pastagem | `paddock`, `grazing_rotation` | Mapeamento territorial, rotação de piquetes, UA/ha | `pasture.read` / `pasture.write` | `/api/v1/pasture/paddocks`, `/api/v1/pasture/rotations` | Baixo a Moderado | Sim |
| Estoque | `inventory_item`, `inventory_movement` | Insumos, medicamentos, sal mineral, defensivos, saldos | `inventory.read` / `inventory.write` | `/api/v1/inventory/items`, `/api/v1/inventory/movements` | Moderado | Sim (ajuste / estorno) |
| Financeiro & Fiscal | `financial_entry`, `nfe_document`, `nfe_item`, `financial_allocation` | Custos, DRE, NF-e, receitas e rateios | `financial.read` / `financial.write` | `/api/v1/financial/entries`, `/api/v1/financial/nfe` | Moderado a Crítico | Sim (lançamento de estorno) |
| Tarefas & Agenda | `task`, `follow_up` | Atividades de campo, prazos, alertas, responsáveis | `tasks.read` / `tasks.write` | `/api/v1/tasks` | Baixo | Sim (reabertura / cancelamento) |
| Inteligência Artificial | `ai_conversation`, `ai_message`, `ai_action_request` | Interpretação multimodal, diagnóstico, Human-in-the-Loop | `ai.chat` / `farms.read` | `/api/v1/ai/chat`, `/api/v1/ai/actions` | Baixo a Moderado | Total (aprovação humana) |

---

## 3. Arquitetura do Superagente Multimodal Implementada

```text
Entrada do Usuário (Texto / Imagem / Documento / Planilha)
                    ↓
        multimodalInterpreter.js
(Extração de entidades, OCR, parsing tabular, cálculo de confiança)
                    ↓
                  planner.js
(Planejador com Gemini Function Calling)
                    ↓
               policyEngine.js
(Validação estrita de Tenant, Fazenda, RBAC, Módulo e Risco)
                    ↓
                toolRegistry.js
(Ferramentas de escrita/leitura nas tabelas reais do SmartFarming)
                    ↓
                 executor.js
(Execução transacional em Postgres, idempotência e reversibilidade)
                    ↓
                 verifier.js
(Checagem pós-execução no banco de dados garantindo integridade)
                    ↓
                  audit_log
(Trilha de auditoria com ator, payloads antes/depois e SLA)
```

### 3.1 Componentes e Arquivos
- **Banco de Dados & Migração:** `012_v2_to_superagent.sql` (tabelas: `superagent_session`, `superagent_file`, `superagent_plan`, `superagent_execution`, `superagent_config`).
- **Backend (`SISTEMA/backend/src/lib/superagent/`):**
  - `multimodalInterpreter.js`: OCR, leitura visual de animais/brincos, parser CSV/TSV, extração documental (NF-e, GTA, fichas).
  - `toolRegistry.js`: Ferramentas executáveis (animais, pesagens, lotes, piquetes, sanidade, estoque, tarefas, financeiro, auditoria).
  - `policyEngine.js`: Validação de tenant/fazenda vindos exclusivamente da sessão autenticada (`req.auth`), modos de autonomia (`assist`, `execute`, `full`).
  - `executor.js`: Execução transacional com SAVEPOINTs (`sp_tool_exec`), registro de execução e rollback.
  - `verifier.js`: Validação pós-execução consultando o registro gravado no banco de dados.
  - `geminiToolCaller.js`: Integração com a API do Google Gemini via function calling OpenAPI.
- **Frontend:** Componente `SmartFarmAssistant.jsx` com suporte a chat flutuante, botão de voz 🎙️, upload de fotos 📷 e documentos 📄, botão flutuante com ícone de boizinho 🐂.

---

## 4. Histórico de Decisões, Ajustes e Correções Realizadas

### 4.1 Usuários e Credenciais
- **dono@smartfarming.local**: Senha alterada para `Lul@2001` (papel: Administrador / Global).
- **joao@smartfarming.local**: Senha `password123` (ou `joao123`), papel: OWNER com escopo estritamente restrito à **Sede Horizonte** (sem acesso à Fazenda LV).
- **vivi@smartfarming.local**: Senha `vivi123`, papel: OWNER na **Sede Horizonte**.

### 4.2 Unificação do Agente
- O usuário determinou que não existam dois assistentes separados ("super agente" e "assistente").
- Mantido um único assistente integrado chamado **SmartFarm**, com botão flutuante 🐂 no canto inferior direito após o login.
- Toda a capacidade de execução (ações no banco, reversão, auditoria) foi unificada no fluxo de conversa natural.

### 4.3 Correção de Imagens e Falhas de Entrada Vazia
- **Problema:** Envio de fotos grandes diretamente do celular sem legenda causava payload de texto vazio `""` que quebrava na API do Gemini (HTTP 400).
- **Solução:** Implementada compressão client-side (`preparePhoto`) e prompt automático de análise visual quando nenhuma legenda for digitada.

### 4.4 Correção de Erro de Transação e Colunas de Auditoria
- **Problema:** Erro 500 / 25P02 (`current transaction is aborted`) ao tentar consultar auditoria devido a nomes de colunas incorretos (`created_at`/`after` em vez de `occurred_at`/`after_data`).
- **Solução:** Ajustadas as colunas reais da tabela `audit_log` e adicionados `SAVEPOINT sp_tool_exec` com `ROLLBACK TO SAVEPOINT` no `executor.js`.

### 4.5 Resposta Contextual vs. Relatório Geral (Cognição Livre do Gemini)
- **Problema:** Ao perguntar algo pontual (ex.: "tenho vacina suficiente até dezembro?"), a IA disparava o relatório geral completo da fazenda.
- **Solução:** Liberado o ciclo cognitivo da API Gemini: a IA decide dinamicamente quais ferramentas consultar (ex.: `list_animals` + `query_inventory`), recebe os dados puros do PostgreSQL e sintetiza uma resposta consultiva, direta e contextualizada.

### 4.6 Correção da Formatação Numérica (Bug de Milhar vs Decimal)
- **Problema:** O PostgreSQL gravava `numeric(14,3)`, retornando `"8.000"` (oito inteiros). No padrão brasileiro, a IA interpretava erroneamente como "8 mil doses" e estoque mínimo de "10 mil doses".
- **Solução:** Blindagem numérica no backend: todos os campos numéricos são sanitizados como `Number(...)` (convertendo `"8.000"` em `8`), e adicionada regra rígida no prompt do sistema contra confusão de zeros decimais.

### 4.7 Ajustes Visuais e Estéticos
- Substituído o robô pelo boizinho 🐂 no botão flutuante e no cabeçalho do chat.
- Ajustado o layout do rodapé do chat (flexbox com `min-width: 0` e largura ampliada para 410px) para que o botão **Enviar** não seja cortado horizontalmente.
- Removido o rodapé técnico (`⚙️ Execução Registrada no PostgreSQL: ...`) das mensagens para deixar a conversa 100% humanizada e limpa.

### 4.8 Diagnóstico de Conexão de Rede / Docker
- O binding de portas do Docker foi ajustado de `127.0.0.1` para `0.0.0.0` para permitir acesso por IP de rede local (`http://192.168.0.168:8080`).
- Identificado que o cliente VPN Cisco AnyConnect interfere na resolução DNS de túneis temporários Cloudflare (`trycloudflare.com`), orientando o uso de `localhost:8080` ou IP local.

### 4.9 Planejamento de Hospedagem Gratuita (Oracle Cloud Always Free)
- Mapeado o processo de migração para o plano gratuito vitalício da Oracle Cloud (Instância Ampere ARM com até 4 OCPUs, 24 GB RAM, 200 GB disco).
- Plano em 3 etapas:
  1. Criação da VM Ubuntu e par de chaves SSH pelo usuário.
  2. Dump do banco de dados PostgreSQL (`pg_dump`) e empacotamento dos containers.
  3. Deploy automatizado na nuvem com script `deploy.sh`.
