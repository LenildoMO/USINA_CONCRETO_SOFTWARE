import socket
import webbrowser
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

print("\n" + "="*60)
print("🌐 VISUALIZADOR REMOTO - USINA BETTO MIX")
print("="*60)

class VisualizadorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # Página HTML simples e funcional
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USINA BETTO MIX</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #003366;
            color: white;
            font-family: Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            width: 100%;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
        }
        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
        }
        h1 {
            color: white;
            margin-bottom: 10px;
            font-size: 2rem;
        }
        h2 {
            color: #a3d9ff;
            margin-bottom: 30px;
            font-size: 1.3rem;
        }
        .status {
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 20px;
            font-weight: bold;
        }
        .ip-box {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            font-size: 1.2rem;
            line-height: 1.8;
        }
        .btn {
            background: #0066cc;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s;
            display: inline-block;
            text-decoration: none;
        }
        .btn:hover {
            background: #0052a3;
            transform: translateY(-2px);
        }
        .instructions {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
            text-align: left;
        }
        .step {
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        .step-num {
            background: #4fc3f7;
            color: #003366;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
            flex-shrink: 0;
        }
        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }
            h1 {
                font-size: 1.5rem;
            }
            .ip-box {
                font-size: 1rem;
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🏭</div>
        <h1>USINA BETTO MIX CONCRETO</h1>
        <h2>Sistema de Gestão - Visualização Remota</h2>
        
        <div class="status">✅ ONLINE E FUNCIONANDO</div>
        
        <div class="ip-box">
            <p><strong>📍 ACESSO LOCAL (no mesmo computador):</strong></p>
            <p>http://localhost:""" + str(self.server.server_port) + """</p>
            
            <p><strong>📡 ACESSO NA REDE (celular/outros PCs):</strong></p>
            <p>http://192.168.1.4:""" + str(self.server.server_port) + """</p>
        </div>
        
        <div>
            <a href="http://localhost:""" + str(self.server.server_port) + """" class="btn" target="_blank">
                🔗 Abrir Agora no Navegador
            </a>
            <button class="btn" onclick="window.location.reload()">
                🔄 Atualizar Página
            </button>
        </div>
        
        <div class="instructions">
            <h3>📱 COMO ACESSAR PELO CELULAR:</h3>
            <div class="step">
                <div class="step-num">1</div>
                <div>
                    <strong>Conecte no MESMO Wi-Fi</strong>
                    <p>Celular e computador devem estar na mesma rede</p>
                </div>
            </div>
            <div class="step">
                <div class="step-num">2</div>
                <div>
                    <strong>Abra o navegador</strong>
                    <p>Chrome, Safari ou qualquer navegador no celular</p>
                </div>
            </div>
            <div class="step">
                <div class="step-num">3</div>
                <div>
                    <strong>Digite o endereço</strong>
                    <p><code>http://192.168.1.4:""" + str(self.server.server_port) + """</code></p>
                </div>
            </div>
            <div class="step">
                <div class="step-num">4</div>
                <div>
                    <strong>Pronto!</strong>
                    <p>Visualize as informações do sistema remotamente</p>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 30px; color: #a3d9ff; font-size: 0.9rem;">
            <p>⚠️ Mantenha esta janela aberta para manter o acesso ativo</p>
            <p>📅 Sistema atualizado em tempo real</p>
        </div>
    </div>
    
    <script>
        // Função para copiar IP
        function copiarIP() {
            const ip = '192.168.1.4:""" + str(self.server.server_port) + """';
            navigator.clipboard.writeText(ip).then(() => {
                alert('✅ Endereço copiado! Cole no celular: ' + ip);
            });
        }
        
        // Mostra notificação ao carregar
        window.onload = function() {
            setTimeout(() => {
                const notif = document.createElement('div');
                notif.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #28a745;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    z-index: 1000;
                    max-width: 300px;
                `;
                notif.innerHTML = '✅ Visualização remota ativa!';
                document.body.appendChild(notif);
                setTimeout(() => notif.remove(), 5000);
            }, 1000);
        };
    </script>
</body>
</html>"""
        
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, *args):
        pass  # Silencia logs

# Função principal
def iniciar_servidor():
    # Tenta portas diferentes
    portas = [8080, 8081, 8082, 8888]
    
    for porta in portas:
        try:
            print(f"🔄 Tentando iniciar na porta {porta}...")
            server = HTTPServer(('0.0.0.0', porta), VisualizadorHandler)
            
            print(f"\n✅ SERVIDOR INICIADO COM SUCESSO!")
            print(f"📍 Porta: {porta}")
            print(f"📍 Computador: {socket.gethostname()}")
            print(f"📍 IP: 192.168.1.4")
            
            print(f"\n🌐 ENDEREÇOS DE ACESSO:")
            print(f"   1. Local:      http://localhost:{porta}")
            print(f"   2. Rede:       http://192.168.1.4:{porta}")
            
            print(f"\n📱 COMO ACESSAR PELO CELULAR:")
            print(f"   • Mesmo Wi-Fi")
            print(f"   • Abra navegador (Chrome/Safari)")
            print(f"   • Digite: 192.168.1.4:{porta}")
            print(f"   • Pronto!")
            
            print(f"\n" + "="*60)
            print("💡 Abrindo navegador em 3 segundos...")
            print("🛑 Para parar: Pressione CTRL+C")
            print("="*60)
            
            # Aguarda e abre navegador
            time.sleep(3)
            webbrowser.open(f'http://localhost:{porta}')
            
            # Mantém servidor rodando
            server.serve_forever()
            break
            
        except Exception as e:
            if porta == portas[-1]:
                print(f"\n❌ Não foi possível iniciar o servidor: {e}")
                input("Pressione ENTER para sair...")
            else:
                print(f"⚠️  Porta {porta} ocupada, tentando próxima...")

if __name__ == "__main__":
    iniciar_servidor()
