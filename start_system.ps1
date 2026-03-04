# start_system.ps1 - SIMPLES E FUNCIONAL

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   BETTO MIX WEB - SISTEMA CORRIGIDO         " -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "📥 Baixe em: https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit
}

# Verificar dependências
Write-Host "🔍 Verificando dependências..." -ForegroundColor Cyan

$packages = @("fastapi", "uvicorn")
foreach ($pkg in $packages) {
    python -c "import $($pkg.Replace('-','_'))" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ $pkg" -ForegroundColor Green
    } else {
        Write-Host "  📦 Instalando $pkg..." -ForegroundColor Yellow
        python -m pip install $pkg --quiet
        Write-Host "    ✅ $pkg instalado" -ForegroundColor Green
    }
}

# Obter IP local
try {
    $ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" }
    $localIPs = $ips.IPAddress | Where-Object { $_ -match "^192\.168\." -or $_ -match "^10\." -or $_ -match "^172\." }
} catch {
    $localIPs = @()
}

# Mostrar URLs
Write-Host ""
Write-Host "🌐 URLs DE ACESSO:" -ForegroundColor Cyan
Write-Host "   Neste computador: http://localhost:8765" -ForegroundColor Green

if ($localIPs) {
    foreach ($ip in $localIPs) {
        Write-Host "   Rede local: http://${ip}:8765" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "📱 Acessível de:" -ForegroundColor Yellow
Write-Host "   • Este computador" -ForegroundColor White
Write-Host "   • Celulares na mesma rede" -ForegroundColor White
Write-Host "   • Outros computadores na rede" -ForegroundColor White
Write-Host ""
Write-Host "🎨 Layout Original Azul (#003366)" -ForegroundColor White
Write-Host "🔧 KeyError RESOLVIDO" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan

# Abrir navegador
try {
    Start-Process "http://localhost:8765"
    Write-Host "🌐 Navegador aberto" -ForegroundColor Green
} catch {
    Write-Host "📌 Acesse: http://localhost:8765" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Iniciando servidor..." -ForegroundColor Cyan
Write-Host "⚠️  Mantenha esta janela aberta" -ForegroundColor Yellow
Write-Host "⚠️  Ctrl+C para encerrar" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor
python web_system\web_server.py
