import json
import urllib.request
import urllib.error
import io
import sys
import frappe
from frappe import _

LLM_API_URL = "http://192.168.173.22:3000/api/chat/completions"
LLM_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjVkODBkM2UwLWViODctNDI0Ni05N2RkLTFkZDY1OGE0YjBjYSIsImV4cCI6MTc5MzcyODE1MSwianRpIjoiZGU5Y2JjNGUtYjhjNS00NTcxLTgyZWItNjQxMWUwMWYzMzYzIiwiaWF0IjoxNzkxMzA4OTUxfQ.oix-994ueq9OHxUTtP_AvJiLiDbwbCNKXmR583cw21s"
DEFAULT_MODEL = "qwen36-pro"
MAX_TOOL_LOOPS = 5

SYSTEM_PROMPTS = {
    "erpi": """Você é o **ERPi**, a Inteligência Artificial corporativa oficial e Super Agente Operacional de todo o **ERPNext**.
Você possui autorização e privilégios de **Owner / Administrador do Sistema** para executar, testar, avaliar, deletar, criar, atualizar e ler qualquer dado ou registro em TODOS os módulos do ERP:
- **Accounting (Contabilidade & Financeiro):** Faturas de Venda (`Sales Invoice`), Faturas de Compra (`Purchase Invoice`), Contas a Receber/Pagar, Plano de Contas (`Account`), Diário Geral (`Journal Entry`), Balanços e Fluxo de Caixa.
- **Stock (Estoque):** Catálogo de itens (12.364 itens, incluindo os 12.353 itens IBM), saldos em armazéns (`Warehouse`), movimentações (`Stock Entry`), números de série e lotes.
- **Selling (Vendas):** Cotações (`Quotation`), Pedidos de Venda (`Sales Order`), Clientes (`Customer`), Lista de Preços oficial `IBM Out 2025` em Reais (BRL).
- **Buying (Compras):** Pedidos de Compra (`Purchase Order`), Solicitações de Material (`Material Request`), Fornecedores (`Supplier`).
- **Manufacturing (Manufatura / Produção):** Ordens de Produção (`Work Order`), Listas de Materiais (`BOM`), postos de trabalho e operações.
- **Assets (Ativos & Patrimônio):** Ativos fixos (`Asset`), depreciação contábil mensal, manutenções preventivas.
- **Projects (Projetos):** Projetos (`Project`), Tarefas (`Task`), Apontamentos de horas (`Timesheet`), acompanhamento de rentabilidade.
- **Quality (Qualidade):** Inspeções de Qualidade (`Quality Inspection`), metas e não-conformidades.
- **Framework & Configurações:** Consultas diretas SQL no MariaDB, scripts Python em lote e auditoria de sistema.

DIRETRIZES:
1. **Ação Direta:** Quando o usuário pedir qualquer consulta, relatório, criação, teste ou exclusão, EXECUTE imediatamente as ferramentas cabíveis.
2. **Dados Reais:** Não invente números nem dados. Sempre consulte as tabelas reais do ERPNext no MariaDB.
3. **Formatação Executiva:** Apresente respostas estruturadas com tabelas markdown, marcadores e negritos em português do Brasil.
""",
    "crmi": """Você é o **CRMi**, o copiloto comercial inteligente oficial do **Frappe CRM**.
Você possui autorização e privilégios de **Owner / Administrador** para gerenciar:
- **CRM Leads & Deals:** Cadastro, qualificação, avanço de etapas de pipeline e conversão em Clientes do ERP.
- **Catálogo de Preços IBM (Outubro 2025):** 12.353 part numbers com faixas de desconto por volume (tiers) e métricas de faturamento em Reais (BRL).
- **Cotações Comerciais:** Elaboração rápida de propostas e busca de itens IBM por SKU ou nome.
- **Consultas no Banco:** Acesso completo ao MariaDB e ferramentas Frappe.

DIRETRIZES:
1. Execute as ferramentas nativas para criar leads, buscar produtos ou alterar negócios.
2. Utilize formatação amigável, clara e comercial em português do Brasil.
""",
    "default": """Você é o **ERPi / CRMi Copilot**, a Inteligência Artificial unificada oficial do ERPNext e Frappe CRM, com autorização de **Owner / Administrador Total** em todos os módulos empresariais e comerciais. Execute ferramentas diretamente para ler, criar, alterar, deletar e testar qualquer registro no sistema."""
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "Executa comando SQL direto no banco de dados MariaDB do ERPNext/CRM (SELECT, INSERT, UPDATE, DELETE).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Comando SQL a executar"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_records",
            "description": "Lista documentos de qualquer DocType no ERPNext/CRM com filtros, campos e limite.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctype": {"type": "string", "description": "Nome do DocType (ex: Item, Customer, CRM Lead, CRM Deal, Sales Order, Sales Invoice, etc.)"},
                    "filters": {"type": "object", "description": "Filtros chave-valor ou lista"},
                    "fields": {"type": "array", "items": {"type": "string"}, "description": "Lista de campos a retornar"},
                    "order_by": {"type": "string", "description": "Ordenação (ex: 'creation desc')"},
                    "limit": {"type": "integer", "description": "Limite de registros (padrão 20)"}
                },
                "required": ["doctype"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_record",
            "description": "Obtém todos os dados e tabelas filhas de um documento específico pelo DocType e ID/Nome.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctype": {"type": "string", "description": "Nome do DocType"},
                    "name": {"type": "string", "description": "ID/Nome do documento"}
                },
                "required": ["doctype", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_record",
            "description": "Cria um novo documento de qualquer DocType no ERPNext ou CRM com permissão de Administrador.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctype": {"type": "string", "description": "Nome do DocType a ser criado"},
                    "doc_data": {"type": "object", "description": "Dicionário com os campos do documento"}
                },
                "required": ["doctype", "doc_data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_record",
            "description": "Atualiza campos de um documento existente no ERPNext ou CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctype": {"type": "string", "description": "Nome do DocType"},
                    "name": {"type": "string", "description": "ID/Nome do documento"},
                    "values": {"type": "object", "description": "Dicionário com os campos e novos valores a atualizar"}
                },
                "required": ["doctype", "name", "values"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_record",
            "description": "Exclui permanentemente um documento de qualquer DocType do banco de dados.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctype": {"type": "string", "description": "Nome do DocType"},
                    "name": {"type": "string", "description": "ID/Nome do documento a ser excluído"}
                },
                "required": ["doctype", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_record",
            "description": "Submete um documento que requer aprovação formal/submissão contábil (Faturas, Pedidos, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctype": {"type": "string", "description": "Nome do DocType"},
                    "name": {"type": "string", "description": "ID/Nome do documento a submeter"}
                },
                "required": ["doctype", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_record",
            "description": "Cancela um documento previamente submetido no ERPNext.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctype": {"type": "string", "description": "Nome do DocType"},
                    "name": {"type": "string", "description": "ID/Nome do documento a cancelar"}
                },
                "required": ["doctype", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_doctype",
            "description": "Inspeciona o schema de um DocType (campos existentes, tipos de dados, campos obrigatórios e links).",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctype": {"type": "string", "description": "Nome do DocType para inspecionar"}
                },
                "required": ["doctype"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "Executa um bloco de código Python com acesso completo ao ambiente Frappe (frappe.db, frappe.get_doc, etc.) para testes, avaliações, scripts em lote e diagnósticos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código Python a ser executado no servidor"}
                },
                "required": ["code"]
            }
        }
    }
]

