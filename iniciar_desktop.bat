@echo off
chcp 65001 > nul
echo ===========================================
echo   BETTO MIX CONCRETO - Desktop Integrado
echo   Sistema sincronizado com main.py
echo ===========================================
echo.

cd /d "%~dp0"

REM Verificar ambiente virtual
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    echo Ambiente virtual ativado.
) else (
    echo Ambiente virtual nao encontrado.
    echo Usando Python global...
)

REM Verificar dependencias
python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo Instalando tkinter...
    pip install tk --quiet
)

REM Executar sistema
echo Iniciando Sistema BETTO MIX Desktop...
python bettomix_desktop.py

if %errorlevel% neq 0 (
    echo.
    echo Erro ao executar sistema.
    pause
)
