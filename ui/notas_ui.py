from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QFormLayout, QGroupBox, QMessageBox,
                             QHeaderView, QDialog, QDialogButtonBox,
                             QDoubleSpinBox, QComboBox, QDateEdit, QFileDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
import sqlite3
import json
from datetime import datetime
import os

class DialogNota(QDialog):
    def __init__(self, nota_id=None, parent=None):
        super().__init__(parent)
        self.nota_id = nota_id
        self.setWindowTitle("Nova Nota Fiscal" if not nota_id else "Editar Nota Fiscal")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Carregar fornecedores do JSON
        try:
            with open('cad_fornecedores.json', 'r', encoding='utf-8') as f:
                self.fornecedores = json.load(f)
        except:
            self.fornecedores = []
        
        # Carregar materiais do JSON
        try:
            with open('cad_materiais.json', 'r', encoding='utf-8') as f:
                self.materiais = json.load(f)
        except:
            self.materiais = []
        
        self.input_numero = QLineEdit()
        self.input_numero.setPlaceholderText("Número da NF")
        
        self.combo_fornecedor = QComboBox()
        for fornecedor in self.fornecedores:
            self.combo_fornecedor.addItem(fornecedor.get('nome', ''), fornecedor.get('id'))
        
        self.input_data_emissao = QDateEdit()
        self.input_data_emissao.setDate(QDate.currentDate())
        self.input_data_emissao.setCalendarPopup(True)
        
        self.input_data_entrada = QDateEdit()
        self.input_data_entrada.setDate(QDate.currentDate())
        self.input_data_entrada.setCalendarPopup(True)
        
        self.combo_material = QComboBox()
        for material in self.materiais:
            self.combo_material.addItem(material.get('nome', ''), material.get('id'))
        
        self.input_quantidade = QDoubleSpinBox()
        self.input_quantidade.setRange(0, 100000)
        
        self.combo_unidade = QComboBox()
        self.combo_unidade.addItems(["kg", "litros", "saco", "tonelada"])
        
        self.input_valor_unitario = QDoubleSpinBox()
        self.input_valor_unitario.setRange(0, 10000)
        self.input_valor_unitario.setPrefix("R$ ")
        
        self.input_valor_total = QDoubleSpinBox()
        self.input_valor_total.setRange(0, 1000000)
        self.input_valor_total.setPrefix("R$ ")
        
        self.input_chave_acesso = QLineEdit()
        self.input_chave_acesso.setPlaceholderText("Chave de acesso da NF-e")
        
        self.btn_selecionar_arquivo = QPushButton("📎 Selecionar Arquivo")
        self.btn_selecionar_arquivo.clicked.connect(self.selecionar_arquivo)
        self.arquivo_path = ""
        
        self.input_observacoes = QLineEdit()
        self.input_observacoes.setPlaceholderText("Observações sobre a nota...")
        
        form.addRow("Número NF *:", self.input_numero)
        form.addRow("Fornecedor *:", self.combo_fornecedor)
        form.addRow("Data Emissão:", self.input_data_emissao)
        form.addRow("Data Entrada:", self.input_data_entrada)
        form.addRow("Material *:", self.combo_material)
        form.addRow("Quantidade *:", self.input_quantidade)
        form.addRow("Unidade:", self.combo_unidade)
        form.addRow("Valor Unitário *:", self.input_valor_unitario)
        form.addRow("Valor Total *:", self.input_valor_total)
        form.addRow("Chave Acesso:", self.input_chave_acesso)
        form.addRow("Arquivo:", self.btn_selecionar_arquivo)
        form.addRow("Observações:", self.input_observacoes)
        
        layout.addLayout(form)
        
        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Conectar sinais para cálculo
        self.input_quantidade.valueChanged.connect(self.calcular_total)
        self.input_valor_unitario.valueChanged.connect(self.calcular_total)
        
        if nota_id:
            self.carregar_dados()
    
    def calcular_total(self):
        quantidade = self.input_quantidade.value()
        unitario = self.input_valor_unitario.value()
        self.input_valor_total.setValue(quantidade * unitario)
    
    def selecionar_arquivo(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo da Nota", 
            "", "PDF Files (*.pdf);;Image Files (*.png *.jpg);;All Files (*)"
        )
        if arquivo:
            self.arquivo_path = arquivo
            self.btn_selecionar_arquivo.setText(f"📎 {os.path.basename(arquivo)}")
    
    def carregar_dados(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notas_fornecedores WHERE id = ?", (self.nota_id,))
            nota = cursor.fetchone()
            conn.close()
            
            if nota:
                self.input_numero.setText(nota[1] or "")
                # Selecionar fornecedor
                if nota[2]:
                    index = self.combo_fornecedor.findText(nota[2])
                    if index >= 0:
                        self.combo_fornecedor.setCurrentIndex(index)
                
                if nota[3]:
                    self.input_data_emissao.setDate(QDate.fromString(nota[3], "yyyy-MM-dd"))
                if nota[4]:
                    self.input_data_entrada.setDate(QDate.fromString(nota[4], "yyyy-MM-dd"))
                
                if nota[5]:
                    index = self.combo_material.findText(nota[5])
                    if index >= 0:
                        self.combo_material.setCurrentIndex(index)
                
                self.input_quantidade.setValue(nota[6] or 0)
                if nota[7]:
                    index = self.combo_unidade.findText(nota[7])
                    if index >= 0:
                        self.combo_unidade.setCurrentIndex(index)
                
                self.input_valor_unitario.setValue(nota[8] or 0)
                self.input_valor_total.setValue(nota[9] or 0)
                self.input_chave_acesso.setText(nota[10] or "")
                
                if nota[11]:
                    self.arquivo_path = nota[11]
                    self.btn_selecionar_arquivo.setText(f"📎 {os.path.basename(nota[11])}")
                
                self.input_observacoes.setText(nota[12] or "")
                
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
    
    def get_dados(self):
        return {
            'numero_nota': self.input_numero.text(),
            'fornecedor': self.combo_fornecedor.currentText(),
            'data_emissao': self.input_data_emissao.date().toString("yyyy-MM-dd"),
            'data_entrada': self.input_data_entrada.date().toString("yyyy-MM-dd"),
            'tipo_material': self.combo_material.currentText(),
            'quantidade': self.input_quantidade.value(),
            'unidade': self.combo_unidade.currentText(),
            'valor_unitario': self.input_valor_unitario.value(),
            'valor_total': self.input_valor_total.value(),
            'chave_acesso': self.input_chave_acesso.text(),
            'arquivo_path': self.arquivo_path,
            'observacoes': self.input_observacoes.text()
        }

class TelaNotas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.nota_selecionada = None
        self.init_ui()
        self.carregar_notas()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("NOTAS FISCAIS DE FORNECEDORES")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #2E7D32; padding: 10px;")
        layout.addWidget(titulo)
        
        # Botões superiores
        btn_layout = QHBoxLayout()
        
        btn_novo = QPushButton("📄 Nova Nota")
        btn_novo.clicked.connect(self.nova_nota)
        
        btn_editar = QPushButton("✏️ Editar")
        btn_editar.clicked.connect(self.editar_nota)
        
        btn_excluir = QPushButton("🗑️ Excluir")
        btn_excluir.clicked.connect(self.excluir_nota)
        
        btn_visualizar = QPushButton("👁️ Visualizar NF")
        btn_visualizar.clicked.connect(self.visualizar_nota)
        
        btn_entrada_estoque = QPushButton("📦 Entrada em Estoque")
        btn_entrada_estoque.clicked.connect(self.entrada_estoque)
        
        btn_exportar = QPushButton("📤 Exportar")
        btn_exportar.clicked.connect(self.exportar_notas)
        
        btn_layout.addWidget(btn_novo)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_excluir)
        btn_layout.addWidget(btn_visualizar)
        btn_layout.addWidget(btn_entrada_estoque)
        btn_layout.addWidget(btn_exportar)
        
        layout.addLayout(btn_layout)
        
        # Filtros
        filtro_layout = QHBoxLayout()
        
        self.filtro_mes = QComboBox()
        meses = ["Todos", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.filtro_mes.addItems(meses)
        self.filtro_mes.setCurrentIndex(datetime.now().month)
        
        self.filtro_ano = QComboBox()
        anos = [str(year) for year in range(2020, datetime.now().year + 2)]
        self.filtro_ano.addItems(anos)
        self.filtro_ano.setCurrentText(str(datetime.now().year))
        
        self.filtro_fornecedor = QComboBox()
        self.filtro_fornecedor.addItem("Todos os Fornecedores", 0)
        
        btn_filtrar = QPushButton("🔍 Filtrar")
        btn_filtrar.clicked.connect(self.filtrar_notas)
        
        filtro_layout.addWidget(QLabel("Mês:"))
        filtro_layout.addWidget(self.filtro_mes)
        filtro_layout.addWidget(QLabel("Ano:"))
        filtro_layout.addWidget(self.filtro_ano)
        filtro_layout.addWidget(QLabel("Fornecedor:"))
        filtro_layout.addWidget(self.filtro_fornecedor)
        filtro_layout.addWidget(btn_filtrar)
        
        layout.addLayout(filtro_layout)
        
        # Tabela de notas
        self.tabela_notas = QTableWidget()
        self.tabela_notas.setColumnCount(10)
        self.tabela_notas.setHorizontalHeaderLabels([
            "ID", "Número NF", "Fornecedor", "Material", "Quantidade", 
            "Unidade", "Valor Unitário", "Valor Total", "Data Entrada", "Status"
        ])
        self.tabela_notas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_notas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_notas.clicked.connect(self.selecionar_nota)
        
        layout.addWidget(self.tabela_notas)
        
        # Estatísticas
        stats_layout = QHBoxLayout()
        
        self.label_total_notas = QLabel("Total de Notas: 0")
        self.label_valor_total = QLabel("Valor Total: R$ 0,00")
        self.label_estoque_pendente = QLabel("Entradas Pendentes: 0")
        
        stats_layout.addWidget(self.label_total_notas)
        stats_layout.addWidget(self.label_valor_total)
        stats_layout.addWidget(self.label_estoque_pendente)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
    
    def carregar_notas(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Carregar fornecedores para filtro
            cursor.execute("SELECT DISTINCT fornecedor FROM notas_fornecedores ORDER BY fornecedor")
            fornecedores = cursor.fetchall()
            
            self.filtro_fornecedor.clear()
            self.filtro_fornecedor.addItem("Todos os Fornecedores", 0)
            
            for fornecedor in fornecedores:
                if fornecedor[0]:
                    self.filtro_fornecedor.addItem(fornecedor[0], fornecedor[0])
            
            # Construir query de filtro
            mes = self.filtro_mes.currentIndex()
            ano = self.filtro_ano.currentText()
            fornecedor = self.filtro_fornecedor.currentData()
            
            query = '''
                SELECT id, numero_nota, fornecedor, tipo_material, quantidade,
                       unidade, valor_unitario, valor_total, data_entrada,
                       CASE WHEN quantidade > 0 THEN 'REGISTRADA' ELSE 'PENDENTE' END as status
                FROM notas_fornecedores
                WHERE 1=1
            '''
            params = []
            
            if mes > 0:  # Não é "Todos"
                query += " AND strftime('%m', data_entrada) = ?"
                params.append(f"{mes:02d}")
            
            if ano != "Todos":
                query += " AND strftime('%Y', data_entrada) = ?"
                params.append(ano)
            
            if fornecedor and fornecedor != 0:
                query += " AND fornecedor = ?"
                params.append(fornecedor)
            
            query += " ORDER BY data_entrada DESC"
            
            cursor.execute(query, params)
            notas = cursor.fetchall()
            conn.close()
            
            self.tabela_notas.setRowCount(len(notas))
            
            total_valor = 0
            pendentes = 0
            
            for i, nota in enumerate(notas):
                for j in range(10):
                    item = QTableWidgetItem(str(nota[j]) if nota[j] is not None else "")
                    
                    # Formatar valores monetários
                    if j == 6:  # valor_unitario
                        item.setText(f"R$ {nota[j]:.2f}" if nota[j] else "R$ 0,00")
                    elif j == 7:  # valor_total
                        valor = nota[j] or 0
                        total_valor += valor
                        item.setText(f"R$ {valor:.2f}")
                    
                    # Colorir status
                    if j == 9:  # status
                        if nota[j] == 'PENDENTE':
                            item.setForeground(QColor(255, 165, 0))  # Laranja
                            pendentes += 1
                        elif nota[j] == 'REGISTRADA':
                            item.setForeground(QColor(0, 128, 0))   # Verde
                    
                    self.tabela_notas.setItem(i, j, item)
            
            # Atualizar estatísticas
            self.label_total_notas.setText(f"Total de Notas: {len(notas)}")
            self.label_valor_total.setText(f"Valor Total: R$ {total_valor:.2f}")
            self.label_estoque_pendente.setText(f"Entradas Pendentes: {pendentes}")
            
            if notas:
                self.tabela_notas.selectRow(0)
                self.selecionar_nota()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar notas: {e}")
    
    def filtrar_notas(self):
        self.carregar_notas()
    
    def selecionar_nota(self):
        linha = self.tabela_notas.currentRow()
        if linha >= 0:
            self.nota_selecionada = int(self.tabela_notas.item(linha, 0).text())
    
    def nova_nota(self):
        dialog = DialogNota()
        if dialog.exec():
            dados = dialog.get_dados()
            
            try:
                conn = sqlite3.connect('usina_concreto.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO notas_fornecedores 
                    (numero_nota, fornecedor, data_emissao, data_entrada,
                     tipo_material, quantidade, unidade, valor_unitario,
                     valor_total, chave_acesso, nf_caminho, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    dados['numero_nota'], dados['fornecedor'], dados['data_emissao'],
                    dados['data_entrada'], dados['tipo_material'], dados['quantidade'],
                    dados['unidade'], dados['valor_unitario'], dados['valor_total'],
                    dados['chave_acesso'], dados['arquivo_path'], dados['observacoes']
                ))
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Sucesso", "Nota fiscal cadastrada com sucesso!")
                self.carregar_notas()
                
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Aviso", "Número de nota já cadastrado!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar nota: {e}")
    
    def editar_nota(self):
        if not self.nota_selecionada:
            QMessageBox.warning(self, "Aviso", "Selecione uma nota para editar!")
            return
        
        dialog = DialogNota(self.nota_selecionada, self)
        if dialog.exec():
            dados = dialog.get_dados()
            
            try:
                conn = sqlite3.connect('usina_concreto.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE notas_fornecedores 
                    SET numero_nota=?, fornecedor=?, data_emissao=?, data_entrada=?,
                        tipo_material=?, quantidade=?, unidade=?, valor_unitario=?,
                        valor_total=?, chave_acesso=?, nf_caminho=?, observacoes=?
                    WHERE id=?
                ''', (
                    dados['numero_nota'], dados['fornecedor'], dados['data_emissao'],
                    dados['data_entrada'], dados['tipo_material'], dados['quantidade'],
                    dados['unidade'], dados['valor_unitario'], dados['valor_total'],
                    dados['chave_acesso'], dados['arquivo_path'], dados['observacoes'],
                    self.nota_selecionada
                ))
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Sucesso", "Nota fiscal atualizada com sucesso!")
                self.carregar_notas()
                
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Aviso", "Número de nota já cadastrado!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao atualizar nota: {e}")
    
    def excluir_nota(self):
        if not self.nota_selecionada:
            QMessageBox.warning(self, "Aviso", "Selecione uma nota para excluir!")
            return
        
        resposta = QMessageBox.question(
            self, "Confirmar Exclusão",
            "Tem certeza que deseja excluir esta nota fiscal?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect('usina_concreto.db')
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM notas_fornecedores WHERE id = ?", (self.nota_selecionada,))
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Sucesso", "Nota fiscal excluída com sucesso!")
                self.carregar_notas()
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir nota: {e}")
    
    def visualizar_nota(self):
        if not self.nota_selecionada:
            QMessageBox.warning(self, "Aviso", "Selecione uma nota para visualizar!")
            return
        
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            cursor.execute("SELECT nf_caminho FROM notas_fornecedores WHERE id = ?", (self.nota_selecionada,))
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado and resultado[0] and os.path.exists(resultado[0]):
                import subprocess
                try:
                    os.startfile(resultado[0])  # Windows
                except:
                    subprocess.run(['xdg-open', resultado[0]])  # Linux
            else:
                QMessageBox.warning(self, "Aviso", "Arquivo da nota não encontrado!")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir nota: {e}")
    
    def entrada_estoque(self):
        if not self.nota_selecionada:
            QMessageBox.warning(self, "Aviso", "Selecione uma nota para registrar entrada!")
            return
        
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Buscar dados da nota
            cursor.execute('''
                SELECT tipo_material, quantidade, unidade 
                FROM notas_fornecedores WHERE id = ?
            ''', (self.nota_selecionada,))
            nota = cursor.fetchone()
            
            if not nota:
                QMessageBox.warning(self, "Aviso", "Nota não encontrada!")
                return
            
            material = nota[0]
            quantidade = nota[1]
            unidade = nota[2]
            
            # Atualizar estoque
            cursor.execute('''
                UPDATE estoque 
                SET quantidade = quantidade + ?
                WHERE material = ?
            ''', (quantidade, material))
            
            # Atualizar status da nota
            cursor.execute('''
                UPDATE notas_fornecedores 
                SET quantidade = ?
                WHERE id = ?
            ''', (quantidade, self.nota_selecionada))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Sucesso", f"Entrada de {quantidade} {unidade} de {material} registrada no estoque!")
            self.carregar_notas()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao registrar entrada: {e}")
    
    def exportar_notas(self):
        try:
            import csv
            from datetime import datetime
            
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT numero_nota, fornecedor, data_emissao, data_entrada,
                       tipo_material, quantidade, unidade, valor_unitario,
                       valor_total, chave_acesso
                FROM notas_fornecedores
                ORDER BY data_entrada DESC
            ''')
            
            notas = cursor.fetchall()
            conn.close()
            
            filename = f"notas_fiscais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow([
                    'Número NF', 'Fornecedor', 'Data Emissão', 'Data Entrada',
                    'Material', 'Quantidade', 'Unidade', 'Valor Unitário',
                    'Valor Total', 'Chave Acesso'
                ])
                
                for nota in notas:
                    writer.writerow(nota)
            
            QMessageBox.information(self, "Sucesso", f"Dados exportados para: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar dados: {e}")