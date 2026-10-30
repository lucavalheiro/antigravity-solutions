import os
import re
import json
import sqlite3
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "/app/data/carvao.db")
os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)

EVOLUTION_URL = os.getenv("EVOLUTION_API_URL", "http://smartfarming-evolution:8080")
EVOLUTION_KEY = os.getenv("EVOLUTION_API_KEY", "smartfarming_secret_token_2026")
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE", "carvao")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "")
ENABLE_WHATSAPP_BOT = os.getenv("ENABLE_WHATSAPP_BOT", "false").lower() in ("true", "1", "yes")

app = FastAPI(title="Carvão Mattos - Gestão de Vendas, Pedidos & IA Mattinhos", version="4.0.0")

# ----------------- BANCO DE DADOS -----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Produtos / Sacos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bag_weight_kg REAL NOT NULL,
            default_price_kg REAL NOT NULL,
            default_price_bag REAL NOT NULL,
            stock_units INTEGER DEFAULT 0,
            stock_kg REAL DEFAULT 0,
            is_packaging INTEGER DEFAULT 0
        )
        """)

        # 2. Clientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'GERAL',
            phone TEXT,
            city TEXT,
            notes TEXT
        )
        """)

        # 3. Fornecedores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            city TEXT,
            notes TEXT
        )
        """)

        # 4. Transações / Romaneios de Carga e Vendas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            type TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            partner_name TEXT,
            total_kg REAL DEFAULT 0,
            gross_total REAL DEFAULT 0,
            partner_cost REAL DEFAULT 0,
            expenses_total REAL DEFAULT 0,
            net_profit REAL DEFAULT 0,
            notes TEXT
        )
        """)

        # 5. Itens da Transação
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            bag_weight_kg REAL NOT NULL,
            units INTEGER NOT NULL,
            total_kg REAL NOT NULL,
            price_per_kg REAL NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE
        )
        """)

        # 6. Fretes e Despesas Operacionais
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            responsible TEXT,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE SET NULL
        )
        """)

        # 7. Pedidos de Clientes (Fila e Gestão de Pedidos)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT,
            delivery_address TEXT,
            status TEXT NOT NULL DEFAULT 'PENDENTE',
            total_kg REAL DEFAULT 0,
            total_price REAL DEFAULT 0,
            delivery_fee REAL DEFAULT 0,
            net_total REAL DEFAULT 0,
            notes TEXT,
            source TEXT DEFAULT 'SISTEMA',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)

        # 8. Itens do Pedido
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            bag_weight_kg REAL NOT NULL,
            units INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
        )
        """)

        # 9. Histórico de Mudança de Status do Pedido (Rastreabilidade & Notificações)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            old_status TEXT,
            new_status TEXT NOT NULL,
            changed_by TEXT DEFAULT 'SISTEMA',
            notes TEXT,
            notified_whatsapp INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
        )
        """)

        # 10. Histórico de Mensagens do WhatsApp (Memória de Atendimento)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS whatsapp_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        conn.commit()

init_db()

# ----------------- MODELOS PYDANTIC -----------------
class CustomerModel(BaseModel):
    name: str
    type: Optional[str] = "GERAL"
    phone: Optional[str] = ""
    city: Optional[str] = ""
    notes: Optional[str] = ""

class SupplierModel(BaseModel):
    name: str
    phone: Optional[str] = ""
    city: Optional[str] = ""
    notes: Optional[str] = ""

class ExpenseModel(BaseModel):
    category: str
    description: str
    amount: float
    responsible: Optional[str] = "Geral"

class ItemInput(BaseModel):
    product_name: str
    bag_weight_kg: float
    units: int
    price_per_kg: float
    unit_price: float
    subtotal: float

class TransactionCreate(BaseModel):
    type: str # 'VENDA_CARGA', 'ENTRADA', 'SAIDA_AVULSA'
    partner_name: Optional[str] = "Balcão / Geral"
    description: str
    partner_cost: Optional[float] = 0.0
    items: List[ItemInput] = []
    expenses: List[ExpenseModel] = []
    notes: Optional[str] = ""

class OrderItemInput(BaseModel):
    product_name: str
    bag_weight_kg: float
    units: int
    price_per_unit: float
    subtotal: float

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = ""
    delivery_address: Optional[str] = ""
    items: List[OrderItemInput] = []
    delivery_fee: Optional[float] = 0.0
    notes: Optional[str] = ""
    source: Optional[str] = "SISTEMA"
    notify_whatsapp: Optional[bool] = True

class OrderStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = ""
    notify_whatsapp: Optional[bool] = True
    deduct_stock_if_delivered: Optional[bool] = False

class WhatsAppSendPayload(BaseModel):
    phone: str
    message: str

class GeminiKeyUpdate(BaseModel):
    api_key: str

class AiQueryPayload(BaseModel):
    message: Optional[str] = ""
    image: Optional[str] = None # Data URL base64
    audio: Optional[str] = None # Data URL base64 para comandos de voz
    phone: Optional[str] = None # Origem WhatsApp se aplicável
    customer_name: Optional[str] = None
    chat_history: Optional[str] = None

# ----------------- OCR PRÉ-PROCESSAMENTO DE IMAGEM -----------------
def extract_ocr_from_base64(image_data: str) -> str:
    try:
        import base64
        import io
        from PIL import Image
        import pytesseract

        if not image_data:
            return ""

        if "," in image_data:
            _, b64_bytes = image_data.split(",", 1)
        else:
            b64_bytes = image_data

        img_bytes = base64.b64decode(b64_bytes)
        img = Image.open(io.BytesIO(img_bytes)).convert("L")
        text = pytesseract.image_to_string(img, lang="por")
        return text.strip()
    except Exception as e:
        print(f"Erro no pytesseract OCR: {e}")
        return ""

# ----------------- PESQUISA NA WEB & INTELIGÊNCIA DE MERCADO -----------------
def perform_web_search(query: str, max_results: int = 5) -> list:
    results = []
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=max_results))
            for item in raw:
                results.append({
                    "title": item.get("title", ""),
                    "href": item.get("href", ""),
                    "snippet": item.get("body", "")
                })
            if results:
                return results
    except Exception as e:
        pass

    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=max_results))
            for item in raw:
                results.append({
                    "title": item.get("title", ""),
                    "href": item.get("href", ""),
                    "snippet": item.get("body", "")
                })
            if results:
                return results
    except Exception as e:
        pass

    return results

def should_search_web(user_query: str) -> bool:
    if not user_query:
        return False
    q = user_query.lower()
    keywords = [
        "pesquis", "busc", "mercado", "preço", "preco", "concorrent", "concorrencia",
        "concorrência", "quanto tá", "quanto ta", "quanto custa", "cotação", "cotacao",
        "madeira", "eucalipto", "ibama", "internet", "google", "notícia", "noticia",
        "atacado", "varejo", "tendência", "tendencia", "marcas", "carvoaria",
        "embalagem", "saco de papel", "saco kraft", "saco plastico", "tonelada",
        "churrascaria", "distribuidora", "brasil", "são paulo", "minas", "comparar"
    ]
    return any(k in q for k in keywords)

