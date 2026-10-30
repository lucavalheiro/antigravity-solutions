import requests
from typing import Dict, Any, Optional

class IBMQuantumClient:
    """Cliente Python para o Simulador IBM Qiskit Aer & MCP Server rodando em 10.1.0.65:8090."""
    
    def __init__(self, base_url: str = "http://10.1.0.65:8090"):
        self.base_url = base_url.rstrip("/")
        
    def health(self) -> Dict[str, Any]:
        """Verifica a saúde do serviço quântico."""
        resp = requests.get(f"{self.base_url}/health", timeout=5)
        resp.raise_for_status()
        return resp.json()
        
    def info(self) -> Dict[str, Any]:
        """Obtém informações do simulador, métodos e chips emulados."""
        resp = requests.get(f"{self.base_url}/api/info", timeout=5)
        resp.raise_for_status()
        return resp.json()
        
    def simulate(self, qasm: str, shots: int = 1024, method: str = "automatic") -> Dict[str, Any]:
        """Executa um circuito OpenQASM no simulador Qiskit Aer."""
        payload = {"qasm": qasm, "shots": shots, "method": method}
        resp = requests.post(f"{self.base_url}/api/simulate", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
        
    def statevector(self, qasm: str) -> Dict[str, Any]:
        """Calcula o vetor de estados completo (amplitudes, probabilidades e fases)."""
        payload = {"qasm": qasm}
        resp = requests.post(f"{self.base_url}/api/statevector", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
        
    def simulate_with_noise(self, qasm: str, backend_name: str = "fake_brisbane", shots: int = 1024) -> Dict[str, Any]:
        """Simula com modelo de ruído realista de chips da IBM (FakeBrisbane, FakeSherbrooke, FakeKyiv, FakeTorino)."""
        payload = {"qasm": qasm, "backend_name": backend_name, "shots": shots}
        resp = requests.post(f"{self.base_url}/api/noise", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
        
    def bell_state(self) -> Dict[str, Any]:
        """Gera e simula o estado entrelaçado de Bell (|Φ+⟩)."""
        resp = requests.get(f"{self.base_url}/api/bell", timeout=10)
        resp.raise_for_status()
        return resp.json()
        
    def ghz_state(self, qubits: int = 3) -> Dict[str, Any]:
        """Gera e simula o estado multipartite GHZ para n qubits."""
        resp = requests.get(f"{self.base_url}/api/ghz", params={"qubits": qubits}, timeout=15)
        resp.raise_for_status()
        return resp.json()
        
    def grover_search(self, target_bitstring: str = "101") -> Dict[str, Any]:
        """Executa o algoritmo de Grover para encontrar o bitstring alvo com aceleração quadrática."""
        payload = {"target_bitstring": target_bitstring}
        resp = requests.post(f"{self.base_url}/api/grover", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()


class QuantinhoAI:
    """Cliente Python para o Copiloto Quântico 'Quantinho' (IBM Granite 8B rodando na GPU NVIDIA L4 em 192.168.173.22:3000)."""
    
    SYSTEM_PROMPT_DEFAULT = (
        "Você é o Quantinho, a Inteligência Artificial Quântica oficial do painel IBM Quantum QPU Dashboard. "
        "Você é alimentado pelo modelo IBM Granite 8B acelerado em GPU NVIDIA L4 no servidor Ubuntu. "
        "Você é especialista em mecânica quântica, Qiskit Aer, portas lógicas e algoritmos em OpenQASM 2.0. "
        "Sempre forneça códigos OpenQASM completos, limpos e prontos para execução."
    )

    def __init__(self, base_url: str = "http://192.168.173.22:3000/quantum-ai/v1", model: str = "ibm-granite-8b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(self, prompt: str, system_prompt: Optional[str] = None, stream: bool = False, max_tokens: int = 600) -> Any:
        """Envia mensagem ao Quantinho (IBM Granite 8B) e retorna a resposta."""
        messages = [
            {"role": "system", "content": system_prompt or self.SYSTEM_PROMPT_DEFAULT},
            {"role": "user", "content": prompt}
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": 0.3,
            "max_tokens": max_tokens
        }
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            timeout=180,
            stream=stream
        )
        resp.raise_for_status()
        if stream:
            return resp
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def explain_circuit(self, qasm: str) -> str:
        """Pede ao Quantinho para dissecar e explicar detalhadamente um circuito OpenQASM."""
        prompt = (
            f"Por favor, analise e explique o seguinte circuito quântico em OpenQASM passo a passo, "
            f"detalhando o papel de cada porta, superposição, fases e o que se espera na medição:\n\n```qasm\n{qasm}\n```"
        )
        return self.chat(prompt)

    def generate_circuit(self, description: str) -> str:
        """Gera um circuito OpenQASM 2.0 a partir de uma descrição textual de algoritmo."""
        prompt = (
            f"Crie um circuito em OpenQASM 2.0 para o seguinte requisito quântico:\n'{description}'\n\n"
            f"Inclua a sintaxe válida (OPENQASM 2.0; include \"qelib1.inc\";), medições e uma breve explicação."
        )
        return self.chat(prompt)

    def interpret_results(self, qasm: str, probabilities: Dict[str, float], backend: str = "fake_brisbane", max_tokens: int = 400) -> str:
        """Interpreta os resultados obtidos da simulação quântica com ruído."""
        probs_str = ", ".join([f"|{k}>: {v*100:.2f}%" for k, v in probabilities.items()])
        prompt = (
            f"Analise os resultados desta simulação quântica no backend '{backend}' de forma concisa e direta (máximo 3 parágrafos):\n"
            f"Circuito QASM:\n```qasm\n{qasm}\n```\n"
            f"Distribuição de probabilidades medidas: {probs_str}\n\n"
            f"O resultado está alinhado com o esperado teoricamente? Comente sobre o significado quântico."
        )
        return self.chat(prompt, max_tokens=max_tokens)


# Alias oficial
QAI = QuantinhoAI