def tool_execute_sql(query):
    query_clean = query.strip()
    is_write = any(query_clean.upper().startswith(k) for k in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"])
    res = frappe.db.sql(query_clean, as_dict=True)
    if is_write:
        frappe.db.commit()
        return {"status": "success", "message": "Comando executado e gravado com sucesso no banco de dados."}
    if isinstance(res, list):
        return res[:40]
    return res

def tool_list_records(doctype, filters=None, fields=None, order_by=None, limit=20):
    limit = min(limit or 20, 50)
    if not fields:
        fields = ["name", "owner", "creation", "modified"]
    records = frappe.get_all(
        doctype,
        filters=filters,
        fields=fields,
        order_by=order_by or "modified desc",
        limit_page_length=limit
    )
    return records

def tool_get_record(doctype, name):
    doc = frappe.get_doc(doctype, name)
    data = doc.as_dict()
    if "password" in data:
        data["password"] = "******"
    return data

def tool_create_record(doctype, doc_data):
    doc_data["doctype"] = doctype
    doc = frappe.get_doc(doc_data)
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "success", "doctype": doctype, "name": doc.name, "message": f"Registro {doc.name} ({doctype}) criado com sucesso."}

def tool_update_record(doctype, name, values):
    doc = frappe.get_doc(doctype, name)
    doc.update(values)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "success", "doctype": doctype, "name": doc.name, "message": f"Registro {doc.name} ({doctype}) atualizado com sucesso."}

def tool_delete_record(doctype, name):
    frappe.delete_doc(doctype, name, force=1, ignore_permissions=True)
    frappe.db.commit()
    return {"status": "success", "doctype": doctype, "name": name, "message": f"Registro {name} ({doctype}) excluído permanentemente com sucesso."}

def tool_submit_record(doctype, name):
    doc = frappe.get_doc(doctype, name)
    doc.submit()
    frappe.db.commit()
    return {"status": "success", "doctype": doctype, "name": doc.name, "docstatus": doc.docstatus, "message": f"Documento {doc.name} submetido com sucesso."}

def tool_cancel_record(doctype, name):
    doc = frappe.get_doc(doctype, name)
    doc.cancel()
    frappe.db.commit()
    return {"status": "success", "doctype": doctype, "name": doc.name, "docstatus": doc.docstatus, "message": f"Documento {doc.name} cancelado com sucesso."}

