import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.173.22', port=22, username='luciano-erp', password='Qawsed321', timeout=10)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

out, err = run('ssh 10.1.0.65 "docker inspect sommelier-portal --format \'{{json .Mounts}}\'"')
print("=== SOMMELIER PORTAL MOUNTS ===")
print(out)

out, err = run('ssh 10.1.0.65 "docker exec erpi-backend-1 ls -la /home/frappe/frappe-bench/sites/erpi.local/public/files | head -n 10"')
print("=== ERPI PUBLIC FILES ===")
print(out)

ssh.close()
