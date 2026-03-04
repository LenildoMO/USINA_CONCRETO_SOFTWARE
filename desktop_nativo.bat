@echo off
echo ========================================
echo   BETTO MIX CONCRETO - Desktop Nativo
echo ========================================
echo.

REM Ir para diretorio do script
cd /d "%~dp0"

REM Usar ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

REM Executar sistema
python abrir_desktop.py

pause