def build_search_query(user_query: str) -> str:
    cleaned = re.sub(r'^(pesquise|pesquisa|busque|busca|procure|procura|veja na internet|consulte na internet)\s*(sobre)?', '', user_query, flags=re.IGNORECASE).strip()
    if not cleaned:
        cleaned = user_query
    if "carv" not in cleaned.lower():
        return f"{cleaned} carvão vegetal mercado brasil"
    return f"{cleaned} mercado brasil"

# ----------------- INTEGRAÇÃO WHATSAPP / EVOLUTION API -----------------
def clean_phone(phone: str) -> str:
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("55"):
        return digits
    if len(digits) in (10, 11):
        return f"55{digits}"
    return digits

async def call_evolution(path: str, method: str = "GET", data: dict = None) -> dict:
    url = f"{EVOLUTION_URL}{path}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_KEY
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            if method.upper() == "POST":
                res = await client.post(url, headers=headers, json=data or {})
            else:
                res = await client.get(url, headers=headers)
            return res.json()
        except Exception as e:
            return {"error": str(e), "status": 500}

async def send_whatsapp_message(phone: str, text: str) -> dict:
    if not ENABLE_WHATSAPP_BOT:
        return {"status": "WHATSAPP_BOT_DISABLED", "message": "Bot WhatsApp desativado"}
    target_num = clean_phone(phone)
    if not target_num:
        return {"error": "Telefone inválido ou ausente"}
    
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_KEY
    }
    body = {
        "number": target_num,
        "text": text
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.post(url, headers=headers, json=body)
            print(f"[WHATSAPP OUT] Send to {target_num}: status {res.status_code}")
            return res.json()
    except Exception as e:
        print(f"[WHATSAPP OUT ERROR] {e}")
        return {"error": str(e)}

STATUS_LABELS = {
    "PENDENTE": "🟡 PENDENTE (Na fila de preparação)",
    "CONFIRMADO": "🔵 CONFIRMADO (Aprovado e agendado)",
    "EM_SEPARACAO": "🟠 EM SEPARAÇÃO (Ensacando / separando no galpão)",
    "SAIU_PARA_ENTREGA": "🚚 SAIU PARA ENTREGA (A caminho com motorista)",
    "ENTREGUE": "✅ ENTREGUE (Finalizado com sucesso)",
    "CANCELADO": "❌ CANCELADO"
}

async def notify_order_status(order_id: int, new_status: str, custom_note: str = "") -> bool:
    if not ENABLE_WHATSAPP_BOT:
        return False
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = c.fetchone()
        if not order:
            return False

        order = dict(order)
        phone = order.get("customer_phone")
        if not phone:
            return False

        c.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        items = [dict(i) for i in c.fetchall()]

    status_str = STATUS_LABELS.get(new_status, new_status)
    items_list_str = "\n".join([f"  • {it['units']}x {it['product_name']} (R$ {it['subtotal']:.2f})" for it in items])
    if not items_list_str:
        items_list_str = "  • Carvão sob medida"

    msg = (
        f"🔥 *CARVÃO MATTOS - Atualização de Pedido*\n\n"
        f"Olá, *{order['customer_name']}*! 👋\n"
        f"Seu pedido *{order['code']}* teve o status atualizado no nosso sistema:\n\n"
        f"📦 *Status Atual:* {status_str}\n"
        f"📍 *Endereço:* {order.get('delivery_address') or 'Retirada / A combinar'}\n"
        f"💰 *Total:* R$ {order.get('net_total', 0.0):.2f}\n\n"
        f"📋 *Itens:*\n{items_list_str}\n"
    )
    if custom_note:
        msg += f"\n💬 *Observação:* {custom_note}\n"

    if new_status == "SAIU_PARA_ENTREGA":
        msg += "\n🚚 O motorista já está a caminho! Por favor, mantenha alguém disponível para o recebimento."
    elif new_status == "ENTREGUE":
        msg += "\n🎉 Pedido entregue! Agradecemos pela preferência e parceria. Bom churrasco / bom trabalho!"
    elif new_status == "CONFIRMADO":
        msg += "\n👍 Pedido confirmado e enviado para nossa equipe de galpão."
    elif new_status == "EM_SEPARACAO":
        msg += "\n⏳ Estamos separando os sacos de carvão com toda a qualidade Mattos."

    msg += "\n\nQualquer dúvida, basta responder esta mensagem. 🔥"

    res = await send_whatsapp_message(phone, msg)
    success = bool(res and "key" in res or res.get("status") in [200, 201])
    
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
        UPDATE order_status_history
        SET notified_whatsapp = ?
        WHERE order_id = ? AND new_status = ?
        """, (1 if success else 0, order_id, new_status))
        conn.commit()

    return success

# ----------------- FUNÇÃO DE EXECUÇÃO DE TOOLS DA IA -----------------
def execute_ai_tool(tool_name: str, args: dict) -> str:
    with get_db() as conn:
        c = conn.cursor()
        
        # 1. TRANSAÇÃO / ROMANEIO
        if tool_name == "create_transaction":
            tx_type = args.get("type", "VENDA_CARGA")
            partner = args.get("partner_name", "Geral")
            desc = args.get("description", "Operação lançada pelo Mattinhos")
            partner_cost = float(args.get("partner_cost", 0.0))
            notes = args.get("notes", "Registrado via IA Mattinhos")
            today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            code = f"ROM-{int(datetime.now().timestamp()) % 100000:05d}"
            
            raw_items = args.get("items", [])
            raw_expenses = args.get("expenses", [])
            
            total_kg = sum(float(i.get("units", 0)) * float(i.get("bag_weight_kg", 0)) for i in raw_items)
            gross_total = sum(float(i.get("subtotal", 0)) for i in raw_items)
            expenses_total = sum(float(e.get("amount", 0)) for e in raw_expenses)
            net_profit = (gross_total - partner_cost) - expenses_total
            
            c.execute("""
            INSERT INTO transactions (code, type, date, description, partner_name, total_kg, gross_total, partner_cost, expenses_total, net_profit, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code, tx_type, today_str, desc, partner, total_kg, gross_total, partner_cost, expenses_total, net_profit, notes))
            tx_id = c.lastrowid
            
            for item in raw_items:
                p_name = item.get("product_name", "Carvão")
                b_weight = float(item.get("bag_weight_kg", 10.0))
                units = int(item.get("units", 0))
                p_kg = float(item.get("price_per_kg", 3.60))
                u_price = float(item.get("unit_price", b_weight * p_kg))
                sub = float(item.get("subtotal", units * u_price))
                
                c.execute("""
                INSERT INTO transaction_items (transaction_id, product_name, bag_weight_kg, units, total_kg, price_per_kg, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (tx_id, p_name, b_weight, units, units * b_weight, p_kg, u_price, sub))
                
                delta = -units if tx_type in ['VENDA_CARGA', 'SAIDA_AVULSA'] else units
                c.execute("""
                UPDATE products 
                SET stock_units = MAX(0, stock_units + ?),
                    stock_kg = MAX(0, stock_kg + (? * bag_weight_kg))
                WHERE name LIKE ?
                """, (delta, delta, f"%{int(b_weight)}%"))
                
            for exp in raw_expenses:
                cat = exp.get("category", "OUTROS")
                e_desc = exp.get("description", "Despesa")
                amt = float(exp.get("amount", 0.0))
                resp = exp.get("responsible", partner)
                c.execute("""
                INSERT INTO expenses (transaction_id, date, category, description, amount, responsible)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (tx_id, today_str, cat, e_desc, amt, resp))
                
            conn.commit()
            return f"Transação {code} (#ID {tx_id}) inserida com sucesso! Faturamento: R$ {gross_total:.2f}, Lucro Líquido: R$ {net_profit:.2f}."

        # 2. DELEÇÃO DE TRANSAÇÃO
        elif tool_name == "delete_transaction":
            tx_id = int(args.get("transaction_id", 0))
            c.execute("SELECT type FROM transactions WHERE id = ?", (tx_id,))
            row = c.fetchone()
            if not row:
                return f"Transação #{tx_id} não encontrada."
            tx_type = row[0]
            
            c.execute("SELECT product_name, units FROM transaction_items WHERE transaction_id = ?", (tx_id,))
            items = c.fetchall()
            for it in items:
                delta = it[1] if tx_type in ['VENDA_CARGA', 'SAIDA_AVULSA'] else -it[1]
                c.execute("UPDATE products SET stock_units = MAX(0, stock_units + ?) WHERE name = ?", (delta, it[0]))
                
            c.execute("DELETE FROM transaction_items WHERE transaction_id = ?", (tx_id,))
            c.execute("DELETE FROM expenses WHERE transaction_id = ?", (tx_id,))
            c.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
            conn.commit()
            return f"Transação #{tx_id} excluída com sucesso e estoque estornado!"

        # 3. CRIAR NOVO PEDIDO DE CLIENTE (FILA & ATENDIMENTO)
        elif tool_name == "create_order":
            cust_name = args.get("customer_name", "Cliente")
            cust_phone = args.get("customer_phone", "")
            address = args.get("delivery_address", "")
            notes = args.get("notes", "Criado pelo Mattinhos")
            source = args.get("source", "IA")
            deliv_fee = float(args.get("delivery_fee", 0.0))
            raw_items = args.get("items", [])
            
            today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            order_code = f"PED-{int(datetime.now().timestamp()) % 100000:05d}"
            
            total_kg = 0.0
            total_price = 0.0
            clean_items = []
            
            for item in raw_items:
                p_name = item.get("product_name", "Saco de Carvão")
                units = int(item.get("units", 1))
                b_weight = float(item.get("bag_weight_kg", 10.0))
                p_unit = float(item.get("price_per_unit", 36.0))
                sub = units * p_unit
                total_kg += (units * b_weight)
                total_price += sub
                clean_items.append((p_name, b_weight, units, p_unit, sub))
                
            net_total = total_price + deliv_fee
            
            c.execute("""
            INSERT INTO orders (code, customer_name, customer_phone, delivery_address, status, total_kg, total_price, delivery_fee, net_total, notes, source, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'PENDENTE', ?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_code, cust_name, cust_phone, address, total_kg, total_price, deliv_fee, net_total, notes, source, today_str, today_str))
            order_id = c.lastrowid
            
            for (p_name, b_weight, units, p_unit, sub) in clean_items:
                c.execute("""
                INSERT INTO order_items (order_id, product_name, bag_weight_kg, units, price_per_unit, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (order_id, p_name, b_weight, units, p_unit, sub))
                
            c.execute("""
            INSERT INTO order_status_history (order_id, old_status, new_status, changed_by, notes, notified_whatsapp, created_at)
            VALUES (?, NULL, 'PENDENTE', ?, 'Pedido aberto e enfileirado no sistema', 0, ?)
            """, (order_id, source, today_str))
            
            # Se o cliente já não existir no cadastro, cadastra automaticamente
            if cust_name:
                if cust_phone:
                    c.execute("SELECT id FROM customers WHERE phone = ? OR name = ?", (cust_phone, cust_name))
                else:
                    c.execute("SELECT id FROM customers WHERE name = ?", (cust_name,))
                if not c.fetchone():
                    c.execute("INSERT INTO customers (name, type, phone, city, notes) VALUES (?, 'VAREJO', ?, ?, 'Cadastrado via Pedido')",
                              (cust_name, cust_phone, address))

            conn.commit()
            return f"Pedido {order_code} (#ID {order_id}) registrado com sucesso para {cust_name}! Total: R$ {net_total:.2f} ({total_kg:.1f} kg). Status: PENDENTE (na fila)."

        # 4. CONSULTAR STATUS DE PEDIDO
        elif tool_name == "check_order_status":
            query = str(args.get("phone_or_code", "") or args.get("order_code_or_id", "") or args.get("customer_name", "")).strip()
            if not query:
                return "Informe o código do pedido (ex: PED-12345) ou o nome do cliente."
                
            c.execute("""
            SELECT id, code, customer_name, customer_phone, delivery_address, status, net_total, created_at, updated_at
            FROM orders
            WHERE code LIKE ? OR customer_name LIKE ? OR customer_phone LIKE ?
            ORDER BY id DESC LIMIT 3
            """, (f"%{query}%", f"%{query}%", f"%{clean_phone(query)}%"))
            rows = c.fetchall()
            if not rows:
                return f"Nenhum pedido recente encontrado para '{query}'. Se desejar, me diga seu nome ou código #PED."
                
            results = []
            for r in rows:
                c.execute("SELECT product_name, units, subtotal FROM order_items WHERE order_id = ?", (r["id"],))
                it_strs = [f"{it['units']}x {it['product_name']}" for it in c.fetchall()]
                results.append(f"• Pedido {r['code']} ({r['customer_name']}): Status '{r['status']}', Total R$ {r['net_total']:.2f}, Itens: [{', '.join(it_strs)}], Atualizado em: {r['updated_at']}.")
                
            return "\n".join(results)

        # 5. ATUALIZAR STATUS DE PEDIDO
        elif tool_name == "update_order_status":
            order_target = args.get("order_code_or_id")
            new_status = args.get("new_status", "EM_SEPARACAO").upper()
            notes = args.get("notes", "Atualizado pela IA Mattinhos")
            today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            if str(order_target).isdigit():
                c.execute("SELECT id, status, customer_name, code FROM orders WHERE id = ?", (int(order_target),))
            else:
                c.execute("SELECT id, status, customer_name, code FROM orders WHERE code = ?", (str(order_target).strip(),))
            row = c.fetchone()
            if not row:
                return f"Pedido '{order_target}' não encontrado."
                
            o_id = row["id"]
            old_st = row["status"]
            c.execute("UPDATE orders SET status = ?, updated_at = ? WHERE id = ?", (new_status, today_str, o_id))
            c.execute("""
            INSERT INTO order_status_history (order_id, old_status, new_status, changed_by, notes, notified_whatsapp, created_at)
            VALUES (?, ?, ?, 'IA_MATTINHOS', ?, 0, ?)
            """, (o_id, old_st, new_status, notes, today_str))
            conn.commit()
            return f"Status do Pedido {row['code']} ({row['customer_name']}) atualizado de '{old_st}' para '{new_status}'!"

        # 6. DEMAIS TOOLS EXISTENTES
        elif tool_name == "create_customer":
            name = args.get("name", "")
            ctype = args.get("type", "GERAL")
            phone = clean_phone(args.get("phone", ""))
            city = args.get("city", "")
            notes = args.get("notes", "")
            c.execute("INSERT INTO customers (name, type, phone, city, notes) VALUES (?, ?, ?, ?, ?)", (name, ctype, phone, city, notes))
            conn.commit()
            return f"Cliente '{name}' cadastrado com sucesso!"

        elif tool_name == "create_supplier":
            name = args.get("name", "")
            phone = clean_phone(args.get("phone", ""))
            city = args.get("city", "")
            notes = args.get("notes", "")
            c.execute("INSERT INTO suppliers (name, phone, city, notes) VALUES (?, ?, ?, ?)", (name, phone, city, notes))
            conn.commit()
            return f"Fornecedor '{name}' cadastrado com sucesso!"

        elif tool_name == "create_expense":
            cat = args.get("category", "OUTROS")
            desc = args.get("description", "")
            amt = float(args.get("amount", 0.0))
            resp = args.get("responsible", "Depósito")
            today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO expenses (date, category, description, amount, responsible) VALUES (?, ?, ?, ?, ?)", (today_str, cat, desc, amt, resp))
            conn.commit()
            return f"Despesa/Frete de R$ {amt:.2f} ({desc}) registrada com sucesso!"

        elif tool_name == "adjust_stock":
            target = args.get("product_name_or_id")
            new_units = int(args.get("stock_units", 0))
            if str(target).isdigit():
                c.execute("UPDATE products SET stock_units = ?, stock_kg = ? * bag_weight_kg WHERE id = ?", (new_units, new_units, int(target)))
            else:
                c.execute("UPDATE products SET stock_units = ?, stock_kg = ? * bag_weight_kg WHERE name LIKE ?", (new_units, new_units, f"%{target}%"))
            conn.commit()
            return f"Estoque de '{target}' ajustado para {new_units} unidades."

        elif tool_name == "search_web":
            target_q = args.get("query", "mercado carvao vegetal atacado brasil")
            s_results = perform_web_search(target_q, max_results=5)
            return f"Pesquisa web executada para '{target_q}': {len(s_results)} fontes encontradas."

    return "Ferramenta não reconhecida."

# ----------------- ROTAS: DASHBOARD -----------------
@app.get("/api/dashboard")
def get_dashboard():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
        SELECT 
            COALESCE(SUM(gross_total), 0) as total_revenue,
            COALESCE(SUM(partner_cost), 0) as total_load_costs,
            COALESCE(SUM(expenses_total), 0) as total_expenses,
            COALESCE(SUM(net_profit), 0) as total_profit,
            COALESCE(SUM(total_kg), 0) as total_kg_sold,
            COUNT(*) as total_transactions
        FROM transactions
        """)
        stats = dict(c.fetchone())

        c.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses")
        stats["all_expenses_sum"] = c.fetchone()[0]

        # Estatísticas de Pedidos
        c.execute("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(CASE WHEN status = 'PENDENTE' THEN 1 ELSE 0 END) as pending_orders,
            SUM(CASE WHEN status = 'EM_SEPARACAO' THEN 1 ELSE 0 END) as preparing_orders,
            SUM(CASE WHEN status = 'SAIU_PARA_ENTREGA' THEN 1 ELSE 0 END) as delivery_orders,
            SUM(CASE WHEN status = 'ENTREGUE' THEN 1 ELSE 0 END) as delivered_orders,
            COALESCE(SUM(net_total), 0) as total_orders_value
        FROM orders
        """)
        stats["orders"] = dict(c.fetchone())

        c.execute("SELECT * FROM products WHERE is_packaging = 0 ORDER BY bag_weight_kg DESC")
        products = [dict(r) for r in c.fetchall()]

        c.execute("SELECT * FROM products WHERE is_packaging = 1")
        packagings = [dict(r) for r in c.fetchall()]

        c.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 5")
        recent_tx = [dict(r) for r in c.fetchall()]

        c.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 5")
        recent_orders = [dict(r) for r in c.fetchall()]

        return {
            "stats": stats,
            "products": products,
            "packagings": packagings,
            "recent_transactions": recent_tx,
            "recent_orders": recent_orders,
            "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
            "whatsapp_configured": True,
            "whatsapp_number": WHATSAPP_PHONE
        }

