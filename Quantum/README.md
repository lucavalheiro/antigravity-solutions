# IBM Quantum MCP Simulator (Qiskit Aer) & IA Quântica QAI (IBM Granite)

Ambiente híbrido avançado de computação e inteligência artificial quântica, combinando o ecossistema oficial **IBM Qiskit Aer** com a IA Quântica **QAI** (carinhosamente chamada de **Quantinho**, baseada no modelo **IBM Granite 8B** acelerado via GPU **NVIDIA L4** no servidor Ubuntu).

---

## 🏗️ Arquitetura Híbrida do Sistema

```
                      +------------------------------------------+
                      |   Frontend Web / Mission Control         |
                      |   (index.html - Dashboard Interativo)    |
                      +-------------------+----------------------+
                                          |
                   +----------------------+----------------------+
                   |                                             |
                   v (REST / JSON)                               v (OpenAI / SSE Stream)
    +------------------------------+             +-------------------------------+
    |  Servidor Qiskit Aer         |             |  Servidor Ubuntu AI GPU       |
    |  Host: 10.1.0.65:8090        |             |  Host: 192.168.173.22:3000    |
    +------------------------------+             +-------------------------------+
    | • Simulador Qiskit Aer v0.15 |             | • GPU NVIDIA L4 (24GB VRAM)   |
    | • QPU 127Q IBM Brisbane      |             | • Modelo IBM Granite 8B       |
    | • QPU 133Q IBM Torino        |             | • Copiloto Embutido "QAI"     |
    | • Ruído Térmico & T1/T2      |             | • Streaming SSE (~27 tok/s)   |
    +------------------------------+             +-------------------------------+
```

### 1. Simulador Qiskit Aer Isolado (`10.1.0.65:8090`)
* **Host:** `10.1.0.65` (Ubuntu 24.04 LTS)
* **Container Docker:** `ibm-quantum-mcp`
* **Porta:** `8090`
* **Isolamento de Recursos:** 1.5 vCPUs / 4 GB RAM.

### 2. IA Quântica "QAI" (Quantinho) - IBM Granite (`192.168.173.22:3000`)
* **Host:** `192.168.173.22` (Ubuntu 24.04 LTS com driver CUDA 13.2)
* **Hardware:** GPU **NVIDIA L4** (24 GB VRAM)
* **Modelo LLM:** `ibm-granite-8b` (`granite-4.2-8b-Q8_0.gguf`)
* **Posicionamento no Frontend:** **Embutido diretamente no lado direito em baixo da tela** (logo abaixo do gráfico de probabilidades), 100% visível ao abrir a página, com opção de desencaixar/flutuar se desejado.
* **Stack:** Llama-server C++ + LiteLLM Gateway + Caddy Reverse Proxy com suporte completo a CORS
* **Desempenho:** ~26.8 tokens/segundo com inferência e streaming em tempo real
* **Recursos do QAI no Frontend:**
  * **Explicação de Circuitos:** Analisa portas quânticas, superposição e entrelaçamento no editor.
  * **Otimização:** Recomenda reduções de portas CX para a topologia Heavy-Hex dos processadores IBM Eagle/Heron.
  * **Interpretação de Resultados:** Analisa as probabilidades medidas no simulador e explica efeitos físicos (ruído, defasagem T2, colapso de onda).
  * **1-Clique no Editor / Simulação:** Blocos OpenQASM gerados pelo QAI possuem botões para transferir o código diretamente para o editor e disparar a simulação instantaneamente.

---

## ⚡ Métodos de Simulação Suportados

1. **`automatic`**: Seleciona a melhor estratégia com base no circuito.
2. **`statevector`**: Simulação analítica com cálculo exato de amplitudes complexas ($2^n$).
3. **`density_matrix`**: Simulação completa com matriz de densidade e ruído quântico.
4. **`stabilizer`**: Simulação ultra-rápida baseada no teorema de Gottesman-Knill para milhares de qubits.
5. **`matrix_product_state` (MPS)**: Redes de tensores para circuitos com baixo entrelaçamento.
6. **`extended_stabilizer`**: Decomposição aproximada para circuitos com poucas portas não-Clifford.
7. **`unitary`**: Cálculo da matriz unitária global do circuito.

---

## 🤖 Réplicas de Hardware Real IBM (Fake Backends)

* **`fake_brisbane`**: Processador Eagle de 127 qubits (topologia Heavy-Hex).
* **`fake_torino`**: Processador Heron de 133 qubits.
* **`fake_sherbrooke`**: Processador Eagle de 127 qubits.
* **`fake_kyiv`**: Processador Eagle de 127 qubits.
* **`fake_osaka`**: Processador Eagle de 127 qubits.

---

## 🔌 Endpoints da API

### IA Quântica Quantinho (IBM Granite 8B - GPU Ubuntu)
* `GET http://192.168.173.22:3000/quantum-ai/v1/models`: Lista de modelos disponíveis na GPU.
* `POST http://192.168.173.22:3000/quantum-ai/v1/chat/completions`: Endpoint padrão OpenAI com suporte a `stream: true` e CORS habilitado.

### Simulador Qiskit Aer (10.1.0.65:8090)
* `GET http://10.1.0.65:8090/health`: Status do simulador.
* `GET http://10.1.0.65:8090/api/info`: Informações e modelos de ruído.
* `POST http://10.1.0.65:8090/api/simulate`: Executa circuito OpenQASM 2.0.
* `POST http://10.1.0.65:8090/api/noise`: Simula o circuito com ruído de um chip físico IBM.
* `POST http://10.1.0.65:8090/api/grover`: Executa busca quântica de Grover.
* `GET http://10.1.0.65:8090/api/bell`: Executa o estado entrelaçado de Bell (|Φ+⟩).
* `GET http://10.1.0.65:8090/api/ghz?qubits=3`: Executa o estado GHZ para $n$ qubits.

---

## 🧪 Como Testar no Windows

### 1. Teste Automatizado de Simulação
```powershell
python test_simulation.py
```

### 2. Usando o Cliente Python Integrado (`quantum_client.py`)
```python
from quantum_client import IBMQuantumClient, QuantinhoAI

# 1. Simular Estado de Bell no Qiskit Aer
sim = IBMQuantumClient("http://10.1.0.65:8090")
resultado = sim.bell_state()
print("Probabilidades da Simulação:", resultado["simulation"]["probabilities"])

# 2. Conversar com a IA Quantinho (IBM Granite na GPU Ubuntu)
quantinho = QuantinhoAI("http://192.168.173.22:3000/quantum-ai/v1")
explicacao = quantinho.explain_circuit(resultado["circuit"]["qasm"])
print("\nExplicação do Quantinho:\n", explicacao)
```

### 3. Abrindo o Frontend no Navegador
Basta abrir o arquivo [index.html](file:///c:/Users/lucav/OneDrive%20-%20TDSYNNEX/Tecnologias%20e%20apresenta%C3%A7%C3%B5es/ProjetoX/Quantum/index.html) no navegador para acessar o **Dashboard & Mission Control com o Quantinho integrado**.
