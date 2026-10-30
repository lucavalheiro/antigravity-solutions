import json
import paramiko
from mcp.server.mcpserver import MCPServer

HOST = "192.168.173.22"
PORT = 22
USER = "luciano-erp"
PASS = "Qawsed321"

server = MCPServer("LucianoAI-Bridge")

def get_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=10)
    return ssh

@server.tool()
def ask_luciano_gpu(prompt: str, system_prompt: str = "") -> str:
    """Envia um prompt para o modelo Qwen 27B rodando na GPU NVIDIA L4 do servidor 192.168.173.22 e retorna a resposta."""
    ssh = get_ssh()
    payload = {
        "model": "qwen36-pro",
        "messages": [],
        "temperature": 0.3
    }
    if system_prompt:
        payload["messages"].append({"role": "system", "content": system_prompt})
    payload["messages"].append({"role": "user", "content": prompt})

    json_str = json.dumps(payload).replace("'", "'\\''")
    cmd = f"""curl -s -X POST http://172.19.0.5:8080/v1/chat/completions \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer sk-2f971530cd7e803325caa7e626c0f016e396e489e2814be4" \\
      -d '{json_str}'"""
    
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    ssh.close()
    try:
        data = json.loads(out)
        return data["choices"][0]["message"]["content"]
    except Exception:
        return out

@server.tool()
def ask_quantinho(prompt: str, system_prompt: str = "") -> str:
    """Envia um prompt para a IA Quântica Quantinho baseada no IBM Granite 8B rodando na GPU NVIDIA L4 do servidor Ubuntu."""
    ssh = get_ssh()
    system_text = system_prompt or (
        "Você é o Quantinho, a IA Quântica oficial especialista em computação quântica, "
        "IBM Qiskit, circuitos OpenQASM e processadores IBM Eagle/Heron rodando acelerado na GPU NVIDIA L4."
    )
    payload = {
        "model": "ibm-granite-8b",
        "messages": [
            {"role": "system", "content": system_text},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    json_str = json.dumps(payload).replace("'", "'\\''")
    cmd = f"""curl -s -X POST http://172.19.0.6:4000/v1/chat/completions \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer sk-2f971530cd7e803325caa7e626c0f016e396e489e2814be4" \\
      -d '{json_str}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    ssh.close()
    try:
        data = json.loads(out)
        return data["choices"][0]["message"]["content"]
    except Exception:
        return out

@server.tool()
def run_aider_task(repo_path: str, instruction: str) -> str:
    """Aciona o agente Aider no servidor 192.168.173.22 para programar, alterar arquivos, rodar testes e commitar no Git."""
    ssh = get_ssh()
    escaped_inst = instruction.replace('"', '\\"').replace("'", "'\\''")
    cmd = f"""cd "{repo_path}" && /home/luciano-erp/.local/bin/aider --message "{escaped_inst}" --yes --exit"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    ssh.close()
    return f"STDOUT:\n{out}\n\nSTDERR:\n{err}"

@server.tool()
def exec_remote_bash(command: str, working_dir: str = "/home/luciano-erp") -> str:
    """Executa um comando bash no servidor Ubuntu 192.168.173.22 (ex: git, docker, pytest, npm, build)."""
    ssh = get_ssh()
    full_cmd = f"cd \"{working_dir}\" && {command}"
    stdin, stdout, stderr = ssh.exec_command(full_cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    code = stdout.channel.recv_exit_status()
    ssh.close()
    return f"[Exit code: {code}]\nOutput:\n{out}\nError:\n{err}"

@server.tool()
def read_remote_file(file_path: str) -> str:
    """Lê o conteúdo de um arquivo no servidor Ubuntu via SFTP."""
    ssh = get_ssh()
    sftp = ssh.open_sftp()
    with sftp.file(file_path, 'r') as f:
        content = f.read().decode('utf-8', errors='replace')
    sftp.close()
    ssh.close()
    return content

@server.tool()
def write_remote_file(file_path: str, content: str) -> str:
    """Escreve ou cria um arquivo no servidor Ubuntu via SFTP."""
    ssh = get_ssh()
    sftp = ssh.open_sftp()
    with sftp.file(file_path, 'w') as f:
        f.write(content)
    sftp.close()
    ssh.close()
    return f"Arquivo {file_path} gravado com sucesso."

@server.tool()
def get_remote_gpu_status() -> str:
    """Retorna o status em tempo real da GPU NVIDIA L4 (VRAM utilizada, temperatura, processos em execução)."""
    ssh = get_ssh()
    stdin, stdout, stderr = ssh.exec_command("nvidia-smi")
    out = stdout.read().decode('utf-8', errors='replace')
    ssh.close()
    return out

if __name__ == "__main__":
    server.run("stdio")