# ----------------- CRUD & FILA: GESTÃO DE PEDIDOS -----------------
@app.get("/api/orders")
def get_orders(status: Optional[str] = None, search: Optional[str] = None):
    with get_db() as conn:
        c = conn.cursor()
        query = "SELECT * FROM orders WHERE 1=1"
        params = []
        if status and status.upper() != "TODOS":
            query += " AND status = ?"
            params.append(status.upper())
        if search:
            query += " AND (code LIKE ? OR customer_name LIKE ? OR customer_phone LIKE ?)"
            s = f"%{search}%"
            params.extend([s, s, s])
            
        query += " ORDER BY id DESC"
        c.execute(query, params)
        orders = [dict(r) for r in c.fetchall()]
        
        for o in orders:
            c.execute("SELECT * FROM order_items WHERE order_id = ?", (o["id"],))
            o["items"] = [dict(i) for i in c.fetchall()]
            c.execute("SELECT * FROM order_status_history WHERE order_id = ? ORDER BY id DESC LIMIT 1", (o["id"],))
            last_hist = c.fetchone()
            o["last_history"] = dict(last_hist) if last_hist else None

        return orders

@app.get("/api/orders/{order_id}")
def get_order_detail(order_id: int):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = c.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        o = dict(order)
        c.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        o["items"] = [dict(i) for i in c.fetchall()]
        c.execute("SELECT * FROM order_status_history WHERE order_id = ? ORDER BY id ASC", (order_id,))
        o["history"] = [dict(h) for h in c.fetchall()]
        return o

