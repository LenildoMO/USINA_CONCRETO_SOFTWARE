import sys
import os
import json
from datetime import datetime

# Forçar UTF-8
sys.stdout.reconfigure(encoding='utf-8')

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    flask_ok = True
except ImportError:
    flask_ok = False
    print("⚠️  Flask não instalado, usando servidor simples...")

app = None
if flask_ok:
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    @app.route('/')
    def home():
        return jsonify({
            "sistema": "Betto Mix API",
            "status": "online",
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/api/v1/test', methods=['GET'])
    def test():
        return jsonify({
            "success": True,
            "message": "✅ API funcionando perfeitamente!",
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
                "message": "✅ Dados recebidos!",
                "id": f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

# Servidor HTTP simples se Flask falhar
class SimpleServer:
    def run(self, host='0.0.0.0', port=5000):
        import http.server
        import socketserver
        
        handler = http.server.SimpleHTTPRequestHandler
        
        class BettoHandler(handler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = json.dumps({
                        "sistema": "Betto Mix API (Simples)",
                        "status": "online",
                        "timestamp": datetime.now().isoformat()
                    })
                    self.wfile.write(response.encode('utf-8'))
                elif self.path == '/api/v1/test':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = json.dumps({
                        "success": True,
                        "message": "✅ API Simples funcionando!"
                    })
                    self.wfile.write(response.encode('utf-8'))
                else:
                    super().do_GET()
        
        with socketserver.TCPServer((host, port), BettoHandler) as httpd:
            print(f"✅ Servidor HTTP simples iniciado em http://{host}:{port}")
            print("📌 Endpoints: /, /api/v1/test")
            httpd.serve_forever()

if __name__ == '__main__':
    print("")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                    BETTO MIX API - SERVIDOR                          ║")
    print("╠══════════════════════════════════════════════════════════════════════╣")
    print("║   🌐 Iniciando servidor na porta 5000...                            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print("")
    
    if app and flask_ok:
        print("🚀 Usando Flask (modo avançado)")
        print("📊 Endpoints disponíveis:")
        print("  • GET  /              - Status")
        print("  • GET  /api/v1/test   - Teste")
        print("  • POST /api/v1/sync   - Sincronizar")
        print("")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    else:
        print("🔧 Usando servidor HTTP simples")
        print("📊 Endpoints disponíveis:")
        print("  • GET  /              - Status")
        print("  • GET  /api/v1/test   - Teste")
        print("")
        server = SimpleServer()
        server.run(host='0.0.0.0', port=5000)
