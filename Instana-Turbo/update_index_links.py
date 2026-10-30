# -*- coding: utf-8 -*-
with open('projeto-sommelier/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

replacements = [
    ('href="http://10.1.0.65:8080/app/sales-order"', 'href="/erpnext"'),
    ('href="http://10.1.0.65:8080"', 'href="/erpnext"'),
    ('href="http://192.168.173.22:8090"', 'href="/glpi"'),
    ('href="http://10.1.0.65:8090"', 'href="/quantum"'),
    ('href="solucoes.html"', 'href="/solucoes"'),
]

for old, new in replacements:
    count = text.count(old)
    text = text.replace(old, new)
    print(f"Replaced {old} -> {new}: {count} times")

# In buyWine function, ensure erpUrl is relative
text = text.replace(
    'let erpUrl = `${erpBaseUrl}/app/sales-order`;',
    'let erpUrl = `/erpnext?order_id=${orderId}`;'
)
text = text.replace(
    'erpUrl = json.message.erp_url || `${erpBaseUrl}/app/sales-order/${orderId}`;',
    'erpUrl = `/erpnext?order_id=${orderId}`;'
)

# Also check top bar: let's add the module navigation pills in index.html header
# Let's inspect where header nav is
with open('projeto-sommelier/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("index.html updated successfully!")
