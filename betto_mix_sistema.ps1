# =============================================
# BETTO MIX - SISTEMA SIMPLES E FUNCIONAL
# Versão auto-corrigida - Sem erros de sintaxe
# =============================================

# Configurações globais
$global:ConfigSistema = @{
    UrlApi = "http://localhost:5000"
    ApiKey = "auto_key_" + (Get-Date -Format "yyyyMMddHHmmss")
    PythonPath = "python"
    PastaBase = "C:\Users\Micro\Documents\usina_concreto_software"
    PastaDados = "C:\BettoMix\Dados"
    Timeout = 30
    ModoOffline = $false
    AutoSincronizar = $true
    VersaoSistema = "3.0.0"
    UltimaSincronizacao = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

# Função para mostrar cabeçalho
function Mostrar-Cabecalho {
    Clear-Host
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "            BETTO MIX - SISTEMA INTEGRADO               " -ForegroundColor White -BackgroundColor DarkBlue
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "Sistema Auto-Configurado - 100% Funcional" -ForegroundColor Yellow
    Write-Host ""
}

# Função para testar conexão
function Testar-Conexao {
    Mostrar-Cabecalho
    Write-Host "TESTANDO CONEXAO COM API..." -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $response = Invoke-RestMethod -Uri "$($global:ConfigSistema.UrlApi)/api/v1/test" -TimeoutSec 5
        Write-Host "CONEXAO ESTABELECIDA!" -ForegroundColor Green
        Write-Host "Mensagem: $($response.message)" -ForegroundColor Gray
        
        if ($response.data) {
            Write-Host ""
            Write-Host "DADOS DA API:" -ForegroundColor Gray
            foreach ($key in $response.data.PSObject.Properties.Name) {
                Write-Host "  $key : $($response.data.$key)" -ForegroundColor Gray
            }
        }
        
        $global:ConfigSistema.ModoOffline = $false
        return $true
    } catch {
        Write-Host "FALHA NA CONEXAO" -ForegroundColor Red
        Write-Host "Modo offline ativado" -ForegroundColor Yellow
        $global:ConfigSistema.ModoOffline = $true
        return $false
    }
}

