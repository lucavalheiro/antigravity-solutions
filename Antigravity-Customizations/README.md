# Antigravity Customizations (Skills & MCP Servers)

Repositório das extensões, habilidades (Skills) e servidores de protocolo de contexto de modelo (MCP Servers) customizados desenvolvidos para o agente Antigravity.

## 🧩 Componentes

### 1. Skills (`skills/`)
- **`ibm-seismic-downloader/SKILL.md`**: Skill automatizada para navegação, autenticação e download de kits de vendas e habilitação técnica do portal IBM Seismic.

### 2. MCP Servers (`mcp_servers/`)
- **`luciano_ai_server.py`**: Servidor MCP local para integração direta com:
  - Execução de tarefas de programação via Aider no servidor remoto Ubuntu.
  - Inferência local na GPU NVIDIA L4 para economia de tokens.
  - Execução remota de bash (`exec_remote_bash`).
  - Leitura e escrita de arquivos remotos (`read_remote_file`, `write_remote_file`).
  - Monitoramento de telemetria de hardware e GPU (`get_remote_gpu_status`).

## 🛠️ Como Utilizar no Antigravity

Esses arquivos podem ser linkados ou copiados para os diretórios de configuração do Antigravity em:
- Skills: `~/.gemini/config/skills/`
- MCP Servers: `~/.gemini/config/mcp_servers/`
