from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QGroupBox,
                             QTableWidget, QTableWidgetItem, QComboBox,
                             QFrame, QProgressBar, QScrollArea,
                             QDateEdit, QLineEdit, QCheckBox,
                             QSplitter, QHeaderView, QMessageBox,
                             QStackedWidget, QTabWidget, QDialog,
                             QFormLayout, QTextEdit, QListWidget,
                             QListWidgetItem, QDialogButtonBox,
                             QDoubleSpinBox, QSpinBox)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont, QColor, QPalette
import sqlite3
from datetime import datetime, timedelta
import json
import csv
import os

# ========== GERENCIADOR DE ESTOQUE ==========
class GerenciadorEstoque:
    """Classe para gerenciar a sincronização de estoque"""
    
    @staticmethod
    def criar_tabelas():
        """Cria tabelas necessárias para o sistema de estoque"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Tabela de movimentações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    material TEXT NOT NULL,
                    quantidade REAL NOT NULL,
                    tipo TEXT NOT NULL,
                    origem TEXT,
                    data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    observacao TEXT,
                    FOREIGN KEY (material) REFERENCES estoque(material)
                )
            ''')
            
            # Verificar e adicionar colunas se não existirem
            cursor.execute('PRAGMA table_info(pesagens)')
            colunas = [col[1] for col in cursor.fetchall()]
            
            if 'estoque_atualizado' not in colunas:
                cursor.execute('''
                    ALTER TABLE pesagens 
                    ADD COLUMN estoque_atualizado BOOLEAN DEFAULT 0
                ''')
            
            cursor.execute('PRAGMA table_info(estoque)')
            colunas_estoque = [col[1] for col in cursor.fetchall()]
            
            colunas_necessarias = ['estoque_maximo', 'custo_unitario', 'fornecedor']
            for coluna in colunas_necessarias:
                if coluna not in colunas_estoque:
                    cursor.execute(f'ALTER TABLE estoque ADD COLUMN {coluna} TEXT')
            
            conn.commit()
            conn.close()
            print("✅ Tabelas de estoque verificadas/criadas com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            return False
    
    @staticmethod
    def atualizar_estoque_apos_pesagem(id_pesagem):
        """Atualiza o estoque após uma pesagem ser concluída"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Buscar dados da pesagem
            cursor.execute('''
                SELECT p.traco_id, p.quantidade, p.materiais_json, p.status
                FROM pesagens p
                WHERE p.id = ?
            ''', (id_pesagem,))
            
            pesagem = cursor.fetchone()
            
            if not pesagem or pesagem[3] != 'CONCLUÍDO':
                conn.close()
                return False
            
            traco_id, quantidade, materiais_json, status = pesagem
            
            # Se já tem materiais_json, usar esses dados
            if materiais_json and materiais_json != 'null':
                try:
                    materiais = json.loads(materiais_json)
                except:
                    materiais = {}
            else:
                # Buscar traço para calcular materiais
                cursor.execute('''
                    SELECT composicao_json, fator_correcao
                    FROM tracos
                    WHERE id = ?
                ''', (traco_id,))
                
                traco = cursor.fetchone()
                if not traco:
                    conn.close()
                    return False
                
                composicao_json, fator_correcao = traco
                try:
                    composicao = json.loads(composicao_json)
                except:
                    composicao = {}
                
                # Calcular quantidades dos materiais
                materiais = {}
                for material, proporcao in composicao.items():
                    if material and proporcao:
                        # Converter proporção (kg/m³) para quantidade total
                        quantidade_material = proporcao * quantidade * (fator_correcao or 1.0)
                        materiais[material] = {
                            'quantidade': quantidade_material,
                            'unidade': 'kg' if material != 'Água' else 'litros'
                        }
                
                # Salvar materiais na pesagem
                cursor.execute('''
                    UPDATE pesagens
                    SET materiais_json = ?
                    WHERE id = ?
                ''', (json.dumps(materiais), id_pesagem))
            
            # Atualizar estoque para cada material
            for material, dados in materiais.items():
                if material and 'quantidade' in dados:
                    quantidade_usada = dados['quantidade']
                    
                    cursor.execute('''
                        UPDATE estoque
                        SET quantidade = ROUND(quantidade - ?, 2)
                        WHERE material = ?
                    ''', (quantidade_usada, material))
                    
                    # Registrar movimentação
                    cursor.execute('''
                        INSERT INTO movimentacoes_estoque 
                        (material, quantidade, tipo, origem, observacao)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        material,
                        -quantidade_usada,
                        'SAÍDA',
                        'PESAGEM',
                        f'Pesagem #{id_pesagem} - Traço {traco_id}'
                    ))
            
            # Marcar como atualizada
            cursor.execute('''
                UPDATE pesagens 
                SET estoque_atualizado = 1 
                WHERE id = ?
            ''', (id_pesagem,))
            
            conn.commit()
            conn.close()
            print(f"✅ Estoque atualizado para pesagem #{id_pesagem}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar estoque: {e}")
            return False
    
    @staticmethod
    def ajustar_estoque(material, quantidade, motivo="Ajuste manual"):
        """Ajusta manualmente o estoque"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE estoque
                SET quantidade = ROUND(quantidade + ?, 2)
                WHERE material = ?
            ''', (quantidade, material))
            
            cursor.execute('''
                INSERT INTO movimentacoes_estoque 
                (material, quantidade, tipo, origem, observacao)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                material,
                quantidade,
                'ENTRADA' if quantidade > 0 else 'SAÍDA',
                'AJUSTE',
                motivo
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Estoque ajustado: {material} ({quantidade:+})")
            return True
            
        except Exception as e:
            print(f"❌ Erro no ajuste de estoque: {e}")
            return False
    
    @staticmethod
    def sincronizar_todas_pesagens():
        """Sincroniza estoque com todas as pesagens pendentes"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Buscar todas as pesagens concluídas que não tiveram estoque atualizado
            cursor.execute('''
                SELECT id FROM pesagens 
                WHERE status = 'CONCLUÍDO' 
                AND (estoque_atualizado = 0 OR estoque_atualizado IS NULL)
                ORDER BY data_pesagem
            ''')
            
            pesagens = cursor.fetchall()
            total_atualizadas = 0
            
            for (id_pesagem,) in pesagens:
                if GerenciadorEstoque.atualizar_estoque_apos_pesagem(id_pesagem):
                    total_atualizadas += 1
            
            conn.close()
            
            return {
                'total': len(pesagens),
                'atualizadas': total_atualizadas,
                'mensagem': f"{total_atualizadas} de {len(pesagens)} pesagem(ns) sincronizada(s)"
            }
            
        except Exception as e:
            print(f"❌ Erro na sincronização completa: {e}")
            return {'total': 0, 'atualizadas': 0, 'mensagem': f'Erro: {e}'}
    
    @staticmethod
    def get_historico_movimentacoes(material=None, data_inicio=None, data_fim=None, limite=100):
        """Retorna histórico de movimentações do estoque"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            query = '''
                SELECT 
                    material,
                    quantidade,
                    tipo,
                    origem,
                    datetime(data_movimentacao) as data_formatada,
                    observacao
                FROM movimentacoes_estoque
                WHERE 1=1
            '''
            params = []
            
            if material and material != "Todos":
                query += " AND material = ?"
                params.append(material)
            
            if data_inicio:
                query += " AND date(data_movimentacao) >= ?"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND date(data_movimentacao) <= ?"
                params.append(data_fim)
            
            query += " ORDER BY data_movimentacao DESC LIMIT ?"
            params.append(limite)
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            conn.close()
            
            return resultados
            
        except Exception as e:
            print(f"❌ Erro ao buscar histórico: {e}")
            return []
    
    @staticmethod
    def get_estoque_atual():
        """Retorna situação atual do estoque"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    material,
                    ROUND(quantidade, 2) as quantidade,
                    unidade,
                    estoque_minimo,
                    estoque_maximo,
                    custo_unitario,
                    fornecedor
                FROM estoque
                ORDER BY 
                    CASE material 
                        WHEN 'Cimento' THEN 1
                        WHEN 'Brita 0' THEN 2
                        WHEN 'Brita 1' THEN 3
                        WHEN 'Areia Média' THEN 4
                        WHEN 'Pó de Brita' THEN 5
                        WHEN 'Aditivo' THEN 6
                        WHEN 'Água' THEN 7
                        ELSE 8
                    END
            ''')
            
            estoque = cursor.fetchall()
            conn.close()
            
            # Calcular totais
            total_valor = 0
            alertas = []
            
            for item in estoque:
                material, quantidade, unidade, minimo, maximo, custo, fornecedor = item
                if custo and quantidade:
                    total_valor += quantidade * custo
                
                if minimo and quantidade < minimo:
                    alertas.append(f"{material}: {quantidade:.2f} {unidade} (mínimo: {minimo:.2f})")
            
            return {
                'itens': estoque,
                'total_valor': total_valor,
                'alertas': alertas,
                'total_itens': len(estoque),
                'itens_criticos': len(alertas)
            }
            
        except Exception as e:
            print(f"❌ Erro ao buscar estoque atual: {e}")
            return None

