import socket
import threading
import json
from datetime import datetime
import time

PORT = 5000
HOST = '0.0.0.0'

print("\n" + "="*60)
print("       BETTO MIX API - SERVIDOR SIMPLES")
print("="*60)

def handle_client(client_socket):
    """Lida com requisições HTTP básicas"""
    try:
        request = client_socket.recv(1024).decode('utf-8')
        
        # Verificar se é requisição para /api/v1/test
        if 'GET /api/v1/test' in request:
            response_data = {
                "success": True,
                "message": "✅ API Betto Mix funcionando!",
                "timestamp": datetime.now().isoformat(),
                "data": {"status": "online", "clientes": 25}
            }
        elif 'GET /' in request:
            response_data = {
                "sistema": "Betto Mix API",
                "status": "online",
                "versao": "1.0",
                "timestamp": datetime.now().isoformat()
            }
        else:
            response_data = {"error": "Endpoint não encontrado"}
        
        response_json = json.dumps(response_data, ensure_ascii=False)
        
        # Resposta HTTP simples
        http_response = f"""HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Access-Control-Allow-Origin: *
Content-Length: {len(response_json.encode('utf-8'))}

{response_json}"""
        
        client_socket.send(http_response.encode('utf-8'))
        
    except Exception as e:
        print(f"Erro no cliente: {e}")
    finally:
        client_socket.close()

def start_server():
    """Inicia o servidor socket"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"✅ Servidor iniciado em http://{HOST}:{PORT}")
        print("📡 Aguardando conexões...")
        
        while True:
            client, addr = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client,))
            client_handler.daemon = True
            client_handler.start()
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        print("🔄 Tentando novamente em 5 segundos...")
        time.sleep(5)
        start_server()  # Tentar novamente

if __name__ == "__main__":
    start_server()
