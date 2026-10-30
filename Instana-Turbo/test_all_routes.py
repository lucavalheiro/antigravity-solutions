import urllib.request
import json

base = "https://psychiatry-sampling-blues-wherever.trycloudflare.com"

routes = [
    ("/", "Adega"),
    ("/solucoes", "Painel de Soluções"),
    ("/erpnext", "ERPNext"),
    ("/glpi", "GLPI"),
    ("/quantum", "Quantum"),
    ("/instana", "Instana"),
    ("/turbonomic", "Turbonomic"),
    ("/images/romanee.jpg", None),
]

print("=== TESTING GET ROUTES ===")
for r, keyword in routes:
    url = base + r
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read()
            text = content[:200].decode('utf-8', errors='ignore')
            has_kw = (keyword.lower() in text.lower()) if keyword else True
            print(f"GET {r:15} -> {resp.status} (Length: {len(content)}, Keyword '{keyword}': {has_kw})")
    except Exception as e:
        print(f"GET {r:15} -> ERROR: {e}")

print("\n=== TESTING POST API ===")
post_url = base + "/api/method/crm.api.sommelier.create_wine_order"
payload = json.dumps({"customer": "VIP Test", "wine_code": "VIN-ROMANEE-2017"}).encode('utf-8')
post_req = urllib.request.Request(post_url, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
try:
    with urllib.request.urlopen(post_req, timeout=5) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print(f"POST {post_url} -> {resp.status}")
        print("Response JSON:", json.dumps(res, indent=2))
except Exception as e:
    print("POST ERROR:", e)
