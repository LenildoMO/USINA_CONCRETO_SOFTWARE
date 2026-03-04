# =============================================
# BETTO MIX - SISTEMA COM INTERFACE GARANTIDA
# Sempre abre a tela corretamente
# =============================================

# Configuração inicial para garantir tela
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$host.UI.RawUI.WindowTitle = "Betto Mix - Sistema Integrado"

# Configurações
$Config = @{
    UrlApi = "http://localhost:5000"
    PastaDados = "C:\BettoMix\Dados"
    ModoOffline = $false
}

# Função para mostrar tela inicial
function Show-SplashScreen {
    Clear-Host
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "              BETTO MIX - SISTEMA PRINCIPAL             " -ForegroundColor White -BackgroundColor DarkBlue
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "             Sistema de Gestão Completo                " -ForegroundColor Yellow
    Write-Host "           Para Usina de Concreto Betto Mix            " -ForegroundColor Gray
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Mostrar status
    Write-Host "📊 STATUS DO SISTEMA:" -ForegroundColor White
    try {
        $response = Invoke-RestMethod -Uri "$($Config.UrlApi)/api/v1/test" -TimeoutSec 3
        Write-Host "  🌐 API: CONECTADA" -ForegroundColor Green
        Write-Host "  📡 $($response.message)" -ForegroundColor Gray
        $Config.ModoOffline = $false
    } catch {
        Write-Host "  🌐 API: OFFLINE" -ForegroundColor Yellow
        Write-Host "  📡 Trabalhando em modo local" -ForegroundColor Gray
        $Config.ModoOffline = $true
    }
    
    Write-Host ""
}

# Função para testar conexão
function Test-Connection {
    Show-SplashScreen
    Write-Host "🔍 TESTANDO CONEXÃO..." -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri "$($Config.UrlApi)/api/v1/test" -TimeoutSec 5
        
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalMilliseconds
        
        Write-Host "✅ CONEXÃO BEM-SUCEDIDA!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 DETALHES:" -ForegroundColor Gray
        Write-Host "  Tempo de resposta: $([math]::Round($duration))ms" -ForegroundColor Gray
        Write-Host "  Mensagem: $($response.message)" -ForegroundColor Gray
        
        if ($response.data) {
            Write-Host ""
            Write-Host "📈 DADOS DO SISTEMA:" -ForegroundColor Gray
            $response.data.PSObject.Properties | ForEach-Object {
                Write-Host "  $($_.Name): $($_.Value)" -ForegroundColor Gray
            }
        }
        
    } catch {
        Write-Host "❌ FALHA NA CONEXÃO" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 SOLUÇÕES:" -ForegroundColor Yellow
        Write-Host "  1. Verifique se a API está rodando" -ForegroundColor Gray
        Write-Host "  2. Execute: python api_simples.py" -ForegroundColor Gray
        Write-Host "  3. O sistema funcionará em modo offline" -ForegroundColor Gray
    }
    
    Write-Host ""
    Wait-ForKeyPress
}

# Função para gerenciar clientes
function Manage-Clients {
    Show-SplashScreen
    Write-Host "👥 GERENCIAMENTO DE CLIENTES" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor DarkGray
    Write-Host ""
    
    # Dados de exemplo
    $clientes = @(
        [PSCustomObject]@{
            Codigo = "CLI-001"
            Nome = "Construtora Alpha LTDA"
            Telefone = "(11) 3333-4444"
            Email = "contato@alpha.com"
            Desde = "2023-01-15"
            Status = "Ativo"
        },
        [PSCustomObject]@{
            Codigo = "CLI-002"
            Nome = "Engenharia Beta S/A"
            Telefone = "(11) 5555-6666"
            Email = "vendas@beta.com"
            Desde = "2023-03-20"
            Status = "Ativo"
        },
        [PSCustomObject]@{
            Codigo = "CLI-003"
            Nome = "Construções Gama"
            Telefone = "(11) 7777-8888"
            Email = "gama@construcoes.com"
            Desde = "2023-05-10"
            Status = "Inativo"
        }
    )
    
    Write-Host "📋 LISTA DE CLIENTES:" -ForegroundColor White
    Write-Host ""
    
    foreach ($cliente in $clientes) {
        $statusColor = if ($cliente.Status -eq "Ativo") { "Green" } else { "Red" }
        Write-Host "  Código: $($cliente.Codigo)" -ForegroundColor Cyan
        Write-Host "  Nome:   $($cliente.Nome)" -ForegroundColor Gray
        Write-Host "  Status: $($cliente.Status)" -ForegroundColor $statusColor
        Write-Host "  ---------------------------------" -ForegroundColor DarkGray
    }
    
    Write-Host ""
    Write-Host "📊 TOTAL: $($clientes.Count) clientes cadastrados" -ForegroundColor Yellow
    
    Write-Host ""
    Wait-ForKeyPress
}

