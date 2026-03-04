@echo off
chcp 65001 >nul
cls

echo ========================================
echo    INSTALADOR RÁPIDO - UsinaConcreto
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado!
    echo Instale Python em: https://python.org
    pause
    exit /b 1
)

REM Ativar ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    echo Ambiente virtual ativado.
) else (
    echo Ambiente virtual não encontrado.
    echo Criando ambiente virtual...
    python -m venv .venv
    call ".venv\Scripts\activate.bat"
    
    echo Instalando dependências...
    pip install pyinstaller Pillow
)

REM Executar o instalador Python
echo.
echo Executando instalador...
python instalador.py

pause