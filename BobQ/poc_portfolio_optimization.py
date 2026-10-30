#!/usr/bin/env python3
"""
PoC: Seleção Ótima de Portfólio (Finanças & Alocação de Ativos)
Simulação local via Qiskit Aer com geração de gráfico PNG.
"""
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

print("=" * 70)
print("PoC Quântica (Windows): Seleção Ótima de Portfólio via QAOA")
print("=" * 70)

assets = ["Ativo_A", "Ativo_B", "Ativo_C", "Ativo_D"]
returns = np.array([0.12, 0.20, 0.15, 0.08])
risks = np.array([0.05, 0.18, 0.10, 0.03])
budget = 2

def score_portfolio(bitstring):
    x = np.array([int(b) for b in bitstring])
    selected_count = np.sum(x)
    total_return = np.sum(returns * x)
    total_risk = np.sum(risks * x)
    penalty = 10.0 * (selected_count - budget)**2
    cost = total_risk - total_return + penalty
    return cost, total_return, total_risk

best_bits = None
best_cost = float('inf')
for i in range(16):
    bits = f"{i:04b}"
    cost, ret, rsk = score_portfolio(bits)
    if np.sum([int(b) for b in bits]) == budget:
        if cost < best_cost:
            best_cost = cost
            best_bits = bits

print(f"Melhor Carteira Clássica: {best_bits} ({[assets[j] for j, b in enumerate(best_bits) if b == '1']}) com Custo={best_cost:.4f}")

def build_qaoa_circuit(gamma, beta):
    n = 4
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for i in range(n):
        cost_i, _, _ = score_portfolio("0" * i + "1" + "0" * (n - 1 - i))
        qc.rz(2 * gamma * cost_i, i)
    for i in range(n):
        for j in range(i + 1, n):
            qc.cx(i, j)
            qc.rz(gamma * 0.5, j)
            qc.cx(i, j)
    for i in range(n):
        qc.rx(2 * beta, i)
    qc.measure_all()
    return qc

sampler = StatevectorSampler()

def objective(params):
    g, b = params
    qc = build_qaoa_circuit(g, b)
    counts = sampler.run([qc], shots=1024).result()[0].data.meas.get_counts()
    total_cost = 0
    total_shots = sum(counts.values())
    for raw_bits, cnt in counts.items():
        cost, _, _ = score_portfolio(raw_bits[::-1])
        total_cost += cnt * cost
    return total_cost / total_shots

res = minimize(objective, [0.3, 0.3], method='COBYLA', options={'maxiter': 35})
opt_g, opt_b = res.x

final_qc = build_qaoa_circuit(opt_g, opt_b)
counts = sampler.run([final_qc], shots=4096).result()[0].data.meas.get_counts()
sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)

labels = [b[::-1] for b, _ in sorted_counts[:6]]
probs = [c / 4096 * 100 for _, c in sorted_counts[:6]]
colors = ['#1f77b4' if b != best_bits else '#2ca02c' for b in labels]

plt.figure(figsize=(9, 5))
plt.bar(labels, probs, color=colors)
plt.title("QAOA Windows: Probabilidade de Seleção de Portfólio", fontsize=12)
plt.xlabel("Configuração de Ativos |x0 x1 x2 x3>", fontsize=11)
plt.ylabel("Probabilidade (%)", fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

output_img = "portfolio_qaoa_result.png"
plt.savefig(output_img, dpi=150)
print(f"\n>>> Gráfico salvo com sucesso em: {output_img} <<<")

top_bits = sorted_counts[0][0][::-1]
print(f"Top Quântico: |{top_bits}>")
if top_bits == best_bits:
    print(">>> SUCESSO: QAOA convergiu exatamente para a carteira ótima clássica! <<<")
