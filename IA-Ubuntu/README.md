# IA-Ubuntu - Configuração de Agentes e GPU NVIDIA Local

Configuração de regras e orquestração de ambiente de desenvolvimento remoto integrado ao Antigravity e ao servidor Ubuntu com aceleração por GPU dedicada.

## 🎯 Objetivo

Fornecer regras contextuais (`.agents/rules`) e configuração de MCP (`mcp_config.json`) para orquestração automática do servidor de desenvolvimento com GPU NVIDIA L4 (`192.168.173.22`).

## ⚙️ Capacidades Configuradas

- **Gatilho de Execução Remota (`gpuubuntu`):** Roteamento transparente de tarefas de desenvolvimento para execução no servidor local Ubuntu.
- **Aceleração por Hardware:** Processamento de inferência e raciocínio na GPU NVIDIA L4 local, economizando quotas de API externas.
- **Desenvolvimento Autônomo com Aider:** Programação assistida remota com commits automáticos e rastreabilidade.
- **Terminal e Ferramentas Remotas:** Execução via MCP (`exec_remote_bash`, `read_remote_file`, `write_remote_file`).
