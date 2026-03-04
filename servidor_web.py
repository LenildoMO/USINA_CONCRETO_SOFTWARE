import http.server
import socketserver
import webbrowser
import threading
import json
from datetime import datetime
import os
import sys

PORT = 5000
HOST = '0.0.0.0'

print("\n" + "="*70)
print("           BETTO MIX - SERVIDOR WEB v1.0")
print("="*70)
print(f"Servidor iniciando em: http://localhost:{PORT}")
print("Abrindo navegador automaticamente...")
print("="*70)

# HTML principal do sistema
HTML_PRINCIPAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Betto Mix - Sistema de Gestão</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1a2980, #26d0ce);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #1a2980, #26d0ce);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .logo h1 {
            font-size: 2.8rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        
        .status-bar {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }
        
        .status-item {
            background: rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 50px;
            font-weight: 600;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 300px 1fr;
            min-height: 600px;
        }
        
        .sidebar {
            background: #f8f9fa;
            padding: 30px;
            border-right: 1px solid #e0e0e0;
        }
        
        .menu {
            list-style: none;
        }
        
        .menu-item {
            padding: 15px 20px;
            margin: 10px 0;
            background: white;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            border-left: 5px solid #26d0ce;
            font-weight: 600;
            color: #1a2980;
        }
        
        .menu-item:hover {
            background: #26d0ce;
            color: white;
            transform: translateX(5px);
        }
        
        .menu-item.active {
            background: #1a2980;
            color: white;
        }
        
        .menu-item i {
            margin-right: 10px;
        }
        
        .content {
            padding: 30px;
        }
        
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-top: 20px;
        }
        
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s ease;
            border-top: 5px solid #26d0ce;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #1a2980;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .card p {
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .btn {
            background: linear-gradient(135deg, #1a2980, #26d0ce);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin-top: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(26, 41, 128, 0.3);
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }
        
        .data-table th {
            background: #1a2980;
            color: white;
            padding: 15px;
            text-align: left;
        }
        
        .data-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .data-table tr:hover {
            background: #f5f9ff;
        }
        
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .badge-success {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .badge-danger {
            background: #f8d7da;
            color: #721c24;
        }
        
        footer {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            border-top: 1px solid #e0e0e0;
            margin-top: 30px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 30px 0;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }
        
        .stat-card h4 {
            color: #1a2980;
            font-size: 2.5rem;
            margin: 10px 0;
        }
        
        .stat-card p {
            color: #666;
            font-weight: 600;
        }
        
        .icon {
            font-size: 2rem;
            color: #26d0ce;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .stats {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <i class="fas fa-industry fa-3x"></i>
                <div>
                    <h1>BETTO MIX</h1>
                    <div class="subtitle">Sistema de Gestão de Usina de Concreto</div>
                </div>
            </div>
            
            <div class="status-bar">
                <div class="status-item">
                    <i class="fas fa-signal"></i> Online
                </div>
                <div class="status-item">
                    <i class="fas fa-database"></i> Banco de Dados Ativo
                </div>
                <div class="status-item">
                    <i class="fas fa-clock"></i> <span id="current-time">--:--:--</span>
                </div>
            </div>
        </header>
        
        <div class="main-content">
            <div class="sidebar">
                <ul class="menu">
                    <li class="menu-item active" onclick="showSection('dashboard')">
                        <i class="fas fa-tachometer-alt"></i> Dashboard
                    </li>
                    <li class="menu-item" onclick="showSection('clientes')">
                        <i class="fas fa-users"></i> Clientes
                    </li>
                    <li class="menu-item" onclick="showSection('pedidos')">
                        <i class="fas fa-clipboard-list"></i> Pedidos
                    </li>
                    <li class="menu-item" onclick="showSection('estoque')">
                        <i class="fas fa-boxes"></i> Estoque
                    </li>
                    <li class="menu-item" onclick="showSection('relatorios')">
                        <i class="fas fa-chart-bar"></i> Relatórios
                    </li>
                    <li class="menu-item" onclick="showSection('config')">
                        <i class="fas fa-cog"></i> Configurações
                    </li>
                </ul>
            </div>
            
            <div class="content">
                <!-- DASHBOARD -->
                <div id="dashboard" class="section active">
                    <h2><i class="fas fa-tachometer-alt"></i> Dashboard</h2>
                    <p>Visão geral do sistema Betto Mix</p>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <div class="icon"><i class="fas fa-users"></i></div>
                            <h4 id="total-clientes">25</h4>
                            <p>Clientes Ativos</p>
                        </div>
                        <div class="stat-card">
                            <div class="icon"><i class="fas fa-clipboard-check"></i></div>
                            <h4 id="total-pedidos">142</h4>
                            <p>Pedidos Hoje</p>
                        </div>
                        <div class="stat-card">
                            <div class="icon"><i class="fas fa-cubes"></i></div>
                            <h4 id="total-estoque">1,250</h4>
                            <p>m³ em Estoque</p>
                        </div>
                        <div class="stat-card">
                            <div class="icon"><i class="fas fa-truck-loading"></i></div>
                            <h4 id="entregas-hoje">18</h4>
                            <p>Entregas Hoje</p>
                        </div>
                    </div>
                    
                    <h3 style="margin-top: 30px;">Atividades Recentes</h3>
                    <div class="card-grid">
                        <div class="card">
                            <h3><i class="fas fa-check-circle text-success"></i> Pedido Concluído</h3>
                            <p>Pedido #PED-2024-001 para Construtora Alpha foi entregue com sucesso.</p>
                            <small>Há 15 minutos</small>
                        </div>
                        <div class="card">
                            <h3><i class="fas fa-truck text-primary"></i> Em Transporte</h3>
                            <p>Entrega para Engenharia Beta saiu para entrega. Previsão: 30 minutos.</p>
                            <small>Há 45 minutos</small>
                        </div>
                        <div class="card">
                            <h3><i class="fas fa-industry text-warning"></i> Em Produção</h3>
                            <p>Produção de 25m³ de concreto 30MPa para Construções Gama iniciada.</p>
                            <small>Há 1 hora</small>
                        </div>
                    </div>
                </div>
                
                <!-- CLIENTES -->
                <div id="clientes" class="section" style="display: none;">
                    <h2><i class="fas fa-users"></i> Gerenciamento de Clientes</h2>
                    <p>Cadastro e consulta de clientes</p>
                    
                    <div style="display: flex; gap: 15px; margin: 20px 0;">
                        <button class="btn" onclick="addCliente()">
                            <i class="fas fa-plus"></i> Novo Cliente
                        </button>
                        <button class="btn" style="background: #6c757d;">
                            <i class="fas fa-download"></i> Exportar
                        </button>
                    </div>
                    
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Código</th>
                                <th>Cliente</th>
                                <th>Telefone</th>
                                <th>Desde</th>
                                <th>Status</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody id="clientes-table">
                            <!-- Dados serão preenchidos via JavaScript -->
                        </tbody>
                    </table>
                </div>
                
                <!-- PEDIDOS -->
                <div id="pedidos" class="section" style="display: none;">
                    <h2><i class="fas fa-clipboard-list"></i> Gerenciamento de Pedidos</h2>
                    <p>Controle de pedidos e produções</p>
                    
                    <div class="card-grid">
                        <div class="card">
                            <h3><i class="fas fa-clock text-warning"></i> Pendentes</h3>
                            <h4>8 Pedidos</h4>
                            <p>Aguardando processamento</p>
                            <button class="btn" onclick="showSection('pedidos')">Ver Detalhes</button>
                        </div>
                        <div class="card">
                            <h3><i class="fas fa-industry text-primary"></i> Em Produção</h3>
                            <h4>5 Pedidos</h4>
                            <p>Em processo de fabricação</p>
                            <button class="btn" onclick="showSection('pedidos')">Acompanhar</button>
                        </div>
                        <div class="card">
                            <h3><i class="fas fa-truck text-info"></i> Para Entrega</h3>
                            <h4>3 Pedidos</h4>
                            <p>Prontos para despacho</p>
                            <button class="btn" onclick="showSection('pedidos')">Agendar</button>
                        </div>
                        <div class="card">
                            <h3><i class="fas fa-check-circle text-success"></i> Concluídos</h3>
                            <h4>126 Pedidos</h4>
                            <p>Entregues este mês</p>
                            <button class="btn" onclick="showSection('pedidos')">Ver Histórico</button>
                        </div>
                    </div>
                    
                    <h3 style="margin-top: 30px;">Pedidos Recentes</h3>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Nº Pedido</th>
                                <th>Cliente</th>
                                <th>Produto</th>
                                <th>Quantidade</th>
                                <th>Status</th>
                                <th>Previsão</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>PED-2024-001</td>
                                <td>Construtora Alpha</td>
                                <td>Concreto 25MPa</td>
                                <td>15 m³</td>
                                <td><span class="badge badge-success">Entregue</span></td>
                                <td>15/01/2024</td>
                            </tr>
                            <tr>
                                <td>PED-2024-002</td>
                                <td>Engenharia Beta</td>
                                <td>Concreto 30MPa</td>
                                <td>8 m³</td>
                                <td><span class="badge badge-warning">Produção</span></td>
                                <td>16/01/2024</td>
                            </tr>
                            <tr>
                                <td>PED-2024-003</td>
                                <td>Construções Gama</td>
                                <td>Concreto 20MPa</td>
                                <td>25 m³</td>
                                <td><span class="badge badge-danger">Pendente</span></td>
                                <td>17/01/2024</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- ESTOQUE -->
                <div id="estoque" class="section" style="display: none;">
                    <h2><i class="fas fa-boxes"></i> Controle de Estoque</h2>
                    <p>Monitoramento de materiais e produtos</p>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <div class="icon"><i class="fas fa-cube"></i></div>
                            <h4>1,250</h4>
                            <p>m³ Concreto Pronto</p>
                        </div>
                        <div class="stat-card">
                            <div class="icon"><i class="fas fa-weight"></i></div>
                            <h4>850</h4>
                            <p>Sacos de Cimento</p>
                        </div>
                        <div class="stat-card">
                            <div class="icon"><i class="fas fa-tint"></i></div>
                            <h4>25,000</h4>
                            <p>Litros de Água</p>
                        </div>
                        <div class="stat-card">
                            <div class="icon"><i class="fas fa-mountain"></i></div>
                            <h4>500</h4>
                            <p>m³ Areia/ Brita</p>
                        </div>
                    </div>
                    
                    <h3>Níveis de Estoque</h3>
                    <div style="background: white; padding: 20px; border-radius: 10px; margin-top: 20px;">
                        <div style="margin: 15px 0;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>Concreto 20MPa</span>
                                <span>450/500 m³</span>
                            </div>
                            <div style="height: 20px; background: #e0e0e0; border-radius: 10px; margin-top: 5px;">
                                <div style="height: 100%; width: 90%; background: #28a745; border-radius: 10px;"></div>
                            </div>
                        </div>
                        
                        <div style="margin: 15px 0;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>Concreto 25MPa</span>
                                <span>380/500 m³</span>
                            </div>
                            <div style="height: 20px; background: #e0e0e0; border-radius: 10px; margin-top: 5px;">
                                <div style="height: 100%; width: 76%; background: #17a2b8; border-radius: 10px;"></div>
                            </div>
                        </div>
                        
                        <div style="margin: 15px 0;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>Concreto 30MPa</span>
                                <span>420/500 m³</span>
                            </div>
                            <div style="height: 20px; background: #e0e0e0; border-radius: 10px; margin-top: 5px;">
                                <div style="height: 100%; width: 84%; background: #007bff; border-radius: 10px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- RELATÓRIOS -->
                <div id="relatorios" class="section" style="display: none;">
                    <h2><i class="fas fa-chart-bar"></i> Relatórios</h2>
                    <p>Análises e estatísticas do sistema</p>
                    
                    <div class="card-grid">
                        <div class="card">
                            <h3>Relatório Diário</h3>
                            <p>Produção e vendas do dia atual</p>
                            <button class="btn" onclick="gerarRelatorio('diario')">
                                <i class="fas fa-file-pdf"></i> Gerar PDF
                            </button>
                        </div>
                        <div class="card">
                            <h3>Relatório Mensal</h3>
                            <p>Análise completa do mês</p>
                            <button class="btn" onclick="gerarRelatorio('mensal')">
                                <i class="fas fa-chart-line"></i> Visualizar
                            </button>
                        </div>
                        <div class="card">
                            <h3>Relatório de Clientes</h3>
                            <p>Histórico e faturamento por cliente</p>
                            <button class="btn" onclick="gerarRelatorio('clientes')">
                                <i class="fas fa-users"></i> Gerar
                            </button>
                        </div>
                        <div class="card">
                            <h3>Relatório Financeiro</h3>
                            <p>Fluxo de caixa e receitas</p>
                            <button class="btn" onclick="gerarRelatorio('financeiro')">
                                <i class="fas fa-money-bill-wave"></i> Visualizar
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- CONFIGURAÇÕES -->
                <div id="config" class="section" style="display: none;">
                    <h2><i class="fas fa-cog"></i> Configurações do Sistema</h2>
                    <p>Ajustes e preferências</p>
                    
                    <div style="background: white; padding: 25px; border-radius: 15px; margin-top: 20px;">
                        <h3 style="margin-bottom: 20px;">Configurações Gerais</h3>
                        
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 600;">Nome da Empresa</label>
                            <input type="text" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" value="Usina de Concreto Betto Mix">
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 600;">Porta do Servidor</label>
                            <input type="number" style="width: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" value="5000">
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 600;">Tema do Sistema</label>
                            <select style="padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                                <option>Claro (Padrão)</option>
                                <option>Escuro</option>
                                <option>Azul</option>
                            </select>
                        </div>
                        
                        <button class="btn" style="width: 100%;">
                            <i class="fas fa-save"></i> Salvar Configurações
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Sistema Betto Mix v1.0 &copy; 2024 - Desenvolvido para Usina de Concreto Betto Mix</p>
            <p style="margin-top: 5px; font-size: 0.9rem;">
                <i class="fas fa-phone"></i> (11) 9999-8888 | 
                <i class="fas fa-envelope"></i> contato@bettomix.com.br
            </p>
        </footer>
    </div>

    <script>
        // Atualizar hora atual
        function updateTime() {
            const now = new Date();
            const timeString = now.toLocaleTimeString('pt-BR');
            document.getElementById('current-time').textContent = timeString;
        }
        
        setInterval(updateTime, 1000);
        updateTime();
        
        // Navegação entre seções
        function showSection(sectionId) {
            // Esconder todas as seções
            document.querySelectorAll('.section').forEach(section => {
                section.style.display = 'none';
            });
            
            // Remover classe active de todos os itens do menu
            document.querySelectorAll('.menu-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Mostrar seção selecionada
            document.getElementById(sectionId).style.display = 'block';
            
            // Adicionar classe active ao item do menu correspondente
            document.querySelector(`.menu-item[onclick="showSection('${sectionId}')"]`).classList.add('active');
        }
        
        // Carregar dados de clientes
        function loadClientes() {
            const clientes = [
                { codigo: 'CLI-001', nome: 'Construtora Alpha LTDA', telefone: '(11) 3333-4444', desde: '2023-01-15', status: 'Ativo' },
                { codigo: 'CLI-002', nome: 'Engenharia Beta S/A', telefone: '(11) 5555-6666', desde: '2023-03-20', status: 'Ativo' },
                { codigo: 'CLI-003', nome: 'Construções Gama', telefone: '(11) 7777-8888', desde: '2023-05-10', status: 'Inativo' },
                { codigo: 'CLI-004', nome: 'Delta Construções', telefone: '(11) 2222-3333', desde: '2023-07-15', status: 'Ativo' },
                { codigo: 'CLI-005', nome: 'Omega Engenharia', telefone: '(11) 8888-9999', desde: '2023-09-01', status: 'Ativo' }
            ];
            
            const tbody = document.getElementById('clientes-table');
            tbody.innerHTML = '';
            
            clientes.forEach(cliente => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${cliente.codigo}</td>
                    <td>${cliente.nome}</td>
                    <td>${cliente.telefone}</td>
                    <td>${cliente.desde}</td>
                    <td><span class="badge ${cliente.status === 'Ativo' ? 'badge-success' : 'badge-danger'}">${cliente.status}</span></td>
                    <td>
                        <button class="btn" style="padding: 5px 10px; font-size: 0.9rem; margin-right: 5px;">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn" style="padding: 5px 10px; font-size: 0.9rem; background: #dc3545;">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
        
        // Adicionar novo cliente
        function addCliente() {
            const nome = prompt('Nome do cliente:');
            if (nome) {
                alert(`Cliente "${nome}" adicionado com sucesso!`);
                loadClientes();
            }
        }
        
        // Gerar relatório
        function gerarRelatorio(tipo) {
            alert(`Relatório ${tipo} gerado com sucesso!`);
        }
        
        // Atualizar estatísticas
        function updateStats() {
            // Simular atualização de dados
            document.getElementById('total-clientes').textContent = Math.floor(Math.random() * 10) + 25;
            document.getElementById('total-pedidos').textContent = Math.floor(Math.random() * 20) + 140;
            document.getElementById('total-estoque').textContent = Math.floor(Math.random() * 100) + 1200;
            document.getElementById('entregas-hoje').textContent = Math.floor(Math.random() * 5) + 18;
        }
        
        // Inicializar
        document.addEventListener('DOMContentLoaded', function() {
            loadClientes();
            updateStats();
            
            // Atualizar estatísticas a cada 30 segundos
            setInterval(updateStats, 30000);
        });
    </script>
</body>
</html>
"""

# Handler personalizado
class BettoMixHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PRINCIPAL.encode('utf-8'))
        
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "online",
                "sistema": "Betto Mix Web",
                "timestamp": datetime.now().isoformat(),
                "clientes": 25,
                "pedidos_hoje": 142
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif self.path == '/api/clientes':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            clientes = [
                {"id": 1, "nome": "Construtora Alpha", "status": "ativo"},
                {"id": 2, "nome": "Engenharia Beta", "status": "ativo"},
                {"id": 3, "nome": "Construções Gama", "status": "inativo"}
            ]
            self.wfile.write(json.dumps(clientes).encode('utf-8'))
        
        else:
            super().do_GET()
    
    def log_message(self, format, *args):
        # Silenciar logs
        pass

# Função para abrir navegador
def open_browser():
    import time
    time.sleep(2)  # Aguardar servidor iniciar
    webbrowser.open(f'http://localhost:{PORT}')
    print("✅ Navegador aberto automaticamente!")

# Iniciar servidor
try:
    # Criar handler
    handler = BettoMixHandler
    
    # Configurar servidor
    with socketserver.TCPServer((HOST, PORT), handler) as httpd:
        print(f"✅ Servidor web iniciado em http://{HOST}:{PORT}")
        print("📁 Pressione Ctrl+C para encerrar")
        
        # Abrir navegador em thread separada
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Manter servidor rodando
        httpd.serve_forever()

except OSError as e:
    print(f"❌ Erro: {e}")
    print(f"💡 A porta {PORT} pode estar em uso.")
    print("   Tente: netstat -ano | findstr :5000")
    input("Pressione Enter para sair...")
except KeyboardInterrupt:
    print("\n\n👋 Servidor encerrado pelo usuário.")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    input("Pressione Enter para sair...")
