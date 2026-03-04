@echo off
chcp 65001 > nul
title Betto Mix - Sistema Integrado
echo.
echo ========================================
echo      BETTO MIX - INICIANDO SISTEMA
echo ========================================
echo.
echo Configurando ambiente...

REM Verificar se Python est? instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo ? Python n?o encontrado!
    echo Instale Python 3.x e tente novamente.
    pause
    exit /b 1
)

REM Verificar se API j? est? rodando
netstat -an | find ":5000" > nul
if errorlevel 1 (
    echo ?? Iniciando API...
    start /B python api_simples.py
    timeout /t 3 /nobreak > nul
) else (
    echo ?? API j? est? rodando...
)

REM Iniciar sistema principal
echo.
echo ???  Abrindo Sistema Betto Mix...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "betto_mix_tela.ps1"

echo.
echo ========================================
echo    Sistema encerrado. Obrigado!
echo ========================================
pause
