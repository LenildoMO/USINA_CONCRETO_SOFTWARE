#!/usr/bin/env python3
# ==============================================================================
# betto_auto_system.py
# SISTEMA BETTO MIX WEB - CORREÇÃO AUTOMÁTICA
# ==============================================================================

import os
import sys
import json
import socket
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

def setup_automatico():
    """Configuração automática completa"""
    print("\n" + "="*60)
    print("⚙️  CONFIGURAÇÃO AUTOMÁTICA DO SISTEMA BETTO MIX")
    print("="*60)
    
    base_dir = Path(__file__).parent.absolute()
    
    # Criar estrutura de pastas
    pastas = [
        "logs",
        "data", 
        "backups",
        "web_sync",
        "original_system/ui/pages",
        "original_system/resources"
    ]
    
    for pasta in pastas:
        path = base_dir / pasta
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Criada pasta: {pasta}")
    
    # Verificar Python
    try:
        import sys
        print(f"✅ Python {sys.version}")
    except:
        print("❌ Python não encontrado")
        return False
    
    # Criar arquivo de configuração
    config = {
        "sistema": "Betto Mix Web Sync",
        "versao": "2.0.0",
        "porta": 8765,
        "auto_fix": True,
        "tema_cor": "#003366",
        "login_obrigatorio": True
    }
    
    config_file = base_dir / "config_auto.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuração salva")
    print("\n" + "="*60)
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("="*60)
    
    return True

def start_server():
    """Inicia servidor web simples"""
    try:
        import http.server
        import socketserver
        
        port = 8765
        
        handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🌐 Servidor iniciado em http://localhost:{port}")
            print("📌 Mantenha esta janela aberta")
            print("📌 Pressione Ctrl+C para parar")
            httpd.serve_forever()
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print(r"""
    ╔═══════════════════════════════════════════════════╗
    ║      BETTO MIX CONCRETO - SISTEMA WEB SYNC       ║
    ║           Correção Automática Ativada           ║
    ║         🚀 Iniciando em modo automático         ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # Executar configuração
    if setup_automatico():
        # Iniciar servidor
        start_server()
    else:
        print("❌ Falha na configuração automática")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
