import subprocess
import sys

def instalar_dependencias():
    """Instala as dependências necessárias"""
    dependencias = [
        "PyQt6",
        "webbrowser",  # Já vem com Python
        "urllib",      # Já vem com Python
        "json",        # Já vem com Python
        "sqlite3",     # Já vem com Python
    ]
    
    print("Instalando dependências...")
    
    for dependencia in dependencias:
        try:
            if dependencia == "PyQt6":
                subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])
                print(f"✅ {dependencia} instalado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao instalar {dependencia}: {e}")
    
    print("\n✅ Todas as dependências foram instaladas!")
    print("\n🎯 Para executar o sistema:")
    print("   python arquivo_completo_corrigido.py")

if __name__ == "__main__":
    instalar_dependencias()