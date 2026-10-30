#!/usr/bin/env python3
"""
Test 2: PoC de Otimização Logística via QAOA (Windows)
Balanceamento de frotas e pacotes comparando busca clássica contra algoritmo quântico.
"""
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

print("=" * 65)
print("PoC: Otimização de Rotas Logísticas via QAOA (Windows)")
print("=" * 65)

costs = np.array([3, 5, 4])
target_load = np.sum(costs) / 2
print(f"Cargas dos pacotes: {costs}")
print(f"Meta de carga por veículo: {target_load:.1f}")

def classical_cost(bitstring):
    x = np.array([int(b) for b in bitstring])
    t1 = np.sum(costs * x)
    t2 = np.sum(costs * (1 - x))
    return abs(t1 - t2)

print("\n--- 1. Busca Exaustiva Clássica ---")
best_cost = float('inf')
best_cfg = None
for i in range(2**len(costs)):
    bits = f"{i:03b}"
    cost = classical_cost(bits)
    print(f"Config {bits}: Carga Veículo 1 = {np.sum(costs * [int(b) for b in bits])}, Discrepância = {cost}")
    if cost < best_cost:
        best_cost = cost
        best_cfg = bits

print(f"Ótimo Clássico: Configuração {best_cfg} (Discrepância = {best_cost})")

def create_qaoa_circuit(gamma, beta):
    n = len(costs)
    qc = QuantumCircuit(n)
    qc.h(range(n))
    
    for i in range(n):
        for j in range(i + 1, n):
            weight = costs[i] * costs[j] * 0.1
            qc.cx(i, j)
            qc.rz(2 * gamma * weight, j)
            qc.cx(i, j)
            
    for i in range(n):
        qc.rx(2 * beta, i)
        
    qc.measure_all()
    return qc

sampler = StatevectorSampler()

def objective(params):
    g, b = params
    qc = create_qaoa_circuit(g, b)
    counts = sampler.run([qc], shots=1024).result()[0].data.meas.get_counts()
    
    avg_cost = 0.0
    total = sum(counts.values())
    for bits, cnt in counts.items():
        avg_cost += cnt * classical_cost(bits[::-1])
    return avg_cost / total

print("\n--- 2. Otimização Híbrida QAOA (Local Aer) ---")
res = minimize(objective, [0.5, 0.5], method='COBYLA', options={'maxiter': 30})
opt_g, opt_b = res.x
print(f"Parâmetros ótimos: gamma={opt_g:.4f}, beta={opt_b:.4f}")

final_qc = create_qaoa_circuit(opt_g, opt_b)
counts = sampler.run([final_qc], shots=2048).result()[0].data.meas.get_counts()
sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

print("\n--- 3. Top 3 Estados Quânticos Amostrados ---")
for raw_bits, cnt in sorted_counts[:3]:
    bits = raw_bits[::-1]
    prob = cnt / 2048
    disc = classical_cost(bits)
    print(f"Estado |{bits}>: Probabilidade = {prob:.2%}, Discrepância = {disc}")

top_state = sorted_counts[0][0][::-1]
if classical_cost(top_state) == best_cost:
    print(f"\n>>> SUCESSO: O circuito QAOA convergiu exatamente para a solução ótima |{top_state}>! <<<")
