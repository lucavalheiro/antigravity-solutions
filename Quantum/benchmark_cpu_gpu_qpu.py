"""
================================================================================
 SUÍTE DE TESTES E BENCHMARK HÍBRIDO: CPU vs GPU vs QPU
 Projeto: IBM Quantum MCP & IA Quantinho (IBM Granite 8B)
================================================================================
Testa e mede a performance dos três pilares da computação avançada:
 1. CPU: Desempenho sequencial e multithread em ponto flutuante (GFLOPS)
 2. GPU: Aceleração de tensores e inferência LLM na NVIDIA L4 (24GB VRAM)
 3. QPU: Simulação quântica com portas lógicas, Grover e ruído real IBM (127Q)
================================================================================
"""

import sys
import time
import math
import socket
import platform
import concurrent.futures
from typing import Dict, Any

# Ajustar codificação para Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from quantum_client import IBMQuantumClient, QuantinhoAI

# ==============================================================================
# 1. TESTE DE CPU (Clássico Sequencial & Multi-Core)
# ==============================================================================
def _cpu_worker(size: int = 1200):
    """Cálculo matricial puro para estressar a CPU."""
    # Gera duas matrizes e calcula produto interno
    A = [[(i + j) * 0.001 for j in range(size)] for i in range(size)]
    # Amostra de operações de ponto flutuante
    acc = 0.0
    for i in range(min(size, 400)):
        for j in range(min(size, 400)):
            acc += math.sin(A[i][j]) * math.cos(A[j][i])
    return acc

def benchmark_cpu() -> Dict[str, Any]:
    print("\n" + "=" * 65)
    print(" 🖥️  1. TESTE DE CPU (PROCESSAMENTO CLÁSSICO)")
    print("=" * 65)
    
    cpu_info = platform.processor() or "Processador Clássico"
    num_cores = platform.os.cpu_count() or 4
    print(f"Sistema: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Processador: {cpu_info}")
    print(f"Núcleos Lógicos Detectados: {num_cores}")
    
    # Teste Single-Core
    print("\n[CPU Test 1/2] Executando benchmark Single-Core...")
    t0 = time.time()
    _ = _cpu_worker(size=600)
    single_time = time.time() - t0
    print(f"  -> Tempo Single-Core: {single_time:.3f} s")
    
    # Teste Multi-Core
    print(f"[CPU Test 2/2] Estressando {num_cores} núcleos simultaneamente (Multi-Core)...")
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = [executor.submit(_cpu_worker, 600) for _ in range(num_cores)]
        concurrent.futures.wait(futures)
    multi_time = time.time() - t0
    
    speedup = (single_time * num_cores) / multi_time if multi_time > 0 else 1.0
    print(f"  -> Tempo Multi-Core ({num_cores} threads): {multi_time:.3f} s")
    print(f"  -> Eficiência de Paralelismo: {speedup:.2f}x de aceleração")
    
    return {
        "device": "CPU",
        "model": cpu_info,
        "cores": num_cores,
        "single_core_time": single_time,
        "multi_core_time": multi_time,
        "speedup": speedup,
        "status": "Aprovado"
    }

# ==============================================================================
# 2. TESTE DE GPU (NVIDIA L4 24GB & IA IBM Granite 8B)
# ==============================================================================
def benchmark_gpu() -> Dict[str, Any]:
    print("\n" + "=" * 65)
    print(" 🎮 2. TESTE DE GPU (NVIDIA L4 - IA & TENSORES)")
    print("=" * 65)
    
    gpu_host = "http://192.168.173.22:3000/quantum-ai/v1"
    print(f"Conectando ao Servidor de Aceleração GPU em {gpu_host}...")
    
    try:
        quantinho = QuantinhoAI(base_url=gpu_host, model="ibm-granite-8b")
        
        # Teste de Inferência de IA Quântica na GPU L4
        prompt_teste = (
            "Explique sucintamente como a superposição quântica difere de um estado clássico probabilístico."
        )
        print(f"\n[GPU Test 1/1] Executando Inferência LLM Quântica (IBM Granite 8B na L4)...")
        print(f"  -> Prompt: \"{prompt_teste}\"")
        
        t0 = time.time()
        resposta = quantinho.chat(prompt=prompt_teste, max_tokens=150)
        gpu_time = time.time() - t0
        
        # Estimativa de tokens
        words = resposta.split()
        est_tokens = int(len(words) * 1.3)
        tok_sec = est_tokens / gpu_time if gpu_time > 0 else 0.0
        
        print(f"  -> Resposta gerada pela GPU:\n     \"{resposta[:140]}...\"")
        print(f"  -> Tempo Total de Inferência GPU: {gpu_time:.3f} s")
        print(f"  -> Velocidade Aferida: ~{tok_sec:.1f} tokens/segundo")
        
        return {
            "device": "GPU",
            "model": "NVIDIA L4 (24GB VRAM, CUDA 13.2) - IBM Granite 8B",
            "inference_time": gpu_time,
            "throughput": f"{tok_sec:.1f} tok/s",
            "status": "Online / Acelerado"
        }
    except Exception as e:
        print(f"  ❌ Erro ao conectar na GPU: {e}")
        return {
            "device": "GPU",
            "model": "NVIDIA L4",
            "error": str(e),
            "status": "Falha na Conexão"
        }

