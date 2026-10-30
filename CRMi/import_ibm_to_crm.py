"""
Importador IBM Price List -> Frappe CRM / ERPNext
=================================================
Popula via API REST:
  1. CRM Product     (Frappe CRM)
  2. Item            (ERPNext)
  3. Item Price      (ERPNext - Price List "IBM Out 2025")

Uso:
    python import_ibm_to_crm.py

Requer: Python 3.7+ (stdlib apenas, sem dependências externas)
"""

import urllib.request
import urllib.parse
import http.cookiejar
import json
import sys
import time
import os

# ─────────────────────────── CONFIG ───────────────────────────
BASE_URL       = "http://10.1.0.65:8080"
USERNAME       = "Administrator"
PASSWORD       = "lula2001"
DATA_FILE      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "produtos_ibm_out_2025.json")
PRICE_LIST     = "IBM Out 2025"
BATCH_SIZE     = 50          # Itens por lote (evitar timeout)
MAX_RETRIES    = 3
RETRY_DELAY    = 2           # segundos entre retentativas
# ───────────────────────────────────────────────────────────────

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
CSRF_TOKEN = None

def log(msg):
    print(msg, flush=True, file=sys.stdout)

# Forcar UTF-8 no stdout do Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def api_get(path):
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        headers={"Accept": "application/json", "X-Frappe-CSRF-Token": CSRF_TOKEN or ""}
    )
    with opener.open(req, timeout=30) as resp:
        return json.loads(resp.read()), resp.status

def api_post(path, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Frappe-CSRF-Token": CSRF_TOKEN or ""
        }
    )
    with opener.open(req, timeout=30) as resp:
        return json.loads(resp.read()), resp.status

def login():
    global CSRF_TOKEN
    log("🔐 Autenticando no Frappe...")
    data = urllib.parse.urlencode({"usr": USERNAME, "pwd": PASSWORD}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/api/method/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    )
    with opener.open(req, timeout=15) as resp:
        body = json.loads(resp.read())
        if body.get("message") != "Logged In":
            log(f"❌ Falha no login: {body}")
            sys.exit(1)

    # Obter CSRF Token
    resp_data, _ = api_get("/api/method/frappe.auth.get_logged_user")
    for cookie in cookie_jar:
        if cookie.name == "csrf_token":
            CSRF_TOKEN = cookie.value
            break
    log(f"✅ Login OK | CSRF: {CSRF_TOKEN[:20] if CSRF_TOKEN else 'N/A'}...")

def doc_exists(doctype, name):
    try:
        encoded = urllib.parse.quote(name, safe="")
        _, status = api_get(f"/api/resource/{urllib.parse.quote(doctype)}/{encoded}")
        return True
    except Exception:
        return False

