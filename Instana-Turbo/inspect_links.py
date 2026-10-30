import re

for filename in ['projeto-sommelier/index.html', 'projeto-sommelier/solucoes.html']:
    print(f'=== {filename} ===')
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    hrefs = re.findall(r'href=[\'"]([^\'"]+)[\'"]', text)
    srcs = re.findall(r'src=[\'"]([^\'"]+)[\'"]', text)
    fetches = re.findall(r'fetch\([\'"]([^\'"]+)[\'"]', text)
    ips = re.findall(r'(https?://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(?::[0-9]+)?(?:/[^\s"\'<>]*)?)', text)
    print('Hrefs:')
    for h in sorted(set(hrefs)):
        print('  ', h)
    print('Fetches:')
    for fe in sorted(set(fetches)):
        print('  ', fe)
    print('IPs:')
    for ip in sorted(set(ips)):
        print('  ', ip)
