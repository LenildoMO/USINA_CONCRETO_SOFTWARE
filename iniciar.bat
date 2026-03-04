@echo off
echo ========================================
echo   BETTO MIX - SISTEMA DE SINCRONIZA??O
echo ========================================
echo.
echo Iniciando sistema...
echo.
cd /d "C:\Users\Micro\Documents\usina_concreto_software"
powershell -ExecutionPolicy Bypass -File betto_sistema.ps1
if %errorlevel% neq 0 (
    echo.
    echo ERRO: Execute manualmente: betto_sistema.ps1
    pause
)
