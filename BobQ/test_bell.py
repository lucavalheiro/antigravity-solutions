#!/usr/bin/env python3
"""
Test 1: Emaranhamento Quântico (Estado de Bell) no Windows
Utiliza Qiskit 2.x e StatevectorSampler (Simulador Local)
"""
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

print("=" * 60)
print("IBM Quantum + Qiskit (Windows): Estado de Bell")
print("=" * 60)

# Circuito (|00> + |11>) / sqrt(2)
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

print("Circuito Quântico:")
print(qc.draw(output="text"))

sampler = StatevectorSampler()
job = sampler.run([qc], shots=1024)
counts = job.result()[0].data.meas.get_counts()

print("\nContagens de medição (1024 tiros):")
print(counts)

total = sum(counts.values())
p00 = counts.get('00', 0) / total
p11 = counts.get('11', 0) / total
print(f"Probabilidade |00>: {p00:.2%}, Probabilidade |11>: {p11:.2%}")

if p00 > 0.4 and p11 > 0.4 and (p00 + p11) > 0.95:
    print("\n>>> SUCESSO: Emaranhamento Quântico verificado no Windows! <<<")
