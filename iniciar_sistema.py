# ============================================================================
# SISTEMA BETTO MIX MEGA ULTRA - INICIALIZADOR
# ============================================================================

import os
import sys
import time
import webbrowser
from threading import Thread

def iniciar_sistema():
    """Inicia o sistema Betto Mix Mega Ultra"""
    
    print("=" * 80)
    print("🏭 BETTO MIX MEGA ULTRA SYSTEM - INICIALIZANDO")
    print("=" * 80)
    
    # Verificar dependências
    print("\n📦 Verificando dependências...")
    try:
        import flask
        print(f"   ✅ Flask {flask.__version__}")
    except ImportError:
        print("   ❌ Flask não encontrado")
        print("   💡 Execute: pip install flask flask-cors")
        return False
    
    try:
        import sqlite3
        print("   ✅ SQLite3")
    except ImportError:
        print("   ⚠️ SQLite3 não disponível")
    
    # Verificar estrutura
    print("\n📁 Verificando estrutura de pastas...")
    pastas_essenciais = ['templates', 'static/css', 'static/js', 'dados', 'ui/pages', 'logs']
    for pasta in pastas_essenciais:
        if os.path.exists(pasta):
            print(f"   ✅ {pasta}/")
        else:
            print(f"   ⚠️ {pasta}/ (criando...)")
            os.makedirs(pasta, exist_ok=True)
    
    # Verificar arquivos principais
    print("\n📄 Verificando arquivos principais...")
    arquivos_essenciais = ['app_mega.py', 'templates/base.html', 'static/css/mega_style.css']
    for arquivo in arquivos_essenciais:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo} (não encontrado)")
    
    # Detectar telas PyQt6
    print("\n🔍 Detectando telas PyQt6...")
    telas_pyqt6 = []
    ui_pages_path = 'ui/pages'
    
    if os.path.exists(ui_pages_path):
        for arquivo in os.listdir(ui_pages_path):
            if arquivo.startswith('tela_') and arquivo.endswith('.py'):
                telas_pyqt6.append(arquivo)
    
    if telas_pyqt6:
        print(f"   ✅ {len(telas_pyqt6)} telas encontradas:")
        for tela in telas_pyqt6[:3]:
            print(f"      • {tela}")
        if len(telas_pyqt6) > 3:
            print(f"      ... e mais {len(telas_pyqt6) - 3} telas")
    else:
        print("   ⚠️ Nenhuma tela PyQt6 encontrada")
        print("   💡 Crie telas em: ui/pages/tela_*.py")
    
    # Informações do sistema
    print("\n💻 Informações do sistema:")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Diretório: {os.getcwd()}")
    print(f"   Plataforma: {sys.platform}")
    
    # URLs disponíveis
    print("\n🌐 URLs que serão abertas:")
    print("   • http://localhost:5000/dashboard")
    print("   • http://localhost:5000/monitor")
    print("   • http://localhost:5000/api/status")
    
    print("\n" + "=" * 80)
    print("✅ Sistema pronto para inicialização!")
    print("=" * 80)
    
    return True

def abrir_navegador():
    """Abre o navegador após o servidor iniciar"""
    time.sleep(3)  # Aguardar servidor iniciar
    
    urls = [
        "http://localhost:5000/dashboard",
        "http://localhost:5000/monitor",
        "http://localhost:5000/api/status"
    ]
    
    for url in urls:
        try:
            webbrowser.open(url)
            print(f"   🌐 Navegador aberto: {url}")
            time.sleep(1)
        except Exception as e:
            print(f"   ⚠️ Erro ao abrir {url}: {e}")

def main():
    """Função principal"""
    
    if not iniciar_sistema():
        print("\n❌ Não foi possível iniciar o sistema.")
        input("\nPressione Enter para sair...")
        return
    
    print("\n🚀 Iniciando servidor Flask...")
    print("🛑 Para parar o sistema: Pressione Ctrl+C\n")
    
    # Iniciar thread para abrir navegador
    browser_thread = Thread(target=abrir_navegador, daemon=True)
    browser_thread.start()
    
    # Iniciar servidor Flask
    try:
        os.environ['FLASK_APP'] = 'app_mega.py'
        os.environ['FLASK_ENV'] = 'development'
        
        # Importar e executar app
        from app_mega import app
        
        print("\n" + "=" * 80)
        print("🏭 SERVIDOR INICIADO COM SUCESSO!")
        print("=" * 80)
        print("\n📢 Use as seguintes URLs:")
        print("   📊 Dashboard: http://localhost:5000/dashboard")
        print("   🖥️  Monitor:  http://localhost:5000/monitor")
        print("   🔧 API:       http://localhost:5000/api/status")
        print("\n🔧 Comandos úteis:")
        print("   • Sincronizar tudo: curl http://localhost:5000/api/sync/todas")
        print("   • Ver telas:       curl http://localhost:5000/api/sync/telas")
        print("   • Ver status:      curl http://localhost:5000/api/status")
        print("\n" + "=" * 80)
        
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
        input("\nPressione Enter para sair...")

if __name__ == '__main__':
    main()
