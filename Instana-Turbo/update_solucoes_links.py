# -*- coding: utf-8 -*-
with open('projeto-sommelier/solucoes.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace hardcoded IP links with relative paths
replacements = [
    ('href="http://10.1.0.65:8080/app/sales-order"', 'href="/erpnext"'),
    ('href="http://10.1.0.65:8080"', 'href="/erpnext"'),
    ('href="http://192.168.173.22:8090"', 'href="/glpi"'),
    ('href="http://10.1.0.65:8090"', 'href="/quantum"'),
    ('href="http://10.1.0.65.nip.io"', 'href="/instana"'),
    ('href="http://10.1.0.65:8443"', 'href="/turbonomic"'),
]

for old, new in replacements:
    count = text.count(old)
    text = text.replace(old, new)
    print(f"Replaced {old} -> {new}: {count} times")

# Add module navigation in header if not already present
old_header_end = '<div class="flex items-center space-x-1.5 sm:space-x-2.5 flex-shrink-0">'
new_header_nav = '''<!-- Module Navigation Pills -->
      <nav class="hidden lg:flex items-center space-x-1 text-xs">
        <a href="/" class="px-3 py-1.5 rounded-full hover:bg-[#f5f5f7] text-[#6e6e73] font-medium transition-colors">Loja Sommelier</a>
        <a href="/solucoes" class="px-3 py-1.5 rounded-full bg-[#1d1d1f] text-white font-medium shadow-xs">Painel O2C</a>
        <a href="/erpnext" class="px-3 py-1.5 rounded-full hover:bg-[#f5f5f7] text-[#6e6e73] font-medium transition-colors">ERPNext</a>
        <a href="/glpi" class="px-3 py-1.5 rounded-full hover:bg-[#f5f5f7] text-[#6e6e73] font-medium transition-colors">GLPI ITIL</a>
        <a href="/quantum" class="px-3 py-1.5 rounded-full hover:bg-[#f5f5f7] text-[#6e6e73] font-medium transition-colors">IBM Quantum</a>
      </nav>

      <div class="flex items-center space-x-1.5 sm:space-x-2.5 flex-shrink-0">'''

if old_header_end in text and '<!-- Module Navigation Pills -->' not in text:
    text = text.replace(old_header_end, new_header_nav, 1)
    print("Added module navigation to header in solucoes.html")

with open('projeto-sommelier/solucoes.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("solucoes.html updated successfully!")