def create_doc(doctype, payload, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            result, status = api_post(f"/api/resource/{urllib.parse.quote(doctype)}", payload)
            return result, status
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if "DuplicateEntryError" in body or "already exists" in body.lower():
                return {"status": "skipped"}, 409
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise
        except Exception:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise

def ensure_price_list():
    log(f"📋 Verificando Price List '{PRICE_LIST}'...")
    try:
        api_get(f"/api/resource/Price%20List/{urllib.parse.quote(PRICE_LIST)}")
        log(f"   Price List já existe.")
    except Exception:
        log(f"   Criando Price List '{PRICE_LIST}'...")
        payload = {
            "doctype": "Price List",
            "price_list_name": PRICE_LIST,
            "currency": "BRL",
            "selling": 1,
            "buying": 0,
            "enabled": 1
        }
        create_doc("Price List", payload)
        log(f"   ✅ Price List criada.")

def ensure_item_group(name):
    try:
        api_get(f"/api/resource/Item%20Group/{urllib.parse.quote(name)}")
    except Exception:
        payload = {
            "doctype": "Item Group",
            "item_group_name": name,
            "parent_item_group": "All Item Groups",
            "is_group": 0
        }
        try:
            create_doc("Item Group", payload)
        except Exception:
            pass  # Pode já existir por race condition

def ensure_brand(name):
    if not name or name.strip() == "":
        return
    try:
        api_get(f"/api/resource/Brand/{urllib.parse.quote(name)}")
    except Exception:
        payload = {"doctype": "Brand", "brand": name}
        try:
            create_doc("Brand", payload)
        except Exception:
            pass

def import_items(items):
    log(f"\n📦 Importando {len(items):,} produtos para CRM Product + Item + Item Price...")
    
    # Coletar grupos e marcas únicas
    brands = set(i["brand"] for i in items if i.get("brand"))
    groups = set(i["brand"] for i in items if i.get("brand"))  # brand vira item_group

    log(f"   → Criando {len(brands)} marcas (Brands)...")
    for b in sorted(brands):
        ensure_brand(b)

    log(f"   → Criando {len(groups)} grupos de itens (Item Groups)...")
    for g in sorted(groups):
        ensure_item_group(g)

    total = len(items)
    crm_ok = crm_skip = crm_err = 0
    item_ok = item_skip = item_err = 0
    price_ok = price_skip = price_err = 0

    for i, product in enumerate(items):
        code      = product.get("product_code", "")
        name      = product.get("product_name", code)[:140]  # Frappe limita a 140 chars
        desc      = product.get("full_description", name)
        brand     = product.get("brand", "")
        rate      = float(product.get("standard_rate") or 0)
        unit      = product.get("charge_unit", "Nos") or "Nos"
        part_type = product.get("part_type", "")
        pid       = product.get("ibm_pid", "")
        tradename = product.get("tradename", "")
        tiers_txt = ""
        if product.get("tiers"):
            lines = [f"Qtd ≥ {t['tier']}: R$ {t['rate']:.2f}" for t in product["tiers"]]
            tiers_txt = "<br>".join(lines)

        full_desc = (
            f"<b>Part Number:</b> {code}<br>"
            f"<b>IBM PID:</b> {pid}<br>"
            f"<b>Tradename:</b> {tradename}<br>"
            f"<b>Tipo:</b> {part_type}<br>"
            f"<b>Unidade:</b> {unit}<br><br>"
            f"{desc}"
            + (f"<br><br><b>Faixas de Preço (BRL):</b><br>{tiers_txt}" if tiers_txt else "")
        )

        # ── 1. CRM Product ──────────────────────────────────────────
        crm_payload = {
            "doctype": "CRM Product",
            "product_code": code,
            "product_name": name,
            "standard_rate": rate,
            "description": full_desc[:65535]
        }
        try:
            _, status = create_doc("CRM Product", crm_payload)
            if status == 409:
                crm_skip += 1
            else:
                crm_ok += 1
        except Exception as e:
            crm_err += 1

        # ── 2. Item (ERPNext) ────────────────────────────────────────
        item_payload = {
            "doctype": "Item",
            "item_code": code,
            "item_name": name,
            "item_group": brand if brand else "All Item Groups",
            "brand": brand if brand else None,
            "stock_uom": "Nos",
            "description": full_desc[:65535],
            "is_stock_item": 0,
            "is_sales_item": 1,
            "is_purchase_item": 0,
            "standard_rate": rate,
            "disabled": 0
            # Nota: sales_uom omitido — valores como "Managed Virtual Server"
            # nao existem como UOM no Frappe. Unidade fica registrada na descricao.
        }
        try:
            _, status = create_doc("Item", item_payload)
            if status == 409:
                item_skip += 1
            else:
                item_ok += 1
        except Exception as e:
            item_err += 1

        # ── 3. Item Price (ERPNext) ──────────────────────────────────
        if rate > 0:
            price_payload = {
                "doctype": "Item Price",
                "item_code": code,
                "price_list": PRICE_LIST,
                "selling": 1,
                "currency": "BRL",
                "price_list_rate": rate,
                "valid_from": "2025-01-01",
                "valid_upto": "2025-12-31",
                "item_name": name,
                "note": f"IBM Price List Out/2025 | Tipo: {part_type}"
            }
            try:
                _, status = create_doc("Item Price", price_payload)
                if status == 409:
                    price_skip += 1
                else:
                    price_ok += 1
            except Exception as e:
                price_err += 1

        # ── Progresso ────────────────────────────────────────────────
        if (i + 1) % BATCH_SIZE == 0 or (i + 1) == total:
            pct = (i + 1) / total * 100
            log(
                f"   [{i+1:5d}/{total}] {pct:5.1f}% | "
                f"CRM: +{crm_ok} skip={crm_skip} err={crm_err} | "
                f"Item: +{item_ok} skip={item_skip} err={item_err} | "
                f"Price: +{price_ok} skip={price_skip} err={price_err}"
            )

    log(f"\n{'='*65}")
    log(f"✅ IMPORTAÇÃO CONCLUÍDA")
    log(f"   CRM Product → {crm_ok} criados | {crm_skip} já existiam | {crm_err} erros")
    log(f"   Item        → {item_ok} criados | {item_skip} já existiam | {item_err} erros")
    log(f"   Item Price  → {price_ok} criados | {price_skip} já existiam | {price_err} erros")
    log(f"{'='*65}")

def main():
    log("=" * 65)
    log("  IBM Price List → Frappe CRM / ERPNext Importer")
    log("=" * 65)

    if not os.path.exists(DATA_FILE):
        log(f"❌ Arquivo não encontrado: {DATA_FILE}")
        sys.exit(1)

    log(f"📂 Carregando dados de: {os.path.basename(DATA_FILE)}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)
    log(f"   {len(items):,} produtos carregados.")

    login()
    ensure_price_list()
    import_items(items)

if __name__ == "__main__":
    main()
