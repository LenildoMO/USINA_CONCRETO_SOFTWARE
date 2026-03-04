@echo off
chcp 65001 >nul
title Verificador de Sincronização

:menu
cls
echo ========================================
echo   VERIFICADOR DE SINCRONIZAÇÃO
echo ========================================
echo.
echo 1. Ver status da sincronização
echo 2. Ver arquivos sincronizados
echo 3. Forçar sincronização agora
echo 4. Abrir pasta OneDrive
echo 5. Ver logs
echo 6. Sair
echo.
set /p choice="Escolha uma opção (1-6): "

if "%choice%"=="1" goto status
if "%choice%"=="2" goto files
if "%choice%"=="3" goto force
if "%choice%"=="4" goto open
if "%choice%"=="5" goto logs
if "%choice%"=="6" exit

goto menu

:status
python sync_control.py status
echo.
pause
goto menu

:files
echo Arquivos na pasta original:
dir /b /s | find /c /v "" | findstr /v "findstr"
echo.
echo Arquivos no OneDrive:
dir /b /s "C:\Users\Micro\OneDrive\usina_concreto_software" | find /c /v "" | findstr /v "findstr" 2>nul
echo.
pause
goto menu

:force
echo Forçando sincronização...
python -c "
import shutil, os, json
with open('sync_config.json') as f:
    config = json.load(f)
count = 0
for root, dirs, files in os.walk(config['source_folder']):
    for file in files:
        if not any(exclude in file for exclude in config['exclude_patterns']):
            src = os.path.join(root, file)
            rel = os.path.relpath(src, config['source_folder'])
            dst = os.path.join(config['onedrive_folder'], rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            count += 1
print(f'Sincronizados {count} arquivos')
"
echo.
pause
goto menu

:open
explorer "C:\Users\Micro\OneDrive\usina_concreto_software"
goto menu

:logs
if exist "C:\SyncLogs\sync_service.log" (
    notepad "C:\SyncLogs\sync_service.log"
) else (
    echo Logs não encontrados
)
pause
goto menu