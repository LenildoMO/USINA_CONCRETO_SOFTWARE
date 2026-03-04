# start_betto_web.ps1
# Inicializador Automático do Sistema Web Betto Mix

param([switch]$Silent = $false)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    if (!$Silent) {
        Write-Host $logMessage -ForegroundColor $Color
    }
}

Clear-Host
Write-Log "================================================" "Cyan"
Write-Log "   BETTO MIX - SISTEMA WEB (LAYOUT ORIGINAL)   " "Yellow"
Write-Log "================================================" "Cyan"
Write-Log ""

# Verificar Python
try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✅ Python encontrado: $pythonVersion" "Green"
    } else {
        Write-Log "❌ Python não encontrado!" "Red"
        Write-Log "📥 Baixe em: https://www.python.org/downloads/" "Yellow"
        if (!$Silent) { pause }
        exit 1
    }
} catch {
    Write-Log "❌ Python não encontrado!" "Red"
    Write-Log "📥 Baixe em: https://www.python.org/downloads/" "Yellow"
    if (!$Silent) { pause }
    exit 1
}

# Verificar dependências
Write-Log "🔍 Verificando dependências..." "Cyan"

$packages = @("fastapi", "uvicorn", "jinja2")
foreach ($pkg in $packages) {
    try {
        & python -c "import $($pkg.Replace('-','_'))" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "  ✅ $pkg" "Green"
        } else {
            Write-Log "  📦 Instalando $pkg..." "Yellow"
            & python -m pip install $pkg --quiet
            Write-Log "    ✅ $pkg instalado" "Green"
        }
    } catch {
        Write-Log "  📦 Instalando $pkg..." "Yellow"
        & python -m pip install $pkg --quiet
        Write-Log "    ✅ $pkg instalado" "Green"
    }
}

# Iniciar sistema
Write-Log ""
Write-Log "🚀 Iniciando Sistema Betto Mix Web..." "Cyan"
Write-Log "⏳ Aguarde alguns segundos..." "Yellow"
Write-Log ""

# Mostrar URLs
Write-Log "🌐 URLs DE ACESSO:" "Cyan"
Write-Log "   Neste computador: http://localhost:8765" "Green"

try {
    $ips = @()
    $adapters = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" }
    foreach ($adapter in $adapters) {
        $ip = $adapter.IPAddress
        if ($ip -match "^192\.168\." -or $ip -match "^10\." -or $ip -match "^172\.") {
            $ips += $ip
        }
    }
    
    if ($ips.Count -gt 0) {
        foreach ($ip in $ips) {
            Write-Log "   Na rede local: http://${ip}:8765" "Green"
        }
    }
} catch {
    # Ignorar erro de rede
}

Write-Log ""
Write-Log "📱 Use qualquer dispositivo na mesma rede" "Yellow"
Write-Log "🔐 Login automático habilitado" "Yellow"
Write-Log "================================================" "Cyan"

# Abrir navegador local
try {
    if (!$Silent) {
        Start-Process "http://localhost:8765"
        Write-Log "🌐 Navegador aberto automaticamente" "Green"
    }
} catch {
    Write-Log "📌 Acesse manualmente: http://localhost:8765" "Yellow"
}

Write-Log ""
Write-Log "✅ SISTEMA INICIADO COM SUCESSO!" "Green"
Write-Log "⚠️  Mantenha esta janela aberta" "Yellow"
Write-Log "⚠️  Pressione Ctrl+C para encerrar" "Yellow"
Write-Log "================================================" "Cyan"
Write-Log ""

# Iniciar servidor Python
try {
    & python start_web.py
} catch {
    Write-Log "❌ Erro ao executar sistema: $_" "Red"
    if (!$Silent) { pause }
}
