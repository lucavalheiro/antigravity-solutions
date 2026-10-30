"""
Script de Teste Integrado: IA Quântica 'Quantinho' (IBM Granite na GPU Ubuntu)
+ Simulador IBM Qiskit Aer (10.1.0.65:8090)
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from quantum_client import IBMQuantumClient, QuantinhoAI

def main():
    print("=" * 70)
    print(" 🚀 Teste Integrado: IA Quantinho (IBM Granite GPU) + Qiskit Aer")
    print("=" * 70)

    # 1. Conectar ao Quantinho na GPU Ubuntu
    print("\n1. Conectando a IA Quantinho na GPU NVIDIA L4 da Ubuntu (192.168.173.22:3000)...")
    quantinho = QuantinhoAI("http://192.168.173.22:3000/quantum-ai/v1")
    
    saudacao = quantinho.chat("Quantinho, apresente-se em 2 frases para nossa equipe e mencione sua GPU.", max_tokens=120)
    print(f"\n[Quantinho]:\n{saudacao}\n", flush=True)

    # 2. Conectar ao Simulador Qiskit Aer
    print("-" * 70, flush=True)
    print("2. Conectando ao Simulador Qiskit Aer em 10.1.0.65:8090...", flush=True)
    sim = IBMQuantumClient("http://10.1.0.65:8090")
    health = sim.health()
    print(f"Status do Simulador: {health['status']} ({health['service']})", flush=True)

    # 3. Pedir para o Quantinho gerar um circuito quântico
    print("-" * 70, flush=True)
    print("3. Executando circuito de Teletransporte Quantico no Qiskit Aer...", flush=True)
    teleport_circuit = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];

// Preparar qubit 0 em superposicao (|psi>)
h q[0];

// Criar par entrelaçado de Bell entre q[1] e q[2]
h q[1];
cx q[1], q[2];

// Teletransporte de Bell measurement
cx q[0], q[1];
h q[0];

// Medicoes
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];"""

    print("Executando circuito no simulador Qiskit Aer com 1024 shots...", flush=True)
    resultado = sim.simulate(teleport_circuit, shots=1024)
    print("Probabilidades medidas:", resultado["probabilities"], flush=True)

    # 4. Enviar resultados de volta ao Quantinho para analise fisica
    print("-" * 70, flush=True)
    print("4. Enviando medicoes para o Quantinho interpretar a mecanica quantica...", flush=True)
    interpretacao = quantinho.interpret_results(teleport_circuit, resultado["probabilities"], backend="Aer Simulator (Ideal)", max_tokens=250)
    print(f"\n[Analise Fisica do Quantinho]:\n{interpretacao}\n", flush=True)

    print("=" * 70)
    print(" ✅ Teste concluido com 100% de sucesso!")
    print("=" * 70)

if __name__ == "__main__":
    main()