def tool_inspect_doctype(doctype):
    meta = frappe.get_meta(doctype)
    fields_info = []
    for f in meta.fields:
        if f.fieldname and not f.hidden:
            fields_info.append({
                "fieldname": f.fieldname,
                "label": f.label,
                "fieldtype": f.fieldtype,
                "options": f.options,
                "reqd": bool(f.reqd)
            })
    return {
        "doctype": doctype,
        "is_submittable": bool(meta.is_submittable),
        "naming_rule": meta.naming_rule or "auto",
        "fields": fields_info
    }

def tool_execute_python(code):
    stdout_buf = io.StringIO()
    old_stdout = sys.stdout
    local_scope = {"frappe": frappe, "result": None}
    try:
        sys.stdout = stdout_buf
        exec(code, {"frappe": frappe}, local_scope)
        frappe.db.commit()
        output = stdout_buf.getvalue()
        res = local_scope.get("result")
        return {"status": "success", "stdout": output, "result": str(res) if res is not None else None}
    except Exception as e:
        frappe.db.rollback()
        return {"status": "error", "error": str(e), "stdout": stdout_buf.getvalue()}
    finally:
        sys.stdout = old_stdout

TOOL_DISPATCHER = {
    "execute_sql": lambda args: tool_execute_sql(args["query"]),
    "list_records": lambda args: tool_list_records(args["doctype"], args.get("filters"), args.get("fields"), args.get("order_by"), args.get("limit", 20)),
    "get_record": lambda args: tool_get_record(args["doctype"], args["name"]),
    "create_record": lambda args: tool_create_record(args["doctype"], args["doc_data"]),
    "update_record": lambda args: tool_update_record(args["doctype"], args["name"], args["values"]),
    "delete_record": lambda args: tool_delete_record(args["doctype"], args["name"]),
    "submit_record": lambda args: tool_submit_record(args["doctype"], args["name"]),
    "cancel_record": lambda args: tool_cancel_record(args["doctype"], args["name"]),
    "inspect_doctype": lambda args: tool_inspect_doctype(args["doctype"]),
    "execute_python": lambda args: tool_execute_python(args["code"]),
}

def call_llm(messages, tools=None):
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "stream": False
    }
    if tools:
        payload["tools"] = tools

    req = urllib.request.Request(
        LLM_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))

@frappe.whitelist(allow_guest=False)
def chat(message, history=None, mode=None):
    if not message or not message.strip():
        agent_title = "ERPi" if mode == "erpi" else "CRMi / ERPi"
        return {"reply": f"Olá! Eu sou o {agent_title}, sua IA com acesso total ao ERPNext e Frappe CRM. Como posso te ajudar?"}

    # Selecionar o prompt do sistema apropriado
    selected_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])
    messages = [{"role": "system", "content": selected_prompt}]

    # Injeta histórico recente
    if history and isinstance(history, list):
        for h in history[-6:]:
            role = h.get("role")
            content = h.get("content")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message.strip()})

    try:
        for _ in range(MAX_TOOL_LOOPS):
            resp = call_llm(messages, tools=TOOLS_SCHEMA)
            choice = resp.get("choices", [{}])[0]
            finish_reason = choice.get("finish_reason")
            msg_obj = choice.get("message", {})

            messages.append(msg_obj)

            if finish_reason == "tool_calls" and msg_obj.get("tool_calls"):
                for tool_call in msg_obj["tool_calls"]:
                    tool_id = tool_call.get("id")
                    fn_data = tool_call.get("function", {})
                    fn_name = fn_data.get("name")
                    fn_args_str = fn_data.get("arguments", "{}")
                    
                    try:
                        args = json.loads(fn_args_str) if isinstance(fn_args_str, str) else fn_args_str
                    except Exception:
                        args = {}

                    handler = TOOL_DISPATCHER.get(fn_name)
                    if handler:
                        try:
                            result = handler(args)
                        except Exception as e:
                            result = {"status": "error", "error": str(e)}
                    else:
                        result = {"status": "error", "error": f"Ferramenta '{fn_name}' não encontrada."}

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "content": json.dumps(result, ensure_ascii=False, default=str)
                    })
            else:
                reply_text = msg_obj.get("content", "Operação concluída.")
                return {"reply": reply_text, "model": DEFAULT_MODEL, "agent": mode or "erpi"}

        final_resp = call_llm(messages)
        final_choice = final_resp.get("choices", [{}])[0]
        final_text = final_choice.get("message", {}).get("content", "Operações executadas.")
        return {"reply": final_text, "model": DEFAULT_MODEL, "agent": mode or "erpi"}

    except Exception as e:
        frappe.log_error(f"Erro no ERPi/CRMi Copilot: {str(e)}")
        return {"reply": f"⚠️ Ocorreu uma instabilidade na execução do copiloto: {str(e)}"}

@frappe.whitelist(allow_guest=False)
def ping():
    return {
        "status": "online",
        "agents": ["ERPi", "CRMi"],
        "llm_model": DEFAULT_MODEL,
        "llm_url": LLM_API_URL,
        "mode": "autonomous_enterprise_owner_agent",
        "tools_count": len(TOOLS_SCHEMA)
    }
