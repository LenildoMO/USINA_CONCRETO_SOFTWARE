from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permitir requisições do PowerShell

# Caminho para dados do Betto Mix
DATA_DIR = "C:/BettoMix/Dados"
PENDING_FILE = os.path.join(DATA_DIR, "pendentes/dados_pendentes.json")
LOG_FILE = os.path.join(DATA_DIR, f"logs/sistema_{datetime.now().strftime('%Y%m%d')}.json")

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "sistema": "Betto Mix API Local",
        "versao": "1.0.0"
    })

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/v1/test', methods=['GET'])
def test_connection():
    return jsonify({
        "success": True,
        "message": "API Betto Mix local funcionando!",
        "data": {
            "clientes": 15,
            "pedidos": 42,
            "estoque": 8
        }
    })

@app.route('/api/v1/sync', methods=['POST'])
def sync_data():
    try:
        data = request.json
        
        # Salvar dados recebidos
        if not os.path.exists(PENDING_FILE):
            os.makedirs(os.path.dirname(PENDING_FILE), exist_ok=True)
            with open(PENDING_FILE, 'w') as f:
                json.dump([], f, indent=2)
        
        with open(PENDING_FILE, 'r') as f:
            pending_data = json.load(f)
        
        # Adicionar timestamp e ID
        data['received_at'] = datetime.now().isoformat()
        data['sync_id'] = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        pending_data.append(data)
        
        with open(PENDING_FILE, 'w') as f:
            json.dump(pending_data, f, indent=2)
        
        # Log
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": "SUCESSO",
            "modulo": "API",
            "mensagem": f"Dados recebidos via API: {data.get('tipo', 'desconhecido')}"
        }
        
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return jsonify({
            "success": True,
            "message": "Dados recebidos e salvos localmente",
            "sync_id": data['sync_id'],
            "pending_count": len(pending_data)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/v1/pending', methods=['GET'])
def get_pending():
    try:
        if os.path.exists(PENDING_FILE):
            with open(PENDING_FILE, 'r') as f:
                data = json.load(f)
            return jsonify({
                "success": True,
                "count": len(data),
                "data": data[:10]  # Retorna apenas os 10 primeiros
            })
        else:
            return jsonify({
                "success": True,
                "count": 0,
                "data": []
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/v1/clear', methods=['POST'])
def clear_pending():
    try:
        if os.path.exists(PENDING_FILE):
            with open(PENDING_FILE, 'r') as f:
                data = json.load(f)
            
            # Cria backup antes de limpar
            backup_file = PENDING_FILE.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Limpa o arquivo
            with open(PENDING_FILE, 'w') as f:
                json.dump([], f, indent=2)
            
            return jsonify({
                "success": True,
                "message": f"Pendentes limpos. Backup em {backup_file}",
                "cleared_count": len(data)
            })
        else:
            return jsonify({"success": True, "message": "Nenhum dado pendente"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando API Betto Mix Local...")
    print(f"📁 Diretório de dados: {DATA_DIR}")
    print("🌐 API disponível em: http://localhost:5000")
    print("📋 Endpoints:")
    print("  GET  /                 - Status da API")
    print("  GET  /api/v1/test      - Teste de conexão")
    print("  POST /api/v1/sync      - Sincronizar dados")
    print("  GET  /api/v1/pending   - Ver pendentes")
    print("  POST /api/v1/clear     - Limpar pendentes")
    print("\nPressione Ctrl+C para parar\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)