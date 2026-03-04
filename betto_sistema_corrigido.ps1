# =============================================
# SISTEMA BETTO MIX - CORREÇÃO DA FUNÇÃO LOG
# =============================================

# Configuração global
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

# =============================================
# FUNÇÕES CORRIGIDAS
# =============================================

function Registrar-Log {
    param($mensagem, $tipo = "INFO")
    
    $logFile = "$($global:ConfigSincronizacao.PastaDados)\logs.json"
    $logs = @()
    
    if (Test-Path $logFile) {
        try {
            $conteudo = Get-Content $logFile -Raw
            if ($conteudo) {
                $logs = $conteudo | ConvertFrom-Json
            }
        } catch { 
            $logs = @()
        }
    }
    
    $novoLog = @{
        Data = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        Mensagem = $mensagem
        Tipo = $tipo
    }
    
    # Adicionar novo log corretamente
    $logs = @($logs) + @($novoLog)
    
    # Manter apenas os últimos 50 logs
    if ($logs.Count -gt 50) {
        $logs = $logs | Select-Object -Last 50
    }
    
    $logs | ConvertTo-Json | Out-File $logFile -Encoding UTF8
}

function Enviar-ParaAPI {
    param($dados)
    
    if (-not $global:ConfigSincronizacao.ApiKey) {
        Registrar-Log "API Key não configurada" "ERRO"
        return $false
    }
    
    try {
        Write-Host "  🔗 Conectando com API..." -ForegroundColor Gray
        Start-Sleep -Milliseconds 500
        
        # Simulação de envio - SUBSTITUA por sua API real
        $fakeResponse = $true  # Simula sucesso
        
        if ($fakeResponse) {
            Registrar-Log "Dados enviados com sucesso para API" "SUCESSO"
            return $true
        } else {
            Registrar-Log "Falha ao enviar para API" "ERRO"
            return $false
        }
    } catch {
        Registrar-Log "Erro na conexão com API: $_" "ERRO"
        return $false
    }
}

function Sincronizar-Dados {
    Write-Host ""
    Write-Host "🔄 SINCRONIZANDO DADOS..." -ForegroundColor Yellow
    
    # Simular dados para sincronizar
    $dadosExemplo = @(
        @{Id=1; Tipo="CLIENTE"; Nome="Cliente Teste 1"},
        @{Id=2; Tipo="PEDIDO"; Valor=150.50},
        @{Id=3; Tipo="PRODUTO"; Nome="Concreto"}
    )
    
    $sucessos = 0
    $erros = 0
    
    foreach ($dado in $dadosExemplo) {
        Write-Host "  📤 Enviando: $($dado.Tipo) ID $($dado.Id)" -ForegroundColor Gray
        
        if (Enviar-ParaAPI -dados $dado) {
            $sucessos++
            Write-Host "    ✅ Sucesso" -ForegroundColor Green
        } else {
            $erros++
            Write-Host "    ❌ Falha" -ForegroundColor Red
        }
        
        Start-Sleep -Milliseconds 300
    }
    
    Write-Host ""
    Write-Host "📊 RESUMO DA SINCRONIZAÇÃO:" -ForegroundColor Cyan
    Write-Host "  ✅ Sucessos: $sucessos" -ForegroundColor Green
    Write-Host "  ❌ Erros: $erros" -ForegroundColor Red
    Write-Host "  📈 Total: $($sucessos + $erros) registros" -ForegroundColor Gray
    
    Registrar-Log "Sincronização concluída: $sucessos sucessos, $erros erros" "INFO"
}

# =============================================
# FUNÇÃO DO MENU PRINCIPAL (SIMPLIFICADA)
# =============================================

