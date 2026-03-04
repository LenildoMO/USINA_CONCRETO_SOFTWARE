# start_sistema.ps1
# Sistema Betto Mix - Iniciador Automático

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Verificar Python
try {
    python --version 2>&1 | Out-Null
    Write-Host "✅ Python encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "📥 Baixe em: https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit
}

# Criar pastas necessárias
$folders = @("logs", "data", "backups", "web_sync")
foreach ($folder in $folders) {
    $path = Join-Path $scriptDir $folder
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

# Iniciar sistema
Write-Host "🚀 Iniciando Sistema Betto Mix..." -ForegroundColor Cyan
Write-Host "📌 Aguarde alguns segundos..." -ForegroundColor Yellow

$process = Start-Process python -ArgumentList "betto_auto_system.py" -NoNewWindow -PassThru -WorkingDirectory $scriptDir

# Aguardar e abrir navegador
Start-Sleep -Seconds 3
try {
    Start-Process "http://localhost:8765"
    Write-Host "🌐 Navegador aberto" -ForegroundColor Green
} catch {
    Write-Host "📌 Acesse: http://localhost:8765" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Sistema iniciado!" -ForegroundColor Green
Write-Host "⚠️  Mantenha esta janela aberta" -ForegroundColor Yellow
Write-Host "⚠️  Pressione Ctrl+C para parar" -ForegroundColor Yellow

$process.WaitForExit()
