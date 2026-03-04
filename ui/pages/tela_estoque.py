from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDialog, QDialogButtonBox,
                             QLineEdit, QComboBox, QDoubleSpinBox,
                             QFormLayout, QTextEdit, QMenu, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QAction
import sqlite3
from datetime import datetime, timedelta
import json  # Adicionado para processar JSON

class DialogSaidaEstoque(QDialog):
    def __init__(self, parent=None, material_info=None):
        super().__init__(parent)
        self.setWindowTitle("Saída de Estoque")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.material_info = material_info  # (material, quantidade_atual, unidade)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Material (não editável)
        self.label_material = QLabel(material_info[0] if material_info else "")
        self.label_material.setStyleSheet("font-weight: bold; color: #0D47A1;")
        
        # Quantidade atual (não editável)
        self.label_quantidade_atual = QLabel(f"{material_info[1]:.2f} {material_info[2]}" if material_info else "")
        self.label_quantidade_atual.setStyleSheet("color: #333333; font-weight: bold;")
        
        # Quantidade para saída
        self.input_quantidade = QDoubleSpinBox()
        self.input_quantidade.setRange(0.01, material_info[1] if material_info else 100000)
        self.input_quantidade.setDecimals(2)
        self.input_quantidade.setValue(0)
        self.input_quantidade.setSuffix(f" {material_info[2]}" if material_info else "")
        self.input_quantidade.setStyleSheet("""
            QDoubleSpinBox {
                border: 2px solid #1976D2;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QDoubleSpinBox:hover {
                border: 2px solid #0D47A1;
            }
        """)
        
        # Destino/Projeto
        self.input_destino = QComboBox()
        self.input_destino.addItems([
            "Pesagem de Concreto",
            "Obra Interna",
            "Manutenção",
            "Teste Laboratório",
            "Outro"
        ])
        self.input_destino.setStyleSheet("""
            QComboBox {
                border: 2px solid #1976D2;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QComboBox:hover {
                border: 2px solid #0D47A1;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        
        # Observações
        self.input_observacoes = QTextEdit()
        self.input_observacoes.setMaximumHeight(80)
        self.input_observacoes.setPlaceholderText("Observações sobre a saída...")
        self.input_observacoes.setStyleSheet("""
            QTextEdit {
                border: 2px solid #1976D2;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QTextEdit:hover {
                border: 2px solid #0D47A1;
            }
        """)
        
        form.addRow("Material:", self.label_material)
        form.addRow("Estoque Atual:", self.label_quantidade_atual)
        form.addRow("Quantidade a Retirar:", self.input_quantidade)
        form.addRow("Destino:", self.input_destino)
        form.addRow("Observações:", self.input_observacoes)
        
        layout.addLayout(form)
        
        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validar_e_aceitar)
        buttons.rejected.connect(self.reject)
        
        # Estilo dos botões
        buttons.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1565C0, stop:1 #0D47A1);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border: 1px solid #1565C0;
            }
        """)
        
        layout.addWidget(buttons)
    
    def validar_e_aceitar(self):
        quantidade = self.input_quantidade.value()
        if quantidade <= 0:
            QMessageBox.warning(self, "Aviso", "Informe uma quantidade válida para saída!")
            return
        if quantidade > self.material_info[1]:
            QMessageBox.warning(self, "Aviso", "Quantidade maior que o estoque disponível!")
            return
        
        self.accept()
    
    def get_dados(self):
        return {
            'material': self.material_info[0],
            'quantidade': self.input_quantidade.value(),
            'destino': self.input_destino.currentText(),
            'observacoes': self.input_observacoes.toPlainText()
        }

