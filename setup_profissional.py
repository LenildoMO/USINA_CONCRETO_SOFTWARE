"""
SETUP PROFISSIONAL - USINA BETTO MIX CONCRETO
Execute este arquivo UMA VEZ para configurar tudo.
"""

import os
import sys
import shutil
import json

print("=" * 60)
print("       USINA BETTO MIX - SETUP PROFISSIONAL")
print("=" * 60)

# Caminhos importantes
caminho_atual = os.path.dirname(os.path.abspath(__file__))
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
pasta_destino = os.path.join(desktop, "USINA_BETTO_MIX_PRO")

print(f"\n📍 Local atual: {caminho_atual}")
print(f"🖥️  Área de Trabalho: {desktop}")
print(f"🎯 Pasta de destino: {pasta_destino}")

# 1. Criar pasta de destino
os.makedirs(pasta_destino, exist_ok=True)
print(f"\n✅ Pasta criada: {pasta_destino}")

# 2. Listar e copiar arquivos
print("\n📦 COPIANDO ARQUIVOS...")
arquivos = os.listdir(caminho_atual)

for arquivo in arquivos:
    if arquivo.endswith(('.py', '.txt', '.db')) and arquivo != 'setup_profissional.py':
        origem = os.path.join(caminho_atual, arquivo)
        destino = os.path.join(pasta_destino, arquivo)
        
        try:
            shutil.copy2(origem, destino)
            print(f"  ✅ {arquivo}")
        except Exception as e:
            print(f"  ⚠ {arquivo} - Erro: {e}")

# 3. Criar arquivo de configuração
config = {
    "sistema": "Usina Betto Mix Concreto",
    "versao": "2.0.1 Pro",
    "empresa": "Usina Betto Mix",
    "backup_automatico": True
}

with open(os.path.join(pasta_destino, 'config.json'), 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)
print("  ✅ config.json criado")

# 4. Criar atalho .BAT
bat_conteudo = f"""@echo off
chcp 65001 >nul
title USINA BETTO MIX CONCRETO

echo ========================================
echo    USINA BETTO MIX CONCRETO
echo    Sistema Profissional de Gestao
echo ========================================
echo.

cd /d "{pasta_destino}"

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python em: python.org
    pause
    exit /b 1
)

echo.
echo Iniciando sistema...
echo.
python main.py

echo.
if errorlevel 1 (
    echo ERRO: Nao foi possivel iniciar o sistema.
    echo Verifique se o arquivo main.py existe.
) else (
    echo Sistema encerrado normalmente.
)

pause
"""

with open(os.path.join(pasta_destino, 'ABRIR_SISTEMA.bat'), 'w', encoding='utf-8') as f:
    f.write(bat_conteudo)
print("  ✅ ABRIR_SISTEMA.bat criado")

# 5. Tentar criar atalho na área de trabalho
try:
    # Criar arquivo .VBS para criar atalho
    vbs_conteudo = f"""
Set WshShell = WScript.CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oShellLink = WshShell.CreateShortcut(strDesktop & "\\\\Usina Betto Mix.lnk")
oShellLink.TargetPath = "{pasta_destino}\\\\ABRIR_SISTEMA.bat"
oShellLink.WorkingDirectory = "{pasta_destino}"
oShellLink.Description = "Sistema Usina Betto Mix Concreto"
oShellLink.Save
"""
    
    vbs_path = os.path.join(caminho_atual, 'criar_atalho.vbs')
    with open(vbs_path, 'w') as f:
        f.write(vbs_conteudo)
    
    # Executar VBS
    os.system(f'cscript //nologo "{vbs_path}"')
    os.remove(vbs_path)
    print("  ✅ Atalho criado na Área de Trabalho")
    
except Exception as e:
    print(f"  ⚠ Não foi possível criar atalho automático: {e}")
    print(f"  📌 Crie manualmente apontando para: {pasta_destino}\\ABRIR_SISTEMA.bat")

# 6. Mensagem final
print("\n" + "=" * 60)
print("🎉 SETUP CONCLUÍDO COM SUCESSO!")
print("=" * 60)
print(f"\n📂 PASTA DO SISTEMA: {pasta_destino}")
print("🔗 ATALHO: 'Usina Betto Mix' na sua Área de Trabalho")
print("\n🚀 PARA USAR:")
print("1. Vá para sua Área de Trabalho")
print("2. Clique duas vezes em 'Usina Betto Mix'")
print("3. Ou abra a pasta e execute 'ABRIR_SISTEMA.bat'")
print("\n⚠ OBSERVAÇÕES:")
print("- Mantenha a pasta USINA_BETTO_MIX_PRO na Área de Trabalho")
print("- Não mova arquivos individuais fora desta pasta")
print("- O sistema criará backups automáticos na pasta 'backups'")

input("\n📌 Pressione ENTER para finalizar...")