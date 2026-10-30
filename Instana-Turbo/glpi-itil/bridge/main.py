import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("instana-glpi-bridge")

GLPI_URL = os.getenv("GLPI_URL", "http://glpi-app")
GLPI_API_URL = os.getenv("GLPI_API_URL", f"{GLPI_URL}/apirest.php")
GLPI_APP_TOKEN = os.getenv("GLPI_APP_TOKEN", "InstanaGLPIToken2026")
GLPI_USER_TOKEN = os.getenv("GLPI_USER_TOKEN", "InstanaUserToken2026")
INSTANA_BASE_URL = os.getenv("INSTANA_BASE_URL", "https://10.1.0.65.nip.io")

# ITIL Mappings
CATEGORY_AIOPS_CRITICAL = int(os.getenv("CATEGORY_AIOPS_CRITICAL", "13")) # Instana - Incidentes Críticos (AIOps)
CATEGORY_AIOPS_WARNING = int(os.getenv("CATEGORY_AIOPS_WARNING", "14"))  # Instana - Degradação & Anomalias (AIOps)
GROUP_ASSIGN_N2 = int(os.getenv("GROUP_ASSIGN_N2", "2"))                 # N2 - Suporte a Aplicações & AIOps
DEFAULT_COMPUTER_CI_ID = int(os.getenv("DEFAULT_COMPUTER_CI_ID", "1"))    # 192.168.173.22 - Luciano GPU Server

app = FastAPI(
    title="Instana <-> GLPI ITIL Integration Bridge",
    description="Bridge oficial de integração AIOps entre IBM Instana e GLPI com Gestão de Incidentes ITIL",
    version="1.0.0"
)

session_cache = {
    "token": None
}