# ========== DIÁLOGO DE AJUSTE DE ESTOQUE ==========
class DialogAjusteEstoque(QDialog):
    """Diálogo para ajuste manual de estoque"""
    
    def __init__(self, parent=None, material=None):
        super().__init__(parent)
        self.material = material
        self.init_ui()
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333333;
                font-weight: bold;
            }
            QComboBox, QDoubleSpinBox, QTextEdit {
                border: 2px solid #1976D2;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
        """)
        
    def init_ui(self):
        self.setWindowTitle("📦 Ajuste de Estoque")
        self.setFixedSize(450, 300)
        
        layout = QFormLayout()
        layout.setSpacing(10)
        
        # Material
        self.combo_material = QComboBox()
        self.carregar_materiais()
        if self.material:
            index = self.combo_material.findText(self.material)
            if index >= 0:
                self.combo_material.setCurrentIndex(index)
        layout.addRow("Material:", self.combo_material)
        
        # Tipo de ajuste
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Entrada (Adicionar)", "Saída (Remover)"])
        self.combo_tipo.currentIndexChanged.connect(self.atualizar_icone)
        layout.addRow("Tipo:", self.combo_tipo)
        
        # Quantidade
        self.spin_quantidade = QDoubleSpinBox()
        self.spin_quantidade.setRange(0, 100000)
        self.spin_quantidade.setDecimals(2)
        self.spin_quantidade.setSuffix(" unidades")
        self.spin_quantidade.setValue(1.0)
        layout.addRow("Quantidade:", self.spin_quantidade)
        
        # Motivo
        self.text_motivo = QTextEdit()
        self.text_motivo.setMaximumHeight(60)
        self.text_motivo.setPlaceholderText("Digite o motivo do ajuste...")
        layout.addRow("Motivo:", self.text_motivo)
        
        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.aceitar)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        
        # Icone inicial
        self.atualizar_icone()
    
    def carregar_materiais(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            cursor.execute("SELECT material FROM estoque ORDER BY material")
            materiais = cursor.fetchall()
            conn.close()
            
            for material, in materiais:
                self.combo_material.addItem(material)
        except Exception as e:
            print(f"❌ Erro ao carregar materiais: {e}")
    
    def atualizar_icone(self):
        tipo = self.combo_tipo.currentText()
        if "Entrada" in tipo:
            self.setWindowTitle("➕ Entrada de Estoque")
        else:
            self.setWindowTitle("➖ Saída de Estoque")
    
    def aceitar(self):
        material = self.combo_material.currentText()
        quantidade = self.spin_quantidade.value()
        motivo = self.text_motivo.toPlainText().strip()
        
        if not material:
            QMessageBox.warning(self, "Aviso", "Selecione um material!")
            return
        
        if quantidade <= 0:
            QMessageBox.warning(self, "Aviso", "A quantidade deve ser maior que zero!")
            return
        
        if not motivo:
            QMessageBox.warning(self, "Aviso", "Informe o motivo do ajuste!")
            return
        
        # Ajustar sinal baseado no tipo
        if "Saída" in self.combo_tipo.currentText():
            quantidade = -quantidade
        
        if GerenciadorEstoque.ajustar_estoque(material, quantidade, motivo):
            QMessageBox.information(self, "Sucesso", "Estoque ajustado com sucesso!")
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", "Erro ao ajustar estoque!")

# ========== TELA DE DASHBOARD COM SINCRONIZAÇÃO ==========
class TelaDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # ALTERAÇÃO: Mantido cinza claro como fundo principal
        self.setStyleSheet("background-color: #F5F5F5;")
        self.init_ui()
        self.carregar_dados_iniciais()
        
        # Inicializar gerenciador de estoque
        GerenciadorEstoque.criar_tabelas()
    
    def init_ui(self):
        # Layout principal com scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #F5F5F5; border: none;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #F5F5F5;")
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # ========== CABEÇALHO E FILTROS COM SINCRONIZAÇÃO ==========
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        # ALTERAÇÃO: Fundo azul claro
        header_frame.setStyleSheet("""
            background-color: #E3F2FD;
            border-radius: 10px;
            padding: 10px;
            border: 2px solid #1976D2;
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Título - ALTERAÇÃO: Texto azul escuro
        titulo = QLabel("🏗️ DASHBOARD - USINA BETTO MIX")
        titulo.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #0D47A1;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(titulo)
        
        # Linha de filtros e sincronização
        linha_superior = QHBoxLayout()
        
        # Filtros à esquerda
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(10)
        
        # Labels dos filtros - ALTERAÇÃO: Texto azul escuro
        label_periodo = QLabel("📅 Período:")
        label_periodo.setStyleSheet("color: #0D47A1; font-weight: bold;")
        
        label_de = QLabel("De:")
        label_de.setStyleSheet("color: #0D47A1; font-weight: bold;")
        
        label_ate = QLabel("Até:")
        label_ate.setStyleSheet("color: #0D47A1; font-weight: bold;")
        
        # Filtro de período - ALTERAÇÃO: Borda azul escuro
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems([
            "HOJE", "ONTEM", "ÚLTIMOS 7 DIAS", "ÚLTIMOS 30 DIAS", 
            "ESTE MÊS", "MÊS ANTERIOR", "CUSTOMIZADO"
        ])
        self.combo_periodo.currentIndexChanged.connect(self.atualizar_dashboard)
        self.combo_periodo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #333333;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                padding: 8px;
                min-width: 150px;
                font-weight: bold;
            }
            QComboBox:hover {
                border: 2px solid #1565C0;
            }
        """)
        
        # Datas customizadas - ALTERAÇÃO: Borda azul escuro
        self.date_inicio = QDateEdit()
        self.date_inicio.setDate(QDate.currentDate().addDays(-7))
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setStyleSheet("""
            QDateEdit {
                background-color: white;
                color: #333333;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QDateEdit:hover {
                border: 2px solid #1565C0;
            }
        """)
        
        self.date_fim = QDateEdit()
        self.date_fim.setDate(QDate.currentDate())
        self.date_fim.setCalendarPopup(True)
        self.date_fim.setStyleSheet("""
            QDateEdit {
                background-color: white;
                color: #333333;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QDateEdit:hover {
                border: 2px solid #1565C0;
            }
        """)
        
        # Botão de atualizar dashboard - ALTERAÇÃO: Botão azul
        btn_atualizar = QPushButton("🔄 Atualizar")
        btn_atualizar.setToolTip("Atualizar todos os dados do dashboard")
        btn_atualizar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1565C0, stop:1 #0D47A1);
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                font-size: 12px;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border: 1px solid #1565C0;
            }
        """)
        btn_atualizar.clicked.connect(self.atualizar_dashboard)
        
        # Botão de sincronização de estoque - ALTERAÇÃO: Botão azul
        btn_sincronizar = QPushButton("⚡ Sincronizar Estoque")
        btn_sincronizar.setToolTip("Sincronizar estoque com todas as pesagens concluídas")
        btn_sincronizar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1565C0, stop:1 #0D47A1);
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                font-size: 12px;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border: 1px solid #1565C0;
            }
        """)
        btn_sincronizar.clicked.connect(self.sincronizar_estoque)
        
        # Botão de ajuste manual de estoque - ALTERAÇÃO: Botão azul
        btn_ajuste_estoque = QPushButton("📝 Ajustar Estoque")
        btn_ajuste_estoque.setToolTip("Ajuste manual de estoque")
        btn_ajuste_estoque.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1565C0, stop:1 #0D47A1);
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                font-size: 12px;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border: 1px solid #1565C0;
            }
        """)
        btn_ajuste_estoque.clicked.connect(self.abrir_ajuste_estoque)
        
        # Adicionar à linha superior
        linha_superior.addLayout(filtros_layout)
        linha_superior.addWidget(btn_sincronizar)
        linha_superior.addWidget(btn_ajuste_estoque)
        
        header_layout.addLayout(linha_superior)
        main_layout.addWidget(header_frame)
        
        # ========== CARDS DE RESUMO ==========
        cards_frame = QFrame()
        cards_frame.setStyleSheet("background-color: #F5F5F5;")
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # Cards principais - ALTERAÇÃO: Cores atualizadas para paleta de azuis
        self.cards = {
            'producao': self.criar_card("Produção (m³)", "0.00", "#0D47A1", "🏗️"),
            'pesagens': self.criar_card("Pesagens", "0", "#1565C0", "⚖️"),
            'estoque_valor': self.criar_card("Valor Estoque", "R$ 0", "#1976D2", "💰"),
            'faturamento': self.criar_card("Faturamento", "R$ 0", "#0D47A1", "💵"),
            'clientes': self.criar_card("Clientes", "0", "#1565C0", "👥"),
            'nao_conformidades': self.criar_card("Não Conformidades", "0", "#1976D2", "⚠️")
        }
        
        # Posicionar cards
        cards_layout.addWidget(self.cards['producao'], 0, 0)
        cards_layout.addWidget(self.cards['pesagens'], 0, 1)
        cards_layout.addWidget(self.cards['estoque_valor'], 0, 2)
        cards_layout.addWidget(self.cards['faturamento'], 1, 0)
        cards_layout.addWidget(self.cards['clientes'], 1, 1)
        cards_layout.addWidget(self.cards['nao_conformidades'], 1, 2)
        
        main_layout.addWidget(cards_frame)
        
        # ========== PRODUÇÃO E ESTOQUE ==========
        splitter1 = QSplitter(Qt.Orientation.Horizontal)
        splitter1.setStyleSheet("""
            QSplitter::handle {
                background-color: #BDBDBD;
                border: 1px solid #9E9E9E;
                width: 4px;
            }
            QSplitter::handle:hover {
                background-color: #757575;
            }
        """)
        
        # Produção
        producao_frame = QFrame()
        producao_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        producao_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #E0E0E0;
                padding: 10px;
            }
        """)
        producao_layout = QVBoxLayout(producao_frame)
        
        # ALTERAÇÃO: Título azul escuro
        producao_title = QLabel("📊 PRODUÇÃO - VOLUME DE CONCRETO")
        producao_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        producao_title.setStyleSheet("color: #0D47A1; padding: 5px; background-color: white;")
        producao_layout.addWidget(producao_title)
        
        self.label_producao_diaria = QLabel("Hoje: 0.00 m³")
        self.label_producao_diaria.setStyleSheet("color: #333333; font-weight: bold; background-color: white; padding: 5px;")
        self.label_producao_semanal = QLabel("Esta semana: 0.00 m³")
        self.label_producao_semanal.setStyleSheet("color: #333333; font-weight: bold; background-color: white; padding: 5px;")
        self.label_producao_mensal = QLabel("Este mês: 0.00 m³")
        self.label_producao_mensal.setStyleSheet("color: #333333; font-weight: bold; background-color: white; padding: 5px;")
        
        for label in [self.label_producao_diaria, self.label_producao_semanal, self.label_producao_mensal]:
            label.setFont(QFont("Arial", 11))
            producao_layout.addWidget(label)
        
        # ALTERAÇÃO: GroupBox com borda azul escuro e fundo azul claro
        progresso_group = QGroupBox("🎯 Meta Diária de Produção")
        progresso_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #333333;
                background-color: #E3F2FD;
            }
            QGroupBox::title {
                color: #0D47A1;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        progresso_layout = QVBoxLayout(progresso_group)
        
        self.progress_meta = QProgressBar()
        self.progress_meta.setRange(0, 250)
        self.progress_meta.setValue(0)
        self.progress_meta.setFormat("%p%")
        self.progress_meta.setStyleSheet("""
            QProgressBar {
                border: 2px solid #0D47A1;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: #E3F2FD;
                color: #0D47A1;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        
        self.label_meta = QLabel("Meta: 0.00/0.00 m³")
        self.label_meta.setStyleSheet("color: #333333; font-weight: bold; background-color: #E3F2FD; padding: 5px;")
        progresso_layout.addWidget(self.progress_meta)
        progresso_layout.addWidget(self.label_meta)
        producao_layout.addWidget(progresso_group)
        
        # ALTERAÇÃO: GroupBox com borda azul escuro e fundo azul claro
        tracos_group = QGroupBox("🏗️ TRAÇOS MAIS UTILIZADOS")
        tracos_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #333333;
                background-color: #E3F2FD;
            }
            QGroupBox::title {
                color: #0D47A1;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        tracos_layout = QVBoxLayout(tracos_group)
        
        self.tabela_tracos = QTableWidget()
        self.tabela_tracos.setColumnCount(3)
        self.tabela_tracos.setHorizontalHeaderLabels(["Traço", "Quantidade (m³)", "Percentual"])
        self.tabela_tracos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabela_tracos.setMaximumHeight(150)
        # ALTERAÇÃO: Tabela com bordas azuis e linhas alternadas
        self.tabela_tracos.setAlternatingRowColors(True)
        self.tabela_tracos.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #1976D2;
                gridline-color: #BBDEFB;
                color: #333333;
                font-weight: bold;
                alternate-background-color: #E3F2FD;
            }
            QHeaderView::section {
                background-color: #0D47A1;
                padding: 5px;
                border: 1px solid #1565C0;
                font-weight: bold;
                color: white;
            }
            QTableWidget::item {
                color: #212121;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        
        tracos_layout.addWidget(self.tabela_tracos)
        producao_layout.addWidget(tracos_group)
        
        # Estoques
        estoque_frame = QFrame()
        estoque_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        estoque_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #E0E0E0;
                padding: 10px;
            }
        """)
        estoque_layout = QVBoxLayout(estoque_frame)
        
        # ALTERAÇÃO: Título azul escuro
        estoque_title = QLabel("📦 ESTOQUE - MATÉRIAS-PRIMAS")
        estoque_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        estoque_title.setStyleSheet("color: #0D47A1; padding: 5px; background-color: white;")
        estoque_layout.addWidget(estoque_title)
        
        # Mini barra de status de sincronização
        self.status_sync_layout = QHBoxLayout()
        self.label_sync_status = QLabel("🔄 Última sincronização: --:--")
        self.label_sync_status.setStyleSheet("color: #666; font-size: 10px;")
        self.status_sync_layout.addWidget(self.label_sync_status)
        self.status_sync_layout.addStretch()
        estoque_layout.addLayout(self.status_sync_layout)
        
        # Tabela de estoque com alertas - ALTERAÇÃO: Estilo azul
        self.tabela_estoque = QTableWidget()
        self.tabela_estoque.setColumnCount(6)
        self.tabela_estoque.setHorizontalHeaderLabels(["Material", "Estoque", "Mínimo", "Status", "%", "Ações"])
        
        header = self.tabela_estoque.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.tabela_estoque.setMaximumHeight(250)
        # ALTERAÇÃO: Tabela com bordas azuis e linhas alternadas
        self.tabela_estoque.setAlternatingRowColors(True)
        self.tabela_estoque.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #1976D2;
                gridline-color: #BBDEFB;
                color: #333333;
                font-weight: bold;
                alternate-background-color: #E3F2FD;
            }
            QHeaderView::section {
                background-color: #0D47A1;
                padding: 5px;
                border: 1px solid #1565C0;
                font-weight: bold;
                color: white;
            }
            QTableWidget::item {
                color: #212121;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        
        estoque_layout.addWidget(self.tabela_estoque)
        
        # Alertas de estoque crítico
        self.label_alertas_estoque = QLabel("✅ Estoque em níveis normais")
        self.label_alertas_estoque.setStyleSheet("""
            padding: 10px; 
            border-radius: 5px; 
            background-color: #E8F5E8;
            color: #2E7D32;
            border: 2px solid #C8E6C9;
            font-weight: bold;
        """)
        estoque_layout.addWidget(self.label_alertas_estoque)
        
        # Adicionar frames ao splitter
        splitter1.addWidget(producao_frame)
        splitter1.addWidget(estoque_frame)
        splitter1.setSizes([400, 400])
        
        main_layout.addWidget(splitter1)
        
        # ========== PESAGEM ATUAL ==========
        pesagem_frame = QFrame()
        pesagem_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        pesagem_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #E0E0E0;
                padding: 10px;
            }
        """)
        pesagem_layout = QVBoxLayout(pesagem_frame)
        
        # ALTERAÇÃO: Título azul escuro
        pesagem_title = QLabel("⚖️ PESAGEM EM ANDAMENTO")
        pesagem_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        pesagem_title.setStyleSheet("color: #0D47A1; padding: 5px; background-color: white;")
        pesagem_layout.addWidget(pesagem_title)
        
        self.label_pesagem_status = QLabel("⏸️ Nenhuma pesagem em andamento")
        self.label_pesagem_status.setFont(QFont("Arial", 12))
        self.label_pesagem_status.setStyleSheet("color: #424242; padding: 5px; font-weight: bold; background-color: white;")
        pesagem_layout.addWidget(self.label_pesagem_status)
        
        # ALTERAÇÃO: GroupBox com borda azul escuro e fundo azul claro
        pesagem_details_group = QGroupBox("📋 Detalhes da Ordem de Serviço")
        pesagem_details_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #333333;
                background-color: #E3F2FD;
            }
            QGroupBox::title {
                color: #0D47A1;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        pesagem_details_layout = QVBoxLayout(pesagem_details_group)
        
        self.label_ordem_info = QLabel("Ordem: N/A")
        self.label_traco_info = QLabel("Traço: N/A")
        self.label_fck_info = QLabel("FCK: N/A")
        self.label_volume_planejado = QLabel("Volume planejado: N/A m³")
        self.label_volume_atual = QLabel("Volume atual: N/A m³")
        
        for label in [self.label_ordem_info, self.label_traco_info, self.label_fck_info, 
                     self.label_volume_planejado, self.label_volume_atual]:
            label.setFont(QFont("Arial", 10))
            label.setStyleSheet("color: #424242; font-weight: bold; background-color: #E3F2FD; padding: 3px;")
            pesagem_details_layout.addWidget(label)
        
        pesagem_layout.addWidget(pesagem_details_group)
        
        # ALTERAÇÃO: GroupBox com borda azul escuro e fundo azul claro
        materiais_group = QGroupBox("📦 MATERIAIS DO TRAÇO")
        materiais_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #333333;
                background-color: #E3F2FD;
            }
            QGroupBox::title {
                color: #0D47A1;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        materiais_layout = QVBoxLayout(materiais_group)
        
        self.tabela_materiais_pesagem = QTableWidget()
        self.tabela_materiais_pesagem.setColumnCount(4)
        self.tabela_materiais_pesagem.setHorizontalHeaderLabels(["Material", "Planejado", "Atual", "Tolerância"])
        self.tabela_materiais_pesagem.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabela_materiais_pesagem.setMaximumHeight(150)
        # ALTERAÇÃO: Tabela com bordas azuis e linhas alternadas
        self.tabela_materiais_pesagem.setAlternatingRowColors(True)
        self.tabela_materiais_pesagem.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #1976D2;
                gridline-color: #BBDEFB;
                color: #333333;
                font-weight: bold;
                alternate-background-color: #E3F2FD;
            }
            QHeaderView::section {
                background-color: #0D47A1;
                padding: 5px;
                border: 1px solid #1565C0;
                font-weight: bold;
                color: white;
            }
            QTableWidget::item {
                color: #212121;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        
        materiais_layout.addWidget(self.tabela_materiais_pesagem)
        pesagem_layout.addWidget(materiais_group)
        
        # ALTERAÇÃO: GroupBox com borda azul escuro e fundo azul claro
        veiculo_group = QGroupBox("🚚 Informações do Veículo")
        veiculo_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #333333;
                background-color: #E3F2FD;
            }
            QGroupBox::title {
                color: #0D47A1;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        veiculo_layout = QVBoxLayout(veiculo_group)
        
        self.label_placa = QLabel("Placa: N/A")
        self.label_motorista = QLabel("Motorista: N/A")
        self.label_operador = QLabel("Operador: N/A")
        self.label_nota_fiscal = QLabel("Nota Fiscal: N/A")
        self.label_destino = QLabel("Destino: N/A")
        
        for label in [self.label_placa, self.label_motorista, self.label_operador, 
                     self.label_nota_fiscal, self.label_destino]:
            label.setFont(QFont("Arial", 10))
            label.setStyleSheet("color: #424242; font-weight: bold; background-color: #E3F2FD; padding: 3px;")
            veiculo_layout.addWidget(label)
        
        pesagem_layout.addWidget(veiculo_group)
        
        main_layout.addWidget(pesagem_frame)
        
        # ========== AÇÕES RÁPIDAS ==========
        acoes_frame = QFrame()
        acoes_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        acoes_frame.setStyleSheet("background-color: #F5F5F5;")
        acoes_layout = QHBoxLayout(acoes_frame)
        acoes_layout.setSpacing(10)
        
        # ALTERAÇÃO: Botões com gradiente de azul
        botoes_acoes = [
            ("⚖️ Nova Pesagem", self.abrir_pesagens, "#1565C0"),
            ("📦 Ver Estoque", self.abrir_estoque, "#1976D2"),
            ("🧾 Notas Fiscais", self.abrir_notas, "#0D47A1"),
            ("📊 Relatórios", self.abrir_relatorios, "#1565C0"),
            ("👥 Clientes", self.abrir_clientes, "#1976D2"),
            ("⚙️ Configurações", self.abrir_configuracoes, "#0D47A1")
        ]
        
        for texto, funcao, cor in botoes_acoes:
            btn = QPushButton(texto)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {cor}, stop:1 #0D47A1);
                    color: white;
                    padding: 12px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 12px;
                    border: 1px solid #0D47A1;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2196F3, stop:1 {self.escurecer_cor(cor)});
                    border: 1px solid #1565C0;
                }}
            """)
            btn.clicked.connect(funcao)
            acoes_layout.addWidget(btn)
        
        main_layout.addWidget(acoes_frame)
        
        # Configurar scroll
        scroll.setWidget(scroll_content)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        
        # Timer para atualização automática
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_dados_tempo_real)
        self.timer.start(30000)  # Atualiza a cada 30 segundos
        
        # Última sincronização
        self.ultima_sincronizacao = None
    
    def criar_card(self, titulo, valor, cor, icone):
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cor}, stop:1 #0D47A1);
                border-radius: 10px;
                padding: 15px;
                border: 2px solid #0D47A1;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        label_icone = QLabel(icone)
        label_icone.setFont(QFont("Arial", 24))
        label_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_titulo = QLabel(titulo)
        label_titulo.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        label_titulo.setStyleSheet("color: white;")
        label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_valor = QLabel(valor)
        label_valor.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        label_valor.setStyleSheet("color: white;")
        label_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(label_icone)
        layout.addWidget(label_titulo)
        layout.addWidget(label_valor)
        
        return card
    
    def escurecer_cor(self, cor):
        """Escurece uma cor hexadecimal"""
        cores = {
            "#1565C0": "#0D47A1",
            "#1976D2": "#1565C0",
            "#0D47A1": "#0A3576",
            "#4CAF50": "#388E3C",
            "#FF9800": "#F57C00",
            "#2196F3": "#1976D2",
            "#9C27B0": "#7B1FA2",
            "#795548": "#5D4037",
            "#607D8B": "#455A64"
        }
        return cores.get(cor, cor)
    
    def carregar_dados_iniciais(self):
        """Carrega dados iniciais do dashboard"""
        self.atualizar_dashboard()
        QTimer.singleShot(1000, self.atualizar_dados_tempo_real)
    
    # ========== FUNÇÕES DE SINCRONIZAÇÃO ==========
    
    def sincronizar_estoque(self):
        """Sincroniza o estoque com todas as pesagens"""
        try:
            # Mostrar progresso
            self.label_sync_status.setText("🔄 Sincronizando...")
            
            # Executar sincronização
            resultado = GerenciadorEstoque.sincronizar_todas_pesagens()
            
            # Atualizar timestamp
            self.ultima_sincronizacao = datetime.now()
            hora_formatada = self.ultima_sincronizacao.strftime("%H:%M:%S")
            
            if resultado['atualizadas'] > 0:
                self.label_sync_status.setText(f"✅ Sincronizado às {hora_formatada}")
                QMessageBox.information(
                    self,
                    "Sincronização Concluída",
                    f"✅ {resultado['mensagem']}\n\n"
                    f"Estoque atualizado com sucesso!"
                )
            else:
                self.label_sync_status.setText(f"✓ Já sincronizado ({hora_formatada})")
                QMessageBox.information(
                    self,
                    "Sincronização",
                    "✅ O estoque já está sincronizado com todas as pesagens."
                )
            
            # Atualizar exibição do estoque
            self.atualizar_estoque_completo()
            
        except Exception as e:
            self.label_sync_status.setText("❌ Erro na sincronização")
            QMessageBox.critical(
                self,
                "Erro na Sincronização",
                f"❌ Erro ao sincronizar estoque:\n{str(e)}"
            )
    
    def abrir_ajuste_estoque(self):
        """Abre diálogo de ajuste manual de estoque"""
        dialog = DialogAjusteEstoque(self)
        if dialog.exec():
            # Atualizar estoque após ajuste
            self.atualizar_estoque_completo()
    
    def atualizar_estoque_completo(self):
        """Atualização completa do estoque com dados sincronizados"""
        try:
            # Buscar dados atualizados
            dados = GerenciadorEstoque.get_estoque_atual()
            if not dados:
                return
            
            # Atualizar tabela de estoque
            self.tabela_estoque.setRowCount(len(dados['itens']))
            
            for i, item in enumerate(dados['itens']):
                material, quantidade, unidade, minimo, maximo, custo, fornecedor = item
                
                # Calcular percentual
                percentual = 0
                if minimo and minimo > 0:
                    percentual = min(100, (quantidade / minimo) * 100)
                
                # Determinar status e cor
                if quantidade <= 0:
                    status = "ESGOTADO"
                    cor = "#F44336"
                elif minimo and quantidade < minimo:
                    status = "CRÍTICO"
                    cor = "#FF9800"
                elif maximo and quantidade > maximo:
                    status = "EXCESSO"
                    cor = "#FFC107"
                else:
                    status = "OK"
                    cor = "#4CAF50"
                
                # Adicionar itens na tabela
                self.tabela_estoque.setItem(i, 0, QTableWidgetItem(material))
                self.tabela_estoque.setItem(i, 1, QTableWidgetItem(f"{quantidade:,.2f} {unidade}"))
                self.tabela_estoque.setItem(i, 2, QTableWidgetItem(f"{minimo:,.2f}" if minimo else "N/A"))
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor(cor))
                self.tabela_estoque.setItem(i, 3, status_item)
                
                percent_item = QTableWidgetItem(f"{percentual:.1f}%")
                self.tabela_estoque.setItem(i, 4, percent_item)
                
                # Botão de ajuste rápido - ALTERAÇÃO: Botão azul
                btn_ajuste = QPushButton("✏️")
                btn_ajuste.setToolTip(f"Ajustar estoque de {material}")
                btn_ajuste.setFixedSize(30, 30)
                btn_ajuste.setStyleSheet(f"""
                    QPushButton {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #1565C0, stop:1 #0D47A1);
                        color: white;
                        border-radius: 3px;
                        font-weight: bold;
                        border: 1px solid #0D47A1;
                    }}
                    QPushButton:hover {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #1976D2, stop:1 #1565C0);
                        border: 1px solid #1565C0;
                    }}
                """)
                btn_ajuste.clicked.connect(lambda checked, m=material: self.ajuste_rapido_estoque(m))
                
                # Adicionar botão na tabela
                self.tabela_estoque.setCellWidget(i, 5, btn_ajuste)
            
            # Atualizar alertas
            if dados['alertas']:
                alertas_texto = "\n".join(dados['alertas'][:3])
                if len(dados['alertas']) > 3:
                    alertas_texto += f"\n... e mais {len(dados['alertas']) - 3} itens críticos"
                
                self.label_alertas_estoque.setText(
                    f"⚠️ {len(dados['alertas'])} item(ns) crítico(s)\n{alertas_texto}"
                )
                self.label_alertas_estoque.setStyleSheet("""
                    padding: 10px; 
                    border-radius: 5px; 
                    background-color: #FFEBEE;
                    color: #C62828;
                    border: 2px solid #ffcdd2;
                    font-weight: bold;
                """)
            else:
                self.label_alertas_estoque.setText("✅ Estoque em níveis normais")
                self.label_alertas_estoque.setStyleSheet("""
                    padding: 10px; 
                    border-radius: 5px; 
                    background-color: #E8F5E8;
                    color: #2E7D32;
                    border: 2px solid #c8e6c9;
                    font-weight: bold;
                """)
            
            # Atualizar card de valor do estoque
            valor_total = f"R$ {dados['total_valor']:,.2f}"
            self.atualizar_card_valor('estoque_valor', valor_total)
            
        except Exception as e:
            print(f"❌ Erro ao atualizar estoque completo: {e}")
    
    def ajuste_rapido_estoque(self, material):
        """Abre diálogo de ajuste para um material específico"""
        dialog = DialogAjusteEstoque(self, material)
        if dialog.exec():
            self.atualizar_estoque_completo()
    
    # ========== MÉTODOS ORIGINAIS (MANTIDOS) ==========
    
    def atualizar_dashboard(self):
        """Atualiza todos os dados do dashboard"""
        try:
            periodo = self.combo_periodo.currentText()
            data_inicio, data_fim = self.obter_datas_periodo(periodo)
            
            # Atualizar cards principais
            self.atualizar_cards_principais(data_inicio, data_fim)
            
            # Atualizar produção
            self.atualizar_producao(data_inicio, data_fim)
            
            # Atualizar estoque COMPLETO (com sincronização)
            self.atualizar_estoque_completo()
            
            # Atualizar pesagem atual
            self.atualizar_pesagem_atual()
            
        except Exception as e:
            print(f"❌ Erro ao atualizar dashboard: {e}")
    
    def obter_datas_periodo(self, periodo):
        hoje = datetime.now()
        
        if periodo == "HOJE":
            inicio = hoje.replace(hour=0, minute=0, second=0, microsecond=0)
            fim = hoje
        elif periodo == "ONTEM":
            inicio = (hoje - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            fim = (hoje - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        elif periodo == "ÚLTIMOS 7 DIAS":
            inicio = (hoje - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
            fim = hoje
        elif periodo == "ÚLTIMOS 30 DIAS":
            inicio = (hoje - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            fim = hoje
        elif periodo == "ESTE MÊS":
            inicio = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fim = hoje
        elif periodo == "MÊS ANTERIOR":
            primeiro_dia_mes_atual = hoje.replace(day=1)
            fim_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
            inicio = fim_mes_anterior.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fim = fim_mes_anterior.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:  # CUSTOMIZADO
            inicio = datetime.combine(self.date_inicio.date().toPyDate(), datetime.min.time())
            fim = datetime.combine(self.date_fim.date().toPyDate(), datetime.max.time())
        
        return inicio, fim
    
    def atualizar_cards_principais(self, data_inicio, data_fim):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Produção total no período
            cursor.execute('''
                SELECT COALESCE(SUM(quantidade), 0) 
                FROM pesagens 
                WHERE status = 'CONCLUÍDO' 
                AND datetime(data_pesagem) BETWEEN ? AND ?
            ''', (data_inicio, data_fim))
            
            producao_total = cursor.fetchone()[0] or 0
            
            # Número de pesagens
            cursor.execute('''
                SELECT COUNT(*) 
                FROM pesagens 
                WHERE status = 'CONCLUÍDO' 
                AND datetime(data_pesagem) BETWEEN ? AND ?
            ''', (data_inicio, data_fim))
            
            num_pesagens = cursor.fetchone()[0] or 0
            
            # Valor do estoque (usando gerenciador)
            dados_estoque = GerenciadorEstoque.get_estoque_atual()
            valor_estoque = dados_estoque['total_valor'] if dados_estoque else 0
            
            # Faturamento estimado
            faturamento = producao_total * 250
            
            # Número de clientes atendidos
            cursor.execute('''
                SELECT COUNT(DISTINCT cliente_id) 
                FROM pesagens 
                WHERE status = 'CONCLUÍDO' 
                AND datetime(data_pesagem) BETWEEN ? AND ?
            ''', (data_inicio, data_fim))
            
            num_clientes = cursor.fetchone()[0] or 0
            
            # Não conformidades
            cursor.execute('''
                SELECT COUNT(*) 
                FROM pesagens 
                WHERE (observacoes LIKE '%problema%' 
                OR observacoes LIKE '%erro%'
                OR observacoes LIKE '%desvio%')
                AND datetime(data_pesagem) BETWEEN ? AND ?
            ''', (data_inicio, data_fim))
            
            nao_conformidades = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Atualizar cards
            self.atualizar_card_valor('producao', f"{producao_total:.2f}")
            self.atualizar_card_valor('pesagens', str(num_pesagens))
            self.atualizar_card_valor('estoque_valor', f"R$ {valor_estoque:,.2f}")
            self.atualizar_card_valor('faturamento', f"R$ {faturamento:,.2f}")
            self.atualizar_card_valor('clientes', str(num_clientes))
            self.atualizar_card_valor('nao_conformidades', str(nao_conformidades))
            
        except Exception as e:
            print(f"❌ Erro ao atualizar cards: {e}")
    
    def atualizar_card_valor(self, card_id, valor):
        if card_id in self.cards:
            card = self.cards[card_id]
            for i in range(card.layout().count()):
                widget = card.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and widget.text() not in ["🏗️", "⚖️", "💰", "💵", "👥", "⚠️"]:
                    widget.setText(valor)
    
    def atualizar_producao(self, data_inicio, data_fim):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            hoje_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cursor.execute('''
                SELECT COALESCE(SUM(quantidade), 0) 
                FROM pesagens 
                WHERE status = 'CONCLUÍDO' 
                AND datetime(data_pesagem) >= ?
            ''', (hoje_inicio,))
            
            producao_hoje = cursor.fetchone()[0] or 0
            
            semana_inicio = (datetime.now() - timedelta(days=datetime.now().weekday()))
            semana_inicio = semana_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
            
            cursor.execute('''
                SELECT COALESCE(SUM(quantidade), 0) 
                FROM pesagens 
                WHERE status = 'CONCLUÍDO' 
                AND datetime(data_pesagem) >= ?
            ''', (semana_inicio,))
            
            producao_semanal = cursor.fetchone()[0] or 0
            
            mes_inicio = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            cursor.execute('''
                SELECT COALESCE(SUM(quantidade), 0) 
                FROM pesagens 
                WHERE status = 'CONCLUÍDO' 
                AND datetime(data_pesagem) >= ?
            ''', (mes_inicio,))
            
            producao_mensal = cursor.fetchone()[0] or 0
            
            # Traços mais utilizados
            cursor.execute('''
                SELECT 
                    t.codigo || ' - ' || t.nome as traco,
                    SUM(p.quantidade) as total,
                    COUNT(*) as quantidade
                FROM pesagens p
                JOIN tracos t ON p.traco_id = t.id
                WHERE p.status = 'CONCLUÍDO'
                AND datetime(p.data_pesagem) BETWEEN ? AND ?
                GROUP BY p.traco_id
                ORDER BY total DESC
                LIMIT 5
            ''', (data_inicio, data_fim))
            
            tracos = cursor.fetchall()
            
            # Meta diária
            meta_diaria = 50
            progresso = min(100, int((producao_hoje / meta_diaria) * 100))
            
            conn.close()
            
            # Atualizar labels
            self.label_producao_diaria.setText(f"📅 Hoje: {producao_hoje:.2f} m³")
            self.label_producao_semanal.setText(f"📊 Esta semana: {producao_semanal:.2f} m³")
            self.label_producao_mensal.setText(f"📈 Este mês: {producao_mensal:.2f} m³")
            
            # Atualizar progresso da meta
            self.progress_meta.setValue(progresso)
            self.label_meta.setText(f"Meta: {producao_hoje:.2f}/{meta_diaria:.2f} m³")
            
            # Atualizar tabela de traços
            self.tabela_tracos.setRowCount(len(tracos))
            total_geral = sum([t[1] for t in tracos]) if tracos else 1
            
            for i, (traco, total, quantidade) in enumerate(tracos):
                percentual = (total / total_geral * 100) if total_geral > 0 else 0
                
                self.tabela_tracos.setItem(i, 0, QTableWidgetItem(traco))
                self.tabela_tracos.setItem(i, 1, QTableWidgetItem(f"{total:.2f}"))
                self.tabela_tracos.setItem(i, 2, QTableWidgetItem(f"{percentual:.1f}%"))
                
        except Exception as e:
            print(f"❌ Erro ao atualizar produção: {e}")
    
    def atualizar_pesagem_atual(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    p.id,
                    p.quantidade,
                    p.placa_veiculo,
                    p.motorista,
                    p.observacoes,
                    p.data_pesagem,
                    p.materiais_json,
                    c.nome as cliente_nome,
                    t.codigo as traco_codigo,
                    t.nome as traco_nome
                FROM pesagens p
                LEFT JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN tracos t ON p.traco_id = t.id
                WHERE p.status = 'PENDENTE'
                ORDER BY p.data_pesagem DESC
                LIMIT 1
            ''')
            
            pesagem = cursor.fetchone()
            
            if pesagem:
                (id_pesagem, quantidade, placa, motorista, observacoes, 
                 data_pesagem, materiais_json, cliente_nome, traco_codigo, traco_nome) = pesagem
                
                # Decodificar materiais
                materiais = {}
                if materiais_json and materiais_json != 'null':
                    try:
                        materiais = json.loads(materiais_json)
                    except:
                        materiais = {}
                
                # Atualizar status
                self.label_pesagem_status.setText(f"▶️ PESAGEM EM ANDAMENTO - Ordem #{id_pesagem}")
                self.label_pesagem_status.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px; background-color: white;")
                
                # Atualizar informações
                self.label_ordem_info.setText(f"📋 Ordem: #{id_pesagem}")
                self.label_traco_info.setText(f"🏗️ Traço: {traco_codigo} - {traco_nome}")
                self.label_fck_info.setText("🔧 FCK: 25 MPa")
                self.label_volume_planejado.setText(f"📏 Volume planejado: {quantidade:.2f} m³")
                self.label_volume_atual.setText(f"⚖️ Volume atual: {quantidade * 0.5:.2f} m³")
                
                # Atualizar informações do veículo
                self.label_placa.setText(f"🚚 Placa: {placa}")
                self.label_motorista.setText(f"👤 Motorista: {motorista}")
                self.label_operador.setText("👷 Operador: Sistema")
                self.label_nota_fiscal.setText(f"🧾 Nota Fiscal: NF-{id_pesagem:06d}")
                self.label_destino.setText(f"🏗️ Destino: {cliente_nome or 'N/A'}")
                
                # Atualizar tabela de materiais
                materiais_lista = [
                    ("Cimento", "kg"),
                    ("Brita 0", "kg"),
                    ("Brita 1", "kg"),
                    ("Areia Média", "kg"),
                    ("Pó de Brita", "kg"),
                    ("Água", "litros"),
                    ("Aditivo", "kg")
                ]
                
                self.tabela_materiais_pesagem.setRowCount(len(materiais_lista))
                
                for i, (material, unidade) in enumerate(materiais_lista):
                    if material in materiais:
                        planejado = materiais[material].get('quantidade', 0)
                        atual = planejado * 0.5
                        tolerancia = "±2%"
                    else:
                        planejado = 0
                        atual = 0
                        tolerancia = "N/A"
                    
                    # Determinar cor
                    if planejado > 0 and abs(atual - planejado) / planejado * 100 > 2:
                        cor = "#F44336"
                    elif planejado > 0 and abs(atual - planejado) / planejado * 100 > 1:
                        cor = "#FF9800"
                    else:
                        cor = "#4CAF50"
                    
                    self.tabela_materiais_pesagem.setItem(i, 0, QTableWidgetItem(material))
                    self.tabela_materiais_pesagem.setItem(i, 1, QTableWidgetItem(f"{planejado:.2f} {unidade}"))
                    
                    atual_item = QTableWidgetItem(f"{atual:.2f} {unidade}")
                    atual_item.setForeground(QColor(cor))
                    self.tabela_materiais_pesagem.setItem(i, 2, atual_item)
                    
                    self.tabela_materiais_pesagem.setItem(i, 3, QTableWidgetItem(tolerancia))
            else:
                # Nenhuma pesagem em andamento
                self.label_pesagem_status.setText("⏸️ Nenhuma pesagem em andamento")
                self.label_pesagem_status.setStyleSheet("color: #757575; padding: 5px; background-color: white;")
                
                # Limpar informações
                self.label_ordem_info.setText("Ordem: N/A")
                self.label_traco_info.setText("Traço: N/A")
                self.label_fck_info.setText("FCK: N/A")
                self.label_volume_planejado.setText("Volume planejado: N/A m³")
                self.label_volume_atual.setText("Volume atual: N/A m³")
                
                self.label_placa.setText("Placa: N/A")
                self.label_motorista.setText("Motorista: N/A")
                self.label_operador.setText("Operador: N/A")
                self.label_nota_fiscal.setText("Nota Fiscal: N/A")
                self.label_destino.setText("Destino: N/A")
                
                # Limpar tabela de materiais
                self.tabela_materiais_pesagem.setRowCount(0)
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao atualizar pesagem atual: {e}")
    
    def atualizar_dados_tempo_real(self):
        """Atualiza dados em tempo real"""
        self.atualizar_pesagem_atual()
        self.atualizar_estoque_completo()
        
        if self.combo_periodo.currentText() == "HOJE":
            self.atualizar_dashboard()
    
    def abrir_pesagens(self):
        if self.parent:
            self.parent.abrir_pesagens()
    
    def abrir_estoque(self):
        if self.parent:
            self.parent.abrir_estoque()
    
    def abrir_clientes(self):
        if self.parent:
            self.parent.abrir_clientes()
    
    def abrir_relatorios(self):
        if self.parent:
            self.parent.abrir_relatorios()
    
    def abrir_notas(self):
        if self.parent:
            self.parent.abrir_notas()
    
    def abrir_configuracoes(self):
        if self.parent:
            QMessageBox.information(self, "Configurações", "Abrindo tela de configurações...")

# ========== INICIALIZAÇÃO DO SISTEMA ==========
def inicializar_sistema_estoque():
    """Função para inicializar o sistema de estoque"""
    print("🔄 Inicializando sistema de estoque...")
    
    # Criar tabelas necessárias
    GerenciadorEstoque.criar_tabelas()
    
    # Sincronizar estoque inicial
    resultado = GerenciadorEstoque.sincronizar_todas_pesagens()
    print(f"✅ Sistema de estoque inicializado: {resultado['mensagem']}")
    
    return resultado

# Para usar, chame esta função no início do seu aplicativo principal:
# inicializar_sistema_estoque()