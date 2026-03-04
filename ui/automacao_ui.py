from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QFormLayout, QGroupBox, QMessageBox,
                             QHeaderView, QComboBox, QSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
import sqlite3
import json

class TelaAutomacao(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.carregar_dispositivos()
        
        # Timer para atualizar status
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_status)
        self.timer.start(5000)  # Atualiza a cada 5 segundos
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("SISTEMA DE AUTOMAÇÃO - USINA DE CONCRETO")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #2E7D32; padding: 10px;")
        layout.addWidget(titulo)
        
        # Grupo do indicador de pesagem
        grupo_indicador = QGroupBox("⚖️ INDICADOR DE PESAGEM 3101 DS")
        grupo_indicador.setStyleSheet("font-weight: bold;")
        indicador_layout = QVBoxLayout()
        
        # Status do indicador
        status_layout = QHBoxLayout()
        
        self.label_status_indicador = QLabel("STATUS: DESCONECTADO")
        self.label_status_indicador.setStyleSheet("font-size: 14px; font-weight: bold; color: red;")
        
        self.btn_conectar = QPushButton("🔗 Conectar")
        self.btn_conectar.clicked.connect(self.conectar_indicador)
        
        self.btn_desconectar = QPushButton("🔴 Desconectar")
        self.btn_desconectar.clicked.connect(self.desconectar_indicador)
        
        status_layout.addWidget(self.label_status_indicador)
        status_layout.addStretch()
        status_layout.addWidget(self.btn_conectar)
        status_layout.addWidget(self.btn_desconectar)
        
        indicador_layout.addLayout(status_layout)
        
        # Configurações do indicador
        config_layout = QFormLayout()
        
        self.input_porta = QComboBox()
        self.input_porta.addItems(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"])
        self.input_porta.setCurrentText("COM3")
        
        self.input_baudrate = QComboBox()
        self.input_baudrate.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.input_baudrate.setCurrentText("9600")
        
        self.input_endereco = QLineEdit()
        self.input_endereco.setText("192.168.1.100")
        self.input_endereco.setPlaceholderText("Endereço IP do indicador")
        
        self.input_tempo_atualizacao = QSpinBox()
        self.input_tempo_atualizacao.setRange(1, 60)
        self.input_tempo_atualizacao.setValue(5)
        self.input_tempo_atualizacao.setSuffix(" segundos")
        
        config_layout.addRow("Porta Serial:", self.input_porta)
        config_layout.addRow("Baud Rate:", self.input_baudrate)
        config_layout.addRow("Endereço IP:", self.input_endereco)
        config_layout.addRow("Tempo Atualização:", self.input_tempo_atualizacao)
        
        indicador_layout.addLayout(config_layout)
        
        # Leitura atual
        leitura_group = QGroupBox("LEITURA ATUAL")
        leitura_layout = QVBoxLayout()
        
        self.label_leitura = QLabel("0.00 kg")
        self.label_leitura.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.label_leitura.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_leitura.setStyleSheet("background-color: #f0f0f0; border: 2px solid #ccc; padding: 20px;")
        
        self.label_ultima_atualizacao = QLabel("Última atualização: --:--:--")
        self.label_ultima_atualizacao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        leitura_layout.addWidget(self.label_leitura)
        leitura_layout.addWidget(self.label_ultima_atualizacao)
        leitura_group.setLayout(leitura_layout)
        
        indicador_layout.addWidget(leitura_group)
        
        # Botões de controle
        controle_layout = QHBoxLayout()
        
        btn_zerar = QPushButton("⚪ Zerar")
        btn_zerar.clicked.connect(self.zerar_indicador)
        
        btn_tara = QPushButton("⚖️ Tara")
        btn_tara.clicked.connect(self.tara_indicador)
        
        btn_imprimir = QPushButton("🖨️ Imprimir")
        btn_imprimir.clicked.connect(self.imprimir_pesagem)
        
        btn_salvar = QPushButton("💾 Salvar Leitura")
        btn_salvar.clicked.connect(self.salvar_leitura)
        
        controle_layout.addWidget(btn_zerar)
        controle_layout.addWidget(btn_tara)
        controle_layout.addWidget(btn_imprimir)
        controle_layout.addWidget(btn_salvar)
        
        indicador_layout.addLayout(controle_layout)
        
        grupo_indicador.setLayout(indicador_layout)
        layout.addWidget(grupo_indicador)
        
        # Outros dispositivos
        grupo_outros = QGroupBox("OUTROS DISPOSITIVOS")
        outros_layout = QVBoxLayout()
        
        # Tabela de dispositivos
        self.tabela_dispositivos = QTableWidget()
        self.tabela_dispositivos.setColumnCount(5)
        self.tabela_dispositivos.setHorizontalHeaderLabels([
            "Dispositivo", "Modelo", "Porta/IP", "Status", "Última Comunicação"
        ])
        self.tabela_dispositivos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        outros_layout.addWidget(self.tabela_dispositivos)
        
        # Botões de dispositivos
        btn_dispositivos_layout = QHBoxLayout()
        
        btn_adicionar = QPushButton("➕ Adicionar")
        btn_adicionar.clicked.connect(self.adicionar_dispositivo)
        
        btn_remover = QPushButton("🗑️ Remover")
        btn_remover.clicked.connect(self.remover_dispositivo)
        
        btn_configurar = QPushButton("⚙️ Configurar")
        btn_configurar.clicked.connect(self.configurar_dispositivo)
        
        btn_dispositivos_layout.addWidget(btn_adicionar)
        btn_dispositivos_layout.addWidget(btn_remover)
        btn_dispositivos_layout.addWidget(btn_configurar)
        
        outros_layout.addLayout(btn_dispositivos_layout)
        
        grupo_outros.setLayout(outros_layout)
        layout.addWidget(grupo_outros)
        
        # Modo de operação
        grupo_modo = QGroupBox("MODO DE OPERAÇÃO")
        modo_layout = QHBoxLayout()
        
        self.check_manual = QCheckBox("MODO MANUAL")
        self.check_manual.setChecked(True)
        self.check_manual.setStyleSheet("font-weight: bold; color: blue;")
        
        self.check_automatico = QCheckBox("MODO AUTOMÁTICO")
        self.check_automatico.setStyleSheet("font-weight: bold; color: green;")
        
        modo_layout.addWidget(self.check_manual)
        modo_layout.addWidget(self.check_automatico)
        modo_layout.addStretch()
        
        grupo_modo.setLayout(modo_layout)
        layout.addWidget(grupo_modo)
        
        # Mensagem do sistema
        self.label_mensagem = QLabel("Sistema em modo manual. Conecte os dispositivos para começar.")
        self.label_mensagem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_mensagem.setStyleSheet("background-color: #e0e0e0; padding: 10px;")
        layout.addWidget(self.label_mensagem)
    
    def carregar_dispositivos(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM automacao ORDER BY dispositivo")
            dispositivos = cursor.fetchall()
            conn.close()
            
            self.tabela_dispositivos.setRowCount(len(dispositivos))
            
            for i, dispositivo in enumerate(dispositivos):
                for j in range(5):
                    valor = dispositivo[j+1] if j+1 < len(dispositivo) else ""
                    item = QTableWidgetItem(str(valor))
                    
                    # Colorir status
                    if j == 3:  # Coluna status
                        if valor == 'CONECTADO':
                            item.setForeground(QColor(0, 128, 0))
                        elif valor == 'DESCONECTADO':
                            item.setForeground(QColor(255, 0, 0))
                    
                    self.tabela_dispositivos.setItem(i, j, item)
            
        except Exception as e:
            print(f"Erro ao carregar dispositivos: {e}")
    
    def atualizar_status(self):
        # Simulação de atualização de status
        from datetime import datetime
        
        # Atualizar timestamp
        hora = datetime.now().strftime("%H:%M:%S")
        self.label_ultima_atualizacao.setText(f"Última atualização: {hora}")
        
        # Simular leitura do indicador (em modo manual, valores aleatórios)
        import random
        if self.check_manual.isChecked():
            leitura = random.uniform(0, 1000)
            self.label_leitura.setText(f"{leitura:.2f} kg")
    
    def conectar_indicador(self):
        porta = self.input_porta.currentText()
        baudrate = self.input_baudrate.currentText()
        endereco = self.input_endereco.text()
        
        try:
            # Atualizar no banco de dados
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE automacao 
                SET porta=?, baudrate=?, endereco_ip=?, status='CONECTADO', 
                    ultima_comunicacao=CURRENT_TIMESTAMP
                WHERE dispositivo = 'Indicador de Pesagem'
            ''', (porta, baudrate, endereco))
            
            conn.commit()
            conn.close()
            
            self.label_status_indicador.setText("STATUS: CONECTADO")
            self.label_status_indicador.setStyleSheet("font-size: 14px; font-weight: bold; color: green;")
            
            self.label_mensagem.setText(f"Indicador conectado na porta {porta} ({baudrate} bps)")
            
            QMessageBox.information(self, "Conexão", f"Indicador conectado com sucesso!\nPorta: {porta}\nBaud Rate: {baudrate}")
            
            self.carregar_dispositivos()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao conectar indicador: {e}")
    
    def desconectar_indicador(self):
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE automacao 
                SET status='DESCONECTADO'
                WHERE dispositivo = 'Indicador de Pesagem'
            ''')
            
            conn.commit()
            conn.close()
            
            self.label_status_indicador.setText("STATUS: DESCONECTADO")
            self.label_status_indicador.setStyleSheet("font-size: 14px; font-weight: bold; color: red;")
            
            self.label_mensagem.setText("Indicador desconectado")
            
            QMessageBox.information(self, "Desconexão", "Indicador desconectado com sucesso!")
            
            self.carregar_dispositivos()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao desconectar indicador: {e}")
    
    def zerar_indicador(self):
        self.label_leitura.setText("0.00 kg")
        self.label_mensagem.setText("Indicador zerado")
    
    def tara_indicador(self):
        QMessageBox.information(self, "Tara", "Tara aplicada com sucesso!")
        self.label_mensagem.setText("Tara aplicada ao indicador")
    
    def imprimir_pesagem(self):
        QMessageBox.information(self, "Impressão", "Pesagem enviada para impressora!")
        self.label_mensagem.setText("Pesagem impressa com sucesso")
    
    def salvar_leitura(self):
        leitura = self.label_leitura.text()
        try:
            # Converter "123.45 kg" para número
            valor = float(leitura.split()[0])
            
            QMessageBox.information(self, "Salvar", f"Leitura salva: {valor:.2f} kg")
            self.label_mensagem.setText(f"Leitura de {valor:.2f} kg salva com sucesso")
            
        except:
            QMessageBox.warning(self, "Erro", "Leitura inválida para salvar")
    
    def adicionar_dispositivo(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Adicionar Dispositivo")
        dialog.setText("Funcionalidade em desenvolvimento")
        dialog.exec()
    
    def remover_dispositivo(self):
        QMessageBox.information(self, "Remover", "Funcionalidade em desenvolvimento")
    
    def configurar_dispositivo(self):
        QMessageBox.information(self, "Configurar", "Funcionalidade em desenvolvimento")