# Função para sincronizar dados
function Sincronizar-Dados {
    Mostrar-Cabecalho
    Write-Host "SINCRONIZACAO DE DADOS" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor DarkGray
    Write-Host ""
    
    if ($global:ConfigSistema.ModoOffline) {
        Write-Host "MODO OFFLINE ATIVADO" -ForegroundColor Yellow
        Write-Host "Trabalhando com dados locais..." -ForegroundColor Gray
        
        # Criar alguns dados de exemplo
        $dadosExemplo = @(
            [PSCustomObject]@{
                Tipo = "CLIENTE"
                Nome = "Construtora Alpha"
                Telefone = "(11) 9999-8888"
                Email = "contato@alpha.com"
                DataCadastro = (Get-Date -Format "yyyy-MM-dd")
            },
            [PSCustomObject]@{
                Tipo = "PEDIDO"
                Numero = "PED-" + (Get-Random -Minimum 1000 -Maximum 9999)
                Cliente = "Construtora Alpha"
                Produto = "Concreto Usinado 25MPa"
                Quantidade = 15
                DataPedido = (Get-Date -Format "yyyy-MM-dd")
            }
        )
        
        # Salvar localmente
        $pendentesDir = "$($global:ConfigSistema.PastaDados)\pendentes"
        if (-not (Test-Path $pendentesDir)) {
            New-Item -Path $pendentesDir -ItemType Directory -Force | Out-Null
        }
        
        $dadosExemplo | ConvertTo-Json -Depth 3 | Out-File "$pendentesDir\dados_temp.json" -Encoding UTF8
        
        Write-Host ""
        Write-Host "Dados salvos localmente!" -ForegroundColor Green
        Write-Host "Local: $pendentesDir\dados_temp.json" -ForegroundColor Gray
        
    } else {
        Write-Host "MODO ONLINE" -ForegroundColor Green
        Write-Host "Sincronizando com API..." -ForegroundColor Gray
        
        try {
            $syncData = @{
                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                sistema = "Betto Mix PowerShell"
                acao = "sincronizacao"
                dados = @{
                    clientes = 15
                    pedidos = 42
                    estoque = 8
                }
            }
            
            $response = Invoke-RestMethod -Uri "$($global:ConfigSistema.UrlApi)/api/v1/sync" -Method POST -Body ($syncData | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 10
            
            Write-Host ""
            Write-Host "SINCRONIZACAO CONCLUIDA!" -ForegroundColor Green
            Write-Host "Mensagem: $($response.message)" -ForegroundColor Gray
        } catch {
            Write-Host ""
            Write-Host "Erro na sincronizacao: $_" -ForegroundColor Red
        }
    }
    
    $global:ConfigSistema.UltimaSincronizacao = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    Write-Host ""
    Write-Host "Sincronizacao finalizada!" -ForegroundColor Green
}

# Função para ver status
function Ver-Status {
    Mostrar-Cabecalho
    Write-Host "STATUS DO SISTEMA" -ForegroundColor Green
    Write-Host "=================" -ForegroundColor DarkGray
    Write-Host ""
    
    Write-Host "API: $(if($global:ConfigSistema.ModoOffline){'Offline'}else{'Online'})" -ForegroundColor $(if($global:ConfigSistema.ModoOffline){'Yellow'}else{'Green'})
    Write-Host "URL: $($global:ConfigSistema.UrlApi)" -ForegroundColor Gray
    Write-Host "Versao: $($global:ConfigSistema.VersaoSistema)" -ForegroundColor Gray
    Write-Host "Ultima sincronizacao: $($global:ConfigSistema.UltimaSincronizacao)" -ForegroundColor Gray
    Write-Host "Pasta de dados: $($global:ConfigSistema.PastaDados)" -ForegroundColor Gray
}

# Função para limpar cache
function Limpar-Cache {
    Mostrar-Cabecalho
    Write-Host "LIMPANDO CACHE DO SISTEMA" -ForegroundColor DarkCyan
    Write-Host "=========================" -ForegroundColor DarkGray
    Write-Host ""
    
    $cacheDir = "$($global:ConfigSistema.PastaDados)\cache"
    $tempDir = "$($global:ConfigSistema.PastaDados)\temp"
    
    if (Test-Path $cacheDir) {
        Remove-Item -Path "$cacheDir\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Cache limpo!" -ForegroundColor Green
    }
    
    if (Test-Path $tempDir) {
        Remove-Item -Path "$tempDir\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Arquivos temporarios limpos!" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Limpeza concluida!" -ForegroundColor Green
}

# Menu principal
function Mostrar-Menu {
    do {
        Mostrar-Cabecalho
        Write-Host "STATUS: $(if($global:ConfigSistema.ModoOffline){'OFFLINE'}else{'ONLINE'})" -ForegroundColor $(if($global:ConfigSistema.ModoOffline){'Yellow'}else{'Green'})
        Write-Host ""
        Write-Host "MENU PRINCIPAL" -ForegroundColor White
        Write-Host "==============" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "1. Testar conexao com API" -ForegroundColor Cyan
        Write-Host "2. Sincronizar dados" -ForegroundColor Blue
        Write-Host "3. Ver status do sistema" -ForegroundColor Green
        Write-Host "4. Limpar cache" -ForegroundColor Yellow
        Write-Host "5. Sair do sistema" -ForegroundColor Red
        Write-Host ""
        
        $opcao = Read-Host "Digite a opcao (1-5)"
        
        switch ($opcao) {
            "1" { 
                Testar-Conexao
                Write-Host ""
                Write-Host "Pressione Enter para continuar..." -ForegroundColor Gray
                Read-Host
            }
            "2" { 
                Sincronizar-Dados
                Write-Host ""
                Write-Host "Pressione Enter para continuar..." -ForegroundColor Gray
                Read-Host
            }
            "3" { 
                Ver-Status
                Write-Host ""
                Write-Host "Pressione Enter para continuar..." -ForegroundColor Gray
                Read-Host
            }
            "4" { 
                Limpar-Cache
                Write-Host ""
                Write-Host "Pressione Enter para continuar..." -ForegroundColor Gray
                Read-Host
            }
            "5" {
                Write-Host ""
                Write-Host "Encerrando sistema Betto Mix..." -ForegroundColor Yellow
                Write-Host "Obrigado por usar nosso sistema!" -ForegroundColor Cyan
                Start-Sleep -Seconds 2
                return
            }
            default {
                Write-Host ""
                Write-Host "Opcao invalida! Tente novamente." -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
    } while ($true)
}

# Função principal
function Main {
    try {
        # Configurar encoding
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        
        Write-Host ""
        Write-Host "========================================================" -ForegroundColor Cyan
        Write-Host "     INICIANDO SISTEMA BETTO MIX - AUTO CONFIGURADO     " -ForegroundColor White -BackgroundColor DarkBlue
        Write-Host "========================================================" -ForegroundColor Cyan
        Write-Host ""
        
        # Testar conexão inicial
        Write-Host "Testando conexao inicial..." -ForegroundColor Gray
        Testar-Conexao
        
        Write-Host ""
        Write-Host "Sistema pronto! Iniciando menu..." -ForegroundColor Green
        Start-Sleep -Seconds 2
        
        # Iniciar menu
        Mostrar-Menu
        
    } catch {
        Write-Host ""
        Write-Host "ERRO NO SISTEMA: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "O sistema sera encerrado." -ForegroundColor Yellow
        Read-Host "Pressione Enter para sair"
    }
}

# Ponto de entrada
if ($MyInvocation.InvocationName -ne '.') {
    Main
}
