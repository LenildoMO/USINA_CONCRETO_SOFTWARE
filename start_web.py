#!/usr/bin/env python3
# start_web.py
# Inicializador simples do sistema web

import os
import sys
import time
from pathlib import Path

def start_system():
    print("🚀 Iniciando Sistema Betto Mix Web...")
    print("⏳ Aguarde alguns segundos...")
    
    # Adicionar diretório ao path
    base_dir = Path(__file__).parent
    web_system = base_dir / "web_system"
    
    sys.path.insert(0, str(web_system))
    
    try:
        # Importar e iniciar servidor
        from web_server import main
        main()
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    start_system()
