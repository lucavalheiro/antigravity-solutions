b64 = open('projeto-sommelier/index.b64', 'r').read().strip()
half = len(b64) // 2
open('projeto-sommelier/p1.b64', 'w').write(b64[:half])
open('projeto-sommelier/p2.b64', 'w').write(b64[half:])
print(f"P1: {len(b64[:half])}, P2: {len(b64[half:])}")
