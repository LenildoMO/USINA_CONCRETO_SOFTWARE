from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QFormLayout, QGroupBox, QMessageBox,
                             QHeaderView, QDialog, QDialogButtonBox,
                             QDoubleSpinBox, QComboBox, QDateEdit, QTimeEdit,
                             QTextEdit)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush
import sqlite3
import json
from datetime import datetime

class SincronizadorEstoque:
    """Classe responsável por sincronizar estoque com pesagens"""
    
    @staticmethod
    def verificar_estoque_disponivel(traco_id: int) -> tuple:
        """Verifica se há estoque suficiente para uma pesagem"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Obter composição do traço
            query = """
                SELECT 
                    COALESCE(cimento, 0) as cimento,
                    COALESCE(brita0, 0) as brita0,
                    COALESCE(brita1, 0) as brita1,
                    COALESCE(areia_media, 0) as areia_media,
                    COALESCE(po_brita, 0) as po_brita,
                    COALESCE(agua, 0) as agua,
                    COALESCE(aditivo, 0) as aditivo
                FROM tracos 
                WHERE id = ?
            """
            cursor.execute(query, (traco_id,))
            traco = cursor.fetchone()
            
            if not traco:
                conn.close()
                return False, {}, "Traço não encontrado"
            
            # Usar valores do traço diretamente (SEM MULTIPLICAÇÃO)
            materiais_necessarios = {
                "Cimento": traco[0],
                "Brita 0": traco[1],
                "Brita 1": traco[2],
                "Areia Média": traco[3],
                "Pó de Brita": traco[4],
                "Água": traco[5],
                "Aditivo": traco[6]
            }
            
            # Verificar estoque para cada material
            materiais_faltantes = []
            for material, qtd_necessaria in materiais_necessarios.items():
                if qtd_necessaria > 0:
                    cursor.execute(
                        "SELECT quantidade, unidade FROM estoque WHERE material = ?",
                        (material,)
                    )
                    estoque = cursor.fetchone()
                    
                    if not estoque:
                        materiais_faltantes.append(f"{material}: não cadastrado")
                    elif estoque[0] < qtd_necessaria:
                        falta = qtd_necessaria - estoque[0]
                        materiais_faltantes.append(f"{material}: falta {falta:.2f} {estoque[1]}")
            
            conn.close()
            
            if materiais_faltantes:
                mensagem = "Estoque insuficiente:\n" + "\n".join(materiais_faltantes)
                return False, materiais_necessarios, mensagem
            
            return True, materiais_necessarios, "Estoque disponível"
            
        except Exception as e:
            return False, {}, f"Erro ao verificar estoque: {str(e)}"
    
    @staticmethod
    def dar_saida_estoque(materiais_utilizados: dict, id_pesagem: int, traco_nome: str) -> tuple:
        """Dá saída no estoque para os materiais utilizados"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            detalhes = []
            cursor.execute("BEGIN TRANSACTION")
            
            try:
                for material, quantidade in materiais_utilizados.items():
                    if quantidade > 0:
                        # Verificar estoque atual
                        cursor.execute(
                            "SELECT quantidade, unidade FROM estoque WHERE material = ?",
                            (material,)
                        )
                        estoque = cursor.fetchone()
                        
                        if estoque:
                            estoque_atual = estoque[0]
                            unidade = estoque[1]
                            
                            if estoque_atual >= quantidade:
                                # Atualizar estoque
                                novo_estoque = estoque_atual - quantidade
                                cursor.execute('''
                                    UPDATE estoque 
                                    SET quantidade = ?,
                                        data_atualizacao = ?
                                    WHERE material = ?
                                ''', (novo_estoque, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), material))
                                
                                # Registrar no histórico
                                cursor.execute('''
                                    INSERT INTO historico_estoque 
                                    (material, quantidade, tipo, destino, data_movimentacao, observacoes)
                                    VALUES (?, ?, 'SAIDA', ?, ?, ?)
                                ''', (
                                    material,
                                    quantidade,
                                    f"Pesagem #{id_pesagem} - {traco_nome}",
                                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    f"Saída automática da pesagem"
                                ))
                                
                                detalhes.append(f"{material}: {estoque_atual:.2f} → {novo_estoque:.2f} {unidade}")
                            else:
                                raise Exception(f"Estoque insuficiente de {material}. Disponível: {estoque_atual:.2f}, Necessário: {quantidade:.2f}")
                
                conn.commit()
                conn.close()
                
                return True, "Saída no estoque realizada com sucesso", detalhes
                
            except Exception as e:
                conn.rollback()
                conn.close()
                return False, f"Erro ao dar saída no estoque: {str(e)}", []
                
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}", []