@app.post("/api/orders")
async def create_order_endpoint(order_in: OrderCreate):
    res_msg = execute_ai_tool("create_order", order_in.dict())
    
    # Extrai o ID criado para notificar via WhatsApp se solicitado
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM orders ORDER BY id DESC LIMIT 1")
        last_id = c.fetchone()[0]

    if order_in.notify_whatsapp and order_in.customer_phone:
        await notify_order_status(last_id, "PENDENTE", order_in.notes)

    return {"status": "success", "message": res_msg, "order_id": last_id}

@app.put("/api/orders/{order_id}/status")
async def update_order_status_endpoint(order_id: int, payload: OrderStatusUpdate):
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT status, customer_name, code FROM orders WHERE id = ?", (order_id,))
        row = c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
            
        old_status = row["status"]
        new_status = payload.status.upper()
        
        c.execute("UPDATE orders SET status = ?, updated_at = ? WHERE id = ?", (new_status, today_str, order_id))
        c.execute("""
        INSERT INTO order_status_history (order_id, old_status, new_status, changed_by, notes, notified_whatsapp, created_at)
        VALUES (?, ?, ?, 'SISTEMA', ?, 0, ?)
        """, (order_id, old_status, new_status, payload.notes, today_str))
        
        # Abate do estoque se entregue e solicitado
        if new_status == "ENTREGUE" and payload.deduct_stock_if_delivered:
            c.execute("SELECT product_name, bag_weight_kg, units FROM order_items WHERE order_id = ?", (order_id,))
            for it in c.fetchall():
                c.execute("""
                UPDATE products 
                SET stock_units = MAX(0, stock_units - ?),
                    stock_kg = MAX(0, stock_kg - (? * bag_weight_kg))
                WHERE name LIKE ?
                """, (it["units"], it["units"], f"%{int(it['bag_weight_kg'])}%"))

        conn.commit()

    if payload.notify_whatsapp:
        await notify_order_status(order_id, new_status, payload.notes)

    return {"status": "success", "message": f"Pedido #{order_id} atualizado para {new_status}"}

