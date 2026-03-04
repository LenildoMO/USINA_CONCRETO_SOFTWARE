@echo off
chcp 65001 >nul
title BETTO MIX - Sistema Web Automático
color 0A

echo.
echo ================================================
echo      BETTO MIX - SISTEMA WEB AUTOMÁTICO
echo ================================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo.
    echo 📥 Instale Python em: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python instalado
echo.

:: Criar pastas necessárias
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "backups" mkdir backups
if not exist "web_sync" mkdir web_sync

echo 🚀 Iniciando sistema...
echo 📌 Aguarde alguns segundos...
echo.

python betto_auto_system.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao iniciar sistema!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Sistema encerrado
pause
