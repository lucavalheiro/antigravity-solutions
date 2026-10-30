# IBM Seismic Enablement Downloader & Sync Automation

Ferramenta automatizada de download, sincronização e organização de materiais de capacitação, sales kits, battlecards e apresentações do IBM Seismic para parceiros de negócios (IBM Business Partners).

## 🚀 Funcionalidades

- **Sincronização Automatizada:** Conecta ao IBM Seismic utilizando credenciais em cache ou sessão do navegador.
- **Estruturação por Categorias:** Organiza automaticamente os arquivos em pastas temáticas (Apresentações de Clientes, Solution Briefs, Battlecards, Guias de Laboratório, Decks Técnicos, etc.).
- **Manifesto Inteligente:** Gera e mantém o `download_manifest.json` com histórico, hash e metadados de cada asset para evitar downloads redundantes.
- **Download Resiliente e Retomável:** Suporte a reconexão automática e download apenas de assets pendentes via `download_remaining.py`.

## 📂 Scripts

- `download_ibm_seismic.py`: Engine principal de extração e download.
- `download_all_assets.py`: Orquestrador de download concorrente com barra de progresso.
- `download_remaining.py`: Validador de integridade e retomada de arquivos parciais.
- `download_manifest.json`: Mapa completo de URLs, categorias e status de download.

## 🛠️ Tecnologias

- Python 3.10+
- `requests`, `urllib3`, `tqdm`
- Integração nativa com a skill Antigravity `ibm-seismic-downloader`.