@app.delete("/api/orders/{order_id}")
def delete_order_endpoint(order_id: int):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        c.execute("DELETE FROM order_status_history WHERE order_id = ?", (order_id,))
        c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
    return {"status": "success", "message": f"Pedido #{order_id} excluído com sucesso."}

# ----------------- ROTAS: WHATSAPP (STATUS, QR CODE & PAIRING) -----------------
@app.get("/api/whatsapp/status")
async def get_whatsapp_status():
    try:
        data = await call_evolution(f"/instance/connectionState/{INSTANCE_NAME}")
        state = data.get("instance", {}).get("state", "disconnected")
        return {
            "instance": INSTANCE_NAME,
            "number": WHATSAPP_PHONE,
            "state": state,
            "raw": data
        }
    except Exception as e:
        return {"instance": INSTANCE_NAME, "number": WHATSAPP_PHONE, "state": "error", "error": str(e)}

@app.get("/api/whatsapp/connect")
async def get_whatsapp_connect():
    try:
        q_param = f"?number={clean_phone(WHATSAPP_PHONE)}" if WHATSAPP_PHONE else ""
        data = await call_evolution(f"/instance/connect/{INSTANCE_NAME}{q_param}")
        pairing = data.get("pairingCode") or data.get("qrcode", {}).get("pairingCode") or ""
        b64 = data.get("base64") or data.get("qrcode", {}).get("base64") or ""
        return {
            "pairingCode": pairing,
            "base64": b64,
            "instance": INSTANCE_NAME,
            "number": WHATSAPP_PHONE
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/whatsapp/qrcode", response_class=HTMLResponse)
async def get_whatsapp_qrcode_html():
    state_res = await call_evolution(f"/instance/connectionState/{INSTANCE_NAME}")
    state = state_res.get("instance", {}).get("state", "connecting")
    
    if state == "open":
        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
          <meta charset="UTF-8">
          <title>WhatsApp Conectado - Carvão Mattos</title>
          <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-slate-950 text-white min-h-screen flex items-center justify-center p-4">
          <div class="bg-slate-900 p-8 rounded-2xl shadow-2xl text-center max-w-md w-full border border-emerald-500/30">
            <div class="w-20 h-20 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-4 text-4xl">
              ✓
            </div>
            <h1 class="text-2xl font-bold text-white mb-2">WhatsApp Conectado!</h1>
            <p class="text-slate-400 text-sm mb-6">O assistente comercial e de pedidos Mattinhos está online e respondendo automaticamente no WhatsApp da empresa.</p>
            <div class="inline-flex items-center px-4 py-2 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold">
              <span class="w-2 h-2 rounded-full bg-emerald-400 mr-2 animate-pulse"></span> Instância '{INSTANCE_NAME}' Online
            </div>
          </div>
        </body>
        </html>
        """

    q_param = f"?number={clean_phone(WHATSAPP_PHONE)}" if WHATSAPP_PHONE else ""
    connect_data = await call_evolution(f"/instance/connect/{INSTANCE_NAME}{q_param}")
    b64 = connect_data.get("base64") or connect_data.get("qrcode", {}).get("base64") or ""
    pairing = connect_data.get("pairingCode") or connect_data.get("qrcode", {}).get("pairingCode") or ""

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <meta http-equiv="refresh" content="5">
      <title>Conectar WhatsApp - Carvão Mattos</title>
      <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-white min-h-screen flex items-center justify-center p-4">
      <div class="bg-slate-900 p-8 rounded-2xl shadow-2xl text-center max-w-md w-full border border-slate-800">
        <div class="flex items-center justify-center space-x-2 mb-3">
          <span class="text-3xl">🔥</span>
          <h1 class="text-2xl font-bold text-white">Carvão <span class="text-amber-500">Mattos</span></h1>
        </div>
        <p class="text-slate-400 text-sm mb-4">Canal Oficial: <strong class="text-emerald-400">WhatsApp Conectado</strong></p>
        
        <div class="bg-white p-4 rounded-xl inline-block shadow-inner mb-4">
          {'<img src="' + (b64 if b64.startswith('data:') else f'data:image/png;base64,{b64}') + '" alt="QR Code WhatsApp" class="w-64 h-64 object-contain">' if b64 else '<div class="w-64 h-64 flex flex-col items-center justify-center text-slate-700 text-xs font-semibold">Gerando QR Code...</div>'}
        </div>

        {f'<div class="bg-slate-800 p-3 rounded-xl mb-4 border border-amber-500/30"><p class="text-xs text-slate-400 mb-1">Código de Pareamento (Digitar no Celular):</p><p class="text-2xl font-mono font-black text-amber-400 tracking-wider">{pairing}</p></div>' if pairing else ''}

        <div class="text-xs text-slate-400 text-left space-y-1.5 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
          <p>1. Abra o WhatsApp no celular da empresa</p>
          <p>2. Toque em <strong>Aparelhos conectados</strong> > <strong>Conectar um aparelho</strong></p>
          <p>3. Escaneie o QR Code ou insira o código de pareamento acima.</p>
        </div>
      </div>
    </body>
    </html>
    """

@app.post("/api/whatsapp/send")
async def send_whatsapp_endpoint(payload: WhatsAppSendPayload):
    res = await send_whatsapp_message(payload.phone, payload.message)
    return res

# ----------------- WEBHOOK DO WHATSAPP (ATENDIMENTO AUTOMÁTICO IA) -----------------
@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(req: Request):
    if not ENABLE_WHATSAPP_BOT:
        return {"status": "WHATSAPP_BOT_DISABLED"}
    try:
        body = await req.json()
    except Exception:
        return {"status": "INVALID_JSON"}

    event = body.get("event")
    data = body.get("data")

    if event != "messages.upsert" or not data:
        return {"status": "IGNORED"}

    key = data.get("key", {})
    if key.get("fromMe"):
        return {"status": "FROM_ME"}

    remote_jid = key.get("remoteJid", "")
    if not remote_jid or "@g.us" in remote_jid:
        return {"status": "GROUP_OR_EMPTY"}

    message = data.get("message", {})
    text = message.get("conversation") or message.get("extendedTextMessage", {}).get("text") or message.get("imageMessage", {}).get("caption") or ""
    image_b64 = None
    if "base64" in data and data["base64"]:
        image_b64 = f"data:image/jpeg;base64,{data['base64']}"

    sender_name = data.get("pushName") or "Cliente"
    customer_phone = remote_jid.replace("@s.whatsapp.net", "").replace("@c.us", "")

    if not text and not image_b64:
        return {"status": "NO_CONTENT"}

    print(f"[WHATSAPP IN] De: {sender_name} ({customer_phone}) -> '{text[:50]}'")

    # Salva mensagem recebida no histórico de chat
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO whatsapp_messages (phone, sender, message, created_at) VALUES (?, 'CLIENTE', ?, ?)",
                  (customer_phone, text or "[Imagem enviada]", now_str))
        conn.commit()

        c.execute("SELECT sender, message FROM whatsapp_messages WHERE phone = ? ORDER BY id DESC LIMIT 12", (customer_phone,))
        hist_rows = c.fetchall()[::-1]
        chat_hist_str = "\n".join([f"{r['sender']}: {r['message']}" for r in hist_rows])

    # Processa pelo Mattinhos (IA Gemini) com ferramentas e contexto de pedidos
    ai_payload = AiQueryPayload(
        message=text,
        image=image_b64,
        phone=customer_phone,
        customer_name=sender_name,
        chat_history=chat_hist_str
    )
    ai_response = await ask_gemini(ai_payload)
    reply_text = ai_response.get("reply", "")

    if reply_text:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO whatsapp_messages (phone, sender, message, created_at) VALUES (?, 'MATTINHOS', ?, ?)",
                      (customer_phone, reply_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
        await send_whatsapp_message(customer_phone, reply_text)

    return {"status": "PROCESSED"}

# ----------------- CRUD: TRANSAÇÕES -----------------
@app.get("/api/transactions")
def get_transactions():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM transactions ORDER BY id DESC")
        txs = [dict(r) for r in c.fetchall()]
        for tx in txs:
            c.execute("SELECT * FROM transaction_items WHERE transaction_id = ?", (tx["id"],))
            tx["items"] = [dict(i) for i in c.fetchall()]
            c.execute("SELECT * FROM expenses WHERE transaction_id = ?", (tx["id"],))
            tx["expenses"] = [dict(e) for e in c.fetchall()]
        return txs

@app.post("/api/transactions")
def create_transaction_endpoint(tx: TransactionCreate):
    res_msg = execute_ai_tool("create_transaction", tx.dict())
    return {"status": "success", "message": res_msg}

@app.delete("/api/transactions/{tx_id}")
def delete_transaction_endpoint(tx_id: int):
    res_msg = execute_ai_tool("delete_transaction", {"transaction_id": tx_id})
    return {"status": "success", "message": res_msg}

# ----------------- CRUD: CLIENTES -----------------
@app.get("/api/customers")
def get_customers():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM customers ORDER BY name ASC")
        return [dict(r) for r in c.fetchall()]

@app.post("/api/customers")
def create_customer(cust: CustomerModel):
    with get_db() as conn:
        c = conn.cursor()
        phone_clean = clean_phone(cust.phone)
        c.execute("INSERT INTO customers (name, type, phone, city, notes) VALUES (?, ?, ?, ?, ?)",
                  (cust.name, cust.type, phone_clean, cust.city, cust.notes))
        conn.commit()
        return {"status": "success", "id": c.lastrowid}

@app.delete("/api/customers/{cust_id}")
def delete_customer(cust_id: int):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM customers WHERE id = ?", (cust_id,))
        conn.commit()
    return {"status": "success"}

# ----------------- CRUD: FORNECEDORES -----------------
@app.get("/api/suppliers")
def get_suppliers():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM suppliers ORDER BY name ASC")
        return [dict(r) for r in c.fetchall()]

@app.post("/api/suppliers")
def create_supplier(supp: SupplierModel):
    with get_db() as conn:
        c = conn.cursor()
        phone_clean = clean_phone(supp.phone)
        c.execute("INSERT INTO suppliers (name, phone, city, notes) VALUES (?, ?, ?, ?)",
                  (supp.name, phone_clean, supp.city, supp.notes))
        conn.commit()
        return {"status": "success", "id": c.lastrowid}

@app.delete("/api/suppliers/{supp_id}")
def delete_supplier(supp_id: int):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM suppliers WHERE id = ?", (supp_id,))
        conn.commit()
    return {"status": "success"}

# ----------------- CRUD: FRETES E DESPESAS -----------------
@app.get("/api/expenses")
def get_expenses():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM expenses ORDER BY id DESC")
        return [dict(r) for r in c.fetchall()]

@app.post("/api/expenses")
def create_expense(exp: ExpenseModel):
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    with get_db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO expenses (date, category, description, amount, responsible) VALUES (?, ?, ?, ?, ?)",
                  (today_str, exp.category, exp.description, exp.amount, exp.responsible))
        conn.commit()
        return {"status": "success", "id": c.lastrowid}