class TelaEstoque(QWidget):
    atualizar_estoque_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.carregar_estoque()
        self.atualizar_estoque_signal.connect(self.carregar_estoque)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        titulo = QLabel("CONTROLE DE ESTOQUE")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # ALTERAÇÃO: Texto azul escuro
        titulo.setStyleSheet("color: #0D47A1; padding: 10px; background-color: #E3F2FD; border-radius: 5px; border: 2px solid #0D47A1;")
        layout.addWidget(titulo)
        
        # Botões superiores - ALTERAÇÃO: Botões com gradiente de azul
        btn_layout = QHBoxLayout()
        
        btn_atualizar = QPushButton("🔄 Atualizar")
        btn_atualizar.clicked.connect(self.carregar_estoque)
        btn_atualizar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1565C0, stop:1 #0D47A1);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border: 1px solid #1565C0;
            }
        """)
        
        btn_saida = QPushButton("➖ Dar Saída")
        btn_saida.clicked.connect(self.dar_saida_estoque)
        btn_saida.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1565C0, stop:1 #0D47A1);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border: 1px solid #1565C0;
            }
        """)
        
        btn_historico = QPushButton("📊 Ver Histórico")
        btn_historico.clicked.connect(self.ver_historico)
        btn_historico.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1565C0, stop:1 #0D47A1);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border: 1px solid #1565C0;
            }
        """)
        
        # BOTÃO: Sincronizar com Pesagens
        btn_sincronizar = QPushButton("⚖️ Sinc. Pesagens")
        btn_sincronizar.clicked.connect(self.sincronizar_com_pesagens)
        btn_sincronizar.setToolTip("Sincronizar com pesagens concluídas")
        btn_sincronizar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                border: 1px solid #1565C0;
            }
        """)
        
        # BOTÃO: Sincronizar com Notas
        btn_sinc_notas = QPushButton("📄 Sinc. Notas")
        btn_sinc_notas.clicked.connect(self.sincronizar_com_notas)
        btn_sinc_notas.setToolTip("Sincronizar com notas de entrada")
        btn_sinc_notas.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                border: 1px solid #1565C0;
            }
        """)
        
        # BOTÃO: Relatório de Consumo
        btn_relatorio = QPushButton("📈 Relatório Consumo")
        btn_relatorio.clicked.connect(self.exibir_relatorio_consumo)
        btn_relatorio.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1565C0, stop:1 #0D47A1);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
                border: 1px solid #1565C0;
            }
        """)
        
        # BOTÃO: Apagar Histórico
        btn_apagar_historico = QPushButton("🗑️ Apagar Histórico")
        btn_apagar_historico.clicked.connect(self.apagar_historico)
        btn_apagar_historico.setToolTip("Apagar todo o histórico de movimentações")
        btn_apagar_historico.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF5722, stop:1 #E64A19);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #E64A19;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF7043, stop:1 #FF5722);
                border: 1px solid #FF5722;
            }
        """)
        
        # BOTÃO: Zerar Estoque
        btn_zerar = QPushButton("❌ Zerar Estoque")
        btn_zerar.clicked.connect(self.zerar_estoque)
        btn_zerar.setToolTip("Zerar estoque do material selecionado")
        btn_zerar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F44336, stop:1 #D32F2F);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #D32F2F;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #EF5350, stop:1 #F44336);
                border: 1px solid #F44336;
            }
        """)
        
        btn_layout.addWidget(btn_atualizar)
        btn_layout.addWidget(btn_saida)
        btn_layout.addWidget(btn_historico)
        btn_layout.addWidget(btn_sincronizar)
        btn_layout.addWidget(btn_sinc_notas)
        btn_layout.addWidget(btn_relatorio)
        btn_layout.addWidget(btn_apagar_historico)
        btn_layout.addWidget(btn_zerar)
        
        layout.addLayout(btn_layout)
        
        # ALTERAÇÃO: Tabela com estilo azul
        self.tabela_estoque = QTableWidget()
        self.tabela_estoque.setColumnCount(5)
        self.tabela_estoque.setHorizontalHeaderLabels([
            "Material", "Quantidade", "Unidade", "Estoque Mínimo", "Status"
        ])
        self.tabela_estoque.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_estoque.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabela_estoque.customContextMenuRequested.connect(self.mostrar_menu_contexto)
        
        # ALTERAÇÃO: Estilo da tabela com paleta de azuis
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
                padding: 8px;
                border: 1px solid #1565C0;
                font-weight: bold;
                color: white;
                font-size: 11px;
            }
            QTableWidget::item {
                color: #212121;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #E3F2FD;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #1565C0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #1976D2;
            }
        """)
        
        layout.addWidget(self.tabela_estoque)
        
        # Estatísticas - ALTERAÇÃO: Estilo azul
        self.label_estatisticas = QLabel("Carregando estoque...")
        self.label_estatisticas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estatisticas.setStyleSheet("""
            padding: 10px; 
            border-radius: 5px; 
            background-color: #E3F2FD;
            color: #0D47A1;
            border: 2px solid #1976D2;
            font-weight: bold;
            font-size: 12px;
        """)
        layout.addWidget(self.label_estatisticas)
    
    def mostrar_menu_contexto(self, pos):
        linha = self.tabela_estoque.currentRow()
        if linha >= 0:
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    border: 2px solid #0D47A1;
                    border-radius: 5px;
                    padding: 5px;
                }
                QMenu::item {
                    background-color: white;
                    padding: 8px 15px;
                    color: #0D47A1;
                    font-weight: bold;
                }
                QMenu::item:selected {
                    background-color: #2196F3;
                    color: white;
                    border-radius: 3px;
                }
            """)
            
            acao_ajustar = QAction("📝 Ajustar Manualmente", self)
            acao_ajustar.triggered.connect(self.ajuste_estoque)
            menu.addAction(acao_ajustar)
            
            acao_zerar = QAction("❌ Zerar Estoque", self)
            acao_zerar.triggered.connect(self.zerar_estoque)
            menu.addAction(acao_zerar)
            
            acao_historico_material = QAction("📊 Histórico do Material", self)
            acao_historico_material.triggered.connect(lambda: self.ver_historico_material(linha))
            menu.addAction(acao_historico_material)
            
            menu.exec(self.tabela_estoque.mapToGlobal(pos))
    
    def ver_historico_material(self, linha):
        material = self.tabela_estoque.item(linha, 0).text()
        self.ver_historico(material)
    
    def criar_tabelas_se_necessario(self, conn):
        """Cria as tabelas necessárias se não existirem"""
        cursor = conn.cursor()
        
        # Tabela estoque
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material TEXT UNIQUE,
                quantidade REAL DEFAULT 0,
                unidade TEXT,
                estoque_minimo REAL DEFAULT 0,
                data_atualizacao TEXT,
                data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # REMOVER MATERIAL "BRITA" SEM ESPECIFICAÇÃO SE EXISTIR
        cursor.execute("DELETE FROM estoque WHERE material = 'Brita'")
        
        # Inicializar APENAS os 7 materiais básicos CORRETOS - TODOS COM ESTOQUE MÍNIMO 5000
        materiais_base = [
            ("Cimento", "kg", 5000),        # Alterado de 1000 para 5000
            ("Brita 0", "kg", 5000),        # Já era 5000
            ("Brita 1", "kg", 5000),        # Já era 5000
            ("Areia Média", "kg", 5000),    # Já era 5000
            ("Pó de Brita", "kg", 5000),    # Alterado de 3000 para 5000
            ("Aditivo", "kg", 5000),        # Alterado de 1000 para 5000
            ("Água", "litros", 5000)        # Alterado de 1000 para 5000
        ]
        
        for material, unidade, estoque_minimo in materiais_base:
            cursor.execute('''
                INSERT OR IGNORE INTO estoque (material, unidade, estoque_minimo, data_atualizacao)
                VALUES (?, ?, ?, ?)
            ''', (material, unidade, estoque_minimo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Tabela de histórico de movimentações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material TEXT,
                quantidade REAL,
                tipo TEXT,  -- ENTRADA, SAIDA, AJUSTE, ZERAGEM
                destino TEXT,
                observacoes TEXT,
                data_movimentacao TEXT,
                usuario TEXT DEFAULT 'SISTEMA',
                relacionamento_id INTEGER, -- ID da pesagem/nota relacionada
                relacionamento_tipo TEXT   -- PESAGEM, NOTA_ENTRADA
            )
        ''')
        
        # Tabela de notas de entrada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas_entrada (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_nota TEXT,
                fornecedor TEXT,
                material TEXT,
                quantidade REAL,
                unidade TEXT,
                data_entrada TEXT,
                observacoes TEXT,
                status TEXT DEFAULT 'ATIVO'
            )
        ''')
        
        # Índices para melhor performance
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_historico_material 
                ON historico_estoque(material, data_movimentacao)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_historico_destino 
                ON historico_estoque(destino)
            ''')
        except:
            pass
        
        conn.commit()
    
    def carregar_estoque(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            
            # Garantir que as tabelas existem e corrigir materiais
            self.criar_tabelas_se_necessario(conn)
            
            cursor = conn.cursor()
            
            # Buscar APENAS os 7 materiais corretos
            cursor.execute('''
                SELECT material, quantidade, unidade, estoque_minimo 
                FROM estoque 
                WHERE material IN ('Cimento', 'Brita 0', 'Brita 1', 'Areia Média', 'Pó de Brita', 'Aditivo', 'Água')
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
            
            self.tabela_estoque.setRowCount(len(estoque))
            
            # Contadores para estatísticas
            total_materiais = 0
            baixo_estoque = 0
            esgotados = 0
            total_valor_estoque = 0
            
            # Valores unitários aproximados APENAS para os 7 materiais
            valores_unitarios = {
                "Cimento": 0.700,
                "Brita 0": 0.070,
                "Brita 1": 0.070,
                "Areia Média": 0.070,
                "Pó de Brita": 0.070,
                "Aditivo": 3.00,
                "Água": 0.000,
            }
            
            for i, item in enumerate(estoque):
                material = item[0] if item[0] else "Desconhecido"
                quantidade = item[1] if item[1] else 0
                unidade = item[2] if item[2] else "un"
                estoque_minimo = item[3] if item[3] else 0
                
                # Material
                self.tabela_estoque.setItem(i, 0, QTableWidgetItem(str(material)))
                
                # Quantidade
                quantidade_item = QTableWidgetItem(f"{float(quantidade):.2f}")
                quantidade_item.setData(Qt.ItemDataRole.UserRole, float(quantidade))
                self.tabela_estoque.setItem(i, 1, quantidade_item)
                
                # Unidade
                self.tabela_estoque.setItem(i, 2, QTableWidgetItem(str(unidade)))
                
                # Estoque Mínimo - ATUALIZADO PARA SEMPRE MOSTRAR 5000
                estoque_minimo_item = QTableWidgetItem("5000.00")
                self.tabela_estoque.setItem(i, 3, estoque_minimo_item)
                
                # Status com cores - CORREÇÃO AQUI: REMOVIDA A CONDIÇÃO DE "ATENÇÃO"
                status = "OK"
                cor_status = QColor(39, 174, 96)  # Verde
                
                if quantidade <= 0:
                    status = "ESGOTADO"
                    cor_status = QColor(231, 76, 60)  # Vermelho
                    esgotados += 1
                elif estoque_minimo > 0 and quantidade < estoque_minimo:
                    status = "BAIXO"
                    cor_status = QColor(243, 156, 18)  # Laranja
                    baixo_estoque += 1
                # REMOVIDO O STATUS "ATENÇÃO" - agora só mostra OK se quantidade >= estoque_minimo
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(cor_status)
                self.tabela_estoque.setItem(i, 4, status_item)
                
                # Cálculo do valor total APENAS para materiais conhecidos
                if material in valores_unitarios:
                    total_valor_estoque += quantidade * valores_unitarios[material]
                
                total_materiais += 1
            
            # Atualizar estatísticas
            self.label_estatisticas.setText(
                f"📊 {total_materiais} materiais | "
                f"⚠️ {baixo_estoque + esgotados} alertas | "
                f"💰 R$ {total_valor_estoque:.2f}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar estoque: {e}")
            print(f"Erro detalhado: {e}")
    
    def dar_saida_estoque(self):
        """Abre diálogo para dar saída no estoque"""
        linha = self.tabela_estoque.currentRow()
        if linha >= 0:
            material = self.tabela_estoque.item(linha, 0).text()
            quantidade_atual = float(self.tabela_estoque.item(linha, 1).text())
            unidade = self.tabela_estoque.item(linha, 2).text()
            
            if quantidade_atual <= 0:
                QMessageBox.warning(self, "Aviso", f"O material {material} está esgotado!")
                return
            
            dialog = DialogSaidaEstoque(self, (material, quantidade_atual, unidade))
            if dialog.exec():
                dados = dialog.get_dados()
                self.registrar_saida(dados, unidade)
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um material para dar saída!")
    
    def registrar_saida(self, dados, unidade):
        """Registra saída no estoque"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Obter quantidade atual
            cursor.execute("SELECT quantidade FROM estoque WHERE material = ?", (dados['material'],))
            resultado = cursor.fetchone()
            if not resultado:
                QMessageBox.critical(self, "Erro", "Material não encontrado no estoque!")
                return
            
            quantidade_atual = resultado[0]
            nova_quantidade = quantidade_atual - dados['quantidade']
            
            # Atualizar estoque
            cursor.execute('''
                UPDATE estoque 
                SET quantidade = ?,
                    data_atualizacao = ?
                WHERE material = ?
            ''', (nova_quantidade, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), dados['material']))
            
            # Registrar no histórico
            cursor.execute('''
                INSERT INTO historico_estoque 
                (material, quantidade, tipo, destino, observacoes, data_movimentacao)
                VALUES (?, ?, 'SAIDA', ?, ?, ?)
            ''', (
                dados['material'],
                dados['quantidade'],
                dados['destino'],
                dados['observacoes'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(
                self, 
                "Sucesso", 
                f"✅ Saída registrada com sucesso!\n\n"
                f"📦 Material: {dados['material']}\n"
                f"📊 Quantidade: {dados['quantidade']:.2f} {unidade}\n"
                f"🎯 Destino: {dados['destino']}"
            )
            
            self.carregar_estoque()
            self.atualizar_estoque_signal.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao registrar saída: {e}")
            print(f"Erro detalhado: {e}")
    
    def ver_historico(self, material_filtro=None):
        """Mostra o histórico de movimentações do estoque - ZERADO"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Construir query base
            query = '''
                SELECT 
                    data_movimentacao,
                    material,
                    quantidade,
                    tipo,
                    destino,
                    observacoes,
                    usuario
                FROM historico_estoque 
            '''
            
            params = []
            if material_filtro:
                query += " WHERE material = ?"
                params.append(material_filtro)
            else:
                # Filtrar apenas materiais válidos
                query += " WHERE material IN ('Cimento', 'Brita 0', 'Brita 1', 'Areia Média', 'Pó de Brita', 'Aditivo', 'Água')"
            
            query += " ORDER BY data_movimentacao DESC LIMIT 100"
            
            cursor.execute(query, params)
            historico = cursor.fetchall()
            conn.close()
            
            if not historico:
                QMessageBox.information(self, "Histórico", "Nenhum registro no histórico.")
                return
            
            # Criar mensagem VAZIA - apenas indicando que está zerado
            titulo = "📊 HISTÓRICO DE MOVIMENTAÇÕES"
            if material_filtro:
                titulo += f" - {material_filtro}"
            
            mensagem = f"{titulo}\n"
            mensagem += "═" * 60 + "\n\n"
            mensagem += "⚠️ HISTÓRICO ZERADO\n"
            mensagem += "Os dados do histórico foram limpos para otimização do sistema.\n\n"
            
            # Mostrar diálogo - ALTERAÇÃO: Estilo azul
            dialog = QDialog(self)
            dialog.setWindowTitle("Histórico de Estoque")
            dialog.setMinimumWidth(700)
            dialog.setMinimumHeight(500)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QTextEdit {
                    border: 2px solid #1976D2;
                    border-radius: 5px;
                    background-color: white;
                    font-family: 'Courier New';
                    font-size: 10pt;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(mensagem)
            layout.addWidget(text_edit)
            
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            buttons.accepted.connect(dialog.accept)
            buttons.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1565C0, stop:1 #0D47A1);
                    color: white;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-weight: bold;
                    border: 1px solid #0D47A1;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1976D2, stop:1 #1565C0);
                    border: 1px solid #1565C0;
                }
            """)
            layout.addWidget(buttons)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar histórico: {e}")
    
    def sincronizar_com_pesagens(self):
        """Sincroniza estoque com pesagens concluídas"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Verificar se tabela pesagens existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pesagens'")
            if not cursor.fetchone():
                QMessageBox.information(self, "Sincronização", 
                                      "Tabela de pesagens não encontrada.")
                conn.close()
                return
            
            # Buscar pesagens concluídas desde a última sincronização
            cursor.execute('''
                SELECT 
                    p.id,
                    p.data_pesagem,
                    p.traco_id,
                    p.quantidade,
                    p.materiais_json,
                    t.codigo || ' - ' || t.nome AS traco_nome
                FROM pesagens p
                LEFT JOIN tracos t ON p.traco_id = t.id
                WHERE p.status = 'CONCLUÍDO'
                AND NOT EXISTS (
                    SELECT 1 FROM historico_estoque h 
                    WHERE h.relacionamento_id = p.id
                    AND h.relacionamento_tipo = 'PESAGEM'
                )
                ORDER BY p.data_pesagem
            ''')
            
            pesagens_pendentes = cursor.fetchall()
            
            if not pesagens_pendentes:
                QMessageBox.information(self, "Sincronização", 
                                      "Todas as pesagens já estão sincronizadas!")
                conn.close()
                return
            
            # Processar cada pesagem
            total_sincronizadas = 0
            materiais_processados = []
            
            for pesagem in pesagens_pendentes:
                pesagem_id = pesagem[0]
                data_pesagem = pesagem[1]
                traco_id = pesagem[2]
                quantidade_pesagem = pesagem[3]  # Quantidade total da pesagem (ex: m³)
                materiais_json = pesagem[4]
                traco_nome = pesagem[5]
                
                # Parsear o JSON de materiais - CORREÇÃO AQUI
                materiais_data = {}
                if materiais_json:
                    try:
                        materiais_data = json.loads(materiais_json) if materiais_json else {}
                    except json.JSONDecodeError as e:
                        print(f"Erro ao parsear JSON na pesagem {pesagem_id}: {e}")
                        continue
                
                # Processar cada material (agora é um dicionário de dicionários)
                for material_nome, info_material in materiais_data.items():
                    if not isinstance(info_material, dict):
                        print(f"Formato inesperado para {material_nome}: {info_material}")
                        continue
                    
                    try:
                        # Obter quantidade do material
                        quantidade_raw = info_material.get('quantidade', 0)
                        
                        # CONVERSÃO SEGURA PARA FLOAT
                        if isinstance(quantidade_raw, str):
                            quantidade = float(quantidade_raw.replace(',', '.'))
                        else:
                            quantidade = float(quantidade_raw)
                        
                        # Ignorar se quantidade for 0 ou negativa
                        if quantidade <= 0:
                            continue
                        
                        # Verificar se material é válido (um dos 7)
                        material_corrigido = material_nome.strip()
                        
                        # Mapear nomes para os materiais padrão
                        mapeamento_materiais = {
                            'cimento': 'Cimento',
                            'cimento cp ii': 'Cimento',
                            'cimento cp-ii': 'Cimento',
                            'brita 0': 'Brita 0',
                            'brita zero': 'Brita 0',
                            'brita 1': 'Brita 1',
                            'brita um': 'Brita 1',
                            'areia': 'Areia Média',
                            'areia media': 'Areia Média',
                            'areia média': 'Areia Média',
                            'po de brita': 'Pó de Brita',
                            'pó de brita': 'Pó de Brita',
                            'po': 'Pó de Brita',
                            'aditivo': 'Aditivo',
                            'aditivo plastificante': 'Aditivo',
                            'agua': 'Água',
                            'água': 'Água',
                            'Água': 'Água'  # Já está correto, mas mantém
                        }
                        
                        chave_lower = material_corrigido.lower()
                        if chave_lower in mapeamento_materiais:
                            material_corrigido = mapeamento_materiais[chave_lower]
                        
                        # Lista dos 7 materiais válidos
                        materiais_validos = ['Cimento', 'Brita 0', 'Brita 1', 'Areia Média', 'Pó de Brita', 'Aditivo', 'Água']
                        
                        if material_corrigido not in materiais_validos:
                            print(f"Material ignorado (não é válido): {material_corrigido}")
                            continue
                        
                        # Verificar se material existe no estoque
                        cursor.execute("SELECT quantidade FROM estoque WHERE material = ?", (material_corrigido,))
                        resultado = cursor.fetchone()
                        
                        if resultado:
                            quantidade_atual = resultado[0]
                            nova_quantidade = quantidade_atual - quantidade
                            
                            # Atualizar estoque
                            cursor.execute('''
                                UPDATE estoque 
                                SET quantidade = ?,
                                    data_atualizacao = ?
                                WHERE material = ?
                            ''', (nova_quantidade, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), material_corrigido))
                            
                            # Registrar no histórico
                            cursor.execute('''
                                INSERT INTO historico_estoque 
                                (material, quantidade, tipo, destino, observacoes, 
                                 data_movimentacao, relacionamento_id, relacionamento_tipo)
                                VALUES (?, ?, 'SAIDA', ?, ?, ?, ?, ?)
                            ''', (
                                material_corrigido,
                                quantidade,
                                f"Pesagem #{pesagem_id}",
                                f"Pesagem sincronizada - {data_pesagem}",
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                pesagem_id,
                                'PESAGEM'
                            ))
                            
                            materiais_processados.append(f"{material_corrigido}: {quantidade:.2f}")
                        else:
                            print(f"Material não encontrado no estoque: {material_corrigido}")
                            
                    except (ValueError, TypeError, AttributeError) as e:
                        print(f"Erro ao processar material {material_nome} na pesagem {pesagem_id}: {e}")
                        print(f"Dados do material: {info_material}")
                        continue
                
                total_sincronizadas += 1
            
            conn.commit()
            conn.close()
            
            # Mostrar resumo
            if total_sincronizadas > 0:
                mensagem = f"✅ {total_sincronizadas} pesagens sincronizadas!\n\n"
                if materiais_processados:
                    # Agrupar por material para melhor visualização
                    resumo_materiais = {}
                    for item in materiais_processados:
                        material, qtd_str = item.split(":")
                        qtd = float(qtd_str.strip())
                        if material in resumo_materiais:
                            resumo_materiais[material] += qtd
                        else:
                            resumo_materiais[material] = qtd
                    
                    mensagem += "Materiais processados:\n"
                    for material, total_qtd in resumo_materiais.items():
                        mensagem += f"  • {material}: {total_qtd:.2f}\n"
                else:
                    mensagem += "⚠️ Nenhum material válido encontrado nas pesagens.\n"
                
                QMessageBox.information(self, "Sincronização", mensagem)
                self.carregar_estoque()
                self.atualizar_estoque_signal.emit()
            else:
                QMessageBox.information(self, "Sincronização", 
                                      "Nenhuma pesagem válida para sincronizar!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao sincronizar pesagens: {str(e)}")
            print(f"Erro detalhado na sincronização: {e}")
    
    def sincronizar_com_notas(self):
        """Sincroniza estoque com notas de entrada"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Buscar notas de entrada não processadas
            cursor.execute('''
                SELECT 
                    id, numero_nota, fornecedor, material, quantidade, unidade, data_entrada
                FROM notas_entrada 
                WHERE status = 'ATIVO'
                AND NOT EXISTS (
                    SELECT 1 FROM historico_estoque h 
                    WHERE h.relacionamento_id = notas_entrada.id 
                    AND h.relacionamento_tipo = 'NOTA_ENTRADA'
                )
                ORDER BY data_entrada
            ''')
            
            notas_pendentes = cursor.fetchall()
            
            if not notas_pendentes:
                QMessageBox.information(self, "Sincronização", 
                                      "Todas as notas já estão sincronizadas!")
                conn.close()
                return
            
            # Processar cada nota
            total_sincronizadas = 0
            
            for nota in notas_pendentes:
                nota_id, numero, fornecedor, material, quantidade, unidade, data_entrada = nota
                
                # CONVERSÃO SEGURA DE QUANTIDADE
                try:
                    if isinstance(quantidade, str):
                        quantidade_float = float(quantidade.replace(',', '.'))
                    else:
                        quantidade_float = float(quantidade)
                except (ValueError, TypeError):
                    print(f"Quantidade inválida na nota {numero}: {quantidade}")
                    continue
                
                # Verificar se material é um dos 7 válidos
                if material not in ['Cimento', 'Brita 0', 'Brita 1', 'Areia Média', 'Pó de Brita', 'Aditivo', 'Água']:
                    continue
                
                # Verificar se material existe no estoque
                cursor.execute("SELECT quantidade FROM estoque WHERE material = ?", (material,))
                resultado = cursor.fetchone()
                
                if resultado:
                    quantidade_atual = resultado[0]
                    nova_quantidade = quantidade_atual + quantidade_float
                else:
                    # Criar novo material no estoque (apenas se for um dos 7 válidos)
                    nova_quantidade = quantidade_float
                    cursor.execute('''
                        INSERT INTO estoque (material, quantidade, unidade, data_atualizacao)
                        VALUES (?, ?, ?, ?)
                    ''', (material, quantidade_float, unidade, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                # Atualizar estoque
                cursor.execute('''
                    UPDATE estoque 
                    SET quantidade = ?,
                        data_atualizacao = ?
                    WHERE material = ?
                ''', (nova_quantidade, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), material))
                
                # Registrar no histórico
                cursor.execute('''
                    INSERT INTO historico_estoque 
                    (material, quantidade, tipo, destino, observacoes, 
                     data_movimentacao, relacionamento_id, relacionamento_tipo)
                    VALUES (?, ?, 'ENTRADA', ?, ?, ?, ?, ?)
                ''', (
                    material,
                    quantidade_float,
                    f"Nota #{numero}",
                    f"Fornecedor: {fornecedor}",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    nota_id,
                    'NOTA_ENTRADA'
                ))
                
                # Marcar nota como processada
                cursor.execute("UPDATE notas_entrada SET status = 'PROCESSADO' WHERE id = ?", (nota_id,))
                
                total_sincronizadas += 1
            
            conn.commit()
            conn.close()
            
            if total_sincronizadas > 0:
                QMessageBox.information(self, "Sincronização", 
                                      f"✅ {total_sincronizadas} notas de entrada sincronizadas!")
                self.carregar_estoque()
                self.atualizar_estoque_signal.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao sincronizar notas: {str(e)}")
    
    def exibir_relatorio_consumo(self):
        """Exibe relatório de consumo por período - ZERADO"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Obter data de 30 dias atrás
            data_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Apenas materiais válidos
            cursor.execute('''
                SELECT 
                    h.material,
                    SUM(CASE WHEN h.tipo = 'SAIDA' THEN h.quantidade ELSE 0 END) as saidas,
                    SUM(CASE WHEN h.tipo = 'ENTRADA' THEN h.quantidade ELSE 0 END) as entradas,
                    e.unidade
                FROM historico_estoque h
                LEFT JOIN estoque e ON h.material = e.material
                WHERE h.data_movimentacao >= ?
                AND h.material IN ('Cimento', 'Brita 0', 'Brita 1', 'Areia Média', 'Pó de Brita', 'Aditivo', 'Água')
                GROUP BY h.material
                ORDER BY saidas DESC
            ''', (data_inicio,))
            
            consumo = cursor.fetchall()
            
            # Estatísticas gerais apenas para materiais válidos
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT CASE WHEN tipo = 'SAIDA' AND destino LIKE '%Pesagem%' THEN relacionamento_id END) as pesagens,
                    COUNT(DISTINCT CASE WHEN tipo = 'ENTRADA' AND destino LIKE '%Nota%' THEN relacionamento_id END) as notas,
                    SUM(CASE WHEN tipo = 'SAIDA' THEN quantidade ELSE 0 END) as total_saidas,
                    SUM(CASE WHEN tipo = 'ENTRADA' THEN quantidade ELSE 0 END) as total_entradas
                FROM historico_estoque 
                WHERE data_movimentacao >= ?
                AND material IN ('Cimento', 'Brita 0', 'Brita 1', 'Areia Média', 'Pó de Brita', 'Aditivo', 'Água')
            ''', (data_inicio,))
            
            stats = cursor.fetchone()
            conn.close()
            
            # Gerar relatório VAZIO
            relatorio = "📊 RELATÓRIO DE CONSUMO (ÚLTIMOS 30 DIAS)\n"
            relatorio += "═" * 60 + "\n\n"
            relatorio += "⚠️ RELATÓRIO ZERADO\n"
            relatorio += "Os dados do relatório foram limpos para otimização do sistema.\n\n"
            relatorio += "📈 Estatísticas Gerais:\n"
            relatorio += f"   • Pesagens processadas: {stats[0] or 0}\n"
            relatorio += f"   • Notas de entrada: {stats[1] or 0}\n"
            relatorio += f"   • Total de entradas: 0.00\n"
            relatorio += f"   • Total de saídas: 0.00\n"
            relatorio += f"   • Saldo líquido: 0.00\n\n"
            relatorio += f"📦 Consumo por Material:\n"
            relatorio += "   • Dados de consumo não disponíveis\n"
            
            # Mostrar diálogo - ALTERAÇÃO: Estilo azul
            dialog = QDialog(self)
            dialog.setWindowTitle("Relatório de Consumo")
            dialog.setMinimumWidth(600)
            dialog.setMinimumHeight(500)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QTextEdit {
                    border: 2px solid #1976D2;
                    border-radius: 5px;
                    background-color: white;
                    font-family: 'Courier New';
                    font-size: 10pt;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(relatorio)
            layout.addWidget(text_edit)
            
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            buttons.accepted.connect(dialog.accept)
            buttons.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1565C0, stop:1 #0D47A1);
                    color: white;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-weight: bold;
                    border: 1px solid #0D47A1;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1976D2, stop:1 #1565C0);
                    border: 1px solid #1565C0;
                }
            """)
            layout.addWidget(buttons)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar relatório: {str(e)}")
    
    def apagar_historico(self):
        """Apaga todo o histórico de movimentações"""
        resposta = QMessageBox.question(
            self, 
            "Apagar Histórico", 
            "⚠️ ATENÇÃO: Esta ação irá apagar TODO o histórico de movimentações!\n\n"
            "Isso inclui:\n"
            "• Todas as saídas registradas\n"
            "• Todas as entradas de notas\n"
            "• Todos os ajustes manuais\n"
            "• Todas as sincronizações de pesagens\n\n"
            "Esta ação NÃO PODE ser desfeita!\n"
            "Deseja continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect('usina_concreto.db')
                cursor = conn.cursor()
                
                # Apagar todo o histórico
                cursor.execute("DELETE FROM historico_estoque")
                
                # Reiniciar o contador do ID (opcional, para manter o banco organizado)
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='historico_estoque'")
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(
                    self, 
                    "Histórico Apagado", 
                    "✅ Todo o histórico de movimentações foi apagado com sucesso!\n\n"
                    "O sistema agora começará com histórico limpo."
                )
                
                # Atualizar a interface se necessário
                self.carregar_estoque()
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao apagar histórico: {e}")
    
    def zerar_estoque(self):
        """Zera o estoque do material selecionado"""
        linha = self.tabela_estoque.currentRow()
        if linha >= 0:
            material = self.tabela_estoque.item(linha, 0).text()
            quantidade_atual = float(self.tabela_estoque.item(linha, 1).text())
            
            if quantidade_atual == 0:
                QMessageBox.information(self, "Zerar Estoque", 
                                      f"O estoque de {material} já está zerado.")
                return
            
            resposta = QMessageBox.question(
                self, 
                "Zerar Estoque", 
                f"Tem certeza que deseja zerar o estoque de {material}?\n\n"
                f"Quantidade atual: {quantidade_atual:.2f}\n"
                f"Esta ação registrará uma saída no histórico.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if resposta == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect('usina_concreto.db')
                    cursor = conn.cursor()
                    
                    # Zerar estoque
                    cursor.execute('''
                        UPDATE estoque 
                        SET quantidade = 0,
                            data_atualizacao = ?
                        WHERE material = ?
                    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), material))
                    
                    # Registrar no histórico
                    cursor.execute('''
                        INSERT INTO historico_estoque 
                        (material, quantidade, tipo, destino, observacoes, data_movimentacao)
                        VALUES (?, ?, 'SAIDA', 'ZERAGEM MANUAL', 'Estoque zerado manualmente', ?)
                    ''', (material, quantidade_atual, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Sucesso", 
                                          f"Estoque de {material} zerado com sucesso.")
                    self.carregar_estoque()
                    self.atualizar_estoque_signal.emit()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao zerar estoque: {e}")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um material para zerar!")
    
    def ajuste_estoque(self):
        """Função para ajuste manual de estoque"""
        linha = self.tabela_estoque.currentRow()
        if linha >= 0:
            material = self.tabela_estoque.item(linha, 0).text()
            quantidade_atual = float(self.tabela_estoque.item(linha, 1).text())
            unidade = self.tabela_estoque.item(linha, 2).text()
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Ajuste de Estoque - {material}")
            dialog.setModal(True)
            dialog.setMinimumWidth(400)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QLabel {
                    color: #333333;
                    font-weight: bold;
                }
                QDoubleSpinBox, QLineEdit {
                    border: 2px solid #1976D2;
                    border-radius: 5px;
                    padding: 5px;
                    background-color: white;
                }
                QDoubleSpinBox:hover, QLineEdit:hover {
                    border: 2px solid #0D47A1;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            form = QFormLayout()
            
            label_atual = QLabel(f"Estoque atual: {quantidade_atual:.2f} {unidade}")
            label_atual.setStyleSheet("color: #0D47A1; font-weight: bold;")
            
            input_novo = QDoubleSpinBox()
            input_novo.setRange(0, 1000000)
            input_novo.setValue(quantidade_atual)
            input_novo.setDecimals(2)
            input_novo.setSuffix(f" {unidade}")
            
            input_observacoes = QLineEdit()
            input_observacoes.setPlaceholderText("Motivo do ajuste...")
            
            form.addRow("Estoque atual:", label_atual)
            form.addRow("Novo valor:", input_novo)
            form.addRow("Observações:", input_observacoes)
            
            layout.addLayout(form)
            
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            
            buttons.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1565C0, stop:1 #0D47A1);
                    color: white;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-weight: bold;
                    border: 1px solid #0D47A1;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1976D2, stop:1 #1565C0);
                    border: 1px solid #1565C0;
                }
            """)
            
            def aplicar_ajuste():
                novo_valor = input_novo.value()
                diferenca = novo_valor - quantidade_atual
                
                if diferenca == 0:
                    QMessageBox.warning(dialog, "Aviso", "O valor não foi alterado!")
                    return
                
                tipo = "ENTRADA" if diferenca > 0 else "SAIDA"
                
                try:
                    conn = sqlite3.connect('usina_concreto.db')
                    cursor = conn.cursor()
                    
                    # Atualizar estoque
                    cursor.execute('''
                        UPDATE estoque 
                        SET quantidade = ?,
                            data_atualizacao = ?
                        WHERE material = ?
                    ''', (novo_valor, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), material))
                    
                    # Registrar no histórico
                    cursor.execute('''
                        INSERT INTO historico_estoque 
                        (material, quantidade, tipo, destino, observacoes, data_movimentacao)
                        VALUES (?, ?, ?, 'AJUSTE MANUAL', ?, ?)
                    ''', (
                        material,
                        abs(diferenca),
                        tipo,
                        input_observacoes.text(),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(dialog, "Sucesso", "Ajuste aplicado com sucesso!")
                    dialog.accept()
                    self.carregar_estoque()
                    self.atualizar_estoque_signal.emit()
                    
                except Exception as e:
                    QMessageBox.critical(dialog, "Erro", f"Erro ao aplicar ajuste: {e}")
            
            buttons.accepted.connect(aplicar_ajuste)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            dialog.exec()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione um material para ajustar!")