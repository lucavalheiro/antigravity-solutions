# -*- coding: utf-8 -*-
import http.server
import socketserver
import os
import mimetypes
import json
import random
import urllib.request
import urllib.error

PORT = 8088
BASE_DIR = os.path.abspath("projeto-sommelier")

class SommelierMasterGateway(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Strip query strings & hash
        path_clean = path.split('?', 1)[0].split('#', 1)[0].rstrip('/')
        
        # Route mapping
        if path_clean in ['', '/', '/sommelier', '/sommelier.html', '/index.html']:
            return os.path.join(BASE_DIR, 'index.html')
        elif path_clean in ['/solucoes', '/solucoes.html']:
            return os.path.join(BASE_DIR, 'solucoes.html')
        elif path_clean.startswith('/erpnext'):
            return os.path.join(BASE_DIR, 'erpnext.html')
        elif path_clean.startswith('/glpi'):
            return os.path.join(BASE_DIR, 'glpi.html')
        elif path_clean.startswith('/quantum') or path_clean.startswith('/qai'):
            return os.path.join(BASE_DIR, 'quantum.html')
        elif path_clean.startswith('/instana'):
            return os.path.join(BASE_DIR, 'instana.html')
        elif path_clean.startswith('/turbonomic'):
            return os.path.join(BASE_DIR, 'turbonomic.html')
        elif path.startswith('/images/'):
            rel_path = path[len('/images/'):].split('?', 1)[0]
            return os.path.join(BASE_DIR, 'images', rel_path)
        else:
            return os.path.join(BASE_DIR, path_clean.lstrip('/'))

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if 'create_wine_order' in self.path:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            
            order_id = f"SAL-ORD-2026-{random.randint(10000, 99999)}"
            erp_order_url = f"/erpnext?order_id={order_id}"
            
            # Attempt live proxy to ERPNext (10.1.0.65:8080) if reachable
            live_success = False
            try:
                req = urllib.request.Request(
                    "http://10.1.0.65:8080/api/method/crm.api.sommelier.create_wine_order",
                    data=post_data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    resp_data = resp.read()
                    live_json = json.loads(resp_data.decode('utf-8'))
                    if 'message' in live_json and 'order_id' in live_json['message']:
                        order_id = live_json['message']['order_id']
                        live_success = True
            except Exception:
                pass

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            res = {
                "message": {
                    "order_id": order_id,
                    "status": "Submitted",
                    "live_backend": live_success,
                    "erp_url": f"/erpnext?order_id={order_id}",
                    "company": "Sommelier Privé Vinhos Finos Ltda",
                    "docstatus": 1
                }
            }
            self.wfile.write(json.dumps(res).encode('utf-8'))
            return
            
        super().do_POST()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SommelierMasterGateway) as httpd:
        print(f"Sommelier Master Gateway running at http://127.0.0.1:{PORT}")
        httpd.serve_forever()
