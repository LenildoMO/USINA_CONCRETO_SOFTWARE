import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)

# Configurações
DATA_DIR = r"C:\BettoMix\Dados"
PENDING_FILE = os.path.join(DATA_DIR, "pendentes", "dados_pendentes.json")
LOG_FILE = os.path.join(DATA_DIR, "logs", f"sistema_{datetime.now().strftime('%Y%m%d')}.json")

# Criar arquivos se não existirem
os.makedirs(os.path.dirname(PENDING_FILE), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def salvar_log(tipo, mensagem):
    try:
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    logs = json.loads(content)
        
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo,
            "mensagem": mensagem
        }
        logs.append(log_entry)
        
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar log: {e}")

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "sistema": "Betto Mix API Local",
        "versao": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/test', methods=['GET'])
def test():
    salvar_log("INFO", "Teste de conexão realizado")
    return jsonify({
        "success": True,
        "message": "✅ API Betto Mix funcionando perfeitamente!",
        "data": {
            "clientes": 15,
            "pedidos": 42,
            "estoque": 8,
            "fornecedores": 5
        }
    })

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/v1/sync', methods=['POST'])
def sync():
    try:
        data = request.json
        data['received'] = datetime.now().isoformat()
        data['id'] = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Salvar dados pendentes
        pendentes = []
        if os.path.exists(PENDING_FILE):
            try:
                with open(PENDING_FILE, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        pendentes = json.loads(content)
            except:
                pendentes = []
        
        pendentes.append(data)
        
        with open(PENDING_FILE, 'w', encoding='utf-8') as f:
            json.dump(pendentes, f, indent=2, ensure_ascii=False)
        
        salvar_log("SUCESSO", f"Dado recebido: {data.get('tipo', 'desconhecido')}")
        
        return jsonify({
            "success": True,
            "message": "✅ Dados recebidos!",
            "id": data['id']
        })
    except Exception as e:
        salvar_log("ERRO", f"Erro na sincronização: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/pending', methods=['GET'])
def pending():
    try:
        if not os.path.exists(PENDING_FILE):
            return jsonify({"success": True, "count": 0, "data": []})
        
        with open(PENDING_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                data = []
            else:
                data = json.loads(content)
        
        return jsonify({
            "success": True,
            "count": len(data),
            "data": data[-10:]  # Últimos 10
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                   BETTO MIX API LOCAL                                ║")
    print("╠══════════════════════════════════════════════════════════════════════╣")
    print("║   🌐 Servidor iniciado em: http://localhost:5000                    ║")
    print("║   📁 Dados: C:\\BettoMix\\Dados                                     ║")
    print("║   📝 Logs: " + LOG_FILE + " ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print("")
    print("📊 Endpoints disponíveis:")
    print("  • GET  /              - Status da API")
    print("  • GET  /api/v1/test   - Teste de conexão")
    print("  • GET  /api/v1/health - Health check")
    print("  • POST /api/v1/sync   - Sincronizar dados")
    print("  • GET  /api/v1/pending- Dados pendentes")
    print("")
    print("🟢 API pronta para receber conexões...")
    print("")
    
    salvar_log("SUCESSO", "API Betto Mix iniciada")
    
    # Configurar para rodar em thread separada
    from werkzeug.serving import make_server
    
    server = make_server('0.0.0.0', 5000, app, threaded=True)
    server.serve_forever()
