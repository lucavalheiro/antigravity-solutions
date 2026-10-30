"""
Script de teste de integracao do Simulador Quantico IBM Qiskit Aer & MCP Server.
Executa simulacoes remotas no container isolado em http://10.1.0.65:8090.
"""

from quantum_client import IBMQuantumClient
import json
import sys

# Forcar UTF-8 no stdout se suportado
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_section(title: str):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def main():
    client = IBMQuantumClient("http://10.1.0.65:8090")
    
    # 1. Healthcheck
    print_section("1. Verificando Conexao e Saude do Servidor")
    health = client.health()
    print(f"Status: {health['status']}")
    print(f"Servico: {health['service']}")
    print(f"Metodos Suportados: {', '.join(health['methods'])}")
    
    # 2. Bell State
    print_section("2. Simulacao de Entrelacamento Quantico (Estado de Bell |Phi+>)")
    bell = client.bell_state()
    print("Circuito QASM:")
    print(bell["qasm"])
    print("\nResultados da Simulacao (1024 shots):")
    for state, prob in bell["simulation"]["probabilities"].items():
        print(f"  Estado |{state}>: {prob * 100:.2f}% ({bell['simulation']['counts'].get(state, 0)} shots)")
        
    # 3. Grover's Algorithm
    print_section("3. Algoritmo de Busca Quantica de Grover (Alvo: '101')")
    grover = client.grover_search(target_bitstring="101")
    print(f"Alvo procurado: '{grover['target']}'")
    print(f"Qubits: {grover['qubits']}")
    print(f"Iteracoes de Grover: {grover['grover_iterations']}")
    print(f"Taxa de sucesso na medicao: {grover['success_rate'] * 100:.2f}%")
    print("Top 3 estados mais medidos:")
    sorted_counts = sorted(grover["simulation"]["counts"].items(), key=lambda x: x[1], reverse=True)[:3]
    for state, count in sorted_counts:
        print(f"  Estado |{state}>: {count} shots ({count / 1024 * 100:.2f}%)")
        
    # 4. Noise Simulation with IBM Hardware
    print_section("4. Simulacao com Ruido Real de Hardware IBM (FakeBrisbane - 127 Qubits)")
    noise_res = client.simulate_with_noise(bell["qasm"], backend_name="fake_brisbane", shots=1024)
    print(f"Hardware Emulado: {noise_res['hardware_emulated']} ({noise_res['total_physical_qubits']} qubits fisicos)")
    print("Distribuicao com ruido termico, erro de portas e readout:")
    for state, prob in sorted(noise_res["probabilities"].items(), key=lambda x: x[1], reverse=True):
        print(f"  Estado |{state}>: {prob * 100:.2f}% ({noise_res['counts'].get(state, 0)} shots)")
        
    print_section("Todos os testes quanticos foram concluidos com sucesso!")

if __name__ == "__main__":
    main()
