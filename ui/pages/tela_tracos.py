# ui/pages/tela_tracos.py
import sys
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon

class TelaTracos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db_path = 'usina_concreto.db'
        self.todos_tracos = []  # Para armazenar todos os traços
        self.init_ui()
        self.criar_tabela()
        self.carregar_tracos()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("📐 GERENCIAMENTO DE TRAÇOS - USINA BETTO MIX CONCRETO")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            color: white;
            background-color: #0D47A1;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        layout.addWidget(titulo)
        
        # Barra de ferramentas
        toolbar = QHBoxLayout()
        
        # Botões de ação
        self.btn_novo = QPushButton("➕ Novo Traço")
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_excluir = QPushButton("🗑️ Excluir")
        self.btn_atualizar = QPushButton("🔄 Atualizar")
        self.btn_detalhes = QPushButton("👁️ Detalhes")
        
        # Estilo dos botões
        for btn in [self.btn_novo, self.btn_editar, self.btn_excluir, self.btn_atualizar, self.btn_detalhes]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                      stop: 0 #1976D2, stop: 1 #1565C0);
                    color: white;
                    border: 1px solid #0D47A1;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 10px;
                    margin-right: 5px;
                }
                QPushButton:hover {
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                      stop: 0 #1565C0, stop: 1 #0D47A1);
                }
                QPushButton:disabled {
                    background-color: #90A4AE;
                }
            """)
        
        # Adiciona botões à barra de ferramentas
        toolbar.addWidget(self.btn_novo)
        toolbar.addWidget(self.btn_editar)
        toolbar.addWidget(self.btn_excluir)
        toolbar.addWidget(self.btn_atualizar)
        toolbar.addWidget(self.btn_detalhes)
        
        # Filtro rápido
        filtro_layout = QHBoxLayout()
        
        # Label
        filtro_label = QLabel("Filtrar por código:")
        filtro_label.setStyleSheet("color: #0D47A1; font-weight: bold; margin-left: 10px;")
        filtro_layout.addWidget(filtro_label)
        
        # Campo código inicial
        self.filtro_codigo_inicio = QSpinBox()
        self.filtro_codigo_inicio.setRange(1, 99999)
        self.filtro_codigo_inicio.setValue(1)
        self.filtro_codigo_inicio.setFixedHeight(35)
        self.filtro_codigo_inicio.setStyleSheet("""
            QSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        filtro_layout.addWidget(self.filtro_codigo_inicio)
        
        # Label "até"
        label_ate = QLabel("até")
        label_ate.setStyleSheet("color: #0D47A1; padding: 0 5px;")
        filtro_layout.addWidget(label_ate)
        
        # Campo código final
        self.filtro_codigo_fim = QSpinBox()
        self.filtro_codigo_fim.setRange(1, 99999)
        self.filtro_codigo_fim.setValue(99999)
        self.filtro_codigo_fim.setFixedHeight(35)
        self.filtro_codigo_fim.setStyleSheet("""
            QSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        filtro_layout.addWidget(self.filtro_codigo_fim)
        
        # Botão aplicar filtro
        self.btn_aplicar_filtro = QPushButton("🔍 Aplicar")
        self.btn_aplicar_filtro.setFixedHeight(35)
        self.btn_aplicar_filtro.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #4CAF50, stop: 1 #2E7D32);
                color: white;
                border: 1px solid #2E7D32;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #2E7D32, stop: 1 #1B5E20);
            }
        """)
        filtro_layout.addWidget(self.btn_aplicar_filtro)
        
        # Botão limpar filtro
        self.btn_limpar_filtro = QPushButton("🗑️ Limpar")
        self.btn_limpar_filtro.setFixedHeight(35)
        self.btn_limpar_filtro.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #F44336, stop: 1 #C62828);
                color: white;
                border: 1px solid #C62828;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #C62828, stop: 1 #B71C1C);
            }
        """)
        filtro_layout.addWidget(self.btn_limpar_filtro)
        
        toolbar.addLayout(filtro_layout)
        
        # Campo de busca por nome
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("🔍 Buscar por nome...")
        self.busca_input.setFixedHeight(40)
        self.busca_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #2196F3;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1976D2;
            }
        """)
        toolbar.addWidget(self.busca_input)
        
        layout.addLayout(toolbar)
        
        # Tabela de traços - COM 13 COLUNAS (incluindo Volume)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(13)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Código", "Nome", "fck (MPa)", "Cimento", 
            "Brita 0", "Brita 1", "Areia média", "Pó de Brita", 
            "Água", "Aditivo", "Volume (m³)", "Status"
        ])
        
        # Configurar tabela
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Ajustar colunas
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Código
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Nome
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # fck
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Cimento
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Brita 0
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Brita 1
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Areia média
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Pó de Brita
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Água
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.ResizeToContents) # Aditivo
        header.setSectionResizeMode(11, QHeaderView.ResizeMode.ResizeToContents) # Volume (m³)
        header.setSectionResizeMode(12, QHeaderView.ResizeMode.ResizeToContents) # Status
        
        # Estilo da tabela
        self.tabela.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #1976D2;
                gridline-color: #BBDEFB;
                alternate-background-color: #E3F2FD;
                selection-background-color: #BBDEFB;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #BBDEFB;
                color: black;
            }
            QHeaderView::section {
                background-color: #0D47A1;
                color: white;
                padding: 5px;
                border: 1px solid #0D47A1;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.tabela)
        
        # Status
        self.status_label = QLabel("Total de traços: 0")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #0D47A1; padding: 5px; background-color: #E3F2FD; border-radius: 5px; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Conectar sinais
        self.btn_novo.clicked.connect(self.novo_traco)
        self.btn_editar.clicked.connect(self.editar_traco)
        self.btn_excluir.clicked.connect(self.excluir_traco)
        self.btn_atualizar.clicked.connect(self.carregar_tracos)
        self.btn_detalhes.clicked.connect(self.ver_detalhes)
        self.busca_input.textChanged.connect(self.filtrar_tracos_por_nome)
        self.tabela.doubleClicked.connect(self.ver_detalhes)
        self.btn_aplicar_filtro.clicked.connect(self.aplicar_filtro_codigo)
        self.btn_limpar_filtro.clicked.connect(self.limpar_filtro_codigo)
        
    def criar_tabela(self):
        """Cria ou recria a tabela de traços no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Primeiro, verificar se a tabela existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracos'")
            tabela_existe = cursor.fetchone()
            
            if tabela_existe:
                # Verificar a estrutura atual da tabela
                cursor.execute("PRAGMA table_info(tracos)")
                colunas = cursor.fetchall()
                colunas_nomes = [coluna[1] for coluna in colunas]
                
                # Verificar se a coluna 'aditivo' existe, se não, adicionar
                if 'aditivo' not in colunas_nomes:
                    try:
                        cursor.execute("ALTER TABLE tracos ADD COLUMN aditivo REAL DEFAULT 0")
                        print("✅ Coluna 'aditivo' adicionada à tabela tracos")
                    except Exception as e:
                        print(f"❌ Erro ao adicionar coluna aditivo: {e}")
                
                # Verificar se a coluna 'po_brita' existe, se não, adicionar
                if 'po_brita' not in colunas_nomes:
                    try:
                        cursor.execute("ALTER TABLE tracos ADD COLUMN po_brita REAL DEFAULT 0")
                        print("✅ Coluna 'po_brita' adicionada à tabela tracos")
                    except Exception as e:
                        print(f"❌ Erro ao adicionar coluna po_brita: {e}")
                        
                # Verificar se a coluna 'volume_m3' existe, se não, adicionar
                if 'volume_m3' not in colunas_nomes:
                    try:
                        cursor.execute("ALTER TABLE tracos ADD COLUMN volume_m3 REAL DEFAULT 0.5")
                        print("✅ Coluna 'volume_m3' adicionada à tabela tracos")
                    except Exception as e:
                        print(f"❌ Erro ao adicionar coluna volume_m3: {e}")
                
                print("✅ Tabela 'tracos' já existe com estrutura verificada")
            else:
                # Criar nova tabela
                print("📋 Criando nova tabela 'tracos'...")
                cursor.execute("""
                    CREATE TABLE tracos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo INTEGER NOT NULL UNIQUE,
                        nome TEXT NOT NULL,
                        descricao TEXT,
                        fck INTEGER DEFAULT 20,
                        cimento REAL DEFAULT 0,
                        brita0 REAL DEFAULT 0,
                        brita1 REAL DEFAULT 0,
                        areia_media REAL DEFAULT 0,
                        po_brita REAL DEFAULT 0,
                        agua REAL DEFAULT 0,
                        aditivo REAL DEFAULT 0,
                        slump TEXT,
                        tipo_brita TEXT,
                        status TEXT DEFAULT 'ATIVO',
                        volume_m3 REAL DEFAULT 0.5,
                        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✅ Tabela 'tracos' criada com sucesso")
            
            conn.commit()
            conn.close()
            print("✅ Tabela 'tracos' verificada/criada com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao acessar banco de dados:\n{str(e)}")
    
    def carregar_tracos(self):
        """Carrega os traços do banco de dados para a tabela em ORDEM DECRESCENTE por código"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se as colunas existem antes de consultar
            cursor.execute("PRAGMA table_info(tracos)")
            colunas = cursor.fetchall()
            colunas_nomes = [coluna[1] for coluna in colunas]
            
            # Definir as colunas que queremos selecionar
            colunas_selecionar = []
            if 'id' in colunas_nomes:
                colunas_selecionar.append('id')
            if 'codigo' in colunas_nomes:
                colunas_selecionar.append('codigo')
            if 'nome' in colunas_nomes:
                colunas_selecionar.append('nome')
            if 'fck' in colunas_nomes:
                colunas_selecionar.append('fck')
            if 'cimento' in colunas_nomes:
                colunas_selecionar.append('cimento')
            if 'brita0' in colunas_nomes:
                colunas_selecionar.append('brita0')
            if 'brita1' in colunas_nomes:
                colunas_selecionar.append('brita1')
            if 'areia_media' in colunas_nomes:
                colunas_selecionar.append('areia_media')
            if 'po_brita' in colunas_nomes:
                colunas_selecionar.append('po_brita')
            if 'agua' in colunas_nomes:
                colunas_selecionar.append('agua')
            if 'aditivo' in colunas_nomes:
                colunas_selecionar.append('aditivo')
            if 'volume_m3' in colunas_nomes:
                colunas_selecionar.append('volume_m3')
            if 'status' in colunas_nomes:
                colunas_selecionar.append('status')
            
            if not colunas_selecionar:
                print("❌ Nenhuma coluna encontrada na tabela tracos")
                conn.close()
                return
            
            # Ordenar por código em ORDEM DECRESCENTE
            query = f"SELECT {', '.join(colunas_selecionar)} FROM tracos ORDER BY codigo DESC"
            cursor.execute(query)
            
            self.todos_tracos = cursor.fetchall()
            conn.close()
            
            # Configurar tabela com o número correto de colunas
            num_colunas = len(colunas_selecionar)
            self.tabela.setColumnCount(num_colunas)
            
            # Definir cabeçalhos baseado nas colunas disponíveis
            headers = []
            for col in colunas_selecionar:
                if col == 'id':
                    headers.append("ID")
                elif col == 'codigo':
                    headers.append("Código")
                elif col == 'nome':
                    headers.append("Nome")
                elif col == 'fck':
                    headers.append("fck (MPa)")
                elif col == 'cimento':
                    headers.append("Cimento")
                elif col == 'brita0':
                    headers.append("Brita 0")
                elif col == 'brita1':
                    headers.append("Brita 1")
                elif col == 'areia_media':
                    headers.append("Areia média")
                elif col == 'po_brita':
                    headers.append("Pó de Brita")
                elif col == 'agua':
                    headers.append("Água")
                elif col == 'aditivo':
                    headers.append("Aditivo")
                elif col == 'volume_m3':
                    headers.append("Volume (m³)")
                elif col == 'status':
                    headers.append("Status")
            
            self.tabela.setHorizontalHeaderLabels(headers)
            
            # Atualizar tabela com todos os traços
            self.atualizar_tabela(self.todos_tracos)
            
            # Atualizar status
            self.status_label.setText(f"Total de traços: {len(self.todos_tracos)} | Ordenação: Código Decrescente")
            print(f"✅ {len(self.todos_tracos)} traços carregados do banco (ordem decrescente por código)")
            
        except Exception as e:
            print(f"❌ Erro ao carregar traços: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar traços:\n{str(e)}")
    
    def atualizar_tabela(self, tracos):
        """Atualiza a tabela com os traços fornecidos"""
        self.tabela.setRowCount(len(tracos))
        
        for row, traco in enumerate(tracos):
            for col, value in enumerate(traco):
                item = QTableWidgetItem(str(value))
                
                # Formatar valores numéricos
                if col == 4:  # Cimento
                    try:
                        valor_float = float(value)
                        item.setText(f"{valor_float:.2f}")
                    except (ValueError, TypeError):
                        pass
                elif col in [5, 6, 7, 8, 10]:  # Brita 0, Brita 1, Areia média, Pó de Brita, Aditivo
                    try:
                        valor_float = float(value)
                        item.setText(f"{valor_float:.2f}")
                    except (ValueError, TypeError):
                        pass
                elif col == 9:  # Água
                    try:
                        valor_float = float(value)
                        item.setText(f"{valor_float:.2f}")
                    except (ValueError, TypeError):
                        pass
                elif col == 11:  # Volume (m³)
                    try:
                        valor_float = float(value)
                        item.setText(f"{valor_float:.2f}")
                    except (ValueError, TypeError):
                        pass
                
                # Colorir status (última coluna)
                if col == len(traco) - 1:  # Status é a última coluna
                    if value == 'ATIVO':
                        item.setForeground(QColor(46, 125, 50))  # Verde escuro
                    elif value == 'INATIVO':
                        item.setForeground(QColor(198, 40, 40))  # Vermelho escuro
                
                self.tabela.setItem(row, col, item)
    
    def aplicar_filtro_codigo(self):
        """Aplica filtro por código"""
        codigo_inicio = self.filtro_codigo_inicio.value()
        codigo_fim = self.filtro_codigo_fim.value()
        
        if codigo_inicio > codigo_fim:
            QMessageBox.warning(self, "Atenção", "O código inicial não pode ser maior que o código final!")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se as colunas existem antes de consultar
            cursor.execute("PRAGMA table_info(tracos)")
            colunas = cursor.fetchall()
            colunas_nomes = [coluna[1] for coluna in colunas]
            
            # Definir as colunas que queremos selecionar
            colunas_selecionar = []
            if 'id' in colunas_nomes:
                colunas_selecionar.append('id')
            if 'codigo' in colunas_nomes:
                colunas_selecionar.append('codigo')
            if 'nome' in colunas_nomes:
                colunas_selecionar.append('nome')
            if 'fck' in colunas_nomes:
                colunas_selecionar.append('fck')
            if 'cimento' in colunas_nomes:
                colunas_selecionar.append('cimento')
            if 'brita0' in colunas_nomes:
                colunas_selecionar.append('brita0')
            if 'brita1' in colunas_nomes:
                colunas_selecionar.append('brita1')
            if 'areia_media' in colunas_nomes:
                colunas_selecionar.append('areia_media')
            if 'po_brita' in colunas_nomes:
                colunas_selecionar.append('po_brita')
            if 'agua' in colunas_nomes:
                colunas_selecionar.append('agua')
            if 'aditivo' in colunas_nomes:
                colunas_selecionar.append('aditivo')
            if 'volume_m3' in colunas_nomes:
                colunas_selecionar.append('volume_m3')
            if 'status' in colunas_nomes:
                colunas_selecionar.append('status')
            
            if not colunas_selecionar:
                print("❌ Nenhuma coluna encontrada na tabela tracos")
                conn.close()
                return
            
            # Filtrar por código e ordenar decrescente
            query = f"SELECT {', '.join(colunas_selecionar)} FROM tracos WHERE codigo BETWEEN ? AND ? ORDER BY codigo DESC"
            cursor.execute(query, (codigo_inicio, codigo_fim))
            
            tracos_filtrados = cursor.fetchall()
            conn.close()
            
            # Atualizar tabela com traços filtrados
            self.atualizar_tabela(tracos_filtrados)
            
            # Atualizar status
            self.status_label.setText(f"Traços filtrados: {len(tracos_filtrados)} | Código: {codigo_inicio} a {codigo_fim} | Ordenação: Decrescente")
            print(f"✅ {len(tracos_filtrados)} traços filtrados por código {codigo_inicio} a {codigo_fim}")
            
        except Exception as e:
            print(f"❌ Erro ao filtrar traços: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao filtrar traços:\n{str(e)}")
    
    def limpar_filtro_codigo(self):
        """Limpa o filtro por código e mostra todos os traços"""
        self.filtro_codigo_inicio.setValue(1)
        self.filtro_codigo_fim.setValue(99999)
        self.busca_input.clear()
        self.carregar_tracos()
    
    def filtrar_tracos_por_nome(self, texto):
        """Filtra os traços por nome (busca local)"""
        texto = texto.lower()
        
        if texto == "":
            # Se campo vazio, mostra todos os traços
            self.atualizar_tabela(self.todos_tracos)
            self.status_label.setText(f"Total de traços: {len(self.todos_tracos)} | Ordenação: Código Decrescente")
            return
        
        # Filtrar localmente
        tracos_filtrados = []
        for traco in self.todos_tracos:
            # Verificar se o texto está no nome (coluna 2)
            if texto in str(traco[2]).lower():
                tracos_filtrados.append(traco)
        
        # Atualizar tabela com traços filtrados
        self.atualizar_tabela(tracos_filtrados)
        
        # Atualizar status
        self.status_label.setText(f"Traços encontrados: {len(tracos_filtrados)} | Busca: '{texto}' | Ordenação: Decrescente")
    
    def novo_traco(self):
        """Abre o formulário para cadastrar novo traço"""
        dialog = DialogTraco(self)
        if dialog.exec():
            self.carregar_tracos()
    
    def editar_traco(self):
        """Edita o traço selecionado"""
        selected_row = self.tabela.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um traço para editar!")
            return
        
        # Obter ID do traço selecionado
        item_id = self.tabela.item(selected_row, 0)
        if not item_id:
            QMessageBox.warning(self, "Erro", "Não foi possível obter o ID do traço selecionado!")
            return
        
        traco_id = item_id.text()
        dialog = DialogTraco(self, traco_id)
        if dialog.exec():
            self.carregar_tracos()
    
    def excluir_traco(self):
        """Exclui o traço selecionado"""
        selected_row = self.tabela.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um traço para excluir!")
            return
        
        # Obter ID e nome do traço selecionado
        item_id = self.tabela.item(selected_row, 0)
        item_nome = self.tabela.item(selected_row, 2)  # Nome está na coluna 2
        
        if not item_id or not item_nome:
            QMessageBox.warning(self, "Erro", "Não foi possível obter informações do traço selecionado!")
            return
        
        traco_id = item_id.text()
        traco_nome = item_nome.text()
        
        # Confirmação
        reply = QMessageBox.question(
            self, 'Confirmar Exclusão',
            f'Tem certeza que deseja excluir o traço:\n"{traco_nome}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tracos WHERE id = ?", (traco_id,))
                conn.commit()
                conn.close()
                
                self.carregar_tracos()
                QMessageBox.information(self, "Sucesso", f"Traço '{traco_nome}' excluído com sucesso!")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir traço:\n{str(e)}")
    
    def ver_detalhes(self):
        """Mostra detalhes do traço selecionado"""
        selected_row = self.tabela.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um traço para ver detalhes!")
            return
        
        # Obter ID do traço selecionado
        item_id = self.tabela.item(selected_row, 0)
        if not item_id:
            QMessageBox.warning(self, "Erro", "Não foi possível obter o ID do traço selecionado!")
            return
        
        traco_id = item_id.text()
        dialog = DialogDetalhesTraco(self, traco_id)
        dialog.exec()


class DialogTraco(QDialog):
    """Diálogo para cadastrar/editar traço"""
    def __init__(self, parent=None, traco_id=None):
        super().__init__(parent)
        self.parent = parent
        self.traco_id = traco_id
        self.setModal(True)
        
        if traco_id:
            self.setWindowTitle("✏️ Editar Traço")
            self.carregar_dados()
        else:
            self.setWindowTitle("➕ Novo Traço")
            
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(10)
        
        # Código
        self.codigo_input = QSpinBox()
        self.codigo_input.setRange(1, 99999)
        self.codigo_input.setStyleSheet("""
            QSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        form.addRow("Código:", self.codigo_input)
        
        # Nome
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Ex: fck 40 MPa  B0+1  120+-20 mm")
        self.nome_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1976D2;
            }
        """)
        form.addRow("Nome:", self.nome_input)
        
        # Descrição
        self.descricao_input = QTextEdit()
        self.descricao_input.setMaximumHeight(80)
        self.descricao_input.setPlaceholderText("Descrição do traço...")
        self.descricao_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QTextEdit:focus {
                border: 2px solid #1976D2;
            }
        """)
        form.addRow("Descrição:", self.descricao_input)
        
        # Resistência fck
        self.fck_spin = QSpinBox()
        self.fck_spin.setRange(5, 100)
        self.fck_spin.setValue(20)
        self.fck_spin.setSuffix(" MPa")
        self.fck_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        form.addRow("Resistência (fck):", self.fck_spin)
        
        # Slump
        self.slump_input = QLineEdit()
        self.slump_input.setPlaceholderText("Ex: 120+-20 mm")
        self.slump_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1976D2;
            }
        """)
        form.addRow("Slump:", self.slump_input)
        
        # Tipo de Brita
        self.tipo_brita_combo = QComboBox()
        self.tipo_brita_combo.addItems(["B0", "B1", "B0+1"])
        self.tipo_brita_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        form.addRow("Tipo de Brita:", self.tipo_brita_combo)
        
        # Volume do traço (m³)
        self.volume_m3_spin = QDoubleSpinBox()
        self.volume_m3_spin.setRange(0.1, 10.0)
        self.volume_m3_spin.setValue(0.5)
        self.volume_m3_spin.setSingleStep(0.5)
        self.volume_m3_spin.setSuffix(" m³")
        self.volume_m3_spin.setDecimals(2)
        self.volume_m3_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        form.addRow("Volume do traço:", self.volume_m3_spin)
        
        # Grupo de composição
        comp_group = QGroupBox("Composição (para o volume especificado acima)")
        comp_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 10px;
                background-color: #E3F2FD;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        comp_layout = QFormLayout()
        
        # Cimento
        self.cimento_spin = QDoubleSpinBox()
        self.cimento_spin.setRange(0, 10000)
        self.cimento_spin.setValue(30000)
        self.cimento_spin.setSuffix(" kg")
        self.cimento_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        comp_layout.addRow("Cimento:", self.cimento_spin)
        
        # Brita 0
        self.brita0_spin = QDoubleSpinBox()
        self.brita0_spin.setRange(0, 20000)
        self.brita0_spin.setValue(10000)
        self.brita0_spin.setSuffix(" kg")
        self.brita0_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        comp_layout.addRow("Brita 0:", self.brita0_spin)
        
        # Brita 1
        self.brita1_spin = QDoubleSpinBox()
        self.brita1_spin.setRange(0, 20000)
        self.brita1_spin.setValue(30000)
        self.brita1_spin.setSuffix(" kg")
        self.brita1_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        comp_layout.addRow("Brita 1:", self.brita1_spin)
        
        # Areia média
        self.areia_media_spin = QDoubleSpinBox()
        self.areia_media_spin.setRange(0, 20000)
        self.areia_media_spin.setValue(8000)
        self.areia_media_spin.setSuffix(" kg")
        self.areia_media_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        comp_layout.addRow("Areia média:", self.areia_media_spin)
        
        # Pó de Brita
        self.po_brita_spin = QDoubleSpinBox()
        self.po_brita_spin.setRange(0, 20000)
        self.po_brita_spin.setValue(30000)
        self.po_brita_spin.setSuffix(" kg")
        self.po_brita_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        comp_layout.addRow("Pó de Brita:", self.po_brita_spin)
        
        # Água
        self.agua_spin = QDoubleSpinBox()
        self.agua_spin.setRange(0, 50000)
        self.agua_spin.setValue(18000)
        self.agua_spin.setSuffix(" L")
        self.agua_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        comp_layout.addRow("Água:", self.agua_spin)
        
        # Aditivo
        self.aditivo_spin = QDoubleSpinBox()
        self.aditivo_spin.setRange(0, 50000)
        self.aditivo_spin.setValue(20000)
        self.aditivo_spin.setSuffix(" kg")
        self.aditivo_spin.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        comp_layout.addRow("Aditivo:", self.aditivo_spin)
        
        comp_group.setLayout(comp_layout)
        form.addRow(comp_group)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["ATIVO", "INATIVO"])
        self.status_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 3px;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #1976D2;
            }
        """)
        form.addRow("Status:", self.status_combo)
        
        layout.addLayout(form)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.btn_salvar = QPushButton("💾 Salvar")
        self.btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #1976D2, stop: 1 #1565C0);
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #1565C0, stop: 1 #0D47A1);
            }
        """)
        self.btn_salvar.clicked.connect(self.salvar)
        
        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #1976D2, stop: 1 #1565C0);
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #1565C0, stop: 1 #0D47A1);
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_salvar)
        button_layout.addWidget(self.btn_cancelar)
        
        layout.addLayout(button_layout)
        
    def carregar_dados(self):
        """Carrega os dados do traço para edição"""
        try:
            conn = sqlite3.connect(self.parent.db_path)
            cursor = conn.cursor()
            
            # Verificar quais colunas existem
            cursor.execute("PRAGMA table_info(tracos)")
            colunas = cursor.fetchall()
            colunas_nomes = [coluna[1] for coluna in colunas]
            
            # Construir query dinamicamente
            colunas_selecionar = []
            if 'codigo' in colunas_nomes:
                colunas_selecionar.append('codigo')
            if 'nome' in colunas_nomes:
                colunas_selecionar.append('nome')
            if 'descricao' in colunas_nomes:
                colunas_selecionar.append('descricao')
            if 'fck' in colunas_nomes:
                colunas_selecionar.append('fck')
            if 'slump' in colunas_nomes:
                colunas_selecionar.append('slump')
            if 'tipo_brita' in colunas_nomes:
                colunas_selecionar.append('tipo_brita')
            if 'volume_m3' in colunas_nomes:
                colunas_selecionar.append('volume_m3')
            if 'cimento' in colunas_nomes:
                colunas_selecionar.append('cimento')
            if 'brita0' in colunas_nomes:
                colunas_selecionar.append('brita0')
            if 'brita1' in colunas_nomes:
                colunas_selecionar.append('brita1')
            if 'areia_media' in colunas_nomes:
                colunas_selecionar.append('areia_media')
            if 'po_brita' in colunas_nomes:
                colunas_selecionar.append('po_brita')
            if 'agua' in colunas_nomes:
                colunas_selecionar.append('agua')
            if 'aditivo' in colunas_nomes:
                colunas_selecionar.append('aditivo')
            if 'status' in colunas_nomes:
                colunas_selecionar.append('status')
            
            if colunas_selecionar:
                query = f"SELECT {', '.join(colunas_selecionar)} FROM tracos WHERE id = ?"
                cursor.execute(query, (self.traco_id,))
                dados = cursor.fetchone()
                
                if dados:
                    idx = 0
                    if 'codigo' in colunas_nomes:
                        valor = dados[idx]
                        # CONVERTER para inteiro, mesmo que seja float ou string
                        try:
                            if valor is not None:
                                self.codigo_input.setValue(int(float(valor)))
                            else:
                                self.codigo_input.setValue(0)
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter código: {e}, valor: {valor}")
                            self.codigo_input.setValue(0)
                        idx += 1
                    
                    if 'nome' in colunas_nomes:
                        valor = dados[idx]
                        self.nome_input.setText(str(valor) if valor is not None else "")
                        idx += 1
                    
                    if 'descricao' in colunas_nomes:
                        valor = dados[idx]
                        self.descricao_input.setText(str(valor) if valor is not None else "")
                        idx += 1
                    
                    if 'fck' in colunas_nomes:
                        valor = dados[idx]
                        # CONVERTER para inteiro
                        try:
                            if valor is not None:
                                self.fck_spin.setValue(int(float(valor)))
                            else:
                                self.fck_spin.setValue(20)
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter fck: {e}, valor: {valor}")
                            self.fck_spin.setValue(20)
                        idx += 1
                    
                    if 'slump' in colunas_nomes:
                        valor = dados[idx]
                        self.slump_input.setText(str(valor) if valor is not None else "")
                        idx += 1
                    
                    if 'tipo_brita' in colunas_nomes:
                        valor = dados[idx]
                        if valor is not None:
                            index = self.tipo_brita_combo.findText(str(valor))
                            if index >= 0:
                                self.tipo_brita_combo.setCurrentIndex(index)
                        idx += 1
                    
                    if 'volume_m3' in colunas_nomes:
                        valor = dados[idx]
                        # CONVERTER para float
                        try:
                            if valor is not None:
                                self.volume_m3_spin.setValue(float(valor))
                            else:
                                self.volume_m3_spin.setValue(0.5)
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter volume_m3: {e}, valor: {valor}")
                            self.volume_m3_spin.setValue(0.5)
                        idx += 1
                    
                    if 'cimento' in colunas_nomes:
                        valor = dados[idx]
                        # CONVERTER para float
                        try:
                            if valor is not None:
                                self.cimento_spin.setValue(float(valor))
                            else:
                                self.cimento_spin.setValue(0)
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter cimento: {e}, valor: {valor}")
                            self.cimento_spin.setValue(0)
                        idx += 1
                    
                    if 'brita0' in colunas_nomes:
                        valor = dados[idx]
                        # CONVERTER para float
                        try:
                            if valor is not None:
                                self.brita0_spin.setValue(float(valor))
                            else:
                                self.brita0_spin.setValue(0)
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter brita0: {e}, valor: {valor}")
                            self.brita0_spin.setValue(0)
                        idx += 1
                    
                    if 'brita1' in colunas_nomes:
                        valor = dados[idx]
                        # CONVERTER para float
                        try:
                            if valor is not None:
                                self.brita1_spin.setValue(float(valor))
                            else:
                                self.brita1_spin.setValue(0)
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter brita1: {e}, valor: {valor}")
                            self.brita1_spin.setValue(0)
                        idx += 1
                    
                    if 'areia_media' in colunas_nomes:
                        valor = dados[idx]
                        # CONVERTER para float
                        try:
                            if valor is not None:
                                self.areia_media_spin.setValue(float(valor))
                            else:
                                self.areia_media_spin.setValue(0)
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter areia_media: {e}, valor: {valor}")
                            self.areia_media_spin.setValue(0)
                        idx += 1
                    
                    if 'po_brita' in colunas_nomes:
                        valor = dados[idx]
                        # CONVERTER para float
                        try:
                            if valor is not None:
                                self.po_brita_spin.setValue(float(valor))
                            else:
                                self.po_brita_spin.setValue(0)
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter po_brita: {e}, valor: {valor}")
                            self.po_brita_spin.setValue(0)
                        idx += 1
                    
                    if 'agua' in colunas_nomes:
                        valor = dados[idx]
                        # CONVERTER para float
                        try:
                            if valor is not None:
                                self.agua_spin.setValue(float(valor))
                            else:
                                self.agua_spin.setValue(0)
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter agua: {e}, valor: {valor}")
                            self.agua_spin.setValue(0)
                        idx += 1
                    
                    if 'aditivo' in colunas_nomes:
                        valor = dados[idx]
                        # CONVERTER para float
                        try:
                            if valor is not None:
                                self.aditivo_spin.setValue(float(valor))
                            else:
                                self.aditivo_spin.setValue(0)
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter aditivo: {e}, valor: {valor}")
                            self.aditivo_spin.setValue(0)
                        idx += 1
                    
                    if 'status' in colunas_nomes:
                        valor = dados[idx]
                        if valor is not None:
                            index = self.status_combo.findText(str(valor))
                            if index >= 0:
                                self.status_combo.setCurrentIndex(index)
                        else:
                            self.status_combo.setCurrentText("ATIVO")
            
            conn.close()
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados:\n{str(e)}")
            
    def salvar(self):
        """Salva o traço no banco de dados"""
        nome = self.nome_input.text().strip()
        if not nome:
            QMessageBox.warning(self, "Atenção", "O nome do traço é obrigatório!")
            self.nome_input.setFocus()
            return
        
        codigo = self.codigo_input.value()
        if codigo <= 0:
            QMessageBox.warning(self, "Atenção", "O código do traço deve ser maior que zero!")
            self.codigo_input.setFocus()
            return
        
        try:
            conn = sqlite3.connect(self.parent.db_path)
            cursor = conn.cursor()
            
            # Verificar quais colunas existem
            cursor.execute("PRAGMA table_info(tracos)")
            colunas = cursor.fetchall()
            colunas_nomes = [coluna[1] for coluna in colunas]
            
            # Preparar dados baseado nas colunas existentes
            dados = []
            colunas_update = []
            valores_update = []
            
            if 'codigo' in colunas_nomes:
                colunas_update.append('codigo')
                valores_update.append(codigo)
                dados.append(codigo)
            
            if 'nome' in colunas_nomes:
                colunas_update.append('nome')
                valores_update.append(nome)
                dados.append(nome)
            
            if 'descricao' in colunas_nomes:
                colunas_update.append('descricao')
                valores_update.append(self.descricao_input.toPlainText().strip())
                dados.append(self.descricao_input.toPlainText().strip())
            
            if 'fck' in colunas_nomes:
                colunas_update.append('fck')
                valores_update.append(self.fck_spin.value())
                dados.append(self.fck_spin.value())
            
            if 'slump' in colunas_nomes:
                colunas_update.append('slump')
                valores_update.append(self.slump_input.text().strip())
                dados.append(self.slump_input.text().strip())
            
            if 'tipo_brita' in colunas_nomes:
                colunas_update.append('tipo_brita')
                valores_update.append(self.tipo_brita_combo.currentText())
                dados.append(self.tipo_brita_combo.currentText())
            
            if 'volume_m3' in colunas_nomes:
                colunas_update.append('volume_m3')
                valores_update.append(self.volume_m3_spin.value())
                dados.append(self.volume_m3_spin.value())
            
            if 'cimento' in colunas_nomes:
                colunas_update.append('cimento')
                valores_update.append(self.cimento_spin.value())
                dados.append(self.cimento_spin.value())
            
            if 'brita0' in colunas_nomes:
                colunas_update.append('brita0')
                valores_update.append(self.brita0_spin.value())
                dados.append(self.brita0_spin.value())
            
            if 'brita1' in colunas_nomes:
                colunas_update.append('brita1')
                valores_update.append(self.brita1_spin.value())
                dados.append(self.brita1_spin.value())
            
            if 'areia_media' in colunas_nomes:
                colunas_update.append('areia_media')
                valores_update.append(self.areia_media_spin.value())
                dados.append(self.areia_media_spin.value())
            
            if 'po_brita' in colunas_nomes:
                colunas_update.append('po_brita')
                valores_update.append(self.po_brita_spin.value())
                dados.append(self.po_brita_spin.value())
            
            if 'agua' in colunas_nomes:
                colunas_update.append('agua')
                valores_update.append(self.agua_spin.value())
                dados.append(self.agua_spin.value())
            
            if 'aditivo' in colunas_nomes:
                colunas_update.append('aditivo')
                valores_update.append(self.aditivo_spin.value())
                dados.append(self.aditivo_spin.value())
            
            if 'status' in colunas_nomes:
                colunas_update.append('status')
                valores_update.append(self.status_combo.currentText())
                dados.append(self.status_combo.currentText())
            
            if self.traco_id:
                # Verificar se o código já existe em outro traço
                cursor.execute("SELECT id FROM tracos WHERE codigo = ? AND id != ?", 
                              (codigo, self.traco_id))
                if cursor.fetchone():
                    QMessageBox.critical(self, "Erro", "Já existe um traço com este código!")
                    conn.close()
                    return
                
                # Atualizar traço existente
                set_clause = ', '.join([f"{col} = ?" for col in colunas_update])
                query = f"UPDATE tracos SET {set_clause} WHERE id = ?"
                cursor.execute(query, valores_update + [self.traco_id])
                mensagem = "atualizado"
            else:
                # Verificar se o código já existe
                cursor.execute("SELECT id FROM tracos WHERE codigo = ?", (codigo,))
                if cursor.fetchone():
                    QMessageBox.critical(self, "Erro", "Já existe um traço com este código!")
                    conn.close()
                    return
                
                # Inserir novo traço
                placeholders = ', '.join(['?' for _ in colunas_update])
                colunas_str = ', '.join(colunas_update)
                query = f"INSERT INTO tracos ({colunas_str}) VALUES ({placeholders})"
                cursor.execute(query, valores_update)
                mensagem = "cadastrado"
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Sucesso", f"Traço {mensagem} com sucesso!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar traço:\n{str(e)}")


class DialogDetalhesTraco(QDialog):
    """Diálogo para mostrar detalhes do traço"""
    def __init__(self, parent=None, traco_id=None):
        super().__init__(parent)
        self.parent = parent
        self.traco_id = traco_id
        self.setModal(True)
        self.setWindowTitle("👁️ Detalhes do Traço")
        self.setMinimumWidth(500)
        
        self.setup_ui()
        self.carregar_detalhes()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.nome_label = QLabel()
        self.nome_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.nome_label.setStyleSheet("color: #0D47A1;")
        self.nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.nome_label)
        
        # Grupo de informações
        info_group = QGroupBox("Informações")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 10px;
                background-color: #E3F2FD;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        info_layout = QFormLayout()
        
        self.codigo_label = QLabel()
        info_layout.addRow("Código:", self.codigo_label)
        
        self.descricao_label = QLabel()
        self.descricao_label.setWordWrap(True)
        info_layout.addRow("Descrição:", self.descricao_label)
        
        self.fck_label = QLabel()
        info_layout.addRow("Resistência (fck):", self.fck_label)
        
        self.slump_label = QLabel()
        info_layout.addRow("Slump:", self.slump_label)
        
        self.tipo_brita_label = QLabel()
        info_layout.addRow("Tipo de Brita:", self.tipo_brita_label)
        
        # Volume do traço (m³)
        self.volume_m3_label = QLabel()
        info_layout.addRow("Volume do traço:", self.volume_m3_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Grupo de composição
        comp_group = QGroupBox("Composição (para o volume especificado)")
        comp_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 10px;
                background-color: #E3F2FD;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        comp_layout = QFormLayout()
        
        self.cimento_label = QLabel()
        comp_layout.addRow("Cimento:", self.cimento_label)
        
        self.brita0_label = QLabel()
        comp_layout.addRow("Brita 0:", self.brita0_label)
        
        self.brita1_label = QLabel()
        comp_layout.addRow("Brita 1:", self.brita1_label)
        
        self.areia_media_label = QLabel()
        comp_layout.addRow("Areia média:", self.areia_media_label)
        
        # Pó de Brita
        self.po_brita_label = QLabel()
        comp_layout.addRow("Pó de Brita:", self.po_brita_label)
        
        self.agua_label = QLabel()
        comp_layout.addRow("Água:", self.agua_label)
        
        self.aditivo_label = QLabel()
        comp_layout.addRow("Aditivo:", self.aditivo_label)
        
        comp_group.setLayout(comp_layout)
        layout.addWidget(comp_group)
        
        # Status
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Botão fechar
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.accept)
        btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #1976D2, stop: 1 #1565C0);
                color: white;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #1565C0, stop: 1 #0D47A1);
            }
        """)
        layout.addWidget(btn_fechar)
        
    def carregar_detalhes(self):
        """Carrega os detalhes do traço"""
        try:
            conn = sqlite3.connect(self.parent.db_path)
            cursor = conn.cursor()
            
            # Verificar quais colunas existem
            cursor.execute("PRAGMA table_info(tracos)")
            colunas = cursor.fetchall()
            colunas_nomes = [coluna[1] for coluna in colunas]
            
            # Construir query dinamicamente
            colunas_selecionar = []
            if 'codigo' in colunas_nomes:
                colunas_selecionar.append('codigo')
            if 'nome' in colunas_nomes:
                colunas_selecionar.append('nome')
            if 'descricao' in colunas_nomes:
                colunas_selecionar.append('descricao')
            if 'fck' in colunas_nomes:
                colunas_selecionar.append('fck')
            if 'slump' in colunas_nomes:
                colunas_selecionar.append('slump')
            if 'tipo_brita' in colunas_nomes:
                colunas_selecionar.append('tipo_brita')
            if 'volume_m3' in colunas_nomes:
                colunas_selecionar.append('volume_m3')
            if 'cimento' in colunas_nomes:
                colunas_selecionar.append('cimento')
            if 'brita0' in colunas_nomes:
                colunas_selecionar.append('brita0')
            if 'brita1' in colunas_nomes:
                colunas_selecionar.append('brita1')
            if 'areia_media' in colunas_nomes:
                colunas_selecionar.append('areia_media')
            if 'po_brita' in colunas_nomes:
                colunas_selecionar.append('po_brita')
            if 'agua' in colunas_nomes:
                colunas_selecionar.append('agua')
            if 'aditivo' in colunas_nomes:
                colunas_selecionar.append('aditivo')
            if 'status' in colunas_nomes:
                colunas_selecionar.append('status')
            
            if colunas_selecionar:
                query = f"SELECT {', '.join(colunas_selecionar)} FROM tracos WHERE id = ?"
                cursor.execute(query, (self.traco_id,))
                dados = cursor.fetchone()
                
                if dados:
                    idx = 0
                    if 'codigo' in colunas_nomes:
                        self.codigo_label.setText(str(dados[idx] if dados[idx] else ""))
                        idx += 1
                    if 'nome' in colunas_nomes:
                        self.nome_label.setText(dados[idx] if dados[idx] else "")
                        idx += 1
                    if 'descricao' in colunas_nomes:
                        self.descricao_label.setText(dados[idx] if dados[idx] else "Sem descrição")
                        idx += 1
                    if 'fck' in colunas_nomes:
                        # Converter para inteiro para exibição
                        try:
                            valor = dados[idx] if dados[idx] is not None else 0
                            self.fck_label.setText(f"{int(float(valor))} MPa")
                        except (ValueError, TypeError):
                            self.fck_label.setText(f"{dados[idx]} MPa" if dados[idx] else "Não informado")
                        idx += 1
                    if 'slump' in colunas_nomes:
                        self.slump_label.setText(dados[idx] if dados[idx] else "Não informado")
                        idx += 1
                    if 'tipo_brita' in colunas_nomes:
                        self.tipo_brita_label.setText(dados[idx] if dados[idx] else "Não informado")
                        idx += 1
                    if 'volume_m3' in colunas_nomes:
                        # Converter para float para exibição
                        try:
                            valor = dados[idx] if dados[idx] is not None else 0.5
                            self.volume_m3_label.setText(f"{float(valor):.2f} m³")
                        except (ValueError, TypeError):
                            self.volume_m3_label.setText(f"{dados[idx]} m³" if dados[idx] else "0.5 m³")
                        idx += 1
                    if 'cimento' in colunas_nomes:
                        # Converter para float para exibição
                        try:
                            valor = dados[idx] if dados[idx] is not None else 0
                            self.cimento_label.setText(f"{float(valor):.2f} kg")
                        except (ValueError, TypeError):
                            self.cimento_label.setText(f"{dados[idx]} kg" if dados[idx] else "0 kg")
                        idx += 1
                    if 'brita0' in colunas_nomes:
                        # Converter para float para exibição
                        try:
                            valor = dados[idx] if dados[idx] is not None else 0
                            self.brita0_label.setText(f"{float(valor):.2f} kg")
                        except (ValueError, TypeError):
                            self.brita0_label.setText(f"{dados[idx]} kg" if dados[idx] else "0 kg")
                        idx += 1
                    if 'brita1' in colunas_nomes:
                        # Converter para float para exibição
                        try:
                            valor = dados[idx] if dados[idx] is not None else 0
                            self.brita1_label.setText(f"{float(valor):.2f} kg")
                        except (ValueError, TypeError):
                            self.brita1_label.setText(f"{dados[idx]} kg" if dados[idx] else "0 kg")
                        idx += 1
                    if 'areia_media' in colunas_nomes:
                        # Converter para float para exibição
                        try:
                            valor = dados[idx] if dados[idx] is not None else 0
                            self.areia_media_label.setText(f"{float(valor):.2f} kg")
                        except (ValueError, TypeError):
                            self.areia_media_label.setText(f"{dados[idx]} kg" if dados[idx] else "0 kg")
                        idx += 1
                    if 'po_brita' in colunas_nomes:
                        # Converter para float para exibição
                        try:
                            valor = dados[idx] if dados[idx] is not None else 0
                            self.po_brita_label.setText(f"{float(valor):.2f} kg")
                        except (ValueError, TypeError):
                            self.po_brita_label.setText(f"{dados[idx]} kg" if dados[idx] else "0 kg")
                        idx += 1
                    if 'agua' in colunas_nomes:
                        # Converter para float para exibição
                        try:
                            valor = dados[idx] if dados[idx] is not None else 0
                            self.agua_label.setText(f"{float(valor):.2f} L")
                        except (ValueError, TypeError):
                            self.agua_label.setText(f"{dados[idx]} L" if dados[idx] else "0 L")
                        idx += 1
                    if 'aditivo' in colunas_nomes:
                        # Converter para float para exibição
                        try:
                            valor = dados[idx] if dados[idx] is not None else 0
                            self.aditivo_label.setText(f"{float(valor):.2f} kg")
                        except (ValueError, TypeError):
                            self.aditivo_label.setText(f"{dados[idx]} kg" if dados[idx] else "0 kg")
                        idx += 1
                    if 'status' in colunas_nomes:
                        status = dados[idx] if dados[idx] else "ATIVO"
                        self.status_label.setText(f"Status: {status}")
                        if status == "ATIVO":
                            self.status_label.setStyleSheet("""
                                background-color: #E8F5E9;
                                color: #2E7D32;
                                padding: 10px;
                                border-radius: 5px;
                                font-weight: bold;
                                border: 1px solid #4CAF50;
                            """)
                        else:
                            self.status_label.setStyleSheet("""
                                background-color: #FFEBEE;
                                color: #C62828;
                                padding: 10px;
                                border-radius: 5px;
                                font-weight: bold;
                                border: 1px solid #F44336;
                            """)
            
            conn.close()
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar detalhes:\n{str(e)}")