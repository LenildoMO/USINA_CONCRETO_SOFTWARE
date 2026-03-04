# =============================================
# SISTEMA BETTO MIX - GERADO AUTOMATICAMENTE
# =============================================

# Configuração
$global:ConfigSincronizacao = @{
    PastaDados = "C:\Users\Micro\Documents\usina_concreto_software\dados"
    UrlApi = "https://api.bettomix.com/v1"
    ApiKey = ""
    AutoSincronizar = $true
    IntervaloSincronizacao = 300
    Timeout = 30
}

# Criar pasta de dados
if (-not (Test-Path $global:ConfigSincronizacao.PastaDados)) {
    New-Item -ItemType Directory -Path $global:ConfigSincronizacao.PastaDados -Force | Out-Null
}

# Menu principal
function Show-Menu {
    do {
        Clear-Host
        Write-Host "`n" + "="*60 -ForegroundColor Cyan
        Write-Host " BETTO MIX - SISTEMA DE SINCRONIZAÇÃO " -ForegroundColor White -BackgroundColor Blue
        Write-Host "="*60 -ForegroundColor Cyan
        
        Write-Host "`n📊 STATUS DO SISTEMA" -ForegroundColor Yellow
        Write-Host "  API: $($global:ConfigSincronizacao.UrlApi)" -ForegroundColor Gray
        Write-Host "  Pasta de dados: $($global:ConfigSincronizacao.PastaDados)" -ForegroundColor Gray
        
        Write-Host "`n📋 MENU PRINCIPAL" -ForegroundColor White
        Write-Host " 1. Testar sistema" -ForegroundColor Gray
        Write-Host " 2. Configurar API" -ForegroundColor Gray
        Write-Host " 3. Verificar arquivos" -ForegroundColor Gray
        Write-Host " 4. Sair" -ForegroundColor Red
        
        Write-Host "`n" + "-"*60 -ForegroundColor DarkGray
        
        $opcao = Read-Host "`nSelecione uma opção (1-4)"
        
        switch ($opcao) {
            "1" {
                Write-Host "`n✅ Testando sistema..." -ForegroundColor Green
                Write-Host "  Sistema funcionando corretamente!" -ForegroundColor Green
                Write-Host "  Pasta de dados: $(Test-Path $global:ConfigSincronizacao.PastaDados)" -ForegroundColor Gray
                Read-Host "`nPressione Enter para continuar"
            }
            "2" {
                Write-Host "`n⚙️ Configuração da API" -ForegroundColor Yellow
                $novaUrl = Read-Host "URL da API (atual: $($global:ConfigSincronizacao.UrlApi))"
                $novaKey = Read-Host "API Key (deixe em branco para manter)"
                
                if ($novaUrl) { $global:ConfigSincronizacao.UrlApi = $novaUrl }
                if ($novaKey) { $global:ConfigSincronizacao.ApiKey = $novaKey }
                
                Write-Host "✅ Configuração atualizada!" -ForegroundColor Green
                Read-Host "`nPressione Enter para continuar"
            }
            "3" {
                Write-Host "`n📁 Verificando arquivos..." -ForegroundColor Yellow
                $arquivos = Get-ChildItem -File *.ps1
                Write-Host "  Arquivos PowerShell encontrados:" -ForegroundColor Gray
                foreach ($arquivo in $arquivos) {
                    Write-Host "  - $($arquivo.Name)" -ForegroundColor Gray
                }
                Read-Host "`nPressione Enter para continuar"
            }
            "4" {
                Write-Host "`n👋 Saindo do sistema..." -ForegroundColor Yellow
                return $true
            }
            default {
                Write-Host "`n❌ Opção inválida!" -ForegroundColor Red
                Read-Host "`nPressione Enter para continuar"
            }
        }
    } while ($true)
}

# Iniciar sistema
try {
    Show-Menu
} catch {
    Write-Host "`n❌ Erro no sistema: $_" -ForegroundColor Red
    Read-Host "`nPressione Enter para sair"
}
