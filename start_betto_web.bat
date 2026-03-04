@echo off
chcp 65001 >nul
title BETTO MIX - Sistema Web
color 0A

echo.
echo ================================================
echo      BETTO MIX - SISTEMA WEB AUTOMATICO
echo ================================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado!
    echo.
    echo 📥 Instale Python em: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python instalado
echo.

:: Verificar/instalar dependencias basicas
echo 🔍 Verificando dependencias...
echo.
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo 📦 Instalando FastAPI, Uvicorn, Jinja2...
    python -m pip install fastapi uvicorn jinja2 --quiet
    echo   ✅ Dependencias instaladas
) else (
    echo ✅ Dependencias OK
)

echo.
echo 🚀 Iniciando Sistema Betto Mix Web...
echo ⏳ Aguarde alguns segundos...
echo.
echo 🌐 O sistema abrira em: http://localhost:8765
echo 📱 Acesse de qualquer dispositivo na rede
echo 🔐 Login automatico habilitado
echo.

:: Iniciar servidor
python start_web.py

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
