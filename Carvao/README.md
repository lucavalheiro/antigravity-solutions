# Carvão Mattos - Gestão de Vendas, Pedidos & IA Mattinhos

Sistema completo de gestão comercial, controle de estoque e vendas com automação integrada via IA e WhatsApp.

## 🚀 Funcionalidades

- **Gestão de Pedidos e Vendas:** Emissão, acompanhamento e histórico de pedidos de carvão em diferentes tipos de embalagens e volumes.
- **Assistente Inteligente (Mattinhos IA):** Integração com Google Gemini AI para suporte ao cliente, recomendações e automação de atendimento.
- **Integração WhatsApp:** Conexão com a Evolution API para comunicação e disparo automatizado de status e pedidos.
- **OCR & Processamento de Documentos:** Extração automatizada de comprovantes e documentos.
- **API REST Moderna:** Desenvolvida em FastAPI com documentação Swagger automática (`/docs`).
- **Deploy Containerizado:** Suporte nativo a Docker e Docker Compose.

## 🛠️ Tecnologias

- **Linguagem & Framework:** Python 3.11+, FastAPI, Pydantic, Uvicorn
- **Banco de Dados:** SQLite
- **IA & NLP:** Google Gemini API (`google-generativeai`), DuckDuckGo Search API
- **Containerização:** Docker, Docker Compose

## 📦 Como Executar

1. Copie o arquivo de variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Configure sua GEMINI_API_KEY no arquivo .env
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Inicie o servidor:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   Ou utilize Docker:
   ```bash
   docker-compose up -d --build
   ```
