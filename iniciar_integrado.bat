@echo off
chcp 65001 > nul
echo ===========================================
echo   BETTO MIX CONCRETO - SISTEMA INTEGRADO
echo   Usando diretorio atual e ambiente virtual
echo ===========================================
echo.

REM Ir para o diretorio do script
cd /d "%~dp0"

REM Ativar ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    echo Ambiente virtual ativado.
) else (
    echo Ambiente virtual nao encontrado, usando Python global.
)

REM Verificar e instalar psutil se necessario
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo Instalando psutil...
    pip install psutil --quiet
)

REM Executar sistema
echo Iniciando sistema BETTO MIX...
python bettomix_integrado.py

REM Manter janela aberta em caso de erro
if %errorlevel% neq 0 (
    echo.
    echo Sistema encerrado com codigo de erro: %errorlevel%
    pause
)
