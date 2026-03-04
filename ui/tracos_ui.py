# tela_tracos.py
import sys
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

class TelaTracos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db_path = 'usina_concreto.db'
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("📐 GERENCIAMENTO DE TRAÇOS")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            QLabel {
                color: white;
                padding: 15px;
                background-color: #2c3e50;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(titulo)
        
        # Barra de ferramentas
        toolbar = QHBoxLayout()
        
        # Botões da barra de ferramentas
        self.btn_novo = QPushButton("➕ Novo Traço")
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_excluir = QPushButton("🗑️ Excluir")
        self.btn_atualizar = QPushButton("🔄 Atualizar")
        
        # Estilo dos botões
        for btn in [self.btn_novo, self.btn_editar, self.btn_excluir, self.btn_atualizar]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
        
        # Adiciona botões à barra de ferramentas
        toolbar.addWidget(self.btn_novo)
        toolbar.addWidget(self.btn_editar)
        toolbar.addWidget(self.btn_excluir)
        toolbar.addWidget(self.btn_atualizar)
        
        # Campo de busca
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("🔍 Buscar traço...")
        self.busca_input.setFixedHeight(40)
        self.busca_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
        toolbar.addWidget(self.busca_input)
        
        layout.addLayout(toolbar)
        
        # Tabela de traços
        self.tabela_tracos = QTableWidget()
        self.tabela_tracos.setColumnCount(5)
        self.tabela_tracos.setHorizontalHeaderLabels(["ID", "Nome", "fck (MPa)", "Status", "Data"])
        
        # Configurar a tabela
        self.tabela_tracos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_tracos.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabela_tracos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Ajustar largura das colunas
        header = self.tabela_tracos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        # Estilo da tabela
        self.tabela_tracos.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dfe6e9;
                gridline-color: #dfe6e9;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        layout.addWidget(self.tabela_tracos)
        
        # Conectar sinais
        self.btn_novo.clicked.connect(self.novo_traco)
        self.btn_editar.clicked.connect(self.editar_traco)
        self.btn_excluir.clicked.connect(self.excluir_traco)
        self.btn_atualizar.clicked.connect(self.carregar_tracos)
        self.busca_input.textChanged.connect(self.filtrar_tracos)
        self.tabela_tracos.doubleClicked.connect(self.editar_traco)
        
        # Inicializar banco de dados
        self.criar_tabela()
        
        # Carregar dados iniciais
        self.carregar_tracos()
        
        print("✅ TelaTracos configurada com sucesso!")
        
    def criar_tabela(self):
        """Cria a tabela de traços se não existir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    descricao TEXT,
                    fck INTEGER DEFAULT 20,
                    agregado_graudo REAL DEFAULT 0,
                    agregado_fino REAL DEFAULT 0,
                    cimento REAL DEFAULT 0,
                    agua REAL DEFAULT 0,
                    aditivo REAL DEFAULT 0,
                    observacoes TEXT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'ATIVO'
                )
            ''')
            
            # Verificar se há dados, se não, inserir exemplos
            cursor.execute("SELECT COUNT(*) FROM tracos")
            count = cursor.fetchone()[0]
            
            if count == 0:
                tracos_exemplo = [
                    ('Concreto 20 MPa', 'Concreto estrutural para lajes', 20, 1000, 800, 300, 180, 2),
                    ('Concreto 25 MPa', 'Concreto para fundações', 25, 950, 750, 350, 165, 3),
                    ('Concreto 30 MPa', 'Alta resistência', 30, 900, 700, 400, 150, 4),
                    ('Argamassa', 'Assentamento de blocos', 5, 0, 1200, 250, 220, 1),
                ]
                
                for traco in tracos_exemplo:
                    cursor.execute('''
                        INSERT INTO tracos (nome, descricao, fck, agregado_graudo, agregado_fino,
                                           cimento, agua, aditivo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', traco)
                
                print("✅ Dados de exemplo inseridos na tabela tracos")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao criar tabela tracos: {e}")
            
    def carregar_tracos(self):
        """Carrega os traços do banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, nome, fck, status, 
                       strftime('%d/%m/%Y', data_criacao) as data
                FROM tracos 
                ORDER BY nome
            ''')
            tracos = cursor.fetchall()
            conn.close()
            
            self.tabela_tracos.setRowCount(len(tracos))
            
            for row, traco in enumerate(tracos):
                for col, value in enumerate(traco):
                    item = QTableWidgetItem(str(value))
                    
                    # Colorir status
                    if col == 3:  # Coluna de status
                        if value == 'ATIVO':
                            item.setForeground(QColor(39, 174, 96))  # Verde
                        elif value == 'INATIVO':
                            item.setForeground(QColor(231, 76, 60))  # Vermelho
                        elif value == 'PENDENTE':
                            item.setForeground(QColor(241, 196, 15))  # Amarelo
                    
                    self.tabela_tracos.setItem(row, col, item)
            
            print(f"✅ {len(tracos)} traços carregados")
                    
        except Exception as e:
            print(f"❌ Erro ao carregar traços: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar traços:\n{str(e)}")
            
    def filtrar_tracos(self, texto):
        """Filtra os traços na tabela"""
        texto = texto.lower()
        for row in range(self.tabela_tracos.rowCount()):
            mostrar = False
            for col in range(self.tabela_tracos.columnCount()):
                item = self.tabela_tracos.item(row, col)
                if item and texto in item.text().lower():
                    mostrar = True
                    break
            self.tabela_tracos.setRowHidden(row, not mostrar)
            
    def novo_traco(self):
        """Abre diálogo para criar novo traço"""
        dialog = DialogTraco(self)
        if dialog.exec():
            self.carregar_tracos()
            
    def editar_traco(self):
        """Abre diálogo para editar traço selecionado"""
        selected_row = self.tabela_tracos.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um traço para editar!")
            return
            
        traco_id = self.tabela_tracos.item(selected_row, 0).text()
        dialog = DialogTraco(self, traco_id)
        if dialog.exec():
            self.carregar_tracos()
            
    def excluir_traco(self):
        """Exclui o traço selecionado"""
        selected_row = self.tabela_tracos.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione um traço para excluir!")
            return
            
        traco_id = self.tabela_tracos.item(selected_row, 0).text()
        traco_nome = self.tabela_tracos.item(selected_row, 1).text()
        
        reply = QMessageBox.question(
            self, 'Confirmar Exclusão',
            f'Tem certeza que deseja excluir o traço "{traco_nome}"?',
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
                print(f"✅ Traço '{traco_nome}' excluído")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir traço:\n{str(e)}")


class DialogTraco(QDialog):
    """Diálogo para criar/editar traço"""
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
        
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome do traço")
        form.addRow("Nome:", self.nome_input)
        
        self.descricao_input = QLineEdit()
        self.descricao_input.setPlaceholderText("Descrição")
        form.addRow("Descrição:", self.descricao_input)
        
        self.fck_spin = QSpinBox()
        self.fck_spin.setRange(5, 100)
        self.fck_spin.setValue(20)
        self.fck_spin.setSuffix(" MPa")
        form.addRow("Resistência (fck):", self.fck_spin)
        
        self.cimento_spin = QDoubleSpinBox()
        self.cimento_spin.setRange(0, 1000)
        self.cimento_spin.setValue(300)
        self.cimento_spin.setSuffix(" kg")
        form.addRow("Cimento:", self.cimento_spin)
        
        self.areia_spin = QDoubleSpinBox()
        self.areia_spin.setRange(0, 2000)
        self.areia_spin.setValue(800)
        self.areia_spin.setSuffix(" kg")
        form.addRow("Areia (Agregado Fino):", self.areia_spin)
        
        self.brita_spin = QDoubleSpinBox()
        self.brita_spin.setRange(0, 2000)
        self.brita_spin.setValue(1000)
        self.brita_spin.setSuffix(" kg")
        form.addRow("Brita (Agregado Graúdo):", self.brita_spin)
        
        self.agua_spin = QDoubleSpinBox()
        self.agua_spin.setRange(0, 500)
        self.agua_spin.setValue(180)
        self.agua_spin.setSuffix(" L")
        form.addRow("Água:", self.agua_spin)
        
        self.aditivo_spin = QDoubleSpinBox()
        self.aditivo_spin.setRange(0, 50)
        self.aditivo_spin.setValue(2)
        self.aditivo_spin.setSuffix(" kg")
        form.addRow("Aditivo:", self.aditivo_spin)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["ATIVO", "INATIVO", "PENDENTE"])
        form.addRow("Status:", self.status_combo)
        
        layout.addLayout(form)
        
        # Botões
        button_layout = QHBoxLayout()
        
        btn_salvar = QPushButton("💾 Salvar")
        btn_salvar.clicked.connect(self.salvar)
        btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        button_layout.addWidget(btn_salvar)
        button_layout.addWidget(btn_cancelar)
        
        layout.addLayout(button_layout)
        
    def carregar_dados(self):
        """Carrega os dados do traço para edição"""
        try:
            conn = sqlite3.connect(self.parent.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT nome, descricao, fck, cimento, agregado_fino, 
                       agregado_graudo, agua, aditivo, status
                FROM tracos WHERE id = ?
            ''', (self.traco_id,))
            
            dados = cursor.fetchone()
            conn.close()
            
            if dados:
                self.nome_input.setText(dados[0])
                self.descricao_input.setText(dados[1] if dados[1] else "")
                self.fck_spin.setValue(dados[2])
                self.cimento_spin.setValue(dados[3])
                self.areia_spin.setValue(dados[4])
                self.brita_spin.setValue(dados[5])
                self.agua_spin.setValue(dados[6])
                self.aditivo_spin.setValue(dados[7] if dados[7] else 0)
                
                index = self.status_combo.findText(dados[8])
                if index >= 0:
                    self.status_combo.setCurrentIndex(index)
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados:\n{str(e)}")
            
    def salvar(self):
        """Salva o traço no banco de dados"""
        nome = self.nome_input.text().strip()
        if not nome:
            QMessageBox.warning(self, "Atenção", "O nome do traço é obrigatório!")
            return
            
        try:
            conn = sqlite3.connect(self.parent.db_path)
            cursor = conn.cursor()
            
            dados = (
                nome,
                self.descricao_input.text(),
                self.fck_spin.value(),
                self.brita_spin.value(),  # agregado_graudo
                self.areia_spin.value(),  # agregado_fino
                self.cimento_spin.value(),
                self.agua_spin.value(),
                self.aditivo_spin.value(),
                self.status_combo.currentText()
            )
            
            if self.traco_id:
                # Atualizar
                cursor.execute('''
                    UPDATE tracos SET
                    nome=?, descricao=?, fck=?, agregado_graudo=?,
                    agregado_fino=?, cimento=?, agua=?, aditivo=?,
                    status=?
                    WHERE id=?
                ''', dados + (self.traco_id,))
                mensagem = "atualizado"
            else:
                # Inserir
                cursor.execute('''
                    INSERT INTO tracos 
                    (nome, descricao, fck, agregado_graudo, agregado_fino,
                     cimento, agua, aditivo, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', dados)
                mensagem = "criado"
            
            conn.commit()
            conn.close()
            self.accept()
            
            QMessageBox.information(self, "Sucesso", f"Traço {mensagem} com sucesso!")
            
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Erro", "Já existe um traço com este nome!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar traço:\n{str(e)}")


# Função para testar isoladamente
def main():
    app = QApplication(sys.argv)
    tela = TelaTracos()
    tela.setWindowTitle("📐 TRAÇOS - Usina Betto Mix Concreto")
    tela.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()