@app.delete("/api/expenses/{exp_id}")
def delete_expense(exp_id: int):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM expenses WHERE id = ?", (exp_id,))
        conn.commit()
    return {"status": "success"}

# ----------------- ESTOQUE: PRODUTOS & AJUSTES -----------------
@app.get("/api/products")
def get_products():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM products ORDER BY is_packaging ASC, bag_weight_kg DESC")
        return [dict(r) for r in c.fetchall()]

@app.post("/api/products/adjust")
def adjust_stock(payload: dict = Body(...)):
    product_id = payload.get("id")
    new_units = payload.get("stock_units")
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT bag_weight_kg FROM products WHERE id = ?", (product_id,))
        row = c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        weight = row[0]
        new_kg = new_units * weight
        c.execute("UPDATE products SET stock_units = ?, stock_kg = ? WHERE id = ?", (new_units, new_kg, product_id))
        conn.commit()
    return {"status": "success"}

# ----------------- CONFIGURAÇÃO GEMINI -----------------
@app.get("/api/config")
def get_config():
    key = os.getenv("GEMINI_API_KEY", "")
    masked = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else ("Configurada" if key else "")
    return {
        "gemini_configured": bool(key),
        "key_preview": masked,
        "whatsapp_phone": WHATSAPP_PHONE
    }

