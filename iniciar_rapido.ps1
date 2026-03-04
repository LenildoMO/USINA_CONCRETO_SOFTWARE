# Inicializador Rápido Betto Mix
Write-Host "🚀 INICIANDO BETTO MIX..." -ForegroundColor Cyan
Write-Host ""

# Verificar API
try {
    $test = Invoke-RestMethod -Uri "http://localhost:5000/api/v1/test" -TimeoutSec 3
    Write-Host "✅ API Online: $($test.message)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  API Offline - Iniciando..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "api_simples.py" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# Iniciar sistema
Write-Host ""
Write-Host "🖥️  Abrindo interface do sistema..." -ForegroundColor Green
Start-Sleep -Seconds 2

# Executar sistema
. ".\betto_mix_tela.ps1"