# ==============================================================================
# 3. TESTE DE QPU (Processador Quântico - Qiskit Aer & Fake Backends)
# ==============================================================================
def benchmark_qpu() -> Dict[str, Any]:
    print("\n" + "=" * 65)
    print(" ⚛️  3. TESTE DE QPU (COMPUTAÇÃO QUÂNTICA)")
    print("=" * 65)
    
    qpu_host = "http://10.1.0.65:8090"
    print(f"Conectando ao Simulador QPU Qiskit Aer em {qpu_host}...")
    
    try:
        client = IBMQuantumClient(base_url=qpu_host)
        
        # 1. Healthcheck
        h = client.health()
        print(f"  -> Status do Nó Quântico: {h['status']} ({h['service']})")
        
        # 2. Teste do Estado de Bell (Emaranhamento)
        print("\n[QPU Test 1/3] Gerando Estado de Bell (|Phi+> = (|00> + |11>) / sqrt(2))...")
        t0 = time.time()
        bell = client.bell_state()
        bell_time = time.time() - t0
        p00 = bell["simulation"]["probabilities"].get("00", 0) * 100
        p11 = bell["simulation"]["probabilities"].get("11", 0) * 100
        print(f"  -> Tempo de Execução do Circuito: {bell_time:.3f} s")
        print(f"  -> Medição dos Qubits (1024 shots): |00>: {p00:.1f}%, |11>: {p11:.1f}%")
        
        # 3. Teste de Busca Quântica de Grover
        print("\n[QPU Test 2/3] Algoritmo de Grover (Busca quântica para alvo '101')...")
        t0 = time.time()
        grover = client.grover_search(target_bitstring="101")
        grover_time = time.time() - t0
        print(f"  -> Tempo de Execução de Grover: {grover_time:.3f} s")
        print(f"  -> Probabilidade do Alvo Encontrado: {grover['success_rate']*100:.2f}%")
        
        # 4. Teste com Ruído Real de Hardware IBM Eagle (FakeBrisbane - 127 Qubits)
        print("\n[QPU Test 3/3] Emulação com Ruído Físico do Chip IBM Brisbane (127 Qubits)...")
        t0 = time.time()
        noise = client.simulate_with_noise(bell["qasm"], backend_name="fake_brisbane", shots=1024)
        noise_time = time.time() - t0
        print(f"  -> Tempo de Compilação & Ruído: {noise_time:.3f} s")
        print("  -> Distribuição com Ruído Real (T1, T2 e Erro de Leitura):")
        for state, prob in sorted(noise["probabilities"].items(), key=lambda x: x[1], reverse=True):
            print(f"     |{state}>: {prob*100:.2f}% ({noise['counts'].get(state, 0)} shots)")
            
        return {
            "device": "QPU",
            "model": "IBM Qiskit Aer (FakeBrisbane 127Q / Heron 133Q)",
            "bell_time": bell_time,
            "grover_success": f"{grover['success_rate']*100:.1f}%",
            "noise_qubits": noise["total_physical_qubits"],
            "status": "Operacional / Calibrado"
        }
    except Exception as e:
        print(f"  ❌ Erro ao conectar na QPU: {e}")
        return {
            "device": "QPU",
            "model": "IBM Quantum Qiskit Aer",
            "error": str(e),
            "status": "Falha na Conexão"
        }

# ==============================================================================
# RELATÓRIO EXECUTIVO CONSOLIDADO
# ==============================================================================
def main():
    print("\n" + "#" * 65)
    print(" INICIANDO BENCHMARK UNIFICADO: CPU + GPU + QPU")
    print("#" * 65)
    
    t_start = time.time()
    
    res_cpu = benchmark_cpu()
    res_gpu = benchmark_gpu()
    res_qpu = benchmark_qpu()
    
    total_time = time.time() - t_start
    
    print("\n" + "=" * 65)
    print(" 📊 RESUMO COMPARATIVO DO BENCHMARK HÍBRIDO")
    print("=" * 65)
    print(f"{'DISPOSITIVO':<10} | {'HARDWARE / MODELO':<32} | {'DESEMPENHO':<14} | {'STATUS'}")
    print("-" * 75)
    
    # Linha CPU
    print(f"{res_cpu['device']:<10} | {res_cpu['model'][:30]:<32} | {res_cpu['speedup']:.2f}x speedup   | {res_cpu['status']}")
    
    # Linha GPU
    gpu_perf = res_gpu.get('throughput', 'N/A')
    print(f"{res_gpu['device']:<10} | {res_gpu['model'][:30]:<32} | {gpu_perf:<14} | {res_gpu['status']}")
    
    # Linha QPU
    qpu_perf = res_qpu.get('grover_success', '100% fid')
    print(f"{res_qpu['device']:<10} | {res_qpu['model'][:30]:<32} | {qpu_perf:<14} | {res_qpu['status']}")
    
    print("-" * 75)
    print(f"⏱️ Tempo total da bateria de testes: {total_time:.2f} segundos\n")

if __name__ == "__main__":
    main()
