# Cria o arquivo sync_installer.ps1
@'
# ============================================
# INSTALADOR DE SINCRONIZAÇÃO AUTOMÁTICA
# ============================================

Write-Host "=== CONFIGURANDO SINCRONIZAÇÃO AUTOMÁTICA ===" -ForegroundColor Cyan

# Verificar se está na pasta correta
$currentDir = Get-Location
$expectedDir = "C:\Users\Micro\Documents\usina_concreto_software"

if ($currentDir.Path -ne $expectedDir) {
    Write-Host "ERRO: Execute este script na pasta do projeto!" -ForegroundColor Red
    Write-Host "Execute: cd `"$expectedDir`"" -ForegroundColor Yellow
    pause
    exit
}

# Verificar OneDrive
$onedriveBase = "C:\Users\Micro\OneDrive"
if (-not (Test-Path $onedriveBase)) {
    Write-Host "ERRO: OneDrive não encontrado!" -ForegroundColor Red
    Write-Host "Instale o OneDrive primeiro." -ForegroundColor Yellow
    pause
    exit
}

# Configurar pastas
$sourceFolder = $currentDir.Path
$targetFolder = "$onedriveBase\usina_concreto_software"

Write-Host "Pasta original: $sourceFolder" -ForegroundColor Green
Write-Host "Pasta OneDrive: $targetFolder" -ForegroundColor Green

# Criar pasta no OneDrive
Write-Host "Criando pasta no OneDrive..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $targetFolder -Force | Out-Null

# Criar script Python simples de sincronização
$pythonCode = @"
import os
import time
import shutil
from pathlib import Path

source = r"$sourceFolder"
target = r"$targetFolder"

print("=" * 60)
print("SINCRONIZADOR AUTOMÁTICO ONEDRIVE")
print("=" * 60)
print(f"Origem:  {source}")
print(f"Destino: {target}")
print("=" * 60)
print("Sincronizando automaticamente...")
print("Pressione Ctrl+C para parar")
print()

# O que ignorar
IGNORE = ['.venv', '__pycache__', '.git', '*.pyc', '*.pyo', '*.pyd']

def should_copy(filepath):
    """Verifica se deve copiar o arquivo"""
    for ignore in IGNORE:
        if ignore.startswith('*'):
            if filepath.endswith(ignore[1:]):
                return False
        elif ignore in filepath:
            return False
    return True

try:
    while True:
        # Percorre todos os arquivos
        for root, dirs, files in os.walk(source):
            # Remove diretórios ignorados
            dirs[:] = [d for d in dirs if should_copy(os.path.join(root, d))]
            
            for file in files:
                if not should_copy(file):
                    continue
                    
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, source)
                dst_path = os.path.join(target, rel_path)
                
                # Verifica se precisa atualizar
                if not os.path.exists(dst_path):
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    print(f"[NOVO] {rel_path}")
                else:
                    # Verifica se o arquivo foi modificado
                    src_time = os.path.getmtime(src_path)
                    dst_time = os.path.getmtime(dst_path)
                    
                    if src_time > dst_time:
                        shutil.copy2(src_path, dst_path)
                        print(f"[ATUALIZADO] {rel_path}")
        
        time.sleep(3)  # Verifica a cada 3 segundos
        
except KeyboardInterrupt:
    print("\nSincronização interrompida. Até logo!")
"@

# Salvar script Python
$pythonCode | Out-File -FilePath "$sourceFolder\sync_auto.py" -Encoding UTF8

# Criar arquivo .bat para iniciar facilmente
$batContent = @'
@echo off
chcp 65001 >nul
echo ========================================
echo   SINCRONIZADOR AUTOMATICO ONEDRIVE
echo ========================================
echo.
echo Iniciando sincronizacao automatica...
echo.
echo Suas alteracoes serao copiadas para:
echo   C:\Users\Micro\OneDrive\usina_concreto_software
echo.
echo Trabalhe normalmente. Tudo sera sincronizado!
echo.
echo Pressione Ctrl+C para parar.
echo ========================================
echo.

python sync_auto.py
'@

$batContent | Out-File -FilePath "$sourceFolder\iniciar_sync.bat" -Encoding ASCII

# Configurar para iniciar com Windows (opcional)
Write-Host "Configurando para iniciar com Windows..." -ForegroundColor Yellow
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$regName = "UsinaConcreteSync"
$pythonPath = (Get-Command python).Source
$pythonwPath = $pythonPath -replace "python.exe", "pythonw.exe"

# Criar script que roda em segundo plano
$backgroundScript = @"
import sys
import os
import time
import shutil

source = r"$sourceFolder"
target = r"$targetFolder"

# Roda em silêncio
while True:
    try:
        for root, dirs, files in os.walk(source):
            if '.venv' in root or '__pycache__' in root:
                continue
            for file in files:
                if file.endswith('.pyc'):
                    continue
                src = os.path.join(root, file)
                dst = os.path.join(target, os.path.relpath(src, source))
                if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
        time.sleep(5)
    except:
        time.sleep(10)
"@

$backgroundScript | Out-File -FilePath "$sourceFolder\sync_background.py" -Encoding UTF8

# Adicionar ao registro para iniciar com Windows
try {
    $regValue = "`"$pythonwPath`" `"$sourceFolder\sync_background.py`""
    New-ItemProperty -Path $regPath -Name $regName -Value $regValue -PropertyType String -Force | Out-Null
    Write-Host "✅ Configurado para iniciar com Windows" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Não foi possível configurar inicialização automática" -ForegroundColor Yellow
}

# Iniciar agora
Write-Host "Iniciando sincronização agora..." -ForegroundColor Green
Start-Process $pythonwPath -ArgumentList "`"$sourceFolder\sync_background.py`"" -WindowStyle Hidden

# Criar arquivo de teste para verificar
$testFile = "teste_sincronizacao_$(Get-Date -Format 'HHmmss').txt"
"Este arquivo foi criado para testar a sincronização automática. Se você vê-lo no OneDrive, está funcionando!" | 
    Out-File -FilePath "$sourceFolder\$testFile" -Encoding UTF8

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ CONFIGURAÇÃO COMPLETA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Agora sua pasta sincroniza automaticamente com:" -ForegroundColor White
Write-Host "   $targetFolder" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para verificar se está funcionando:" -ForegroundColor Yellow
Write-Host "1. Verifique se o arquivo existe no OneDrive:" -ForegroundColor White
Write-Host "   $targetFolder\$testFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Modifique qualquer arquivo nesta pasta" -ForegroundColor White
Write-Host "3. Em poucos segundos aparecerá no OneDrive" -ForegroundColor White
Write-Host ""
Write-Host "Para acessar de casa:" -ForegroundColor Yellow
Write-Host "1. Use a mesma conta do OneDrive no outro PC" -ForegroundColor White
Write-Host "2. Acesse: C:\Users\SeuUsuario\OneDrive\usina_concreto_software" -ForegroundColor White
Write-Host ""
Write-Host "Trabalhe normalmente! Tudo será sincronizado automaticamente." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

pause
'@ | Out-File -FilePath "sync_installer.ps1" -Encoding UTF8