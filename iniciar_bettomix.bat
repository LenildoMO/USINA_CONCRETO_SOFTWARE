@echo off
chcp 65001 > nul
echo ===========================================
echo   SISTEMA BETTO MIX CONCRETO
echo   Inicializando sistema...
echo ===========================================
echo.

cd /d "%~dp0"

REM Verificar se ambiente virtual existe
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    echo Ambiente virtual ativado.
) else (
    echo Ambiente virtual nao encontrado.
    echo Iniciando sem ambiente virtual...
)

REM Executar sistema
python bettomix.py

REM Manter janela aberta
if %errorlevel% neq 0 (
    echo.
    echo Sistema encerrado com erro.
    pause
) else (
    echo.
    echo Sistema encerrado com sucesso.
    timeout /t 3 > nul
)