class DialogPesagem(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Pesagem")
        self.setModal(True)
        self.setMinimumWidth(700)
        
        layout = QVBoxLayout(self)
        
        # Formulário
        form = QFormLayout()
        
        # Data e Hora
        self.input_data = QDateEdit()
        self.input_data.setDate(QDate.currentDate())
        self.input_data.setCalendarPopup(True)
        
        self.input_hora = QTimeEdit()
        self.input_hora.setTime(QTime.currentTime())
        
        # Cliente
        self.combo_cliente = QComboBox()
        self.carregar_clientes()
        
        # Traço
        self.combo_traco = QComboBox()
        self.carregar_tracos()
        
        # Placa
        self.input_placa = QLineEdit()
        self.input_placa.setPlaceholderText("AAA-0000")
        
        # Motorista
        self.input_motorista = QLineEdit()
        self.input_motorista.setPlaceholderText("Nome do motorista")
        
        # Volume do Traço (alterado de Quantidade)
        self.input_volume_traco = QDoubleSpinBox()
        self.input_volume_traco.setRange(0.1, 50)
        self.input_volume_traco.setValue(1)
        self.input_volume_traco.setSuffix(" m³")
        self.input_volume_traco.setReadOnly(True)
        self.input_volume_traco.setStyleSheet("background-color: #F5F5F5; color: #333;")
        
        form.addRow("Data:", self.input_data)
        form.addRow("Hora:", self.input_hora)
        form.addRow("Cliente:", self.combo_cliente)
        form.addRow("Traço:", self.combo_traco)
        form.addRow("Placa do Veículo:", self.input_placa)
        form.addRow("Motorista:", self.input_motorista)
        form.addRow("Volume do Traço:", self.input_volume_traco)
        
        layout.addLayout(form)
        
        # Informações do traço selecionado
        info_group = QGroupBox("📋 INFORMAÇÕES DO TRAÇO")
        info_layout = QVBoxLayout()
        
        self.label_info_traco = QLabel("Selecione um traço para ver as informações")
        self.label_info_traco.setWordWrap(True)
        self.label_info_traco.setStyleSheet("padding: 5px; background-color: #E8F5E9; border-radius: 5px;")
        
        info_layout.addWidget(self.label_info_traco)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Materiais do traço
        materiais_group = QGroupBox("💡 COMPOSIÇÃO DO TRAÇO")
        materiais_layout = QVBoxLayout()
        
        # Tabela de materiais do traço
        self.tabela_materiais = QTableWidget()
        self.tabela_materiais.setColumnCount(3)
        self.tabela_materiais.setHorizontalHeaderLabels(["Material", "Quantidade", "Unidade"])
        self.tabela_materiais.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela_materiais.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabela_materiais.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_materiais.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_materiais.setMaximumHeight(200)
        
        materiais_layout.addWidget(self.tabela_materiais)
        
        # Total de materiais
        self.label_total_materiais = QLabel("Total de materiais: 0 kg")
        self.label_total_materiais.setStyleSheet("font-weight: bold; color: #0D47A1;")
        materiais_layout.addWidget(self.label_total_materiais)
        
        materiais_group.setLayout(materiais_layout)
        layout.addWidget(materiais_group)
        
        # Observações
        self.input_observacoes = QLineEdit()
        self.input_observacoes.setPlaceholderText("Observações da pesagem...")
        layout.addWidget(QLabel("Observações:"))
        layout.addWidget(self.input_observacoes)
        
        # Conectar sinais para carregar informações do traço
        self.combo_traco.currentIndexChanged.connect(self.carregar_informacoes_traco)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validar_e_aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Carregar informações iniciais
        self.carregar_informacoes_traco()
        
        # Aplicar estilos
        self.aplicar_estilos()
    
    def aplicar_estilos(self):
        """Aplica os estilos de cores azuis"""
        # Estilo para GroupBox
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #E3F2FD;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QDoubleSpinBox, QTextEdit {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, 
            QDoubleSpinBox:focus, QTextEdit:focus {
                border: 2px solid #1976D2;
            }
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                border: 1px solid #0D47A1;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        # Estilo para tabela de materiais
        self.tabela_materiais.setStyleSheet("""
            QTableWidget {
                border: 2px solid #1976D2;
                border-radius: 5px;
                background-color: white;
                alternate-background-color: #E3F2FD;
                gridline-color: #2196F3;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #BBDEFB;
            }
            QTableWidget::item:selected {
                background-color: #BBDEFB;
                color: #0D47A1;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #0D47A1;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
                border-right: 1px solid #1565C0;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
    
    def carregar_clientes(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
            clientes = cursor.fetchall()
            conn.close()
            
            # Armazenar ID e nome
            self.clientes_dict = {}
            for cliente_id, cliente_nome in clientes:
                self.combo_cliente.addItem(cliente_nome)
                self.clientes_dict[cliente_nome] = cliente_id
            
            if not clientes:
                self.combo_cliente.addItem("Sem clientes cadastrados")
                
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
    
    def carregar_tracos(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, codigo, nome, fck, volume_m3 
                FROM tracos 
                WHERE status = 'ATIVO' 
                ORDER BY codigo
            """)
            tracos = cursor.fetchall()
            conn.close()
            
            # Armazenar ID e informações
            self.tracos_dict = {}
            self.tracos_info = {}
            for traco_id, traco_codigo, traco_nome, fck, volume_m3 in tracos:
                display_text = f"{traco_codigo} - {traco_nome}"
                self.combo_traco.addItem(display_text)
                self.tracos_dict[display_text] = traco_id
                self.tracos_info[display_text] = {
                    'codigo': traco_codigo,
                    'nome': traco_nome,
                    'fck': fck,
                    'volume_m3': volume_m3 if volume_m3 else 0.5
                }
            
            if not tracos:
                self.combo_traco.addItem("Sem traços cadastrados")
                
        except Exception as e:
            print(f"Erro ao carregar traços: {e}")
    
    def carregar_informacoes_traco(self):
        """Carrega as informações do traço selecionado"""
        try:
            traco_texto = self.combo_traco.currentText()
            if traco_texto and " - " in traco_texto:
                traco_id = self.tracos_dict.get(traco_texto)
                
                if traco_id:
                    conn = sqlite3.connect('usina_concreto.db')
                    cursor = conn.cursor()
                    
                    # Query para obter todos os materiais do traço
                    query = """
                        SELECT 
                            COALESCE(cimento, 0) as cimento,
                            COALESCE(brita0, 0) as brita0,
                            COALESCE(brita1, 0) as brita1,
                            COALESCE(areia_media, 0) as areia_media,
                            COALESCE(po_brita, 0) as po_brita,
                            COALESCE(agua, 0) as agua,
                            COALESCE(aditivo, 0) as aditivo,
                            COALESCE(volume_m3, 0.5) as volume_m3,
                            COALESCE(fck, 0) as fck
                        FROM tracos 
                        WHERE id = ?
                    """
                    cursor.execute(query, (traco_id,))
                    traco = cursor.fetchone()
                    
                    if traco:
                        # Atualizar volume do traço no campo
                        volume_traco = traco[7] if traco[7] else 0.5
                        self.input_volume_traco.setValue(float(volume_traco))
                        
                        # Atualizar informações do traço
                        if traco_texto in self.tracos_info:
                            info = self.tracos_info[traco_texto]
                            self.label_info_traco.setText(
                                f"Traço: {info['codigo']} - {info['nome']}\n"
                                f"fck: {info['fck']} MPa | Volume: {volume_traco:.2f} m³"
                            )
                        
                        # Usar valores do traço diretamente (SEM MULTIPLICAÇÃO)
                        materiais = [
                            ("Cimento", traco[0], "kg"),
                            ("Brita 0", traco[1], "kg"),
                            ("Brita 1", traco[2], "kg"),
                            ("Areia Média", traco[3], "kg"),
                            ("Pó de Brita", traco[4], "kg"),
                            ("Água", traco[5], "litros"),
                            ("Aditivo", traco[6], "kg")
                        ]
                        
                        # Atualizar tabela de materiais
                        self.tabela_materiais.setRowCount(len(materiais))
                        total_kg = 0
                        
                        for i, (material, qtd, unidade) in enumerate(materiais):
                            self.tabela_materiais.setItem(i, 0, QTableWidgetItem(material))
                            self.tabela_materiais.setItem(i, 1, QTableWidgetItem(f"{qtd:.2f}"))
                            self.tabela_materiais.setItem(i, 2, QTableWidgetItem(unidade))
                            
                            # Somar materiais em kg (exceto água que é em litros)
                            if unidade == "kg":
                                total_kg += qtd
                        
                        # Armazenar materiais calculados para uso posterior
                        self.materiais_calculados = materiais
                        
                        # Atualizar total
                        self.label_total_materiais.setText(f"Total de materiais: {total_kg:.2f} kg")
                    
                    conn.close()
                    
        except Exception as e:
            print(f"Erro ao carregar informações do traço: {e}")
    
    def validar_e_aceitar(self):
        # Validar campos obrigatórios
        if self.combo_cliente.currentText() == "Sem clientes cadastrados" or not self.combo_cliente.currentText():
            QMessageBox.warning(self, "Atenção", "Selecione um cliente válido!")
            return
        
        if self.combo_traco.currentText() == "Sem traços cadastrados" or not self.combo_traco.currentText():
            QMessageBox.warning(self, "Atenção", "Selecione um traço válido!")
            return
        
        if not self.input_placa.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe a placa do veículo!")
            self.input_placa.setFocus()
            return
        
        if not self.input_motorista.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o nome do motorista!")
            self.input_motorista.setFocus()
            return
        
        if self.input_volume_traco.value() <= 0:
            QMessageBox.warning(self, "Atenção", "O volume do traço deve ser maior que zero!")
            self.input_volume_traco.setFocus()
            return
        
        # Verificação de estoque antes de criar pesagem
        traco_texto = self.combo_traco.currentText()
        traco_id = self.tracos_dict.get(traco_texto)
        
        if traco_id:
            sucesso, materiais, mensagem = SincronizadorEstoque.verificar_estoque_disponivel(traco_id)
            
            if not sucesso:
                resposta = QMessageBox.warning(
                    self, "Estoque Insuficiente",
                    f"{mensagem}\n\nDeseja criar a pesagem mesmo assim?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if resposta == QMessageBox.StandardButton.No:
                    return
        
        self.accept()
    
    def get_dados(self):
        # Combinar data e hora para data_pesagem
        data_str = self.input_data.date().toString("yyyy-MM-dd")
        hora_str = self.input_hora.time().toString("HH:mm")
        data_pesagem = f"{data_str} {hora_str}"
        
        # Obter IDs dos combos
        cliente_nome = self.combo_cliente.currentText()
        cliente_id = self.clientes_dict.get(cliente_nome)
        
        traco_texto = self.combo_traco.currentText()
        traco_id = self.tracos_dict.get(traco_texto)
        
        # Criar JSON com materiais do traço (SEM MULTIPLICAÇÃO)
        materiais_json = {}
        if hasattr(self, 'materiais_calculados'):
            for material, qtd, unidade in self.materiais_calculados:
                materiais_json[material] = {
                    "quantidade": qtd,
                    "unidade": unidade
                }
        else:
            # Criar estrutura padrão com todos os materiais
            materiais_json = {
                "Cimento": {"quantidade": 0, "unidade": "kg"},
                "Brita 0": {"quantidade": 0, "unidade": "kg"},
                "Brita 1": {"quantidade": 0, "unidade": "kg"},
                "Areia Média": {"quantidade": 0, "unidade": "kg"},
                "Pó de Brita": {"quantidade": 0, "unidade": "kg"},
                "Água": {"quantidade": 0, "unidade": "litros"},
                "Aditivo": {"quantidade": 0, "unidade": "kg"}
            }
        
        return {
            'cliente_id': cliente_id,
            'traco_id': traco_id,
            'quantidade': self.input_volume_traco.value(),
            'placa_veiculo': self.input_placa.text().strip(),
            'motorista': self.input_motorista.text().strip(),
            'data_pesagem': data_pesagem,
            'observacoes': self.input_observacoes.text().strip(),
            'materiais_json': json.dumps(materiais_json, ensure_ascii=False)
        }

class DialogEditarPesagem(QDialog):
    def __init__(self, parent=None, id_pesagem=None, dados_pesagem=None):
        super().__init__(parent)
        self.id_pesagem = id_pesagem
        self.dados_pesagem = dados_pesagem
        self.setWindowTitle(f"Editar Pesagem #{id_pesagem}")
        self.setModal(True)
        self.setMinimumWidth(700)
        
        layout = QVBoxLayout(self)
        
        # Formulário
        form = QFormLayout()
        
        # Data e Hora
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        
        self.input_hora = QTimeEdit()
        
        # Cliente
        self.combo_cliente = QComboBox()
        self.carregar_clientes()
        
        # Traço
        self.combo_traco = QComboBox()
        self.carregar_tracos()
        
        # Placa
        self.input_placa = QLineEdit()
        
        # Motorista
        self.input_motorista = QLineEdit()
        
        # Volume do Traço (alterado de Quantidade)
        self.input_volume_traco = QDoubleSpinBox()
        self.input_volume_traco.setRange(0.1, 50)
        self.input_volume_traco.setSuffix(" m³")
        self.input_volume_traco.setReadOnly(True)
        self.input_volume_traco.setStyleSheet("background-color: #F5F5F5; color: #333;")
        
        form.addRow("Data:", self.input_data)
        form.addRow("Hora:", self.input_hora)
        form.addRow("Cliente:", self.combo_cliente)
        form.addRow("Traço:", self.combo_traco)
        form.addRow("Placa do Veículo:", self.input_placa)
        form.addRow("Motorista:", self.input_motorista)
        form.addRow("Volume do Traço:", self.input_volume_traco)
        
        layout.addLayout(form)
        
        # Informações do traço selecionado
        info_group = QGroupBox("📋 INFORMAÇÕES DO TRAÇO")
        info_layout = QVBoxLayout()
        
        self.label_info_traco = QLabel("Selecione um traço para ver as informações")
        self.label_info_traco.setWordWrap(True)
        self.label_info_traco.setStyleSheet("padding: 5px; background-color: #E8F5E9; border-radius: 5px;")
        
        info_layout.addWidget(self.label_info_traco)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Materiais do traço
        materiais_group = QGroupBox("💡 COMPOSIÇÃO DO TRAÇO")
        materiais_layout = QVBoxLayout()
        
        # Tabela de materiais do traço
        self.tabela_materiais = QTableWidget()
        self.tabela_materiais.setColumnCount(3)
        self.tabela_materiais.setHorizontalHeaderLabels(["Material", "Quantidade", "Unidade"])
        self.tabela_materiais.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela_materiais.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabela_materiais.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_materiais.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_materiais.setMaximumHeight(200)
        
        materiais_layout.addWidget(self.tabela_materiais)
        
        # Total de materiais
        self.label_total_materiais = QLabel("Total de materiais: 0 kg")
        self.label_total_materiais.setStyleSheet("font-weight: bold; color: #0D47A1;")
        materiais_layout.addWidget(self.label_total_materiais)
        
        materiais_group.setLayout(materiais_layout)
        layout.addWidget(materiais_group)
        
        # Observações
        self.input_observacoes = QTextEdit()
        self.input_observacoes.setPlaceholderText("Observações da pesagem...")
        self.input_observacoes.setMaximumHeight(100)
        layout.addWidget(QLabel("Observações:"))
        layout.addWidget(self.input_observacoes)
        
        # Preencher com dados existentes
        self.preencher_dados()
        
        # Conectar sinais para carregar informações do traço
        self.combo_traco.currentIndexChanged.connect(self.carregar_informacoes_traco)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validar_e_aceitar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Carregar informações iniciais
        self.carregar_informacoes_traco()
        
        # Aplicar estilos
        self.aplicar_estilos()
    
    def aplicar_estilos(self):
        """Aplica os estilos de cores azuis"""
        # Estilo para GroupBox
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #E3F2FD;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QDoubleSpinBox, QTextEdit {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, 
            QDoubleSpinBox:focus, QTextEdit:focus {
                border: 2px solid #1976D2;
            }
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                border: 1px solid #0D47A1;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        # Estilo para tabela de materiais
        self.tabela_materiais.setStyleSheet("""
            QTableWidget {
                border: 2px solid #1976D2;
                border-radius: 5px;
                background-color: white;
                alternate-background-color: #E3F2FD;
                gridline-color: #2196F3;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #BBDEFB;
            }
            QTableWidget::item:selected {
                background-color: #BBDEFB;
                color: #0D47A1;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #0D47A1;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
                border-right: 1px solid #1565C0;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
    
    def preencher_dados(self):
        """Preenche o formulário com os dados atuais da pesagem"""
        if self.dados_pesagem:
            # Data e hora
            data_pesagem = self.dados_pesagem[5]  # data_pesagem
            if data_pesagem:
                try:
                    if ' ' in data_pesagem:
                        data_str, hora_str = data_pesagem.split(' ')
                        self.input_data.setDate(QDate.fromString(data_str, "yyyy-MM-dd"))
                        self.input_hora.setTime(QTime.fromString(hora_str, "HH:mm"))
                except:
                    pass
            
            # Cliente
            cliente_nome = self.dados_pesagem[8]  # cliente_nome
            if cliente_nome:
                index = self.combo_cliente.findText(cliente_nome)
                if index >= 0:
                    self.combo_cliente.setCurrentIndex(index)
            
            # Traço
            traco_nome = self.dados_pesagem[9]  # traco_nome
            if traco_nome:
                index = self.combo_traco.findText(traco_nome)
                if index >= 0:
                    self.combo_traco.setCurrentIndex(index)
            
            # Outros campos
            self.input_placa.setText(str(self.dados_pesagem[3] if self.dados_pesagem[3] else ""))
            self.input_motorista.setText(str(self.dados_pesagem[4] if self.dados_pesagem[4] else ""))
            # Volume do traço será carregado automaticamente quando o traço for selecionado
            self.input_observacoes.setPlainText(str(self.dados_pesagem[6] if self.dados_pesagem[6] else ""))
    
    def carregar_clientes(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
            clientes = cursor.fetchall()
            conn.close()
            
            # Armazenar ID e nome
            self.clientes_dict = {}
            for cliente_id, cliente_nome in clientes:
                self.combo_cliente.addItem(cliente_nome)
                self.clientes_dict[cliente_nome] = cliente_id
                
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
    
    def carregar_tracos(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, codigo, nome, fck, volume_m3 
                FROM tracos 
                WHERE status = 'ATIVO' 
                ORDER BY codigo
            """)
            tracos = cursor.fetchall()
            conn.close()
            
            # Armazenar ID e informações
            self.tracos_dict = {}
            self.tracos_info = {}
            for traco_id, traco_codigo, traco_nome, fck, volume_m3 in tracos:
                display_text = f"{traco_codigo} - {traco_nome}"
                self.combo_traco.addItem(display_text)
                self.tracos_dict[display_text] = traco_id
                self.tracos_info[display_text] = {
                    'codigo': traco_codigo,
                    'nome': traco_nome,
                    'fck': fck,
                    'volume_m3': volume_m3 if volume_m3 else 0.5
                }
                
        except Exception as e:
            print(f"Erro ao carregar traços: {e}")
    
    def carregar_informacoes_traco(self):
        """Carrega as informações do traço selecionado"""
        try:
            traco_texto = self.combo_traco.currentText()
            if traco_texto and " - " in traco_texto:
                traco_id = self.tracos_dict.get(traco_texto)
                
                if traco_id:
                    conn = sqlite3.connect('usina_concreto.db')
                    cursor = conn.cursor()
                    
                    query = """
                        SELECT 
                            COALESCE(cimento, 0) as cimento,
                            COALESCE(brita0, 0) as brita0,
                            COALESCE(brita1, 0) as brita1,
                            COALESCE(areia_media, 0) as areia_media,
                            COALESCE(po_brita, 0) as po_brita,
                            COALESCE(agua, 0) as agua,
                            COALESCE(aditivo, 0) as aditivo,
                            COALESCE(volume_m3, 0.5) as volume_m3,
                            COALESCE(fck, 0) as fck
                        FROM tracos 
                        WHERE id = ?
                    """
                    cursor.execute(query, (traco_id,))
                    traco = cursor.fetchone()
                    
                    if traco:
                        # Atualizar volume do traço no campo
                        volume_traco = traco[7] if traco[7] else 0.5
                        self.input_volume_traco.setValue(float(volume_traco))
                        
                        # Atualizar informações do traço
                        if traco_texto in self.tracos_info:
                            info = self.tracos_info[traco_texto]
                            self.label_info_traco.setText(
                                f"Traço: {info['codigo']} - {info['nome']}\n"
                                f"fck: {info['fck']} MPa | Volume: {volume_traco:.2f} m³"
                            )
                        
                        # Usar valores do traço diretamente (SEM MULTIPLICAÇÃO)
                        materiais = [
                            ("Cimento", traco[0], "kg"),
                            ("Brita 0", traco[1], "kg"),
                            ("Brita 1", traco[2], "kg"),
                            ("Areia Média", traco[3], "kg"),
                            ("Pó de Brita", traco[4], "kg"),
                            ("Água", traco[5], "litros"),
                            ("Aditivo", traco[6], "kg")
                        ]
                        
                        # Atualizar tabela de materiais
                        self.tabela_materiais.setRowCount(len(materiais))
                        total_kg = 0
                        
                        for i, (material, qtd, unidade) in enumerate(materiais):
                            self.tabela_materiais.setItem(i, 0, QTableWidgetItem(material))
                            self.tabela_materiais.setItem(i, 1, QTableWidgetItem(f"{qtd:.2f}"))
                            self.tabela_materiais.setItem(i, 2, QTableWidgetItem(unidade))
                            
                            if unidade == "kg":
                                total_kg += qtd
                        
                        # Armazenar materiais calculados
                        self.materiais_calculados = materiais
                        
                        # Atualizar total
                        self.label_total_materiais.setText(f"Total de materiais: {total_kg:.2f} kg")
                    
                    conn.close()
                    
        except Exception as e:
            print(f"Erro ao carregar informações do traço: {e}")
    
    def validar_e_aceitar(self):
        # Validar campos obrigatórios
        if not self.combo_cliente.currentText():
            QMessageBox.warning(self, "Atenção", "Selecione um cliente válido!")
            return
        
        if not self.combo_traco.currentText():
            QMessageBox.warning(self, "Atenção", "Selecione um traço válido!")
            return
        
        if not self.input_placa.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe a placa do veículo!")
            self.input_placa.setFocus()
            return
        
        if not self.input_motorista.text().strip():
            QMessageBox.warning(self, "Atenção", "Informe o nome do motorista!")
            self.input_motorista.setFocus()
            return
        
        if self.input_volume_traco.value() <= 0:
            QMessageBox.warning(self, "Atenção", "O volume do traço deve ser maior que zero!")
            self.input_volume_traco.setFocus()
            return
        
        self.accept()
    
    def get_dados(self):
        # Combinar data e hora para data_pesagem
        data_str = self.input_data.date().toString("yyyy-MM-dd")
        hora_str = self.input_hora.time().toString("HH:mm")
        data_pesagem = f"{data_str} {hora_str}"
        
        # Obter IDs dos combos
        cliente_nome = self.combo_cliente.currentText()
        cliente_id = self.clientes_dict.get(cliente_nome)
        
        traco_texto = self.combo_traco.currentText()
        traco_id = self.tracos_dict.get(traco_texto)
        
        # Criar JSON com materiais do traço
        materiais_json = {}
        if hasattr(self, 'materiais_calculados'):
            for material, qtd, unidade in self.materiais_calculados:
                materiais_json[material] = {
                    "quantidade": qtd,
                    "unidade": unidade
                }
        else:
            materiais_json = {
                "Cimento": {"quantidade": 0, "unidade": "kg"},
                "Brita 0": {"quantidade": 0, "unidade": "kg"},
                "Brita 1": {"quantidade": 0, "unidade": "kg"},
                "Areia Média": {"quantidade": 0, "unidade": "kg"},
                "Pó de Brita": {"quantidade": 0, "unidade": "kg"},
                "Água": {"quantidade": 0, "unidade": "litros"},
                "Aditivo": {"quantidade": 0, "unidade": "kg"}
            }
        
        return {
            'cliente_id': cliente_id,
            'traco_id': traco_id,
            'quantidade': self.input_volume_traco.value(),
            'placa_veiculo': self.input_placa.text().strip(),
            'motorista': self.input_motorista.text().strip(),
            'data_pesagem': data_pesagem,
            'observacoes': self.input_observacoes.toPlainText().strip(),
            'materiais_json': json.dumps(materiais_json, ensure_ascii=False)
        }

class TelaPesagens(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        # Corrigir tabela antes de carregar
        self.corrigir_tabela_pesagens()
        # Adicionar um pequeno delay antes de carregar as pesagens
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.carregar_pesagens)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("⚖️ CONTROLE DE PESAGENS - BETTO MIX")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            color: white;
            background-color: #0D47A1;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 2px solid #1565C0;
        """)
        layout.addWidget(titulo)
        
        # Botões superiores
        btn_layout = QHBoxLayout()
        
        btn_novo = QPushButton("⚖️ Nova Pesagem")
        btn_novo.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        btn_novo.clicked.connect(self.nova_pesagem)
        
        btn_editar = QPushButton("✏️ Editar")
        btn_editar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        btn_editar.clicked.connect(self.editar_pesagem)
        
        btn_excluir = QPushButton("🗑️ Excluir")
        btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        btn_excluir.clicked.connect(self.excluir_pesagem)
        
        btn_concluir = QPushButton("✅ Concluir")
        btn_concluir.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        btn_concluir.clicked.connect(self.concluir_pesagem)
        
        btn_materiais = QPushButton("📦 Materiais")
        btn_materiais.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        btn_materiais.clicked.connect(self.ver_materiais)
        
        # NOVO BOTÃO: Sincronizar com Estoque
        btn_sincronizar = QPushButton("🔄 Sinc. Estoque")
        btn_sincronizar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        btn_sincronizar.clicked.connect(self.verificar_sincronizacao)
        btn_sincronizar.setToolTip("Verificar sincronização com estoque")
        
        btn_layout.addWidget(btn_novo)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_excluir)
        btn_layout.addWidget(btn_concluir)
        btn_layout.addWidget(btn_materiais)
        btn_layout.addWidget(btn_sincronizar)  # ADICIONADO
        
        layout.addLayout(btn_layout)
        
        # Filtros
        filtro_layout = QHBoxLayout()
        
        self.filtro_data_inicio = QDateEdit()
        self.filtro_data_inicio.setDate(QDate.currentDate().addDays(-7))
        self.filtro_data_inicio.setCalendarPopup(True)
        
        self.filtro_data_fim = QDateEdit()
        self.filtro_data_fim.setDate(QDate.currentDate())
        self.filtro_data_fim.setCalendarPopup(True)
        
        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos", "PENDENTE", "CONCLUÍDO", "CANCELADO"])
        
        btn_filtrar = QPushButton("🔍 Filtrar")
        btn_filtrar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
        """)
        btn_filtrar.clicked.connect(self.filtrar_pesagens)
        
        btn_limpar = QPushButton("🔄 Limpar")
        btn_limpar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #0D47A1;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
        """)
        btn_limpar.clicked.connect(self.limpar_filtros)
        
        filtro_layout.addWidget(QLabel("De:"))
        filtro_layout.addWidget(self.filtro_data_inicio)
        filtro_layout.addWidget(QLabel("Até:"))
        filtro_layout.addWidget(self.filtro_data_fim)
        filtro_layout.addWidget(QLabel("Status:"))
        filtro_layout.addWidget(self.filtro_status)
        filtro_layout.addWidget(btn_filtrar)
        filtro_layout.addWidget(btn_limpar)
        filtro_layout.addStretch()
        
        layout.addLayout(filtro_layout)
        
        # Tabela de pesagens - AGORA COM 11 COLUNAS (adicionando Observações)
        self.tabela_pesagens = QTableWidget()
        self.tabela_pesagens.setColumnCount(11)  # Alterado de 10 para 11
        self.tabela_pesagens.setHorizontalHeaderLabels([
            "ID", "Data", "Hora", "Cliente", "Traço", "Placa", "Motorista", 
            "Volume (m³)", "Status", "Materiais", "Observações"  # Alterado "Quantidade (m³)" para "Volume (m³)"
        ])
        
        # Configurar largura das colunas
        header = self.tabela_pesagens.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Data
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Hora
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Cliente
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)           # Traço
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Placa
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Motorista
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Volume
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Materiais
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.Stretch)          # Observações - Stretch para expandir
        
        # Aplicar estilo à tabela
        self.tabela_pesagens.setStyleSheet("""
            QTableWidget {
                border: 2px solid #1976D2;
                border-radius: 5px;
                background-color: white;
                alternate-background-color: #E3F2FD;
                gridline-color: #2196F3;
                selection-background-color: #BBDEFB;
                selection-color: #0D47A1;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #BBDEFB;
            }
            QTableWidget::item:selected {
                background-color: #BBDEFB;
                color: #0D47A1;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #0D47A1;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
                border-right: 1px solid #1565C0;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QHeaderView::section:hover {
                background-color: #1565C0;
            }
        """)
        
        layout.addWidget(self.tabela_pesagens)
        
        # Estatísticas
        self.label_estatisticas = QLabel("Carregando pesagens...")
        self.label_estatisticas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estatisticas.setStyleSheet("font-weight: bold; color: #0D47A1; font-size: 11pt;")
        layout.addWidget(self.label_estatisticas)
        
        # Aplicar estilos aos inputs de filtro
        self.filtro_data_inicio.setStyleSheet("""
            QDateEdit {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QDateEdit:focus {
                border: 2px solid #1976D2;
            }
        """)
        
        self.filtro_data_fim.setStyleSheet("""
            QDateEdit {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QDateEdit:focus {
                border: 2px solid #1976D2;
            }
        """)
        
        self.filtro_status.setStyleSheet("""
            QComboBox {
                border: 1px solid #2196F3;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #1976D2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #0D47A1;
            }
        """)
    
    def corrigir_tabela_pesagens(self):
        """Função para corrigir a tabela pesagens uma vez"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Verificar se a coluna data_registro existe
            cursor.execute("PRAGMA table_info(pesagens)")
            colunas = [col[1] for col in cursor.fetchall()]
            
            if 'data_registro' not in colunas:
                print("Corrigindo tabela pesagens...")
                
                # Criar tabela temporária
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pesagens_temp (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente_id INTEGER,
                        traco_id INTEGER,
                        quantidade REAL,
                        placa_veiculo TEXT,
                        motorista TEXT,
                        data_pesagem TEXT,
                        observacoes TEXT,
                        status TEXT DEFAULT 'PENDENTE',
                        materiais_json TEXT,
                        data_registro TEXT,
                        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                        FOREIGN KEY (traco_id) REFERENCES tracos(id)
                    )
                ''')
                
                # Copiar dados da tabela antiga para a nova
                cursor.execute("SELECT * FROM pesagens")
                pesagens = cursor.fetchall()
                
                for pesagem in pesagens:
                    cursor.execute('''
                        INSERT INTO pesagens_temp 
                        (id, cliente_id, traco_id, quantidade, placa_veiculo, motorista, 
                         data_pesagem, observacoes, status, materiais_json, data_registro)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        pesagem[0], pesagem[1], pesagem[2], pesagem[3], pesagem[4], 
                        pesagem[5], pesagem[6], 
                        pesagem[7] if len(pesagem) > 7 else '',  # observacoes
                        pesagem[8] if len(pesagem) > 8 else 'PENDENTE',  # status
                        pesagem[9] if len(pesagem) > 9 else '{}',  # materiais_json
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # data_registro
                    ))
                
                # Remover tabela antiga e renomear nova
                cursor.execute("DROP TABLE pesagens")
                cursor.execute("ALTER TABLE pesagens_temp RENAME TO pesagens")
                
                conn.commit()
                conn.close()
                print("✅ Tabela pesagens corrigida com sucesso!")
                
        except Exception as e:
            print(f"⚠️ Erro ao corrigir tabela pesagens: {e}")
    
    def criar_tabelas_se_necessario(self, conn):
        """Cria ou verifica as tabelas necessárias"""
        cursor = conn.cursor()
        
        # Tabela de pesagens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                traco_id INTEGER,
                quantidade REAL,
                placa_veiculo TEXT,
                motorista TEXT,
                data_pesagem TEXT,
                observacoes TEXT,
                status TEXT DEFAULT 'PENDENTE',
                materiais_json TEXT,
                data_registro TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (traco_id) REFERENCES tracos(id)
            )
        ''')
        
        # Verificar se as colunas existem
        cursor.execute("PRAGMA table_info(pesagens)")
        colunas_pesagens = [col[1] for col in cursor.fetchall()]
        
        # Adicionar colunas faltantes
        if 'observacoes' not in colunas_pesagens:
            try:
                cursor.execute("ALTER TABLE pesagens ADD COLUMN observacoes TEXT")
                print("✅ Coluna 'observacoes' adicionada à tabela pesagens")
            except Exception as e:
                print(f"⚠️ Erro ao adicionar coluna 'observacoes': {e}")
        
        if 'materiais_json' not in colunas_pesagens:
            try:
                cursor.execute("ALTER TABLE pesagens ADD COLUMN materiais_json TEXT")
                print("✅ Coluna 'materiais_json' adicionada à tabela pesagens")
            except Exception as e:
                print(f"⚠️ Erro ao adicionar coluna 'materiais_json': {e}")
        
        if 'data_registro' not in colunas_pesagens:
            try:
                # Adicionar coluna sem valor padrão primeiro
                cursor.execute("ALTER TABLE pesagens ADD COLUMN data_registro TEXT")
                print("✅ Coluna 'data_registro' adicionada à tabela pesagens")
                
                # Atualizar registros existentes com a data atual
                cursor.execute("UPDATE pesagens SET data_registro = datetime('now') WHERE data_registro IS NULL")
                print("✅ Registros existentes atualizados com data_registro")
            except Exception as e:
                print(f"⚠️ Erro ao adicionar coluna 'data_registro': {e}")
        
        conn.commit()
    
    def carregar_pesagens(self):
        """Carrega as pesagens do banco de dados"""
        try:
            print("Carregando pesagens...")
            
            conn = sqlite3.connect('usina_concreto.db')
            
            # Garantir que a tabela existe
            self.criar_tabelas_se_necessario(conn)
            
            cursor = conn.cursor()
            
            # Primeiro, verificar se a coluna materiais_json existe
            cursor.execute("PRAGMA table_info(pesagens)")
            colunas = [col[1] for col in cursor.fetchall()]
            
            # Construir query dinamicamente - AGORA INCLUINDO OBSERVAÇÕES
            colunas_selecionar = [
                "p.id",
                "p.data_pesagem",
                "c.nome AS cliente_nome",
                "t.codigo || ' - ' || t.nome AS traco_nome",
                "p.placa_veiculo",
                "p.motorista",
                "p.quantidade",
                "p.status",
                "p.observacoes"  # ADICIONADO: campo observações
            ]
            
            # Adicionar materiais_json se existir
            if 'materiais_json' in colunas:
                colunas_selecionar.append("p.materiais_json")
            else:
                colunas_selecionar.append("'{}' as materiais_json")
            
            query = f'''
                SELECT 
                    {', '.join(colunas_selecionar)}
                FROM pesagens p
                LEFT JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN tracos t ON p.traco_id = t.id
                ORDER BY p.data_pesagem DESC, p.id DESC
            '''
            
            cursor.execute(query)
            pesagens = cursor.fetchall()
            
            conn.close()
            
            # Atualizar tabela
            self.tabela_pesagens.setRowCount(len(pesagens))
            
            total_volume = 0
            pendentes = 0
            concluidas = 0
            
            for i, pesagem in enumerate(pesagens):
                # Separar data e hora
                data_pesagem = pesagem[1]
                if data_pesagem:
                    try:
                        if ' ' in data_pesagem:
                            data_str, hora_str = data_pesagem.split(' ')
                        else:
                            data_str = data_pesagem
                            hora_str = "00:00"
                    except:
                        data_str = data_pesagem
                        hora_str = "00:00"
                else:
                    data_str = ""
                    hora_str = ""
                
                # Preencher os dados na tabela
                self.tabela_pesagens.setItem(i, 0, QTableWidgetItem(str(pesagem[0])))  # ID
                self.tabela_pesagens.setItem(i, 1, QTableWidgetItem(data_str))  # Data
                self.tabela_pesagens.setItem(i, 2, QTableWidgetItem(hora_str))  # Hora
                self.tabela_pesagens.setItem(i, 3, QTableWidgetItem(str(pesagem[2] if pesagem[2] else "")))  # Cliente
                self.tabela_pesagens.setItem(i, 4, QTableWidgetItem(str(pesagem[3] if pesagem[3] else "")))  # Traço
                self.tabela_pesagens.setItem(i, 5, QTableWidgetItem(str(pesagem[4] if pesagem[4] else "")))  # Placa
                self.tabela_pesagens.setItem(i, 6, QTableWidgetItem(str(pesagem[5] if pesagem[5] else "")))  # Motorista
                self.tabela_pesagens.setItem(i, 7, QTableWidgetItem(f"{pesagem[6]:.2f}" if pesagem[6] else "0.00"))  # Volume
                
                # Status com cores
                status = str(pesagem[7] if pesagem[7] else "PENDENTE")
                status_item = QTableWidgetItem(status)
                
                if status == 'PENDENTE':
                    status_item.setForeground(QColor(255, 165, 0))  # Laranja
                    pendentes += 1
                elif status == 'CONCLUÍDO' or status == 'CONCLUIDO':
                    status_item.setForeground(QColor(0, 128, 0))   # Verde
                    concluidas += 1
                elif status == 'CANCELADO':
                    status_item.setForeground(QColor(255, 0, 0))   # Vermelho
                
                self.tabela_pesagens.setItem(i, 8, status_item)  # Status
                
                # Coluna de materiais (ícone/resumo)
                materiais_json = pesagem[9] if len(pesagem) > 9 and pesagem[9] else "{}"
                materiais_item = QTableWidgetItem("📦 Ver")
                materiais_item.setData(Qt.ItemDataRole.UserRole, materiais_json)  # Armazenar JSON
                materiais_item.setForeground(QColor(33, 150, 243))  # Azul
                self.tabela_pesagens.setItem(i, 9, materiais_item)  # Materiais
                
                # NOVO: Coluna de observações (coluna 10)
                observacoes = str(pesagem[8] if len(pesagem) > 8 and pesagem[8] else "")
                # Limitar o texto para não sobrecarregar a visualização
                if len(observacoes) > 100:
                    observacoes_display = observacoes[:97] + "..."
                    observacoes_item = QTableWidgetItem(observacoes_display)
                    observacoes_item.setToolTip(observacoes)  # Mostrar completo no tooltip
                else:
                    observacoes_item = QTableWidgetItem(observacoes)
                
                # Destacar se houver observações
                if observacoes.strip():
                    observacoes_item.setForeground(QColor(106, 27, 154))  # Roxo para destacar
                    observacoes_item.setFont(QFont("Arial", 9, QFont.Weight.Normal))
                else:
                    observacoes_item.setText("-")
                    observacoes_item.setForeground(QColor(150, 150, 150))  # Cinza
                
                self.tabela_pesagens.setItem(i, 10, observacoes_item)  # Observações
                
                if pesagem[6]:  # quantidade
                    total_volume += pesagem[6]
            
            self.label_estatisticas.setText(
                f"📊 Total: {len(pesagens)} pesagens | "
                f"📦 Volume: {total_volume:.2f} m³ | "
                f"🟠 Pendentes: {pendentes} | "
                f"🟢 Concluídas: {concluidas}"
            )
            print(f"✓ Pesagens carregadas: {len(pesagens)} registros")
            
        except Exception as e:
            error_msg = f"Erro ao carregar pesagens: {str(e)}"
            print(f"✗ {error_msg}")
            self.label_estatisticas.setText("Erro ao carregar pesagens")
    
    def filtrar_pesagens(self):
        """Filtra as pesagens por data e status"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Verificar colunas disponíveis
            cursor.execute("PRAGMA table_info(pesagens)")
            colunas = [col[1] for col in cursor.fetchall()]
            
            # Construir query com filtros - INCLUINDO OBSERVAÇÕES
            colunas_selecionar = [
                "p.id",
                "p.data_pesagem",
                "c.nome AS cliente_nome",
                "t.codigo || ' - ' || t.nome AS traco_nome",
                "p.placa_veiculo",
                "p.motorista",
                "p.quantidade",
                "p.status",
                "p.observacoes"  # ADICIONADO
            ]
            
            if 'materiais_json' in colunas:
                colunas_selecionar.append("p.materiais_json")
            else:
                colunas_selecionar.append("'{}' as materiais_json")
            
            query = f'''
                SELECT 
                    {', '.join(colunas_selecionar)}
                FROM pesagens p
                LEFT JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN tracos t ON p.traco_id = t.id
                WHERE 1=1
            '''
            
            params = []
            
            # Filtrar por data
            if self.filtro_data_inicio.date() and self.filtro_data_fim.date():
                query += " AND date(substr(p.data_pesagem, 1, 10)) BETWEEN ? AND ?"
                params.extend([
                    self.filtro_data_inicio.date().toString("yyyy-MM-dd"),
                    self.filtro_data_fim.date().toString("yyyy-MM-dd")
                ])
            
            # Filtrar por status
            status = self.filtro_status.currentText()
            if status != "Todos":
                query += " AND p.status = ?"
                params.append(status)
            
            query += " ORDER BY p.data_pesagem DESC, p.id DESC"
            
            cursor.execute(query, params)
            pesagens = cursor.fetchall()
            conn.close()
            
            # Atualizar tabela
            self.tabela_pesagens.setRowCount(len(pesagens))
            
            total_volume = 0
            
            for i, pesagem in enumerate(pesagens):
                # Separar data e hora
                data_pesagem = pesagem[1]
                if data_pesagem:
                    try:
                        if ' ' in data_pesagem:
                            data_str, hora_str = data_pesagem.split(' ')
                        else:
                            data_str = data_pesagem
                            hora_str = "00:00"
                    except:
                        data_str = data_pesagem
                        hora_str = "00:00"
                else:
                    data_str = ""
                    hora_str = ""
                
                # Preencher os dados na tabela
                self.tabela_pesagens.setItem(i, 0, QTableWidgetItem(str(pesagem[0])))  # ID
                self.tabela_pesagens.setItem(i, 1, QTableWidgetItem(data_str))  # Data
                self.tabela_pesagens.setItem(i, 2, QTableWidgetItem(hora_str))  # Hora
                self.tabela_pesagens.setItem(i, 3, QTableWidgetItem(str(pesagem[2] if pesagem[2] else "")))  # Cliente
                self.tabela_pesagens.setItem(i, 4, QTableWidgetItem(str(pesagem[3] if pesagem[3] else "")))  # Traço
                self.tabela_pesagens.setItem(i, 5, QTableWidgetItem(str(pesagem[4] if pesagem[4] else "")))  # Placa
                self.tabela_pesagens.setItem(i, 6, QTableWidgetItem(str(pesagem[5] if pesagem[5] else "")))  # Motorista
                self.tabela_pesagens.setItem(i, 7, QTableWidgetItem(f"{pesagem[6]:.2f}" if pesagem[6] else "0.00"))  # Volume
                
                # Status com cores
                status = str(pesagem[7] if pesagem[7] else "PENDENTE")
                status_item = QTableWidgetItem(status)
                
                if status == 'PENDENTE':
                    status_item.setForeground(QColor(255, 165, 0))
                elif status == 'CONCLUÍDO' or status == 'CONCLUIDO':
                    status_item.setForeground(QColor(0, 128, 0))
                elif status == 'CANCELADO':
                    status_item.setForeground(QColor(255, 0, 0))
                
                self.tabela_pesagens.setItem(i, 8, status_item)  # Status
                
                # Coluna de materiais
                materiais_json = pesagem[9] if len(pesagem) > 9 and pesagem[9] else "{}"
                materiais_item = QTableWidgetItem("📦 Ver")
                materiais_item.setData(Qt.ItemDataRole.UserRole, materiais_json)
                materiais_item.setForeground(QColor(33, 150, 243))
                self.tabela_pesagens.setItem(i, 9, materiais_item)  # Materiais
                
                # Coluna de observações (coluna 10)
                observacoes = str(pesagem[8] if len(pesagem) > 8 and pesagem[8] else "")
                if len(observacoes) > 100:
                    observacoes_display = observacoes[:97] + "..."
                    observacoes_item = QTableWidgetItem(observacoes_display)
                    observacoes_item.setToolTip(observacoes)
                else:
                    observacoes_item = QTableWidgetItem(observacoes)
                
                if observacoes.strip():
                    observacoes_item.setForeground(QColor(106, 27, 154))
                    observacoes_item.setFont(QFont("Arial", 9, QFont.Weight.Normal))
                else:
                    observacoes_item.setText("-")
                    observacoes_item.setForeground(QColor(150, 150, 150))
                
                self.tabela_pesagens.setItem(i, 10, observacoes_item)  # Observações
                
                if pesagem[6]:
                    total_volume += pesagem[6]
            
            self.label_estatisticas.setText(f"Total de pesagens: {len(pesagens)} | Volume total: {total_volume:.2f} m³")
            
        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Erro ao filtrar pesagens: {e}")
            self.carregar_pesagens()
    
    def limpar_filtros(self):
        """Limpa os filtros"""
        self.filtro_data_inicio.setDate(QDate.currentDate().addDays(-7))
        self.filtro_data_fim.setDate(QDate.currentDate())
        self.filtro_status.setCurrentIndex(0)
        self.carregar_pesagens()
    
    def nova_pesagem(self):
        """Abre diálogo para nova pesagem"""
        dialog = DialogPesagem()
        if dialog.exec():
            dados = dialog.get_dados()
            
            try:
                conn = sqlite3.connect('usina_concreto.db')
                cursor = conn.cursor()
                
                # Verificar se as colunas existem
                cursor.execute("PRAGMA table_info(pesagens)")
                colunas = [col[1] for col in cursor.fetchall()]
                
                # Obter a data e hora atual para data_registro
                data_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Construir a query dinamicamente baseado nas colunas existentes
                if 'materiais_json' in colunas and 'data_registro' in colunas:
                    cursor.execute('''
                        INSERT INTO pesagens 
                        (cliente_id, traco_id, quantidade, placa_veiculo, motorista, 
                         data_pesagem, observacoes, materiais_json, data_registro, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDENTE')
                    ''', (
                        dados['cliente_id'], dados['traco_id'], dados['quantidade'],
                        dados['placa_veiculo'], dados['motorista'], dados['data_pesagem'],
                        dados['observacoes'], dados['materiais_json'], data_registro
                    ))
                elif 'materiais_json' in colunas:
                    cursor.execute('''
                        INSERT INTO pesagens 
                        (cliente_id, traco_id, quantidade, placa_veiculo, motorista, 
                         data_pesagem, observacoes, materiais_json, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDENTE')
                    ''', (
                        dados['cliente_id'], dados['traco_id'], dados['quantidade'],
                        dados['placa_veiculo'], dados['motorista'], dados['data_pesagem'],
                        dados['observacoes'], dados['materiais_json']
                    ))
                else:
                    cursor.execute('''
                        INSERT INTO pesagens 
                        (cliente_id, traco_id, quantidade, placa_veiculo, motorista, 
                         data_pesagem, observacoes, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDENTE')
                    ''', (
                        dados['cliente_id'], dados['traco_id'], dados['quantidade'],
                        dados['placa_veiculo'], dados['motorista'], dados['data_pesagem'],
                        dados['observacoes']
                    ))
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Sucesso", "✅ Pesagem cadastrada com sucesso!")
                self.carregar_pesagens()
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"❌ Erro ao salvar pesagem: {e}")
                print(f"Erro detalhado: {e}")
    
    def editar_pesagem(self):
        """Edita a pesagem selecionada"""
        linha = self.tabela_pesagens.currentRow()
        if linha >= 0:
            id_pesagem = self.tabela_pesagens.item(linha, 0).text()
            
            try:
                # Buscar dados atuais da pesagem
                conn = sqlite3.connect('usina_concreto.db')
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        p.cliente_id, p.traco_id, p.quantidade, p.placa_veiculo,
                        p.motorista, p.data_pesagem, p.observacoes, p.materiais_json,
                        c.nome as cliente_nome, t.codigo || ' - ' || t.nome as traco_nome
                    FROM pesagens p
                    LEFT JOIN clientes c ON p.cliente_id = c.id
                    LEFT JOIN tracos t ON p.traco_id = t.id
                    WHERE p.id = ?
                ''', (id_pesagem,))
                pesagem = cursor.fetchone()
                
                if not pesagem:
                    QMessageBox.warning(self, "Aviso", "Pesagem não encontrada!")
                    conn.close()
                    return
                
                conn.close()
                
                # Criar diálogo de edição
                dialog = DialogEditarPesagem(self, id_pesagem, pesagem)
                if dialog.exec():
                    # Atualizar dados no banco
                    dados_atualizados = dialog.get_dados()
                    
                    conn = sqlite3.connect('usina_concreto.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE pesagens SET
                            cliente_id = ?,
                            traco_id = ?,
                            quantidade = ?,
                            placa_veiculo = ?,
                            motorista = ?,
                            data_pesagem = ?,
                            observacoes = ?,
                            materiais_json = ?
                        WHERE id = ?
                    ''', (
                        dados_atualizados['cliente_id'],
                        dados_atualizados['traco_id'],
                        dados_atualizados['quantidade'],
                        dados_atualizados['placa_veiculo'],
                        dados_atualizados['motorista'],
                        dados_atualizados['data_pesagem'],
                        dados_atualizados['observacoes'],
                        dados_atualizados['materiais_json'],
                        id_pesagem
                    ))
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Sucesso", "✅ Pesagem atualizada com sucesso!")
                    self.carregar_pesagens()
                    
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao editar pesagem: {str(e)}")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma pesagem para editar!")
    
    def excluir_pesagem(self):
        """Exclui a pesagem selecionada"""
        linha = self.tabela_pesagens.currentRow()
        if linha >= 0:
            id_pesagem = self.tabela_pesagens.item(linha, 0).text()
            cliente = self.tabela_pesagens.item(linha, 3).text()
            
            resposta = QMessageBox.question(
                self, "Confirmar Exclusão",
                f"Tem certeza que deseja excluir a pesagem #{id_pesagem} do cliente {cliente}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if resposta == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect('usina_concreto.db')
                    cursor = conn.cursor()
                    
                    cursor.execute('DELETE FROM pesagens WHERE id = ?', (id_pesagem,))
                    
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Sucesso", "✅ Pesagem excluída com sucesso!")
                    self.carregar_pesagens()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"❌ Erro ao excluir pesagem: {e}")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma pesagem para excluir!")
    
    def concluir_pesagem(self):
        """Conclui a pesagem selecionada e dá saída no estoque"""
        linha = self.tabela_pesagens.currentRow()
        if linha >= 0:
            id_pesagem = self.tabela_pesagens.item(linha, 0).text()
            traco_nome = self.tabela_pesagens.item(linha, 4).text()
            status_atual = self.tabela_pesagens.item(linha, 8).text()
            
            # Verificar se já está concluída
            if status_atual in ['CONCLUÍDO', 'CONCLUIDO']:
                QMessageBox.information(self, "Informação", f"A pesagem #{id_pesagem} já está concluída!")
                return
            
            # Obter JSON de materiais
            materiais_item = self.tabela_pesagens.item(linha, 9)
            materiais_json_str = materiais_item.data(Qt.ItemDataRole.UserRole) if materiais_item else "{}"
            
            try:
                materiais_json = json.loads(materiais_json_str)
                
                # Extrair materiais utilizados
                materiais_utilizados = {}
                materiais_lista = [
                    "Cimento", "Brita 0", "Brita 1", "Areia Média", 
                    "Pó de Brita", "Água", "Aditivo"
                ]
                
                for material in materiais_lista:
                    if material in materiais_json:
                        dados = materiais_json[material]
                        if isinstance(dados, dict) and 'quantidade' in dados:
                            materiais_utilizados[material] = dados['quantidade']
                        else:
                            materiais_utilizados[material] = 0
                    else:
                        materiais_utilizados[material] = 0
                
                # Se todos os materiais forem zero, tentar obter do traço
                if all(qtd == 0 for qtd in materiais_utilizados.values()):
                    # Obter traco_id para obter materiais
                    try:
                        conn = sqlite3.connect('usina_concreto.db')
                        cursor = conn.cursor()
                        cursor.execute("SELECT traco_id FROM pesagens WHERE id = ?", (id_pesagem,))
                        result = cursor.fetchone()
                        conn.close()
                        
                        if result:
                            traco_id = result[0]
                            # Obter materiais do traço
                            sucesso, materiais_calculados, mensagem = SincronizadorEstoque.verificar_estoque_disponivel(traco_id)
                            
                            if sucesso:
                                materiais_utilizados = materiais_calculados
                            else:
                                QMessageBox.warning(self, "Estoque Insuficiente", 
                                                  f"Não é possível concluir a pesagem:\n\n{mensagem}")
                                return
                        else:
                            QMessageBox.warning(self, "Erro", "Não foi possível obter os dados do traço.")
                            return
                    except Exception as e:
                        QMessageBox.warning(self, "Erro", f"Erro ao obter materiais: {str(e)}")
                        return
                
                # Criar mensagem de confirmação
                materiais_display = []
                for material, qtd in materiais_utilizados.items():
                    if qtd > 0:
                        # Determinar unidade
                        unidade = "kg"
                        if material == "Água":
                            unidade = "litros"
                        materiais_display.append(f"- {material}: {qtd:.2f} {unidade}")
                
                if not materiais_display:
                    QMessageBox.warning(self, "Aviso", "Não foram encontrados materiais para esta pesagem.")
                    return
                
                resposta = QMessageBox.question(
                    self, "Confirmar Conclusão",
                    f"Confirmar conclusão da pesagem #{id_pesagem}?\n\n"
                    f"Traço: {traco_nome}\n\n"
                    f"Isso dará saída nos seguintes materiais do estoque:\n" + 
                    "\n".join(materiais_display),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if resposta == QMessageBox.StandardButton.Yes:
                    # Dar saída no estoque
                    sucesso, mensagem, detalhes = SincronizadorEstoque.dar_saida_estoque(
                        materiais_utilizados, int(id_pesagem), traco_nome
                    )
                    
                    if sucesso:
                        # Atualizar status da pesagem
                        try:
                            conn = sqlite3.connect('usina_concreto.db')
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE pesagens SET status = 'CONCLUÍDO' WHERE id = ?",
                                (id_pesagem,)
                            )
                            conn.commit()
                            conn.close()
                            
                            # Atualizar tabela
                            status_item = QTableWidgetItem("CONCLUÍDO")
                            status_item.setForeground(QColor(0, 128, 0))
                            self.tabela_pesagens.setItem(linha, 8, status_item)
                            
                            # Mostrar resumo
                            mensagem_sucesso = f"✅ Pesagem #{id_pesagem} concluída com sucesso!\n\n"
                            if detalhes:
                                mensagem_sucesso += "📊 Estoque atualizado:\n"
                                for detalhe in detalhes:
                                    mensagem_sucesso += f"  • {detalhe}\n"
                            
                            QMessageBox.information(self, "Sucesso", mensagem_sucesso)
                            self.carregar_pesagens()
                            
                        except Exception as e:
                            QMessageBox.critical(self, "Erro", f"Erro ao atualizar status da pesagem: {str(e)}")
                    else:
                        QMessageBox.critical(self, "Erro", mensagem)
                        
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao processar materiais: {str(e)}")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma pesagem para concluir!")
    
    def ver_materiais(self):
        """Mostra os materiais calculados da pesagem selecionada"""
        linha = self.tabela_pesagens.currentRow()
        if linha >= 0:
            id_pesagem = self.tabela_pesagens.item(linha, 0).text()
            traco_nome = self.tabela_pesagens.item(linha, 4).text()
            
            # Obter JSON de materiais
            materiais_item = self.tabela_pesagens.item(linha, 9)
            materiais_json_str = materiais_item.data(Qt.ItemDataRole.UserRole) if materiais_item else "{}"
            
            try:
                materiais = json.loads(materiais_json_str)
                
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Materiais da Pesagem #{id_pesagem}")
                dialog.setMinimumWidth(500)
                
                layout = QVBoxLayout(dialog)
                
                # Título
                titulo = QLabel(f"📦 Composição do Traço")
                titulo.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(titulo)
                
                # Informações
                info_label = QLabel(f"Traço: {traco_nome}")
                layout.addWidget(info_label)
                
                # Tabela de materiais - SEMPRE MOSTRAR TODOS OS 7 MATERIAIS
                tabela = QTableWidget()
                tabela.setColumnCount(3)
                tabela.setHorizontalHeaderLabels(["Material", "Quantidade", "Unidade"])
                
                # Lista de todos os materiais em ordem fixa
                materiais_lista = [
                    ("Cimento", "kg"),
                    ("Brita 0", "kg"),
                    ("Brita 1", "kg"),
                    ("Areia Média", "kg"),
                    ("Pó de Brita", "kg"),
                    ("Água", "litros"),
                    ("Aditivo", "kg")
                ]
                
                tabela.setRowCount(len(materiais_lista))
                total_kg = 0
                
                for row, (material_nome, unidade_padrao) in enumerate(materiais_lista):
                    # Obter dados do JSON ou usar 0 se não existir
                    dados = materiais.get(material_nome, {})
                    qtd = dados.get('quantidade', 0)
                    unidade = dados.get('unidade', unidade_padrao)
                    
                    tabela.setItem(row, 0, QTableWidgetItem(material_nome))
                    tabela.setItem(row, 1, QTableWidgetItem(f"{qtd:.2f}"))
                    tabela.setItem(row, 2, QTableWidgetItem(unidade))
                    
                    if unidade == "kg":
                        total_kg += qtd
                
                tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
                tabela.setMinimumHeight(300)
                
                # Aplicar estilo azul à tabela
                tabela.setStyleSheet("""
                    QTableWidget {
                        border: 2px solid #1976D2;
                        border-radius: 5px;
                        background-color: white;
                        alternate-background-color: #E3F2FD;
                        gridline-color: #2196F3;
                    }
                    QTableWidget::item {
                        padding: 8px;
                        border-bottom: 1px solid #BBDEFB;
                    }
                    QTableWidget::item:selected {
                        background-color: #BBDEFB;
                        color: #0D47A1;
                        font-weight: bold;
                    }
                    QHeaderView::section {
                        background-color: #0D47A1;
                        color: white;
                        padding: 10px;
                        border: none;
                        font-weight: bold;
                        font-size: 10pt;
                        border-right: 1px solid #1565C0;
                    }
                    QHeaderView::section:last {
                        border-right: none;
                    }
                """)
                
                layout.addWidget(tabela)
                
                # Total
                total_label = QLabel(f"📊 Total de materiais: {total_kg:.2f} kg")
                total_label.setStyleSheet("font-weight: bold; color: #0D47A1;")
                layout.addWidget(total_label)
                
                # Botão fechar
                btn_fechar = QPushButton("Fechar")
                btn_fechar.setStyleSheet("""
                    QPushButton {
                        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                          stop:0 #1976D2, stop:1 #1565C0);
                        color: white;
                        border: 1px solid #0D47A1;
                        border-radius: 5px;
                        padding: 8px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                          stop:0 #1565C0, stop:1 #0D47A1);
                    }
                """)
                btn_fechar.clicked.connect(dialog.accept)
                layout.addWidget(btn_fechar)
                
                dialog.exec()
                
            except Exception as e:
                QMessageBox.warning(self, "Aviso", f"Erro ao carregar materiais: {e}")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma pesagem para ver os materiais!")
    
    def imprimir_romaneio(self):
        """Simula impressão de romaneio"""
        linha = self.tabela_pesagens.currentRow()
        if linha >= 0:
            id_pesagem = self.tabela_pesagens.item(linha, 0).text()
            cliente = self.tabela_pesagens.item(linha, 3).text()
            QMessageBox.information(self, "Impressão", f"📄 Romaneio #{id_pesagem} para {cliente} enviado para impressão!")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma pesagem para imprimir!")
    
    def verificar_sincronizacao(self):
        """Verifica a sincronização com o estoque"""
        try:
            # Verificar pesagens concluídas sem saída no estoque
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Verificar se a tabela historico_estoque existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historico_estoque'")
            if not cursor.fetchone():
                QMessageBox.information(self, "Sincronização", 
                                      "Tabela de histórico não encontrada.\nO sistema criará automaticamente quando necessário.")
                conn.close()
                return
            
            # Contar pesagens concluídas sem histórico
            cursor.execute('''
                SELECT COUNT(*) 
                FROM pesagens 
                WHERE status = 'CONCLUÍDO' 
                AND id NOT IN (
                    SELECT DISTINCT CAST(SUBSTR(destino, INSTR(destino, '#') + 1) AS INTEGER)
                    FROM historico_estoque 
                    WHERE destino LIKE '%Pesagem #%'
                )
            ''')
            
            pendentes = cursor.fetchone()[0]
            conn.close()
            
            if pendentes > 0:
                resposta = QMessageBox.question(
                    self, "Sincronização Necessária",
                    f"Foram encontradas {pendentes} pesagem(ns) concluída(s)\n"
                    f"sem saída registrada no estoque.\n\n"
                    f"Deseja sincronizar agora?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if resposta == QMessageBox.StandardButton.Yes:
                    self.sincronizar_pesagens_pendentes()
            else:
                QMessageBox.information(self, "Sincronização", 
                                      "✅ Todas as pesagens estão sincronizadas com o estoque!")
                
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao verificar sincronização: {str(e)}")
    
    def sincronizar_pesagens_pendentes(self):
        """Sincroniza pesagens concluídas sem histórico"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            # Buscar pesagens concluídas sem histórico
            cursor.execute('''
                SELECT p.id, p.traco_id, p.quantidade, t.codigo || ' - ' || t.nome as traco_nome
                FROM pesagens p
                LEFT JOIN tracos t ON p.traco_id = t.id
                WHERE p.status = 'CONCLUÍDO' 
                AND p.id NOT IN (
                    SELECT DISTINCT CAST(SUBSTR(destino, INSTR(destino, '#') + 1) AS INTEGER)
                    FROM historico_estoque 
                    WHERE destino LIKE '%Pesagem #%'
                )
            ''')
            
            pesagens_pendentes = cursor.fetchall()
            conn.close()
            
            if not pesagens_pendentes:
                QMessageBox.information(self, "Sincronização", "Nenhuma pesagem pendente para sincronizar.")
                return
            
            sincronizadas = 0
            erros = 0
            
            for id_pesagem, traco_id, quantidade, traco_nome in pesagens_pendentes:
                try:
                    # Obter materiais do traço
                    sucesso, materiais, mensagem = SincronizadorEstoque.verificar_estoque_disponivel(traco_id)
                    
                    if sucesso:
                        # Dar saída no estoque
                        sucesso_saida, msg_saida, detalhes = SincronizadorEstoque.dar_saida_estoque(
                            materiais, id_pesagem, traco_nome
                        )
                        
                        if sucesso_saida:
                            sincronizadas += 1
                        else:
                            erros += 1
                            print(f"Erro na pesagem #{id_pesagem}: {msg_saida}")
                    else:
                        erros += 1
                        print(f"Estoque insuficiente para pesagem #{id_pesagem}")
                        
                except Exception as e:
                    erros += 1
                    print(f"Erro na pesagem #{id_pesagem}: {str(e)}")
            
            # Atualizar estatísticas
            if sincronizadas > 0:
                self.carregar_pesagens()
            
            QMessageBox.information(
                self, "Sincronização Concluída",
                f"✅ {sincronizadas} pesagem(ns) sincronizada(s)\n"
                f"⚠️ {erros} erro(s) encontrado(s)"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na sincronização: {str(e)}")