@app.post("/api/config/key")
def set_gemini_key(data: GeminiKeyUpdate):
    key = data.api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="Chave inválida.")
    
    os.environ["GEMINI_API_KEY"] = key
    try:
        env_path = "/app/.env"
        with open(env_path, "w") as f:
            f.write(f"GEMINI_API_KEY={key}\nDATABASE_PATH=/app/data/carvao.db\nEVOLUTION_API_URL={EVOLUTION_URL}\nEVOLUTION_API_KEY={EVOLUTION_KEY}\nEVOLUTION_INSTANCE={INSTANCE_NAME}\nWHATSAPP_PHONE={WHATSAPP_PHONE}\n")
    except Exception:
        pass
        
    return {"status": "success", "message": "Chave da Gemini configurada!"}

# ----------------- IA MULTIMODAL & TOTAL CONTROL (MATTINHOS) -----------------
@app.post("/api/ai/ask")
async def ask_gemini(payload: AiQueryPayload):
    user_query = (payload.message or "").strip()
    image_data = payload.image
    audio_data = payload.audio
    client_phone = payload.phone
    client_name = payload.customer_name or "Cliente"

    if not user_query and not image_data and not audio_data:
        raise HTTPException(status_code=400, detail="Nenhum texto, áudio ou imagem fornecido.")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return {
            "reply": "Fala chefe! Eu sou o **Mattinhos**, da Carvão Mattos! 🔥\n\nAinda falta configurar a **GEMINI_API_KEY** no sistema para que eu possa analisar tudo, processar imagens e executar ações no banco de dados."
        }

    # Coletar todo o contexto em tempo real do banco
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, stock_units, stock_kg, default_price_kg, default_price_bag FROM products")
        products = [dict(r) for r in c.fetchall()]

        c.execute("SELECT id, code, date, partner_name, total_kg, gross_total, partner_cost, expenses_total, net_profit FROM transactions ORDER BY id DESC LIMIT 5")
        txs = [dict(r) for r in c.fetchall()]

        # Contexto de Pedidos recentes na fila
        c.execute("""
        SELECT id, code, customer_name, customer_phone, delivery_address, status, net_total, created_at, updated_at
        FROM orders ORDER BY id DESC LIMIT 10
        """)
        orders = [dict(r) for r in c.fetchall()]

        c.execute("SELECT id, name, type, city, phone FROM customers")
        customers = [dict(r) for r in c.fetchall()]

        c.execute("SELECT id, name, city, phone FROM suppliers")
        suppliers = [dict(r) for r in c.fetchall()]

        c.execute("SELECT id, category, description, amount, responsible FROM expenses ORDER BY id DESC LIMIT 10")
        expenses = [dict(r) for r in c.fetchall()]

        c.execute("""
        SELECT 
            COALESCE(SUM(gross_total), 0) as faturamento_total,
            COALESCE(SUM(partner_cost), 0) as custos_cargas,
            COALESCE(SUM(expenses_total), 0) as total_despesas,
            COALESCE(SUM(net_profit), 0) as lucro_liquido_total,
            COALESCE(SUM(total_kg), 0) as total_quilos_vendidos
        FROM transactions
        """)
        summary = dict(c.fetchone())

    # Contexto de atendimento comercial e gestão de pedidos do Mattinhos
    order_channel_prompt = (
        "\n=======================================================\n"
        "CANAL DE ATENDIMENTO COMERCIAL E FILA DE PEDIDOS:\n"
        f"Você está conversando diretamente com o cliente '{client_name}'.\n"
        f"- Seja amigável, acolhedor, rápido e comercial ('Fala {client_name}! Aqui é o Mattinhos da Carvão Mattos 🔥').\n"
        "- Não mencione números de telefone ou termos técnicos de conexão na conversa.\n"
        "- Se o cliente quiser fazer um pedido: identifique quantos sacos ele precisa (10kg, 6kg, 3kg, 2kg), confira disponibilidade no estoque, calcule o total e anote o endereço de entrega.\n"
        "- IMPORTANTE: Quando o cliente passar os itens e endereço (ou disser 'fecha', 'pode fechar', 'confirmo'), CHAME IMEDIATAMENTE a ferramenta create_order para registrar o pedido no banco com status PENDENTE e forneça o código gerado pro cliente (#PED-XXXXX)!\n"
        "- Se o cliente perguntar o status do pedido dele: chame a ferramenta check_order_status com o código (#PED-XXXXX) ou o nome do cliente para informá-lo em qual etapa está (ex: Em separação, Saiu para entrega 🚚).\n"
        "- Não invente preços; utilize os preços padrão dos produtos cadastrados no sistema (ex: 10kg R$ 36,00, 6kg R$ 21,60, 3kg R$ 10,80, 2kg R$ 7,60).\n"
    )
    if payload.chat_history:
        order_channel_prompt += f"HISTÓRICO RECENTE DA CONVERSA:\n{payload.chat_history}\n"
    order_channel_prompt += "=======================================================\n"

    prompt_template = """
Você é o 'Mattinhos', a inteligência artificial com CONTROLE TOTAL do sistema operacional e de atendimento da empresa 'Carvão Mattos'.
Você tem permissão para:
1. GESTÃO E FILA DE PEDIDOS DE CLIENTES:
   - Registrar novos pedidos de clientes com itens, quantidades, valores e endereço de entrega através da ferramenta `create_order` (status inicial: PENDENTE).
   - Consultar o status de pedidos de clientes (via código #PED ou nome do cliente) através da ferramenta `check_order_status`.
   - Atualizar status de pedidos (PENDENTE -> CONFIRMADO -> EM_SEPARACAO -> SAIU_PARA_ENTREGA -> ENTREGUE) via `update_order_status`.
   - Acompanhar a fila de pedidos e organizar a logística de entrega.

2. LANÇAMENTO DE CARGAS E ROMANEIOS:
   - Inserir romaneios, cargas e vendas no sistema (`create_transaction`).
   - Deletar romaneios ou despesas se o usuário solicitar (`delete_transaction`).
   - Cadastrar clientes (`create_customer`), fornecedores (`create_supplier`) e despesas (`create_expense`).
   - Ajustar estoque de sacos de carvão (`adjust_stock`).

3. LEITURA DE FOTOS E IMAGENS COM OCR (ROMANEIOS, NOTAS, CADERNO, PEDÁGIOS):
   - Identifique cada linha (quantidade de sacos, peso unitário, peso total em kg, preço por kg, subtotal).
   - Identifique valores pagos a fornecedores (custo da carga) e despesas.
   - Calcule a Sobra Bruta e a Sobra Líquida Real e registre no sistema.

4. PESQUISA NA INTERNET, MERCADO E CONCORRENTES:
   - Panorama de mercado e marcas concorrentes (Bom de Brasa, Carvão São José, Carvão Ipê, Carvão Bonanza, etc.).
   - Faixa de preços real praticada no Brasil.

DADOS REAIS DO SISTEMA EM TEMPO REAL:
- Resumo Financeiro: __SUMMARY__
- Estoque de Sacos: __PRODUCTS__
- Fila de Pedidos Atuais: __ORDERS__
- Últimas Transações / Romaneios: __TXS__
- Clientes Cadastrados: __CUSTOMERS__
- Fornecedores: __SUPPLIERS__
- Despesas Recentes: __EXPENSES__

COMO EXECUTAR AÇÕES NO SISTEMA:
Sempre que precisar criar pedidos, atualizar status ou lançar transações, inclua blocos especiais no final da sua resposta:

```tool_call
{"tool": "create_order", "args": {
    "customer_name": "Nome do Cliente",
    "delivery_address": "Rua X, 123 - Bairro",
    "items": [
        {"product_name": "Saco 10 kg", "bag_weight_kg": 10.0, "units": 5, "price_per_unit": 36.0}
    ],
    "delivery_fee": 10.0,
    "notes": "Entregar até as 17h"
}}
```

Outras ferramentas disponíveis:
- check_order_status: `{"tool": "check_order_status", "args": {"phone_or_code": "PED-12345"}}` (ou o nome do cliente)
- update_order_status: `{"tool": "update_order_status", "args": {"order_code_or_id": "PED-12345", "new_status": "SAIU_PARA_ENTREGA", "notes": "Com motorista João"}}`
- create_transaction: `{"tool": "create_transaction", "args": {...}}`
- create_customer: `{"tool": "create_customer", "args": {"name": "...", "phone": "...", "city": "..."}}`
- create_supplier: `{"tool": "create_supplier", "args": {"name": "...", "phone": "...", "city": "..."}}`
- create_expense: `{"tool": "create_expense", "args": {"category": "FRETE|PEDAGIO|EMBALAGEM|OUTROS", "description": "...", "amount": 100.0, "responsible": "..."}}`
- adjust_stock: `{"tool": "adjust_stock", "args": {"product_name_or_id": "10", "stock_units": 200}}`
"""
    system_prompt = prompt_template \
        .replace("__SUMMARY__", json.dumps(summary, ensure_ascii=False)) \
        .replace("__PRODUCTS__", json.dumps(products, ensure_ascii=False)) \
        .replace("__ORDERS__", json.dumps(orders, ensure_ascii=False)) \
        .replace("__TXS__", json.dumps(txs, ensure_ascii=False)) \
        .replace("__CUSTOMERS__", json.dumps(customers, ensure_ascii=False)) \
        .replace("__SUPPLIERS__", json.dumps(suppliers, ensure_ascii=False)) \
        .replace("__EXPENSES__", json.dumps(expenses, ensure_ascii=False)) \
        + order_channel_prompt

    # Pesquisa na web se aplicável
    web_search_section = ""
    if user_query and should_search_web(user_query):
        search_q = build_search_query(user_query)
        web_results = perform_web_search(search_q, max_results=5)
        if web_results:
            items_str = [f"[{i+1}] {r['title']} - {r['href']}\n    {r['snippet']}" for i, r in enumerate(web_results)]
            web_search_section = (
                "\n\n=======================================================\n"
                f"🌐 RESULTADOS REAIS DE PESQUISA NA WEB:\n{chr(10).join(items_str)}\n"
                "=======================================================\n"
            )

    content_parts = []

    # OCR se imagem fornecida
    ocr_section = ""
    if image_data and "," in image_data:
        try:
            header, b64_bytes = image_data.split(",", 1)
            mime = header.split(";")[0].replace("data:", "")
            content_parts.append({
                "inline_data": {
                    "mime_type": mime,
                    "data": b64_bytes
                }
            })
            raw_ocr = extract_ocr_from_base64(image_data)
            if raw_ocr:
                ocr_section = f"\n\n=== OCR BRUTO PRÉ-EXTRAÍDO ===\n{raw_ocr}\n===============================\n"
        except Exception:
            pass

    # Áudio se presente
    if audio_data and "," in audio_data:
        try:
            header, b64_audio = audio_data.split(",", 1)
            audio_mime = header.split(";")[0].replace("data:", "")
            content_parts.append({
                "inline_data": {
                    "mime_type": audio_mime,
                    "data": b64_audio
                }
            })
        except Exception:
            pass

    default_instruction = "Analise esta imagem com OCR detalhado, faça os cálculos de conferência e registre no sistema Carvão Mattos." if image_data else "Comando por voz ou mensagem: atenda a solicitação."
    prompt_text = user_query if user_query else default_instruction
    content_parts.append({"text": f"{system_prompt}{web_search_section}{ocr_section}\n\nMENSAGEM:\n{prompt_text}"})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
    body = {
        "contents": [
            {
                "role": "user",
                "parts": content_parts
            }
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=body)
            if resp.status_code != 200:
                fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
                resp2 = await client.post(fallback_url, json=body)
                if resp2.status_code != 200:
                    return {"reply": f"Erro na Gemini ({resp.status_code}): {resp.text}"}
                data = resp2.json()
            else:
                data = resp.json()

            reply = data["candidates"][0]["content"]["parts"][0]["text"]

            # PARSER DE TOOL_CALL: Executar comandos no banco de dados
            executed_actions = []
            tool_matches = re.findall(r"```tool_call\s*(.*?)\s*```", reply, re.DOTALL)
            for raw_json in tool_matches:
                try:
                    call_obj = json.loads(raw_json)
                    tool_name = call_obj.get("tool")
                    tool_args = call_obj.get("args", {})
                    action_result = execute_ai_tool(tool_name, tool_args)
                    executed_actions.append(action_result)
                except Exception as ex:
                    executed_actions.append(f"Erro ao processar ação: {str(ex)}")

            # Limpar blocos de código tool_call da resposta visível
            clean_reply = re.sub(r"```tool_call\s*.*?\s*```", "", reply, flags=re.DOTALL).strip()

            if executed_actions:
                badge = "\n\n---\n### 🟢 Ações no Sistema pelo Mattinhos:\n" + "\n".join([f"* {act}" for act in executed_actions])
                clean_reply += badge

            return {"reply": clean_reply, "actions_executed": len(executed_actions)}

    except Exception as e:
        return {"reply": f"Erro de comunicação com o Mattinhos: {str(e)}"}

# ----------------- ARQUIVOS ESTÁTICOS -----------------
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("/app/static/index.html")