def get_glpi_session() -> str:
    """Obtém ou reutiliza o token de sessão da API REST do GLPI."""
    if session_cache["token"]:
        return session_cache["token"]
    
    url = f"{GLPI_API_URL}/initSession?user_token={GLPI_USER_TOKEN}"
    logger.info(f"Solicitando nova sessao GLPI: {url}")
    try:
        resp = requests.get(url, headers={"App-Token": GLPI_APP_TOKEN}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        token = data.get("session_token")
        if not token:
            raise ValueError(f"Sessao retornou resposta invalida: {data}")
        session_cache["token"] = token
        logger.info(f"Sessao GLPI autenticada com sucesso (token: {token[:8]}...)")
        return token
    except Exception as e:
        logger.error(f"Erro ao autenticar no GLPI: {e}")
        raise

def glpi_request(method: str, path: str, json_data: Any = None, params: Any = None) -> requests.Response:
    """Executa requisição à API do GLPI com tratamento automático de expiração de sessão."""
    token = get_glpi_session()
    headers = {
        "App-Token": GLPI_APP_TOKEN,
        "Session-Token": token,
        "Content-Type": "application/json"
    }
    url = f"{GLPI_API_URL}/{path.lstrip('/')}"
    
    resp = requests.request(method, url, headers=headers, json=json_data, params=params, timeout=15)
    if resp.status_code == 401:
        logger.warning("Token de sessao expirado. Renovando token...")
        session_cache["token"] = None
        new_token = get_glpi_session()
        headers["Session-Token"] = new_token
        resp = requests.request(method, url, headers=headers, json=json_data, params=params, timeout=15)
    return resp

def find_ticket_by_instana_issue(issue_id: str) -> Optional[Dict[str, Any]]:
    """Localiza chamado aberto correspondente ao Issue ID do Instana."""
    try:
        resp = glpi_request("GET", "search/Ticket", params={
            "criteria[0][field]": "1", # Name
            "criteria[0][searchtype]": "contains",
            "criteria[0][value]": issue_id,
            "forcedisplay[0]": "1",
            "forcedisplay[1]": "2", # id
            "forcedisplay[2]": "12" # status
        })
        if resp.status_code == 200:
            data = resp.json()
            rows = data.get("data", [])
            for row in rows:
                ticket_id = row.get("2") or row.get("id")
                status = row.get("12") or row.get("status")
                if ticket_id and int(status or 1) < 5:
                    return {"id": int(ticket_id), "status": int(status)}
                elif ticket_id:
                    return {"id": int(ticket_id), "status": int(status)}
    except Exception as e:
        logger.warning(f"Erro ao buscar ticket por Issue ID {issue_id}: {e}")
    return None

def create_itil_ticket(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Cria um chamado de Incidente ITIL no GLPI baseado no alerta do Instana."""
    issue_id = event_data.get("issue_id", "UNKNOWN")
    title = event_data.get("title", "Alerta Instana")
    description = event_data.get("description", "")
    suggestion = event_data.get("suggestion", "Verificar métricas no dashboard do Instana.")
    link = event_data.get("link", f"{INSTANA_BASE_URL}")
    severity = event_data.get("severity", 5)
    host = event_data.get("host", "192.168.173.22")
    zone = event_data.get("zone", "Luciano-GPU-Production")
    start_time = event_data.get("start_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Mapeamento ITIL (Severidade Instana -> Urgência / Impacto / Prioridade)
    if severity >= 10:
        urgency = 5  # Muito Alta
        impact = 5   # Muito Alto
        priority = 5 # Crítica (P1)
        category_id = CATEGORY_AIOPS_CRITICAL
        sla_note = "SLA P1 Crítico: Resposta em 15m | Solução em 2h"
    elif severity >= 5:
        urgency = 3  # Média
        impact = 3   # Médio
        priority = 3 # Média (P3)
        category_id = CATEGORY_AIOPS_WARNING
        sla_note = "SLA P3 Médio: Resposta em 2h | Solução em 8h"
    else:
        urgency = 2  # Baixa
        impact = 2   # Baixo
        priority = 2 # Baixa (P4)
        category_id = CATEGORY_AIOPS_WARNING
        sla_note = "SLA P4 Baixo: Resposta em 4h | Solução em 24h"

    content_html = f"""
<h3>🚨 Incidente AIOps Detectado pelo IBM Instana</h3>
<p><strong>Identificador Instana:</strong> <code>{issue_id}</code></p>
<p><strong>Host / Alvo:</strong> <code>{host}</code> (Zona: <em>{zone}</em>)</p>
<p><strong>Início do Evento:</strong> {start_time}</p>
<p><strong>Severidade:</strong> {severity} ({'Crítico' if severity >= 10 else 'Alerta/Aviso'})</p>
<p><strong>Acordo de Nível de Serviço:</strong> {sla_note}</p>
<hr/>
<h4>Detalhes Operacionais:</h4>
<p>{description}</p>
<h4>Ação Recomendada (Instana AI Suggestion):</h4>
<p style="color: #0b5cab; font-weight: bold;">{suggestion}</p>
<hr/>
<p>🔗 <strong><a href="{link}" target="_blank">Acessar Incidente no IBM Instana Console</a></strong></p>
"""

    ticket_name = f"[Instana #{issue_id}] {title}"

    payload = {
        "input": {
            "name": ticket_name,
            "content": content_html,
            "type": 1,                      # 1 = Incidente (ITIL)
            "urgency": urgency,
            "impact": impact,
            "priority": priority,
            "status": 1,                    # 1 = Novo (Novo incidente ITIL)
            "itilcategories_id": category_id,
            "_groups_id_assign": GROUP_ASSIGN_N2,
            "items_id": {
                "Computer": [DEFAULT_COMPUTER_CI_ID]
            }
        }
    }

    logger.info(f"Criando chamado ITIL para Issue {issue_id} (Prioridade: {priority})...")
    resp = glpi_request("POST", "Ticket", json_data=payload)
    if resp.status_code in [200, 201]:
        data = resp.json()
        logger.info(f"Chamado criado com sucesso: {data}")
        return data
    else:
        logger.error(f"Falha ao criar chamado no GLPI: HTTP {resp.status_code} - {resp.text}")
        raise HTTPException(status_code=500, detail=f"GLPI Error: {resp.text}")

def solve_itil_ticket(ticket_id: int, issue_id: str, end_time: str) -> Dict[str, Any]:
    """Marca o chamado como Solucionado (Status 5) com parecer de normalização AIOps."""
    solution_text = f"""
<h4>✅ Incidente Normalizado no IBM Instana</h4>
<p>O evento de observabilidade <code>{issue_id}</code> foi normalizado na plataforma Instana às <strong>{end_time}</strong>.</p>
<p>A métrica operacional retornou aos limites aceitáveis. Chamado solucionado automaticamente seguindo a governança ITIL.</p>
"""
    # 1. Adiciona a Solução ITIL
    sol_payload = {
        "input": {
            "items_id": ticket_id,
            "itemtype": "Ticket",
            "content": solution_text,
            "status": 2 # 2 = Solução Aprovada/Concedida
        }
    }
    logger.info(f"Registrando solucao ITIL para Ticket #{ticket_id}...")
    glpi_request("POST", f"Ticket/{ticket_id}/ITILSolution", json_data=sol_payload)

    # 2. Atualiza Status do Ticket para 5 (Solucionado)
    update_payload = {
        "input": {
            "id": ticket_id,
            "status": 5 # 5 = Solucionado
        }
    }
    resp = glpi_request("PUT", f"Ticket/{ticket_id}", json_data=update_payload)
    logger.info(f"Ticket #{ticket_id} atualizado para status SOLUCIONADO: {resp.status_code}")
    return {"ticket_id": ticket_id, "status": "SOLVED", "issue_id": issue_id}

def add_ticket_followup(ticket_id: int, message: str) -> None:
    """Adiciona acompanhamento (followup) a um chamado existente."""
    payload = {
        "input": {
            "items_id": ticket_id,
            "itemtype": "Ticket",
            "content": message
        }
    }
    glpi_request("POST", f"Ticket/{ticket_id}/ITILFollowup", json_data=payload)

@app.get("/health")
def health_check():
    """Verifica saúde do bridge e conectividade com a API do GLPI."""
    try:
        session = get_glpi_session()
        return {
            "status": "healthy",
            "glpi_connected": True,
            "session_active": bool(session),
            "glpi_api_url": GLPI_API_URL,
            "instana_base_url": INSTANA_BASE_URL,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "glpi_connected": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/webhook/instana")
async def instana_webhook(request: Request):
    """
    Endpoint principal para recebimento de webhooks de Alertas/Incidentes do IBM Instana.
    Processa payloads de Issues, Incidentes ou Eventos.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Corpo da requisicao deve ser JSON valido")

    logger.info(f"Webhook recebido do Instana: {json.dumps(payload, ensure_ascii=False)[:300]}...")

    # Extrai o objeto principal
    data_obj = payload.get("issue") or payload.get("incident") or payload.get("event") or payload

    issue_id = str(data_obj.get("id") or payload.get("id") or f"INSTANA-{int(datetime.now().timestamp())}")
    state = str(data_obj.get("state") or payload.get("state") or "OPEN").upper()
    title = data_obj.get("text") or data_obj.get("title") or payload.get("text") or "Alerta Observabilidade"
    description = data_obj.get("description") or title
    suggestion = data_obj.get("suggestion") or "Verificar topologia e traces no Instana."
    severity = int(data_obj.get("severity") or payload.get("severity") or 10)
    link = data_obj.get("link") or payload.get("link") or f"{INSTANA_BASE_URL}/#/events?eventId={issue_id}"
    host = data_obj.get("fqdn") or data_obj.get("entityLabel") or "192.168.173.22"
    zone = data_obj.get("zone") or "Luciano-GPU-Production"

    event_data = {
        "issue_id": issue_id,
        "state": state,
        "title": title,
        "description": description,
        "suggestion": suggestion,
        "severity": severity,
        "link": link,
        "host": host,
        "zone": zone,
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Tratamento ITIL baseado no estado do Alerta
    existing_ticket = find_ticket_by_instana_issue(issue_id)

    if state == "OPEN":
        if existing_ticket and existing_ticket["status"] < 5:
            ticket_id = existing_ticket["id"]
            logger.info(f"Incidente {issue_id} ja possui ticket ativo #{ticket_id}. Adicionando acompanhamento...")
            add_ticket_followup(
                ticket_id,
                f"ℹ️ <strong>Reincidência de Alerta Instana</strong> às {datetime.now().strftime('%H:%M:%S')}. Gravidade mantida em {severity}."
            )
            return {"action": "followup_added", "ticket_id": ticket_id, "issue_id": issue_id}
        else:
            result = create_itil_ticket(event_data)
            return {"action": "ticket_created", "result": result, "issue_id": issue_id}

    elif state in ["CLOSED", "RESOLVED"]:
        if existing_ticket and existing_ticket["status"] < 5:
            ticket_id = existing_ticket["id"]
            res = solve_itil_ticket(ticket_id, issue_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return {"action": "ticket_solved", "details": res}
        else:
            logger.info(f"Alerta de fechamento para {issue_id}, nenhum ticket ativo pendente.")
            return {"action": "ignored_no_active_ticket", "issue_id": issue_id}

    return {"action": "received", "state": state, "issue_id": issue_id}

class SimulationRequest(BaseModel):
    title: Optional[str] = "Alta Utilização de CPU no Servidor GPU (>95%)"
    description: Optional[str] = "O processo llama-server excedeu o limiar de 95% de uso contínuo de CPU por mais de 5 minutos."
    severity: Optional[int] = 10
    state: Optional[str] = "OPEN"
    host: Optional[str] = "192.168.173.22"
    issue_id: Optional[str] = None

@app.post("/simulate-alert")
def simulate_instana_alert(sim: SimulationRequest):
    """
    Endpoint para testar e demonstrar a integração Instana <-> GLPI.
    Gera um payload sintético com todos os campos de um alerta real do Instana.
    """
    issue_id = sim.issue_id or f"instana-sim-{int(datetime.now().timestamp())}"
    event_data = {
        "issue_id": issue_id,
        "state": sim.state.upper(),
        "title": sim.title,
        "description": sim.description,
        "suggestion": "Analisar threads concorrentes ou dimensionamento de memória.",
        "link": f"{INSTANA_BASE_URL}/#/events;eventId={issue_id}",
        "severity": sim.severity,
        "host": sim.host,
        "zone": "Luciano-GPU-Production",
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if sim.state.upper() == "OPEN":
        existing = find_ticket_by_instana_issue(issue_id)
        if existing and existing["status"] < 5:
            add_ticket_followup(existing["id"], f"ℹ️ Reincidência de alerta simulado às {datetime.now().strftime('%H:%M:%S')}")
            return {"status": "followup_added", "ticket_id": existing["id"], "issue_id": issue_id}
        res = create_itil_ticket(event_data)
        return {
            "status": "success",
            "mode": "simulation",
            "issue_id": issue_id,
            "ticket": res
        }
    else:
        existing = find_ticket_by_instana_issue(issue_id)
        if existing and existing["status"] < 5:
            res = solve_itil_ticket(existing["id"], issue_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return {"status": "success", "mode": "simulation", "solved": res}
        return {"status": "warning", "message": f"Nenhum ticket ativo encontrado para {issue_id}"}

@app.get("/tickets")
def list_instana_tickets():
    """Lista os chamados de incidentes abertos no GLPI."""
    resp = glpi_request("GET", "Ticket", params={"expand_dropdowns": "true"})
    if resp.status_code == 200:
        return resp.json()
    return {"error": resp.text}