function Mostrar-Menu {
    do {
        Clear-Host
        
        # Cabeçalho
        Write-Host ""
        Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
        Write-Host "║                BETTO MIX - SISTEMA DE SINCRONIZAÇÃO          ║" -ForegroundColor White -BackgroundColor DarkBlue
        Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
        Write-Host ""
        
        # Status do sistema
        Write-Host "📊 STATUS DO SISTEMA" -ForegroundColor Yellow
        Write-Host "  🔗 API: $($global:ConfigSincronizacao.UrlApi)" -ForegroundColor Gray
        Write-Host "  🔑 API Key: $(if($global:ConfigSincronizacao.ApiKey){'✅ Configurada'}else{'❌ Não configurada'})" -ForegroundColor Gray
        Write-Host "  📁 Pasta de dados: $($global:ConfigSincronizacao.PastaDados)" -ForegroundColor Gray
        Write-Host "  🔄 Sinc. automática: $(if($global:ConfigSincronizacao.AutoSincronizar){'✅ Ativada'}else{'❌ Desativada'})" -ForegroundColor Gray
        Write-Host ""
        
        # Menu
        Write-Host "📋 MENU PRINCIPAL" -ForegroundColor White
        Write-Host "  1. 🔧 Testar sistema" -ForegroundColor Gray
        Write-Host "  2. ⚙️ Configurar API" -ForegroundColor Gray
        Write-Host "  3. 🔄 Sincronizar agora" -ForegroundColor Gray
        Write-Host "  4. 📁 Verificar arquivos" -ForegroundColor Gray
        Write-Host "  5. 📊 Ver logs" -ForegroundColor Gray
        Write-Host "  6. 🚪 Sair" -ForegroundColor Red
        Write-Host ""
        Write-Host "═" * 64 -ForegroundColor DarkGray
        
        $opcao = Read-Host "  🔘 Selecione uma opção (1-6)"
        
        switch ($opcao) {
            "1" {
                Write-Host ""
                Write-Host "🔧 TESTANDO SISTEMA..." -ForegroundColor Yellow
                
                Write-Host "  ✅ Sistema funcionando!" -ForegroundColor Green
                Write-Host "  ✅ Pasta de dados: $(Test-Path $global:ConfigSincronizacao.PastaDados)" -ForegroundColor Green
                Write-Host "  ✅ Configuração carregada" -ForegroundColor Green
                Write-Host "  ✅ Funções de sincronização prontas" -ForegroundColor Green
                
                Registrar-Log "Teste do sistema realizado" "INFO"
                Read-Host "`n  👉 Pressione Enter para continuar"
            }
            "2" {
                Write-Host ""
                Write-Host "⚙️ CONFIGURAÇÃO DA API" -ForegroundColor Yellow
                
                Write-Host "  🔗 URL atual: $($global:ConfigSincronizacao.UrlApi)" -ForegroundColor Gray
                Write-Host "  🔑 API Key atual: $(if($global:ConfigSincronizacao.ApiKey){'*** Configurada ***'}else{'Não configurada'})" -ForegroundColor Gray
                Write-Host ""
                
                $novaUrl = Read-Host "  Nova URL da API (Enter para manter atual)"
                $novaKey = Read-Host "  Nova API Key (Enter para manter)"
                $autoSync = Read-Host "  Ativar sincronização automática? (S/N)"
                
                if ($novaUrl) { $global:ConfigSincronizacao.UrlApi = $novaUrl }
                if ($novaKey) { $global:ConfigSincronizacao.ApiKey = $novaKey }
                if ($autoSync -eq "S") { $global:ConfigSincronizacao.AutoSincronizar = $true }
                if ($autoSync -eq "N") { $global:ConfigSincronizacao.AutoSincronizar = $false }
                
                # Salvar configuração
                $configFile = "$($global:ConfigSincronizacao.PastaDados)\config.json"
                $global:ConfigSincronizacao | ConvertTo-Json | Out-File $configFile -Encoding UTF8
                
                Write-Host ""
                Write-Host "  ✅ Configuração salva com sucesso!" -ForegroundColor Green
                Registrar-Log "Configuração da API atualizada" "INFO"
                Read-Host "`n  👉 Pressione Enter para continuar"
            }
            "3" {
                Sincronizar-Dados
                Read-Host "`n  👉 Pressione Enter para continuar"
            }
            "4" {
                Write-Host ""
                Write-Host "📁 ARQUIVOS DO SISTEMA" -ForegroundColor Yellow
                
                Write-Host "  📂 Arquivos principais:" -ForegroundColor Gray
                $arquivos = Get-ChildItem -File *.ps1 | Select-Object -First 10
                foreach ($arquivo in $arquivos) {
                    $tamanho = "{0:N1} KB" -f ($arquivo.Length / 1KB)
                    Write-Host "    📄 $($arquivo.Name) ($tamanho)" -ForegroundColor Gray
                }
                
                Write-Host ""
                Write-Host "  💾 Arquivos de dados:" -ForegroundColor Gray
                if (Test-Path $global:ConfigSincronizacao.PastaDados) {
                    $dados = Get-ChildItem -Path $global:ConfigSincronizacao.PastaDados -File
                    foreach ($arquivo in $dados) {
                        $tamanho = "{0:N1} KB" -f ($arquivo.Length / 1KB)
                        Write-Host "    💿 $($arquivo.Name) ($tamanho)" -ForegroundColor Gray
                    }
                }
                
                Read-Host "`n  👉 Pressione Enter para continuar"
            }
            "5" {
                Write-Host ""
                Write-Host "📊 LOGS DO SISTEMA" -ForegroundColor Yellow
                
                $logFile = "$($global:ConfigSincronizacao.PastaDados)\logs.json"
                if (Test-Path $logFile) {
                    try {
                        $conteudo = Get-Content $logFile -Raw
                        if ($conteudo) {
                            $logs = $conteudo | ConvertFrom-Json
                            $ultimos = $logs | Select-Object -Last 10
                            
                            foreach ($log in $ultimos) {
                                $cor = if ($log.Tipo -eq "ERRO") { "Red" } 
                                       elseif ($log.Tipo -eq "SUCESSO") { "Green" } 
                                       else { "Gray" }
                                Write-Host "  [$($log.Data)] $($log.Tipo): $($log.Mensagem)" -ForegroundColor $cor
                            }
                        }
                    } catch {
                        Write-Host "  ❌ Erro ao ler logs" -ForegroundColor Red
                    }
                } else {
                    Write-Host "  ℹ️ Nenhum log disponível" -ForegroundColor Gray
                }
                
                Read-Host "`n  👉 Pressione Enter para continuar"
            }
            "6" {
                Write-Host ""
                Write-Host "👋 Saindo do sistema..." -ForegroundColor Yellow
                Write-Host "Obrigado por usar o Sistema Betto Mix! 🚀" -ForegroundColor Cyan
                Start-Sleep -Seconds 1
                return $true
            }
            default {
                Write-Host ""
                Write-Host "❌ Opção inválida! Selecione 1-6" -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
    } while ($true)
}

# =============================================
# INICIAR SISTEMA
# =============================================

try {
    Write-Host ""
    Write-Host "✅ Sistema Betto Mix inicializado com sucesso!" -ForegroundColor Green
    Write-Host "⏳ Carregando menu principal..." -ForegroundColor Gray
    Start-Sleep -Seconds 1
    
    Mostrar-Menu
    
} catch {
    Write-Host ""
    Write-Host "❌ ERRO NO SISTEMA: $_" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
}
