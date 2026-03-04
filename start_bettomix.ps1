# Betto Mix - Inicializador Rápido
# Execute este script para iniciar o sistema rapidamente

$ApiPort = "5000"
$DataDir = "C:\BettoMix\Dados"

Write-Host "🚀 Iniciando Betto Mix..." -ForegroundColor Cyan

# Verificar API
try {
    $test = Invoke-RestMethod -Uri "http://localhost:$ApiPort/api/v1/test" -TimeoutSec 3
    Write-Host "✅ API Online: $($test.message)" -ForegroundColor Green
    $apiOnline = $true
} catch {
    Write-Host "⚠️  API Offline - Modo local ativado" -ForegroundColor Yellow
    $apiOnline = $false
}

# Carregar configuração
$configFile = "$DataDir\config\config_sistema.json"
if (Test-Path $configFile) {
    $config = Get-Content $configFile | ConvertFrom-Json
    $config.ModoOffline = -not $apiOnline
    $config | ConvertTo-Json -Depth 3 | Out-File $configFile -Encoding UTF8
}

# Iniciar sistema
$mainScript = ".\betto_mix_powershell.ps1"
if (Test-Path $mainScript) {
    . $mainScript
    Main
} else {
    Write-Host "❌ Script principal não encontrado" -ForegroundColor Red
}
