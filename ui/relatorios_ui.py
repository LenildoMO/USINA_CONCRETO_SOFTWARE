from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QGroupBox, QMessageBox,
                             QHeaderView, QTabWidget, QTextEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
import sqlite3
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd

class TelaRelatorios(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.carregar_dados_iniciais()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("RELATÓRIOS E ESTATÍSTICAS")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #2E7D32; padding: 10px;")
        layout.addWidget(titulo)
        
        # Abas
        self.tabs = QTabWidget()
        
        # Aba 1: Consumo Diário
        tab_consumo = QWidget()
        self.setup_tab_consumo(tab_consumo)
        self.tabs.addTab(tab_consumo, "📊 Consumo Diário")
        
        # Aba 2: Relatórios Semanais
        tab_semanal = QWidget()
        self.setup_tab_semanal(tab_semanal)
        self.tabs.addTab(tab_semanal, "📈 Relatório Semanal")
        
        # Aba 3: Relatórios Mensais
        tab_mensal = QWidget()
        self.setup_tab_mensal(tab_mensal)
        self.tabs.addTab(tab_mensal, "📅 Relatório Mensal")
        
        # Aba 4: Gastos da Usina
        tab_gastos = QWidget()
        self.setup_tab_gastos(tab_gastos)
        self.tabs.addTab(tab_gastos, "💰 Gastos da Usina")
        
        # Aba 5: Gráficos
        tab_graficos = QWidget()
        self.setup_tab_graficos(tab_graficos)
        self.tabs.addTab(tab_graficos, "📈 Gráficos")
        
        layout.addWidget(self.tabs)
    
    def setup_tab_consumo(self, parent):
        layout = QVBoxLayout(parent)
        
        # Controles
        controle_layout = QHBoxLayout()
        
        self.data_consumo = QDateEdit()
        self.data_consumo.setDate(QDate.currentDate())
        self.data_consumo.setCalendarPopup(True)
        
        btn_gerar = QPushButton("🔍 Gerar Relatório")
        btn_gerar.clicked.connect(self.gerar_relatorio_consumo)
        
        btn_salvar = QPushButton("💾 Salvar como PDF")
        btn_salvar.clicked.connect(self.salvar_relatorio_pdf)
        
        controle_layout.addWidget(QLabel("Data:"))
        controle_layout.addWidget(self.data_consumo)
        controle_layout.addWidget(btn_gerar)
        controle_layout.addWidget(btn_salvar)
        controle_layout.addStretch()
        
        layout.addLayout(controle_layout)
        
        # Tabela de consumo
        self.tabela_consumo = QTableWidget()
        self.tabela_consumo.setColumnCount(6)
        self.tabela_consumo.setHorizontalHeaderLabels([
            "Material", "Estoque Inicial", "Entradas", "Saídas", 
            "Consumo do Dia", "Estoque Final"
        ])
        self.tabela_consumo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_consumo)
        
        # Resumo
        self.label_resumo_consumo = QLabel("Selecione uma data e clique em Gerar Relatório")
        self.label_resumo_consumo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_resumo_consumo)
    
    def setup_tab_semanal(self, parent):
        layout = QVBoxLayout(parent)
        
        # Controles
        controle_layout = QHBoxLayout()
        
        self.semana_selecionada = QComboBox()
        
        # Gerar semanas do ano
        ano_atual = datetime.now().year
        semanas = []
        for semana in range(1, 53):
            semanas.append(f"Semana {semana} - {ano_atual}")
        
        self.semana_selecionada.addItems(semanas)
        self.semana_selecionada.setCurrentIndex(datetime.now().isocalendar()[1] - 1)
        
        btn_gerar_semanal = QPushButton("🔍 Gerar Relatório Semanal")
        btn_gerar_semanal.clicked.connect(self.gerar_relatorio_semanal)
        
        controle_layout.addWidget(QLabel("Semana:"))
        controle_layout.addWidget(self.semana_selecionada)
        controle_layout.addWidget(btn_gerar_semanal)
        controle_layout.addStretch()
        
        layout.addLayout(controle_layout)
        
        # Tabela semanal
        self.tabela_semanal = QTableWidget()
        self.tabela_semanal.setColumnCount(4)
        self.tabela_semanal.setHorizontalHeaderLabels([
            "Dia", "Produção (m³)", "Clientes Atendidos", "Faturamento"
        ])
        self.tabela_semanal.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_semanal)
        
        # Resumo semanal
        self.label_resumo_semanal = QLabel("Selecione uma semana para gerar o relatório")
        self.label_resumo_semanal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_resumo_semanal)
    
    def setup_tab_mensal(self, parent):
        layout = QVBoxLayout(parent)
        
        # Controles
        controle_layout = QHBoxLayout()
        
        self.mes_selecionado = QComboBox()
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.mes_selecionado.addItems(meses)
        self.mes_selecionado.setCurrentIndex(datetime.now().month - 1)
        
        self.ano_selecionado = QComboBox()
        anos = [str(year) for year in range(2020, datetime.now().year + 2)]
        self.ano_selecionado.addItems(anos)
        self.ano_selecionado.setCurrentText(str(datetime.now().year))
        
        btn_gerar_mensal = QPushButton("🔍 Gerar Relatório Mensal")
        btn_gerar_mensal.clicked.connect(self.gerar_relatorio_mensal)
        
        controle_layout.addWidget(QLabel("Mês:"))
        controle_layout.addWidget(self.mes_selecionado)
        controle_layout.addWidget(QLabel("Ano:"))
        controle_layout.addWidget(self.ano_selecionado)
        controle_layout.addWidget(btn_gerar_mensal)
        controle_layout.addStretch()
        
        layout.addLayout(controle_layout)
        
        # Tabela mensal
        self.tabela_mensal = QTableWidget()
        self.tabela_mensal.setColumnCount(5)
        self.tabela_mensal.setHorizontalHeaderLabels([
            "Material", "Consumo Total", "Custo Total", "Média Diária", "% do Total"
        ])
        self.tabela_mensal.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_mensal)
        
        # Resumo mensal
        self.label_resumo_mensal = QLabel("Selecione mês e ano para gerar o relatório")
        self.label_resumo_mensal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_resumo_mensal)
    
    def setup_tab_gastos(self, parent):
        layout = QVBoxLayout(parent)
        
        # Controles
        controle_layout = QHBoxLayout()
        
        self.periodo_gastos = QComboBox()
        self.periodo_gastos.addItems(["Últimos 7 dias", "Últimos 30 dias", "Este mês", "Mês anterior", "Personalizado"])
        
        btn_gerar_gastos = QPushButton("🔍 Gerar Relatório de Gastos")
        btn_gerar_gastos.clicked.connect(self.gerar_relatorio_gastos)
        
        controle_layout.addWidget(QLabel("Período:"))
        controle_layout.addWidget(self.periodo_gastos)
        controle_layout.addWidget(btn_gerar_gastos)
        controle_layout.addStretch()
        
        layout.addLayout(controle_layout)
        
        # Tabela de gastos
        self.tabela_gastos = QTableWidget()
        self.tabela_gastos.setColumnCount(4)
        self.tabela_gastos.setHorizontalHeaderLabels([
            "Fornecedor", "Material", "Quantidade", "Valor Total"
        ])
        self.tabela_gastos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_gastos)
        
        # Total de gastos
        self.label_total_gastos = QLabel("Total de Gastos: R$ 0,00")
        self.label_total_gastos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_total_gastos.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.label_total_gastos)
    
    def setup_tab_graficos(self, parent):
        layout = QVBoxLayout(parent)
        
        # Controles
        controle_layout = QHBoxLayout()
        
        self.tipo_grafico = QComboBox()
        self.tipo_grafico.addItems([
            "Consumo de Materiais",
            "Produção Mensal",
            "Gastos por Fornecedor",
            "Clientes Mais Frequentes"
        ])
        
        btn_gerar_grafico = QPushButton("📊 Gerar Gráfico")
        btn_gerar_grafico.clicked.connect(self.gerar_grafico)
        
        controle_layout.addWidget(QLabel("Tipo de Gráfico:"))
        controle_layout.addWidget(self.tipo_grafico)
        controle_layout.addWidget(btn_gerar_grafico)
        controle_layout.addStretch()
        
        layout.addLayout(controle_layout)
        
        # Área do gráfico
        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def carregar_dados_iniciais(self):
        # Gerar relatório do dia atual
        self.gerar_relatorio_consumo()
    
    def gerar_relatorio_consumo(self):
        data = self.data_consumo.date().toString("yyyy-MM-dd")
        
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Buscar materiais
            cursor.execute("SELECT material FROM estoque ORDER BY material")
            materiais = [row[0] for row in cursor.fetchall()]
            
            self.tabela_consumo.setRowCount(len(materiais))
            
            total_consumo = 0
            
            for i, material in enumerate(materiais):
                # Estoque inicial (do dia anterior)
                cursor.execute('''
                    SELECT quantidade FROM estoque 
                    WHERE material = ? 
                    AND date(ultima_atualizacao) < ?
                    ORDER BY ultima_atualizacao DESC LIMIT 1
                ''', (material, data))
                
                estoque_inicial = cursor.fetchone()
                estoque_inicial = estoque_inicial[0] if estoque_inicial else 0
                
                # Entradas do dia (de notas fiscais)
                cursor.execute('''
                    SELECT COALESCE(SUM(quantidade), 0) 
                    FROM notas_fornecedores 
                    WHERE tipo_material = ? 
                    AND date(data_entrada) = ?
                ''', (material, data))
                
                entradas = cursor.fetchone()[0]
                
                # Saídas do dia (de pesagens)
                cursor.execute('''
                    SELECT COALESCE(SUM(
                        CASE 
                            WHEN material = 'Cimento' THEN cimento_kg
                            WHEN material = 'Brita 0' THEN brita_0_kg
                            WHEN material = 'Brita 1' THEN brita_1_kg
                            WHEN material = 'Areia' THEN areia_kg
                            WHEN material = 'Pó de Brita' THEN po_brita_kg
                            WHEN material = 'Aditivo' THEN aditivo_kg
                            WHEN material = 'Água' THEN agua_litros
                            ELSE 0
                        END
                    ), 0)
                    FROM pesagens_detalhadas 
                    WHERE date(data) = ?
                ''', (data,))
                
                saidas = cursor.fetchone()[0]
                
                consumo_dia = saidas
                estoque_final = estoque_inicial + entradas - saidas
                total_consumo += consumo_dia
                
                # Preencher tabela
                self.tabela_consumo.setItem(i, 0, QTableWidgetItem(material))
                self.tabela_consumo.setItem(i, 1, QTableWidgetItem(f"{estoque_inicial:.2f}"))
                self.tabela_consumo.setItem(i, 2, QTableWidgetItem(f"{entradas:.2f}"))
                self.tabela_consumo.setItem(i, 3, QTableWidgetItem(f"{saidas:.2f}"))
                self.tabela_consumo.setItem(i, 4, QTableWidgetItem(f"{consumo_dia:.2f}"))
                self.tabela_consumo.setItem(i, 5, QTableWidgetItem(f"{estoque_final:.2f}"))
            
            conn.close()
            
            self.label_resumo_consumo.setText(
                f"Consumo total do dia {data}: {total_consumo:.2f} unidades"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório: {e}")
    
    def gerar_relatorio_semanal(self):
        semana_num = self.semana_selecionada.currentIndex() + 1
        ano_atual = datetime.now().year
        
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Dias da semana
            dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            self.tabela_semanal.setRowCount(7)
            
            total_producao = 0
            total_faturamento = 0
            
            for i, dia in enumerate(dias_semana):
                # Produção do dia
                cursor.execute('''
                    SELECT COALESCE(SUM(quantidade_m3), 0), COUNT(DISTINCT cliente_id)
                    FROM pesagens_detalhadas 
                    WHERE strftime('%W', data) = ? 
                    AND strftime('%Y', data) = ?
                    AND strftime('%w', data) = ?
                ''', (f"{semana_num:02d}", str(ano_atual), str(i+1)))
                
                resultado = cursor.fetchone()
                producao = resultado[0] if resultado else 0
                clientes = resultado[1] if resultado else 0
                
                # Faturamento estimado (simulado)
                faturamento = producao * 300  # R$ 300/m³ (valor exemplo)
                
                total_producao += producao
                total_faturamento += faturamento
                
                self.tabela_semanal.setItem(i, 0, QTableWidgetItem(dia))
                self.tabela_semanal.setItem(i, 1, QTableWidgetItem(f"{producao:.2f} m³"))
                self.tabela_semanal.setItem(i, 2, QTableWidgetItem(str(clientes)))
                self.tabela_semanal.setItem(i, 3, QTableWidgetItem(f"R$ {faturamento:.2f}"))
            
            conn.close()
            
            self.label_resumo_semanal.setText(
                f"Semana {semana_num}: Produção total: {total_producao:.2f} m³ | "
                f"Faturamento estimado: R$ {total_faturamento:.2f}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório semanal: {e}")
    
    def gerar_relatorio_mensal(self):
        mes = self.mes_selecionado.currentIndex() + 1
        ano = self.ano_selecionado.currentText()
        
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Buscar consumo de materiais no mês
            query = '''
                SELECT 
                    tipo_material as material,
                    COALESCE(SUM(quantidade), 0) as consumo_total,
                    COALESCE(SUM(quantidade * valor_unitario), 0) as custo_total
                FROM notas_fornecedores 
                WHERE strftime('%m', data_entrada) = ? 
                AND strftime('%Y', data_entrada) = ?
                GROUP BY tipo_material
                ORDER BY consumo_total DESC
            '''
            
            cursor.execute(query, (f"{mes:02d}", ano))
            resultados = cursor.fetchall()
            
            self.tabela_mensal.setRowCount(len(resultados))
            
            total_custo = 0
            total_consumo = 0
            
            for i, resultado in enumerate(resultados):
                material = resultado[0]
                consumo = resultado[1] or 0
                custo = resultado[2] or 0
                
                total_custo += custo
                total_consumo += consumo
                
                self.tabela_mensal.setItem(i, 0, QTableWidgetItem(material))
                self.tabela_mensal.setItem(i, 1, QTableWidgetItem(f"{consumo:.2f}"))
                self.tabela_mensal.setItem(i, 2, QTableWidgetItem(f"R$ {custo:.2f}"))
                self.tabela_mensal.setItem(i, 3, QTableWidgetItem(f"{consumo/30:.2f}/dia"))
                self.tabela_mensal.setItem(i, 4, QTableWidgetItem(
                    f"{(consumo/total_consumo*100 if total_consumo > 0 else 0):.1f}%"
                ))
            
            conn.close()
            
            self.label_resumo_mensal.setText(
                f"Mês {mes}/{ano}: Custo total: R$ {total_custo:.2f} | "
                f"Consumo total: {total_consumo:.2f} unidades"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório mensal: {e}")
    
    def gerar_relatorio_gastos(self):
        periodo = self.periodo_gastos.currentText()
        
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            if periodo == "Últimos 7 dias":
                data_inicio = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                data_fim = datetime.now().strftime("%Y-%m-%d")
            elif periodo == "Últimos 30 dias":
                data_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                data_fim = datetime.now().strftime("%Y-%m-%d")
            elif periodo == "Este mês":
                data_inicio = datetime.now().replace(day=1).strftime("%Y-%m-%d")
                data_fim = datetime.now().strftime("%Y-%m-%d")
            elif periodo == "Mês anterior":
                primeiro_dia_mes_anterior = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
                ultimo_dia_mes_anterior = datetime.now().replace(day=1) - timedelta(days=1)
                data_inicio = primeiro_dia_mes_anterior.strftime("%Y-%m-%d")
                data_fim = ultimo_dia_mes_anterior.strftime("%Y-%m-%d")
            else:
                # Personalizado - usar últimos 30 dias como padrão
                data_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                data_fim = datetime.now().strftime("%Y-%m-%d")
            
            query = '''
                SELECT fornecedor, tipo_material, 
                       SUM(quantidade), SUM(valor_total)
                FROM notas_fornecedores 
                WHERE date(data_entrada) BETWEEN ? AND ?
                GROUP BY fornecedor, tipo_material
                ORDER BY SUM(valor_total) DESC
            '''
            
            cursor.execute(query, (data_inicio, data_fim))
            gastos = cursor.fetchall()
            
            self.tabela_gastos.setRowCount(len(gastos))
            
            total_gastos = 0
            
            for i, gasto in enumerate(gastos):
                fornecedor = gasto[0]
                material = gasto[1]
                quantidade = gasto[2] or 0
                valor = gasto[3] or 0
                
                total_gastos += valor
                
                self.tabela_gastos.setItem(i, 0, QTableWidgetItem(fornecedor))
                self.tabela_gastos.setItem(i, 1, QTableWidgetItem(material))
                self.tabela_gastos.setItem(i, 2, QTableWidgetItem(f"{quantidade:.2f}"))
                self.tabela_gastos.setItem(i, 3, QTableWidgetItem(f"R$ {valor:.2f}"))
            
            conn.close()
            
            self.label_total_gastos.setText(f"Total de Gastos: R$ {total_gastos:.2f}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório de gastos: {e}")
    
    def gerar_grafico(self):
        tipo = self.tipo_grafico.currentText()
        
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            if tipo == "Consumo de Materiais":
                # Gráfico de barras do consumo mensal
                cursor.execute('''
                    SELECT tipo_material, SUM(quantidade)
                    FROM notas_fornecedores 
                    WHERE strftime('%Y-%m', data_entrada) = strftime('%Y-%m', 'now')
                    GROUP BY tipo_material
                    ORDER BY SUM(quantidade) DESC
                    LIMIT 10
                ''')
                
                dados = cursor.fetchall()
                materiais = [d[0] for d in dados]
                quantidades = [d[1] for d in dados]
                
                ax.bar(materiais, quantidades, color='skyblue')
                ax.set_xlabel('Material')
                ax.set_ylabel('Quantidade Consumida')
                ax.set_title('Consumo de Materiais no Mês')
                ax.tick_params(axis='x', rotation=45)
                
            elif tipo == "Produção Mensal":
                # Gráfico de linha da produção
                cursor.execute('''
                    SELECT strftime('%Y-%m', data) as mes, 
                           SUM(quantidade_m3) as producao
                    FROM pesagens_detalhadas 
                    GROUP BY strftime('%Y-%m', data)
                    ORDER BY mes DESC
                    LIMIT 12
                ''')
                
                dados = cursor.fetchall()
                meses = [d[0] for d in dados]
                producao = [d[1] for d in dados]
                
                ax.plot(meses, producao, marker='o', color='green')
                ax.set_xlabel('Mês')
                ax.set_ylabel('Produção (m³)')
                ax.set_title('Produção Mensal de Concreto')
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True, alpha=0.3)
                
            elif tipo == "Gastos por Fornecedor":
                # Gráfico de pizza
                cursor.execute('''
                    SELECT fornecedor, SUM(valor_total)
                    FROM notas_fornecedores 
                    WHERE strftime('%Y-%m', data_entrada) = strftime('%Y-%m', 'now')
                    GROUP BY fornecedor
                    ORDER BY SUM(valor_total) DESC
                    LIMIT 8
                ''')
                
                dados = cursor.fetchall()
                fornecedores = [d[0] for d in dados]
                valores = [d[1] for d in dados]
                
                ax.pie(valores, labels=fornecedores, autopct='%1.1f%%', startangle=90)
                ax.set_title('Distribuição de Gastos por Fornecedor')
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                
            elif tipo == "Clientes Mais Frequentes":
                # Gráfico de barras horizontais
                cursor.execute('''
                    SELECT c.nome, COUNT(p.id) as frequencia
                    FROM pesagens_detalhadas p
                    JOIN clientes c ON p.cliente_id = c.id
                    WHERE strftime('%Y', p.data) = strftime('%Y', 'now')
                    GROUP BY c.nome
                    ORDER BY COUNT(p.id) DESC
                    LIMIT 10
                ''')
                
                dados = cursor.fetchall()
                clientes = [d[0] for d in dados]
                frequencia = [d[1] for d in dados]
                
                ax.barh(clientes, frequencia, color='orange')
                ax.set_xlabel('Número de Pesagens')
                ax.set_ylabel('Cliente')
                ax.set_title('Clientes Mais Frequentes no Ano')
            
            conn.close()
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar gráfico: {e}")
    
    def salvar_relatorio_pdf(self):
        QMessageBox.information(self, "Exportar", "Funcionalidade de exportar PDF em desenvolvimento!")