#!/usr/bin/env python3
"""
VISUALIZADOR REMOTO - USINA BETTO MIX
Execute este arquivo EM PARALELO com seu sistema principal
"""

import socket
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

print("\n" + "="*60)
print("🌐 USINA BETTO MIX - VISUALIZADOR REMOTO")
print("="*60)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # Página HTML simples
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>USINA BETTO MIX</title>
    <style>
        body {{
            background: #003366;
            color: white;
            font-family: Arial;
            padding: 50px;
            text-align: center;
        }}
        h1 {{
            color: white;
        }}
        .ip-box {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px;
            font-size: 1.2rem;
        }}
    </style>
</head>
<body>
    <h1>🏭 USINA BETTO MIX CONCRETO</h1>
    <h2>Visualização Remota Ativa</h2>
    
    <div class="ip-box">
        <p><strong>📍 ACESSO LOCAL:</strong></p>
        <p>http://localhost:{self.server.server_port}</p>
        
        <p><strong>📡 ACESSO NA REDE:</strong></p>
        <p>http://{socket.gethostbyname(socket.gethostname())}:{self.server.server_port}</p>
    </div>
    
    <p><strong>📱 Como acessar no celular:</strong></p>
    <p>1. Conecte no MESMO Wi-Fi</p>
    <p>2. Abra Chrome ou Safari</p>
    <p>3. Digite: {socket.gethostbyname(socket.gethostname())}:{self.server.server_port}</p>
</body>
</html>"""
        
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, *args):
        pass

# Tenta iniciar servidor
try:
    porta = 8080
    server = HTTPServer(('0.0.0.0', porta), Handler)
    
    print(f"✅ Visualizador iniciado na porta {porta}")
    print(f"📍 Acesso: http://localhost:{porta}")
    
    ip = socket.gethostbyname(socket.gethostname())
    print(f"📍 IP da rede: {ip}")
    print(f"📱 No celular: {ip}:{porta}")
    print("\n🛑 Pressione CTRL+C para parar")
    
    # Abre navegador
    webbrowser.open(f'http://localhost:{porta}')
    
    # Mantém servidor rodando
    server.serve_forever()
    
except KeyboardInterrupt:
    print("\n🔴 Visualizador parado")
except Exception as e:
    print(f"\n❌ Erro: {e}")
    input("Pressione ENTER para sair...")
