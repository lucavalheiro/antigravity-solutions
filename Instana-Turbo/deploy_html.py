import paramiko
import os
import sys

print("Connecting to 192.168.173.22 via SSH/SFTP...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.173.22', port=22, username='luciano-erp', password='Qawsed321', timeout=15)

sftp = ssh.open_sftp()
for d in ['/home/luciano-erp/sommelier_web', '/home/luciano-erp/sommelier_web/images']:
    try:
        sftp.mkdir(d)
    except Exception:
        pass

# 1. Upload index.html and solucoes.html
local_html = os.path.join('projeto-sommelier', 'index.html')
sftp.put(local_html, '/home/luciano-erp/sommelier_web/index.html')
print("Uploaded index.html to 192.168.173.22")

local_sol = os.path.join('projeto-sommelier', 'solucoes.html')
sftp.put(local_sol, '/home/luciano-erp/sommelier_web/solucoes.html')
print("Uploaded solucoes.html to 192.168.173.22")

# 2. Upload images
img_dir = os.path.join('projeto-sommelier', 'images')
for f in os.listdir(img_dir):
    local_f = os.path.join(img_dir, f)
    remote_f = f'/home/luciano-erp/sommelier_web/images/{f}'
    sftp.put(local_f, remote_f)
    print(f"Uploaded {f} to 192.168.173.22")

sftp.close()
print("SFTP sync to 192.168.173.22 complete.\n")

# 3. Remote commands executed on 192.168.173.22 to push to 10.1.0.65
cmds = [
    ("Create images dir on 10.1.0.65", 'ssh 10.1.0.65 "mkdir -p /home/luciano-erp/sommelier_web/images"'),
    ("SCP index.html to 10.1.0.65", 'scp /home/luciano-erp/sommelier_web/index.html 10.1.0.65:/home/luciano-erp/sommelier_web/index.html'),
    ("SCP solucoes.html to 10.1.0.65", 'scp /home/luciano-erp/sommelier_web/solucoes.html 10.1.0.65:/home/luciano-erp/sommelier_web/solucoes.html'),
    ("SCP images to 10.1.0.65", 'scp -r /home/luciano-erp/sommelier_web/images/* 10.1.0.65:/home/luciano-erp/sommelier_web/images/'),
    ("List files on 10.1.0.65", 'ssh 10.1.0.65 "cp -f /home/luciano-erp/sommelier_web/solucoes.html /home/luciano-erp/sommelier_web/solucoes 2>/dev/null || true; ls -la /home/luciano-erp/sommelier_web && ls -la /home/luciano-erp/sommelier_web/images"'),
    ("Copy index.html to erpi-backend-1", 'ssh 10.1.0.65 "docker cp /home/luciano-erp/sommelier_web/index.html erpi-backend-1:/home/frappe/frappe-bench/apps/crm/crm/www/sommelier.html"'),
    ("Copy index.html to erpi-frontend-1", 'ssh 10.1.0.65 "docker cp /home/luciano-erp/sommelier_web/index.html erpi-frontend-1:/home/frappe/frappe-bench/apps/crm/crm/www/sommelier.html"'),
    ("Copy solucoes.html to erpi-backend-1", 'ssh 10.1.0.65 "docker cp /home/luciano-erp/sommelier_web/solucoes.html erpi-backend-1:/home/frappe/frappe-bench/apps/crm/crm/www/solucoes.html"'),
    ("Copy solucoes.html to erpi-frontend-1", 'ssh 10.1.0.65 "docker cp /home/luciano-erp/sommelier_web/solucoes.html erpi-frontend-1:/home/frappe/frappe-bench/apps/crm/crm/www/solucoes.html"'),
    ("Create images dir in containers", 'ssh 10.1.0.65 "docker exec erpi-backend-1 mkdir -p /home/frappe/frappe-bench/apps/crm/crm/www/images && docker exec erpi-frontend-1 mkdir -p /home/frappe/frappe-bench/apps/crm/crm/www/images"'),
    ("Copy images to erpi-backend-1", 'ssh 10.1.0.65 "docker cp /home/luciano-erp/sommelier_web/images/. erpi-backend-1:/home/frappe/frappe-bench/apps/crm/crm/www/images/"'),
    ("Copy images to erpi-frontend-1", 'ssh 10.1.0.65 "docker cp /home/luciano-erp/sommelier_web/images/. erpi-frontend-1:/home/frappe/frappe-bench/apps/crm/crm/www/images/"'),
    ("Fix permissions in erpi-backend-1", 'ssh 10.1.0.65 "docker exec erpi-backend-1 chown -R frappe:root /home/frappe/frappe-bench/apps/crm/crm/www/sommelier.html /home/frappe/frappe-bench/apps/crm/crm/www/solucoes.html /home/frappe/frappe-bench/apps/crm/crm/www/images"'),
    ("Fix permissions in erpi-frontend-1", 'ssh 10.1.0.65 "docker exec erpi-frontend-1 chown -R frappe:root /home/frappe/frappe-bench/apps/crm/crm/www/sommelier.html /home/frappe/frappe-bench/apps/crm/crm/www/solucoes.html /home/frappe/frappe-bench/apps/crm/crm/www/images"'),
    ("Copy images to Frappe public files", 'ssh 10.1.0.65 "docker cp /home/luciano-erp/sommelier_web/images/. erpi-backend-1:/home/frappe/frappe-bench/sites/erpi.local/public/files/ && docker exec erpi-backend-1 chown -R frappe:root /home/frappe/frappe-bench/sites/erpi.local/public/files/"'),
    ("Clear Frappe cache", 'ssh 10.1.0.65 "docker exec erpi-backend-1 bench --site erpi.local clear-cache"'),
]

for label, cmd in cmds:
    print(f">> {label}...")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"   {out}")
    if err:
        print(f"   STDERR: {err}")
    if code != 0:
        print(f"   EXIT CODE: {code}")

ssh.close()
print("\nAll deployments finished successfully!")
