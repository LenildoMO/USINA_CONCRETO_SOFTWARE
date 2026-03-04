from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configurações
DATA_DIR = "C:/BettoMix/Dados"
os.makedirs(DATA_DIR, exist_ok=True)

PENDING_FILE = os.path.join(DATA_DIR, "pendentes.json")
LOG_FILE = os.path.join(DATA_DIR, "logs.json")

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "sistema": "Betto Mix API",
        "versao": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/test', methods=['GET'])
def test_connection():
    return jsonify({
        "success": True,
        "message": "✅ API Betto Mix funcionando!",
        "data": {"clientes": 15, "pedidos": 42, "estoque": 8}
    })

@app.route('/api/v1/sync', methods=['POST'])
def sync_data():
    try:
        return jsonify({
            "success": True,
            "message": "✅ Dados sincronizados!",
            "sync_id": f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/pending', methods=['GET'])
def get_pending():
    try:
        if os.path.exists(PENDING_FILE):
            with open(PENDING_FILE, 'r') as f:
                data = json.load(f)
            return jsonify({"success": True, "count": len(data), "data": data})
        else:
            return jsonify({"success": True, "count": 0, "data": []})
    except:
        return jsonify({"success": False, "error": "Erro ao ler dados"}), 500

if __name__ == '__main__':
    print("🚀 API Betto Mix iniciada em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
