# ui/pages/tela_notas.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QFormLayout, QGroupBox, QMessageBox,
    QHeaderView, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QComboBox, QDateEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
import sqlite3
import json
from datetime import datetime
import time
import os
import contextlib

@contextlib.contextmanager
def suppress_exc():
    """
    Context manager simples para suprimir exceções em blocos de migração.
    Uso: with suppress_exc(): cursor.execute("ALTER ...")
    """
    try:
        yield
    except Exception as _:
        pass

class TelaNotas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        # carregar_notas chama criar_tabelas_se_necessario internamente
        self.carregar_notas()

    # ----------------------------
    # UI (mantido layout original com cores azuis)
    # ----------------------------
    def init_ui(self):
        layout = QVBoxLayout(self)

        # Título - ALTERAÇÃO: Texto azul escuro
        titulo = QLabel("NOTAS FISCAIS DE FORNECEDORES")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            color: #0D47A1; 
            padding: 10px; 
            background-color: #E3F2FD; 
            border-radius: 5px; 
            border: 2px solid #0D47A1;
        """)
        layout.addWidget(titulo)

        # Botões superiores - ALTERAÇÃO: Botões com gradiente de azul
        btn_layout = QHBoxLayout()

        btn_novo = QPushButton("📄 Nova Nota")
        btn_novo.clicked.connect(self.nova_nota)
        btn_novo.setStyleSheet("""
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

        btn_editar = QPushButton("✏️ Editar")
        btn_editar.clicked.connect(self.editar_nota)
        btn_editar.setStyleSheet("""
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

        btn_excluir = QPushButton("🗑️ Excluir")
        btn_excluir.clicked.connect(self.excluir_nota)
        btn_excluir.setStyleSheet("""
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

        btn_entrada = QPushButton("📦 Entrada Estoque")
        btn_entrada.clicked.connect(self.entrada_estoque)
        btn_entrada.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #2E7D32);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #2E7D32;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66BB6A, stop:1 #4CAF50);
                border: 1px solid #4CAF50;
            }
        """)

        btn_layout.addWidget(btn_novo)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_excluir)
        btn_layout.addWidget(btn_entrada)

        layout.addLayout(btn_layout)

        # Filtros - ALTERAÇÃO: Estilo azul para combobox e botão
        filtro_layout = QHBoxLayout()

        self.combo_fornecedor = QComboBox()
        self.combo_fornecedor.addItem("Todos os fornecedores")
        self.combo_fornecedor.setStyleSheet("""
            QComboBox {
                border: 2px solid #1976D2;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 2px solid #0D47A1;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)

        self.combo_material = QComboBox()
        self.combo_material.addItem("Todos os materiais")
        # manter lista de materiais coerente com o restante do sistema
        self.combo_material.addItems([
            "Cimento", "Brita 0", "Brita 1", "Areia Média",
            "Pó de Brita", "Aditivo", "Água"
        ])
        self.combo_material.setStyleSheet("""
            QComboBox {
                border: 2px solid #1976D2;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 2px solid #0D47A1;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)

        btn_filtrar = QPushButton("🔍 Filtrar")
        btn_filtrar.clicked.connect(self.filtrar_notas)
        btn_filtrar.setStyleSheet("""
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

        filtro_layout.addWidget(QLabel("Fornecedor:"))
        filtro_layout.addWidget(self.combo_fornecedor)
        filtro_layout.addWidget(QLabel("Material:"))
        filtro_layout.addWidget(self.combo_material)
        filtro_layout.addWidget(btn_filtrar)

        layout.addLayout(filtro_layout)

        # Tabela de notas - ALTERAÇÃO: Estilo azul
        self.tabela_notas = QTableWidget()
        self.tabela_notas.setColumnCount(8)
        self.tabela_notas.setHorizontalHeaderLabels([
            "Número", "Fornecedor", "Material", "Quantidade", "Unidade",
            "Valor Total", "Data", "Status"
        ])
        self.tabela_notas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # ALTERAÇÃO: Estilo da tabela com paleta de azuis
        self.tabela_notas.setAlternatingRowColors(True)
        self.tabela_notas.setStyleSheet("""
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

        layout.addWidget(self.tabela_notas)

        # Estatísticas - ALTERAÇÃO: Estilo azul
        self.label_estatisticas = QLabel("Total em notas: R$ 0,00 | Itens pendentes: 0")
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

    # ----------------------------
    # Banco de dados — helpers
    # ----------------------------
    def get_db_connection(self, timeout=10):
        """
        Retorna uma conexão sqlite com timeout e tratamento de locked.
        Usa retry simples para evitar problemas de concorrência.
        """
        db_path = 'usina_concreto.db'
        for attempt in range(timeout):
            try:
                conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
                # timeout em milissegundos para operações bloqueadas
                conn.execute("PRAGMA busy_timeout = 5000")
                return conn
            except sqlite3.OperationalError as e:
                if 'locked' in str(e).lower() and attempt < timeout - 1:
                    time.sleep(0.3)
                    continue
                raise

    def criar_tabelas_se_necessario(self, conn):
        """
        Cria as tabelas necessárias, e faz migrações seguras sem recriar colunas duplicadas.
        Não altera o layout da UI.
        """
        cursor = conn.cursor()

        # notas (NF) - estrutura principal
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE,
                fornecedor TEXT,
                material TEXT,
                quantidade REAL,
                unidade TEXT,
                valor_unitario REAL,
                valor_total REAL,
                data_emissao TEXT,
                status TEXT DEFAULT 'PENDENTE'
            )
        ''')

        # estoque - apenas criar se não existir (não sobrescreve)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material TEXT UNIQUE,
                quantidade REAL DEFAULT 0,
                unidade TEXT,
                estoque_minimo REAL DEFAULT 0,
                data_atualizacao TEXT
            )
        ''')

        # notas_entrada - compatibilidade com sincronização
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

        # historico_estoque - criar se não existir, e garantir colunas sem duplicar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material TEXT,
                quantidade REAL,
                tipo TEXT,
                destino TEXT,
                observacoes TEXT,
                data_movimentacao TEXT,
                usuario TEXT DEFAULT 'SISTEMA',
                relacionamento_id INTEGER,
                relacionamento_tipo TEXT
            )
        ''')

        # agora verificações de colunas (migrações seguras)
        cursor.execute("PRAGMA table_info(historico_estoque)")
        colunas = [c[1] for c in cursor.fetchall()]

        # Se por algum motivo faltar coluna (compatibilidade com versões antigas), adiciona sem quebrar
        # (note: SQLite não permite DEFAULT com NOT NULL em ALTER facilmente — por isso fazemos simples)
        with suppress_exc():
            if 'data_movimentacao' not in colunas:
                cursor.execute("ALTER TABLE historico_estoque ADD COLUMN data_movimentacao TEXT")
        with suppress_exc():
            if 'usuario' not in colunas:
                cursor.execute("ALTER TABLE historico_estoque ADD COLUMN usuario TEXT DEFAULT 'SISTEMA'")
        with suppress_exc():
            if 'relacionamento_id' not in colunas:
                cursor.execute("ALTER TABLE historico_estoque ADD COLUMN relacionamento_id INTEGER")
        with suppress_exc():
            if 'relacionamento_tipo' not in colunas:
                cursor.execute("ALTER TABLE historico_estoque ADD COLUMN relacionamento_tipo TEXT")
        # commits de garantia
        conn.commit()

    # ----------------------------
    # Funções principais
    # ----------------------------
    def carregar_notas(self):
        """Carrega todas as notas (exibição) e atualiza combobox de fornecedores."""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            # garante estrutura
            self.criar_tabelas_se_necessario(conn)

            cursor.execute('''
                SELECT numero, fornecedor, material, quantidade, unidade, 
                       valor_total, data_emissao, status
                FROM notas
                ORDER BY data_emissao DESC
            ''')
            notas = cursor.fetchall()
            conn.close()

            self.tabela_notas.setRowCount(len(notas))

            total_valor = 0.0
            pendentes = 0

            for i, nota in enumerate(notas):
                # cada nota tem 8 campos (mesma ordem do header)
                for j in range(8):
                    val = nota[j] if j < len(nota) else ""
                    item_text = ""
                    if val is None:
                        item_text = ""
                    elif j == 5:  # valor_total
                        try:
                            valor = float(val)
                        except (ValueError, TypeError):
                            valor = 0.0
                        total_valor += valor
                        item_text = f"R$ {valor:.2f}"
                    else:
                        item_text = str(val)

                    item = QTableWidgetItem(item_text)

                    # colorir status
                    if j == 7:
                        status = str(nota[7]) if nota[7] else "PENDENTE"
                        if status.upper() == 'PENDENTE':
                            item.setForeground(QColor(255, 165, 0))
                            pendentes += 1
                        elif status.upper() in ('REGISTRADO', 'PROCESSADO'):
                            item.setForeground(QColor(39, 174, 96))  # Verde

                    self.tabela_notas.setItem(i, j, item)

            self.label_estatisticas.setText(
                f"Total em notas: R$ {total_valor:.2f} | Itens pendentes: {pendentes}"
            )

            # atualizar combobox de fornecedores
            fornecedores = sorted({nota[1] for nota in notas if nota[1]})
            self.combo_fornecedor.clear()
            self.combo_fornecedor.addItem("Todos os fornecedores")
            for f in fornecedores:
                self.combo_fornecedor.addItem(f)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar notas: {e}")
            print(f"[TelaNotas.carregar_notas] Erro detalhado: {e}")

    def filtrar_notas(self):
        """
        Implementação simples de filtro — respeita layout original.
        Se quiser filtro por fornecedor/material mais avançado eu adiciono.
        """
        try:
            fornecedor = self.combo_fornecedor.currentText()
            material = self.combo_material.currentText()

            conn = self.get_db_connection()
            cursor = conn.cursor()
            self.criar_tabelas_se_necessario(conn)

            query = '''
                SELECT numero, fornecedor, material, quantidade, unidade, 
                       valor_total, data_emissao, status
                FROM notas
            '''
            conditions = []
            params = []
            if fornecedor and fornecedor != "Todos os fornecedores":
                conditions.append("fornecedor = ?")
                params.append(fornecedor)
            if material and material != "Todos os materiais":
                conditions.append("material = ?")
                params.append(material)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY data_emissao DESC"

            cursor.execute(query, params)
            notas = cursor.fetchall()
            conn.close()

            # atualizar tabela com resultados filtrados
            self.tabela_notas.setRowCount(len(notas))
            total_valor = 0.0
            pendentes = 0
            for i, nota in enumerate(notas):
                for j in range(8):
                    val = nota[j] if j < len(nota) else ""
                    item_text = ""
                    if val is None:
                        item_text = ""
                    elif j == 5:
                        try:
                            valor = float(val)
                        except:
                            valor = 0.0
                        total_valor += valor
                        item_text = f"R$ {valor:.2f}"
                    else:
                        item_text = str(val)
                    item = QTableWidgetItem(item_text)
                    if j == 7:
                        st = str(nota[7]) if nota[7] else "PENDENTE"
                        if st.upper() == 'PENDENTE':
                            item.setForeground(QColor(255, 165, 0))
                            pendentes += 1
                        elif st.upper() in ('REGISTRADO', 'PROCESSADO'):
                            item.setForeground(QColor(39, 174, 96))
                    self.tabela_notas.setItem(i, j, item)
            self.label_estatisticas.setText(
                f"Total em notas: R$ {total_valor:.2f} | Itens pendentes: {pendentes}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao filtrar notas: {e}")
            print(f"[TelaNotas.filtrar_notas] {e}")

    # ----------------------------
    # CRUD de notas (mantendo layout)
    # ----------------------------
    def nova_nota(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nova Nota Fiscal")
        dialog.setModal(True)
        # ALTERAÇÃO: Estilo azul para o diálogo
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #0D47A1;
                font-weight: bold;
            }
            QLineEdit, QComboBox, QDoubleSpinBox {
                border: 2px solid #1976D2;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:hover, QComboBox:hover, QDoubleSpinBox:hover {
                border: 2px solid #0D47A1;
            }
        """)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        input_numero = QLineEdit()
        input_numero.setPlaceholderText("Ex: 123456")

        input_fornecedor = QLineEdit()
        input_fornecedor.setPlaceholderText("Nome do fornecedor")

        input_material = QComboBox()
        input_material.addItems([
            "Cimento", "Brita 0", "Brita 1", "Areia Média",
            "Pó de Brita", "Aditivo", "Água"
        ])

        input_quantidade = QDoubleSpinBox()
        input_quantidade.setRange(0, 10000000000)
        input_quantidade.setDecimals(2)
        input_quantidade.setValue(0)

        input_unidade = QComboBox()
        input_unidade.addItems(["kg", "litros", "tonelada", "saco", "unidade"])

        input_valor_total = QDoubleSpinBox()
        input_valor_total.setRange(0, 10000000000)
        input_valor_total.setDecimals(2)
        input_valor_total.setPrefix("R$ ")
        input_valor_total.setValue(0)

        form.addRow("Número NF:", input_numero)
        form.addRow("Fornecedor:", input_fornecedor)
        form.addRow("Material:", input_material)
        form.addRow("Quantidade:", input_quantidade)
        form.addRow("Unidade:", input_unidade)
        form.addRow("Valor Total:", input_valor_total)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        # ALTERAÇÃO: Estilo azul para os botões
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

        if dialog.exec():
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                self.criar_tabelas_se_necessario(conn)

                material_selecionado = input_material.currentText()

                # Inserir nota (INSERT OR REPLACE mantido para evitar duplicidade por número)
                cursor.execute('''
                    INSERT OR REPLACE INTO notas
                    (numero, fornecedor, material, quantidade, unidade, valor_total, data_emissao)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    input_numero.text().strip(),
                    input_fornecedor.text().strip(),
                    material_selecionado,
                    input_quantidade.value(),
                    input_unidade.currentText(),
                    input_valor_total.value(),
                    datetime.now().strftime("%Y-%m-%d")
                ))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "Sucesso", "Nota fiscal cadastrada!")
                self.carregar_notas()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Aviso", "Número de nota já cadastrado!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar nota: {e}")
                print(f"[TelaNotas.nova_nota] {e}")

    def editar_nota(self):
        linha = self.tabela_notas.currentRow()
        if linha >= 0:
            numero_item = self.tabela_notas.item(linha, 0)
            if not numero_item:
                QMessageBox.warning(self, "Aviso", "Número inválido selecionado.")
                return
            numero = numero_item.text()

            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT numero, fornecedor, material, quantidade, unidade, valor_total
                    FROM notas WHERE numero = ?
                ''', (numero,))
                nota = cursor.fetchone()
                conn.close()

                if nota:
                    dialog = QDialog(self)
                    dialog.setWindowTitle(f"Editar Nota {numero}")
                    dialog.setModal(True)
                    # ALTERAÇÃO: Estilo azul para o diálogo
                    dialog.setStyleSheet("""
                        QDialog {
                            background-color: white;
                        }
                        QLabel {
                            color: #0D47A1;
                            font-weight: bold;
                        }
                        QLineEdit, QComboBox, QDoubleSpinBox {
                            border: 2px solid #1976D2;
                            border-radius: 5px;
                            padding: 5px;
                            background-color: white;
                        }
                        QLineEdit:hover, QComboBox:hover, QDoubleSpinBox:hover {
                            border: 2px solid #0D47A1;
                        }
                    """)

                    layout = QVBoxLayout(dialog)
                    form = QFormLayout()

                    input_numero = QLineEdit(nota[0])
                    input_numero.setReadOnly(True)

                    input_fornecedor = QLineEdit(nota[1] or "")

                    input_material = QComboBox()
                    input_material.addItems([
                        "Cimento", "Brita 0", "Brita 1", "Areia Média",
                        "Pó de Brita", "Aditivo", "Água"
                    ])
                    index = input_material.findText(nota[2])
                    if index >= 0:
                        input_material.setCurrentIndex(index)

                    input_quantidade = QDoubleSpinBox()
                    input_quantidade.setRange(0, 10000000000)
                    input_quantidade.setDecimals(2)
                    input_quantidade.setValue(float(nota[3]) if nota[3] else 0)

                    input_unidade = QComboBox()
                    input_unidade.addItems(["kg", "litros", "tonelada", "saco", "unidade"])
                    index_unidade = input_unidade.findText(nota[4])
                    if index_unidade >= 0:
                        input_unidade.setCurrentIndex(index_unidade)

                    input_valor_total = QDoubleSpinBox()
                    input_valor_total.setRange(0, 10000000000)
                    input_valor_total.setDecimals(2)
                    input_valor_total.setPrefix("R$ ")
                    input_valor_total.setValue(float(nota[5]) if nota[5] else 0)

                    form.addRow("Número NF:", input_numero)
                    form.addRow("Fornecedor:", input_fornecedor)
                    form.addRow("Material:", input_material)
                    form.addRow("Quantidade:", input_quantidade)
                    form.addRow("Unidade:", input_unidade)
                    form.addRow("Valor Total:", input_valor_total)

                    layout.addLayout(form)

                    buttons = QDialogButtonBox(
                        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                    )

                    # ALTERAÇÃO: Estilo azul para os botões
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

                    def salvar_edicao():
                        try:
                            conn = self.get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute('''
                                UPDATE notas
                                SET fornecedor = ?, material = ?, quantidade = ?,
                                    unidade = ?, valor_total = ?
                                WHERE numero = ?
                            ''', (
                                input_fornecedor.text().strip(),
                                input_material.currentText(),
                                input_quantidade.value(),
                                input_unidade.currentText(),
                                input_valor_total.value(),
                                numero
                            ))
                            conn.commit()
                            conn.close()
                            QMessageBox.information(dialog, "Sucesso", "Nota atualizada!")
                            dialog.accept()
                            self.carregar_notas()
                        except Exception as e:
                            QMessageBox.critical(dialog, "Erro", f"Erro ao atualizar nota: {e}")
                            print(f"[TelaNotas.editar_nota.salvar_edicao] {e}")

                    buttons.accepted.connect(salvar_edicao)
                    buttons.rejected.connect(dialog.reject)
                    layout.addWidget(buttons)

                    dialog.exec()
                else:
                    QMessageBox.warning(self, "Aviso", "Nota não encontrada no banco.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao buscar nota: {e}")
                print(f"[TelaNotas.editar_nota] {e}")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma nota para editar!")

    def excluir_nota(self):
        linha = self.tabela_notas.currentRow()
        if linha >= 0:
            numero_item = self.tabela_notas.item(linha, 0)
            if not numero_item:
                QMessageBox.warning(self, "Aviso", "Número inválido.")
                return
            numero = numero_item.text()

            resposta = QMessageBox.question(
                self, "Confirmar Exclusão",
                f"Tem certeza que deseja excluir a nota {numero}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if resposta == QMessageBox.StandardButton.Yes:
                try:
                    conn = self.get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM notas WHERE numero = ?", (numero,))
                    conn.commit()
                    conn.close()
                    QMessageBox.information(self, "Sucesso", "Nota excluída!")
                    self.carregar_notas()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao excluir nota: {e}")
                    print(f"[TelaNotas.excluir_nota] {e}")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma nota para excluir!")

    # ----------------------------
    # Entrada no estoque (robusta)
    # ----------------------------
    def entrada_estoque(self):
        """
        Função completa e robusta para registrar a entrada de uma nota no estoque.
        Mantém layout e sinaliza a TelaEstoque via parent.atualizar_estoque_signal se existir.
        """
        linha = self.tabela_notas.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma nota para registrar entrada!")
            return

        # Ler campos da linha selecionada (com proteções)
        numero = (self.tabela_notas.item(linha, 0).text() if self.tabela_notas.item(linha, 0) else "").strip()
        fornecedor = (self.tabela_notas.item(linha, 1).text() if self.tabela_notas.item(linha, 1) else "").strip()
        material = (self.tabela_notas.item(linha, 2).text() if self.tabela_notas.item(linha, 2) else "").strip()

        # Ajuste de nomenclatura histórica
        if material == "Areia":
            material = "Areia Média"

        # Quantidade (com fallback)
        try:
            quantidade = float(self.tabela_notas.item(linha, 3).text())
        except Exception:
            quantidade = 0.0

        unidade = (self.tabela_notas.item(linha, 4).text() if self.tabela_notas.item(linha, 4) else "kg")

        if quantidade <= 0:
            QMessageBox.warning(self, "Aviso", "Quantidade inválida para entrada no estoque!")
            return

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            # garante estruturas e colunas básicas
            self.criar_tabelas_se_necessario(conn)

            # Inicia transação explícita
            cursor.execute("BEGIN")

            # Atualiza ou insere no estoque
            cursor.execute("SELECT quantidade FROM estoque WHERE material = ?", (material,))
            row = cursor.fetchone()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if row:
                # atualiza
                cursor.execute('''
                    UPDATE estoque
                    SET quantidade = quantidade + ?,
                        data_atualizacao = ?
                    WHERE material = ?
                ''', (quantidade, now_str, material))
            else:
                # insere novo (apenas se material for um dos permitidos ou desejar criar)
                cursor.execute('''
                    INSERT INTO estoque (material, quantidade, unidade, estoque_minimo, data_atualizacao)
                    VALUES (?, ?, ?, 0, ?)
                ''', (material, quantidade, unidade, now_str))

            # marca nota como registrada
            cursor.execute('''
                UPDATE notas
                SET status = 'REGISTRADO'
                WHERE numero = ?
            ''', (numero,))

            # registra no historico_estoque com campos consistentes
            cursor.execute('''
                INSERT INTO historico_estoque
                (material, quantidade, tipo, destino, observacoes, data_movimentacao, usuario, relacionamento_id, relacionamento_tipo)
                VALUES (?, ?, 'ENTRADA', ?, ?, ?, 'SISTEMA', ?, 'NOTA_ENTRADA')
            ''', (
                material,
                quantidade,
                f"Nota #{numero}",
                f"Fornecedor: {fornecedor}",
                now_str,
                numero
            ))

            # registra na tabela notas_entrada (evita duplicar por numero+material)
            cursor.execute('''
                SELECT id FROM notas_entrada WHERE numero_nota = ? AND material = ?
            ''', (numero, material))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO notas_entrada
                    (numero_nota, fornecedor, material, quantidade, unidade, data_entrada, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (numero, fornecedor, material, quantidade, unidade, now_str, "Entrada automática via tela de notas"))

            conn.commit()

            # obter novo saldo
            cursor.execute("SELECT quantidade FROM estoque WHERE material = ?", (material,))
            novo_saldo_row = cursor.fetchone()
            novo_saldo = novo_saldo_row[0] if novo_saldo_row else 0.0

            # feedback visual
            QMessageBox.information(
                self,
                "Sucesso",
                f"✅ Entrada registrada com sucesso!\n\n"
                f"📋 Nota: {numero}\n"
                f"🏭 Fornecedor: {fornecedor}\n"
                f"📦 Material: {material}\n"
                f"📊 Quantidade: {quantidade:.2f} {unidade}\n"
                f"💰 Saldo atual: {novo_saldo:.2f} {unidade}"
            )

            # recarregar dados na tela de notas
            self.carregar_notas()

            # avisar tela estoque para recarregar (se existir)
            if hasattr(self.parent, 'atualizar_estoque_signal'):
                try:
                    self.parent.atualizar_estoque_signal.emit()
                except Exception:
                    # sinal pode não existir — não quebra
                    pass

        except Exception as e:
            # tentar rollback seguro
            try:
                conn.rollback()
            except:
                pass
            QMessageBox.critical(self, "Erro", f"Erro ao registrar entrada: {e}")
            print(f"[TelaNotas.entrada_estoque] {e}")
        finally:
            try:
                conn.close()
            except:
                pass

    # ----------------------------
    # Migração auxiliar (não altera layout)
    # ----------------------------
    def migrar_notas_antigas(self):
        """
        Atualiza notas antigas que usam 'Areia' para 'Areia Média'.
        É segura: faz UPDATE somente se existir.
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE notas SET material = 'Areia Média' WHERE material = 'Areia'")
            conn.commit()
            conn.close()
            self.carregar_notas()
        except Exception as e:
            print(f"[TelaNotas.migrar_notas_antigas] Erro: {e}")