# Função para gerenciar pedidos
function Manage-Orders {
    Show-SplashScreen
    Write-Host "📦 GERENCIAMENTO DE PEDIDOS" -ForegroundColor Cyan
    Write-Host "============================" -ForegroundColor DarkGray
    Write-Host ""
    
    # Dados de exemplo
    $pedidos = @(
        [PSCustomObject]@{
            Numero = "PED-2024-001"
            Cliente = "Construtora Alpha"
            Produto = "Concreto 25MPa"
            Quantidade = "15 m³"
            Data = "2024-01-15"
            Status = "Entregue"
        },
        [PSCustomObject]@{
            Numero = "PED-2024-002"
            Cliente = "Engenharia Beta"
            Produto = "Concreto 30MPa"
            Quantidade = "8 m³"
            Data = "2024-01-16"
            Status = "Produção"
        },
        [PSCustomObject]@{
            Numero = "PED-2024-003"
            Cliente = "Construções Gama"
            Produto = "Concreto 20MPa"
            Quantidade = "25 m³"
            Data = "2024-01-17"
            Status = "Aguardando"
        }
    )
    
    Write-Host "📋 PEDIDOS RECENTES:" -ForegroundColor White
    Write-Host ""
    
    foreach ($pedido in $pedidos) {
        $statusColor = switch ($pedido.Status) {
            "Entregue" { "Green" }
            "Produção" { "Yellow" }
            "Aguardando" { "Red" }
            default { "Gray" }
        }
        
        Write-Host "  Pedido:   $($pedido.Numero)" -ForegroundColor Cyan
        Write-Host "  Cliente:  $($pedido.Cliente)" -ForegroundColor Gray
        Write-Host "  Produto:  $($pedido.Produto)" -ForegroundColor Gray
        Write-Host "  Status:   $($pedido.Status)" -ForegroundColor $statusColor
        Write-Host "  ---------------------------------" -ForegroundColor DarkGray
    }
    
    Write-Host ""
    Write-Host "📊 TOTAL: $($pedidos.Count) pedidos listados" -ForegroundColor Yellow
    
    Write-Host ""
    Wait-ForKeyPress
}

# Função para aguardar tecla
function Wait-ForKeyPress {
    Write-Host "⏎  Pressione ENTER para continuar..." -ForegroundColor Gray -NoNewline
    $null = Read-Host
}

# Função para mostrar menu principal
function Show-MainMenu {
    do {
        Show-SplashScreen
        
        Write-Host "📋 MENU PRINCIPAL" -ForegroundColor White
        Write-Host "=================" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "1. 🔍 Testar Conexão com API" -ForegroundColor Cyan
        Write-Host "2. 👥 Gerenciar Clientes" -ForegroundColor Blue
        Write-Host "3. 📦 Gerenciar Pedidos" -ForegroundColor Green
        Write-Host "4. 📊 Relatórios" -ForegroundColor Yellow
        Write-Host "5. ⚙️  Configurações" -ForegroundColor Magenta
        Write-Host "6. ❌ Sair do Sistema" -ForegroundColor Red
        Write-Host ""
        
        $opcao = Read-Host "Digite a opção desejada (1-6)"
        
        switch ($opcao) {
            "1" { Test-Connection }
            "2" { Manage-Clients }
            "3" { Manage-Orders }
            "4" { 
                Show-SplashScreen
                Write-Host "📊 RELATÓRIOS DO SISTEMA" -ForegroundColor Cyan
                Write-Host "========================" -ForegroundColor DarkGray
                Write-Host ""
                Write-Host "Em desenvolvimento..." -ForegroundColor Yellow
                Write-Host "Esta funcionalidade estará disponível em breve!" -ForegroundColor Gray
                Write-Host ""
                Wait-ForKeyPress
            }
            "5" { 
                Show-SplashScreen
                Write-Host "⚙️  CONFIGURAÇÕES" -ForegroundColor Magenta
                Write-Host "================" -ForegroundColor DarkGray
                Write-Host ""
                Write-Host "URL da API: $($Config.UrlApi)" -ForegroundColor Gray
                Write-Host "Pasta de Dados: $($Config.PastaDados)" -ForegroundColor Gray
                Write-Host "Modo: $(if($Config.ModoOffline){'Offline'}else{'Online'})" -ForegroundColor Gray
                Write-Host ""
                Write-Host "💡 Configurações automáticas otimizadas" -ForegroundColor Yellow
                Write-Host ""
                Wait-ForKeyPress
            }
            "6" {
                Show-SplashScreen
                Write-Host "👋 ENCERRANDO SISTEMA..." -ForegroundColor Yellow
                Write-Host ""
                Write-Host "Obrigado por usar o Sistema Betto Mix!" -ForegroundColor Cyan
                Write-Host "Volte sempre! 🚀" -ForegroundColor Green
                Write-Host ""
                Start-Sleep -Seconds 2
                exit
            }
            default {
                Write-Host ""
                Write-Host "❌ Opção inválida! Tente novamente." -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
    } while ($true)
}

# Ponto de entrada principal
try {
    # Garantir que estamos no diretório correto
    if (Test-Path "api_simples.py") {
        Write-Host "✅ Sistema localizado corretamente" -ForegroundColor Green
    }
    
    # Iniciar menu principal
    Show-MainMenu
    
} catch {
    Write-Host ""
    Write-Host "❌ ERRO NO SISTEMA: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔄 Reinicie o sistema ou contate o suporte." -ForegroundColor Yellow
    Write-Host ""
    Wait-ForKeyPress
}
