import sys
import os
import json
from datetime import datetime
import socket
import time

# Configurações
PORT = 5000
HOST = '0.0.0.0'

print("")
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                   BETTO MIX API - SERVIDOR                          ║")
print("╠══════════════════════════════════════════════════════════════════════╣")
print(f"║   🌐 Iniciando servidor na porta {PORT}...                         ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print("")

# Tentar Flask primeiro
try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    @app.route('/')
    def home():
        return jsonify({
            "sistema": "Betto Mix API",
            "status": "online",
            "versao": "1.0.0",
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/api/v1/test', methods=['GET'])
    def test():
        return jsonify({
            "success": True,
            "message": "✅ API Betto Mix funcionando perfeitamente!",
            "data": {
                "clientes": 25,
                "pedidos": 150,
                "estoque": 42,
                "fornecedores": 8
            }
        })
    
    @app.route('/api/v1/sync', methods=['POST'])
    def sync():
        try:
            data = request.json
            return jsonify({
                "success": True,
                "message": "✅ Dados sincronizados com sucesso!",
                "id": f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/v1/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
    
    print("🚀 Usando Flask (modo avançado)")
    print("📊 Endpoints disponíveis:")
    print("  • GET  /              - Status da API")
    print("  • GET  /api/v1/test   - Teste de conexão")
    print("  • POST /api/v1/sync   - Sincronizar dados")
    print("  • GET  /api/v1/health - Health check")
    print("")
    print(f"🟢 API rodando em: http://localhost:{PORT}")
    print("")
    
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
    
except ImportError:
    # Se Flask não estiver instalado, usar servidor socket simples
    print("🔧 Usando servidor socket simples")
    print("📊 Endpoints: /api/v1/test")
    print("")
    
    import http.server
    import socketserver
    
    class SimpleHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/api/v1/test':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({
                    "success": True,
                    "message": "✅ API Betto Mix (Simples) funcionando!",
                    "data": {"status": "online", "sistema": "Betto Mix"}
                })
                self.wfile.write(response.encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({
                    "sistema": "Betto Mix API (Simples)",
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                })
                self.wfile.write(response.encode('utf-8'))
        
        def log_message(self, format, *args):
            # Silenciar logs
            pass
    
    with socketserver.TCPServer((HOST, PORT), SimpleHandler) as httpd:
        print(f"✅ Servidor iniciado em http://{HOST}:{PORT}")
        print("📌 Aguardando conexões...")
        httpd.serve_forever()

except Exception as e:
    print(f"❌ Erro crítico: {e}")
    print("🔄 Tentando método de emergência...")
    
    # Método de emergência: socket raw
    import threading
    
    def handle_client(client_socket):
        try:
            request = client_socket.recv(1024).decode('utf-8')
            
            if 'GET /api/v1/test' in request:
                response = json.dumps({
                    "success": True,
                    "message": "✅ API Emergencial Betto Mix!"
                })
                http_response = f"""HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *
Content-Length: {len(response)}

{response}"""
                client_socket.send(http_response.encode('utf-8'))
            else:
                response = json.dumps({"status": "online", "sistema": "Betto Mix"})
                http_response = f"""HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: {len(response)}

{response}"""
                client_socket.send(http_response.encode('utf-8'))
        except:
            pass
        finally:
            client_socket.close()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    
    print(f"🔧 Servidor de emergência em porta {PORT}")
    
    while True:
        client, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()
