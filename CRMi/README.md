# CRMi - Base de Conhecimento e Catálogo de Preços IBM (Outubro 2025)

Este diretório contém a base tratada, mapeada e estruturada da **Tabela de Preços IBM (Outubro 2025)** para integração com o **Frappe CRM** e **ERPNext** no servidor `10.1.0.65`.

---

## 📁 Arquivos Disponíveis

| Arquivo | Descrição | Tamanho |
| :--- | :--- | :--- |
| `produtos_ibm_out_2025.json` | Catálogo completo tratado em formato JSON (12.353 produtos únicos, faixas de preço e metadados). | ~10,3 MB |
| `produtos_ibm_out_2025.csv` | Tabela formatada em CSV (delimitador `;`, UTF-8) com colunas normalizadas e preços em R$. | ~3,9 MB |
| `import_ibm_to_crm.py` | Script pronto para execução de carga em lote no MariaDB / Frappe Docker. | ~2 KB |

---

## 📊 Resumo da Base de Dados

- **Arquivo Original:** `Lista de Preço Out 2025.xlsx`
- **Total de Linhas Originais:** 18.362 linhas
- **Total de Produtos Únicos (SKUs / Part Numbers):** 12.353
- **Moeda:** BRL (Real brasileiro)
- **Vigência Padrão:** 01/01/2025 até 31/12/2025
- **Preço Médio (SRP):** R$ 77.407,41
- **Top Categorias:**
  - *Analytics - Platform* (3.880 registros)
  - *Cloud* (3.251 registros)
  - *Security* (2.556 registros)
  - *Internet of Things* (2.072 registros)
  - *Commerce* (1.756 registros)
  - *Systems - Middleware* (1.461 registros)

---

## 🗺️ Mapeamento de Campos (Frappe CRM & ERPNext)

| Campo na Base | Destino Frappe CRM (`tabCRM Product`) | Destino ERPNext (`tabItem` / `tabItem Price`) |
| :--- | :--- | :--- |
| `product_code` | `product_code` e `name` (ID único) | `item_code` e `name` |
| `product_name` | `product_name` | `item_name` |
| `standard_rate` | `standard_rate` (Preço de Venda Sugerido) | `price_list_rate` na tabela "Standard Selling" / "IBM Out 2025" |
| `brand` | Detalhes da descrição / Busca | `brand` e `item_group` |
| `charge_unit` | Informação no corpo do produto | `stock_uom` / `sales_uom` |
| `full_description` | `description` (Texto rico formatado) | `description` |
| `tiers` | Lista de faixas de volume na descrição | Regras de preço escalonado por quantidade |

---

## 🤖 Integração do Assistente Virtual CRMi

O widget flutuante no CRM ([http://10.1.0.65:8080/crm](http://10.1.0.65:8080/crm)) foi configurado com:
- Nome oficial: **CRMi**
- Indicador de status: **● Online** (sem expor IPs internos)
- Modelo LLM: `qwen36-pro` via Open WebUI em `http://192.168.173.22:3000`
- Conexão em tempo real com o banco de dados MariaDB do container Docker.
