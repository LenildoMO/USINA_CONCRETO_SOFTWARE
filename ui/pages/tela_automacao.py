from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QMessageBox,
                             QLineEdit, QFormLayout, QComboBox,
                             QProgressBar, QTextEdit, QCheckBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QMainWindow, QTabWidget, QApplication, QGridLayout,
                             QInputDialog, QDialog, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QFont, QColor
import sqlite3
import random
import json
import os
import sys
import time
import webbrowser
from urllib.parse import quote
from datetime import datetime
import threading

# ==================== CLASSE DE SINCRONIZAÇÃO ====================
class SincronizadorPesagensAutomacao:
    """Classe responsável por sincronizar pesagens pendentes com a automação"""
    
    @staticmethod
    def obter_pesagens_pendentes():
        """Obtém todas as pesagens pendentes do banco de dados"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    p.id,
                    p.quantidade,
                    p.materiais_json,
                    p.status,
                    p.traco_id,
                    t.codigo || ' - ' || t.nome as traco_nome
                FROM pesagens p
                LEFT JOIN tracos t ON p.traco_id = t.id
                WHERE p.status = 'PENDENTE'
                ORDER BY p.data_pesagem ASC
            ''')
            
            pesagens = cursor.fetchall()
            conn.close()
            
            return pesagens
            
        except Exception as e:
            print(f"Erro ao obter pesagens pendentes: {e}")
            return []
    
    @staticmethod
    def extrair_agregados_pesagem(pesagem_id):
        """Extrai os agregados específicos de uma pesagem"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT traco_id, quantidade, materiais_json 
                FROM pesagens 
                WHERE id = ?
            ''', (pesagem_id,))
            
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return {"Brita 0": 0, "Brita 1": 0, "Areia": 0, "Pó de Brita": 0}
            
            traco_id, quantidade, materiais_json_str = resultado
            
            agregados = {"Brita 0": 0, "Brita 1": 0, "Areia": 0, "Pó de Brita": 0}
            
            if materiais_json_str and materiais_json_str != '{}':
                try:
                    materiais_json = json.loads(materiais_json_str)
                    
                    # Buscar por nomes exatos
                    for nome in materiais_json:
                        nome_lower = nome.lower()
                        
                        if "brita 0" in nome_lower or "brita0" in nome_lower:
                            if isinstance(materiais_json[nome], dict):
                                agregados["Brita 0"] = materiais_json[nome].get("quantidade", 0)
                            else:
                                agregados["Brita 0"] = materiais_json[nome]
                        
                        elif "brita 1" in nome_lower or "brita1" in nome_lower:
                            if isinstance(materiais_json[nome], dict):
                                agregados["Brita 1"] = materiais_json[nome].get("quantidade", 0)
                            else:
                                agregados["Brita 1"] = materiais_json[nome]
                        
                        elif "areia" in nome_lower:
                            if isinstance(materiais_json[nome], dict):
                                agregados["Areia"] = materiais_json[nome].get("quantidade", 0)
                            else:
                                agregados["Areia"] = materiais_json[nome]
                        
                        elif "pó" in nome_lower or "po" in nome_lower:
                            if isinstance(materiais_json[nome], dict):
                                agregados["Pó de Brita"] = materiais_json[nome].get("quantidade", 0)
                            else:
                                agregados["Pó de Brita"] = materiais_json[nome]
                    
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON da pesagem {pesagem_id}: {e}")
            
            # Se não encontrou no JSON, buscar do traço
            if all(v == 0 for v in agregados.values()) and traco_id and quantidade:
                agregados = SincronizadorPesagensAutomacao.calcular_agregados_do_traco(traco_id, quantidade)
            
            conn.close()
            return agregados
            
        except Exception as e:
            print(f"Erro ao extrair agregados da pesagem {pesagem_id}: {e}")
            return {"Brita 0": 0, "Brita 1": 0, "Areia": 0, "Pó de Brita": 0}
    
    @staticmethod
    def calcular_agregados_do_traco(traco_id, quantidade):
        """Calcula os agregados a partir da definição do traço"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COALESCE(brita0, 0) as brita0,
                    COALESCE(brita1, 0) as brita1,
                    COALESCE(areia_media, 0) as areia_media,
                    COALESCE(po_brita, 0) as po_brita
                FROM tracos 
                WHERE id = ?
            ''', (traco_id,))
            
            traco = cursor.fetchone()
            conn.close()
            
            if traco:
                agregados = {
                    "Brita 0": traco[0] * quantidade,
                    "Brita 1": traco[1] * quantidade,
                    "Areia": traco[2] * quantidade,
                    "Pó de Brita": traco[3] * quantidade
                }
                return agregados
            
            return {"Brita 0": 0, "Brita 1": 0, "Areia": 0, "Pó de Brita": 0}
            
        except Exception as e:
            print(f"Erro ao calcular agregados do traço {traco_id}: {e}")
            return {"Brita 0": 0, "Brita 1": 0, "Areia": 0, "Pó de Brita": 0}
    
    @staticmethod
    def calcular_soma_acumulada_total_pendentes():
        """Calcula a soma ACUMULADA total de todas as pesagens pendentes"""
        try:
            pesagens = SincronizadorPesagensAutomacao.obter_pesagens_pendentes()
            
            total_brita0 = 0
            total_brita1 = 0
            total_areia = 0
            total_po_brita = 0
            detalhes_pesagens = []
            
            for pesagem in pesagens:
                pesagem_id = pesagem[0]
                
                agregados = SincronizadorPesagensAutomacao.extrair_agregados_pesagem(pesagem_id)
                
                # Acumular totais
                total_brita0 += agregados["Brita 0"]
                total_brita1 += agregados["Brita 1"]
                total_areia += agregados["Areia"]
                total_po_brita += agregados["Pó de Brita"]
                
                detalhes_pesagens.append({
                    "id": pesagem_id,
                    "agregados": agregados,
                    "traco_nome": pesagem[5] if len(pesagem) > 5 else "Desconhecido",
                    "quantidade": pesagem[1] if len(pesagem) > 1 else 0
                })
            
            # Calcular SOMA ACUMULADA CORRETA
            soma_etapa1 = total_brita0
            soma_etapa2 = total_brita0 + total_brita1
            soma_etapa3 = total_brita0 + total_brita1 + total_areia
            soma_etapa4 = total_brita0 + total_brita1 + total_areia + total_po_brita
            
            return {
                "brita0": total_brita0,
                "brita1": total_brita1,
                "areia": total_areia,
                "po_brita": total_po_brita,
                "soma_etapa1": soma_etapa1,
                "soma_etapa2": soma_etapa2,
                "soma_etapa3": soma_etapa3,
                "soma_etapa4": soma_etapa4,
                "detalhes_pesagens": detalhes_pesagens,
                "total_pesagens": len(detalhes_pesagens)
            }
            
        except Exception as e:
            print(f"Erro ao calcular soma acumulada total: {e}")
            return {
                "brita0": 0,
                "brita1": 0,
                "areia": 0,
                "po_brita": 0,
                "soma_etapa1": 0,
                "soma_etapa2": 0,
                "soma_etapa3": 0,
                "soma_etapa4": 0,
                "detalhes_pesagens": [],
                "total_pesagens": 0
            }

# ==================== CONFIGURAÇÕES WHATSAPP ====================
class ConfiguracaoWhatsApp:
    """Gerencia as configurações do WhatsApp"""
    
    CONFIG_FILE = "config_whatsapp.json"
    
    @staticmethod
    def carregar_config():
        """Carrega as configurações do arquivo"""
        try:
            if os.path.exists(ConfiguracaoWhatsApp.CONFIG_FILE):
                with open(ConfiguracaoWhatsApp.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"numeros": [], "mensagem_padrao": True}
        except:
            return {"numeros": [], "mensagem_padrao": True}
    
    @staticmethod
    def salvar_config(config):
        """Salva as configurações no arquivo"""
        try:
            with open(ConfiguracaoWhatsApp.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    @staticmethod
    def formatar_numero(numero):
        """Formata número para WhatsApp"""
        # Remove caracteres não numéricos
        numero = ''.join(filter(str.isdigit, numero))
        
        if numero.startswith('0'):
            numero = numero[1:]
        
        if len(numero) == 11:
            return f"55{numero}"
        elif len(numero) == 10:
            return f"55{numero}"
        
        return numero

# ==================== TELA DE CONFIGURAÇÃO WHATSAPP ====================
class TelaConfigWhatsApp(QDialog):
    """Tela simples de configuração do WhatsApp"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.config = ConfiguracaoWhatsApp.carregar_config()
        self.init_ui()
        self.carregar_dados()
    
    def init_ui(self):
        """Inicializa a interface"""
        self.setWindowTitle("⚙️ Configuração WhatsApp")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("📱 CONFIGURAÇÃO WHATSAPP")
        titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("""
            color: white;
            background-color: #25D366;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(titulo)
        
        # Instruções
        instrucoes = QLabel("Adicione os números dos operadores (com DDD, ex: 11999999999):")
        instrucoes.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(instrucoes)
        
        # Lista de números
        self.lista_numeros = QListWidget()
        self.lista_numeros.setMaximumHeight(150)
        layout.addWidget(self.lista_numeros)
        
        # Campo para adicionar número
        hbox_add = QHBoxLayout()
        self.input_numero = QLineEdit()
        self.input_numero.setPlaceholderText("Digite o número (ex: 11999999999)")
        btn_adicionar = QPushButton("➕ Adicionar")
        btn_adicionar.clicked.connect(self.adicionar_numero)
        btn_adicionar.setStyleSheet("""
            QPushButton {
                background-color: #25D366;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
        """)
        
        hbox_add.addWidget(self.input_numero)
        hbox_add.addWidget(btn_adicionar)
        layout.addLayout(hbox_add)
        
        # Botão remover
        btn_remover = QPushButton("➖ Remover Selecionado")
        btn_remover.clicked.connect(self.remover_numero)
        btn_remover.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)
        layout.addWidget(btn_remover)
        
        layout.addSpacing(20)
        
        # Checkbox mensagem
        self.check_mensagem = QCheckBox("Usar mensagem padrão (recomendado)")
        self.check_mensagem.setChecked(self.config.get("mensagem_padrao", True))
        layout.addWidget(self.check_mensagem)
        
        # Botões
        hbox_botoes = QHBoxLayout()
        
        btn_salvar = QPushButton("💾 Salvar")
        btn_salvar.clicked.connect(self.salvar_config)
        btn_salvar.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
        """)
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        
        btn_testar = QPushButton("🔍 Testar")
        btn_testar.clicked.connect(self.testar_envio)
        btn_testar.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        hbox_botoes.addWidget(btn_salvar)
        hbox_botoes.addWidget(btn_testar)
        hbox_botoes.addWidget(btn_cancelar)
        
        layout.addLayout(hbox_botoes)
        
        # Status
        self.label_status = QLabel("")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_status)
    
    def carregar_dados(self):
        """Carrega os dados da configuração"""
        self.lista_numeros.clear()
        for numero in self.config.get("numeros", []):
            self.lista_numeros.addItem(numero)
    
    def adicionar_numero(self):
        """Adiciona um número à lista"""
        numero = self.input_numero.text().strip()
        
        if not numero:
            self.label_status.setText("⚠️ Digite um número!")
            self.label_status.setStyleSheet("color: #FFC107;")
            return
        
        # Validar formato
        if not numero.isdigit() or len(numero) < 10 or len(numero) > 11:
            self.label_status.setText("⚠️ Formato inválido! Use: 11999999999")
            self.label_status.setStyleSheet("color: #DC3545;")
            return
        
        # Verificar duplicado
        for i in range(self.lista_numeros.count()):
            if self.lista_numeros.item(i).text() == numero:
                self.label_status.setText("⚠️ Número já cadastrado!")
                self.label_status.setStyleSheet("color: #DC3545;")
                return
        
        self.lista_numeros.addItem(numero)
        self.input_numero.clear()
        self.label_status.setText("✅ Número adicionado!")
        self.label_status.setStyleSheet("color: #28A745;")
    
    def remover_numero(self):
        """Remove número selecionado"""
        item = self.lista_numeros.currentItem()
        if item:
            self.lista_numeros.takeItem(self.lista_numeros.row(item))
            self.label_status.setText("✅ Número removido!")
            self.label_status.setStyleSheet("color: #28A745;")
    
    def testar_envio(self):
        """Testa envio de mensagem"""
        if self.lista_numeros.count() == 0:
            self.label_status.setText("⚠️ Adicione números primeiro!")
            self.label_status.setStyleSheet("color: #DC3545;")
            return
        
        # Obter primeiro número
        numero = self.lista_numeros.item(0).text()
        
        # Mensagem de teste
        mensagem = """🚚 *TESTE WHATSAPP - USINA DE CONCRETO* 🚚

✅ Sistema de envio configurado com sucesso!

📊 *DADOS DE TESTE:*
• Brita 0: 1.500 kg
• Brita 1: 1.200 kg
• Areia: 900 kg
• Pó de Brita: 600 kg

📦 Total: 4.200 kg
⏰ Data: TESTE
⚠️ Sistema funcionando corretamente!"""

        # Formatar número
        numero_formatado = ConfiguracaoWhatsApp.formatar_numero(numero)
        
        # Gerar link WhatsApp
        mensagem_codificada = quote(mensagem)
        link = f"https://web.whatsapp.com/send?phone={numero_formatado}&text={mensagem_codificada}"
        
        # Abrir no navegador
        webbrowser.open(link)
        
        self.label_status.setText("✅ WhatsApp aberto para teste!")
        self.label_status.setStyleSheet("color: #28A745;")
    
    def salvar_config(self):
        """Salva a configuração"""
        # Coletar números
        numeros = []
        for i in range(self.lista_numeros.count()):
            numeros.append(self.lista_numeros.item(i).text())
        
        # Atualizar configuração
        self.config["numeros"] = numeros
        self.config["mensagem_padrao"] = self.check_mensagem.isChecked()
        
        # Salvar
        if ConfiguracaoWhatsApp.salvar_config(self.config):
            self.label_status.setText("✅ Configurações salvas com sucesso!")
            self.label_status.setStyleSheet("color: #28A745;")
            
            # Fechar após 2 segundos
            QTimer.singleShot(2000, self.accept)
        else:
            self.label_status.setText("❌ Erro ao salvar configurações!")
            self.label_status.setStyleSheet("color: #DC3545;")

# ==================== TELA DE AUTOMAÇÃO (MODIFICADA) ====================
class TelaAutomacao(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.conectado = False
        self.peso_atual = 0.0
        self.pesando = False
        self.pesos_traco = {}
        self.traco_id_atual = None
        self.init_ui()
        self.iniciar_simulacao()
        self.iniciar_monitoramento_pesagens()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título (MANTIDO ORIGINAL)
        titulo = QLabel("⚙️ AUTOMAÇÃO - INDICADOR PARA CARREGADEIRA")
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
        
        # Layout principal (MANTIDO ORIGINAL)
        hbox = QHBoxLayout()
        
        # Coluna esquerda: Status e Controle (MANTIDO ORIGINAL)
        col_esquerda = QVBoxLayout()
        
        # Status do dispositivo (MANTIDO ORIGINAL)
        grupo_status = QGroupBox("⚖️ INDICADOR DE PESAGEM - CARREGADEIRA")
        grupo_status.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 3px solid #0D47A1;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #E3F2FD;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #0D47A1;
                font-size: 12pt;
            }
        """)
        status_layout = QVBoxLayout()
        
        self.label_status = QLabel("🔴 DESCONECTADO")
        self.label_status.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Display principal de peso (MANTIDO ORIGINAL)
        self.label_peso = QLabel("0.00 kg")
        self.label_peso.setFont(QFont("Arial", 42, QFont.Weight.Bold))
        self.label_peso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_peso.setStyleSheet("""
            background-color: #0D47A1;
            color: white;
            padding: 25px;
            border-radius: 15px;
            font-family: 'Courier New', monospace;
            border: 4px solid #1565C0;
            margin: 10px;
        """)
        
        # Painel de SOMA ACUMULADA DOS AGREGADOS (MANTIDO ORIGINAL)
        grupo_detalhes = QGroupBox("📊 SOMA ACUMULADA DOS AGREGADOS")
        grupo_detalhes.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2E7D32;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #E8F5E9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2E7D32;
                font-size: 11pt;
            }
        """)
        detalhes_layout = QVBoxLayout()
        
        self.label_etapa1 = QLabel("1️⃣ BRITA 0 = 0 kg")
        self.label_etapa1.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.label_etapa1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_etapa1.setStyleSheet("""
            color: #0D47A1;
            background-color: #BBDEFB;
            padding: 12px;
            border-radius: 5px;
            border: 2px solid #2196F3;
            margin: 3px;
        """)
        
        self.label_etapa2 = QLabel("2️⃣ BRITA 0 + BRITA 1 = 0 kg")
        self.label_etapa2.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.label_etapa2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_etapa2.setStyleSheet("""
            color: #1565C0;
            background-color: #90CAF9;
            padding: 12px;
            border-radius: 5px;
            border: 2px solid #1976D2;
            margin: 3px;
        """)
        
        self.label_etapa3 = QLabel("3️⃣ BRITA 0 + BRITA 1 + AREIA = 0 kg")
        self.label_etapa3.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.label_etapa3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_etapa3.setStyleSheet("""
            color: #D84315;
            background-color: #FFCC80;
            padding: 12px;
            border-radius: 5px;
            border: 2px solid #FF9800;
            margin: 3px;
        """)
        
        self.label_etapa4 = QLabel("4️⃣ BRITA 0 + BRITA 1 + AREIA + PÓ = 0 kg")
        self.label_etapa4.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.label_etapa4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_etapa4.setStyleSheet("""
            color: #6A1B9A;
            background-color: #E1BEE7;
            padding: 12px;
            border-radius: 5px;
            border: 2px solid #9C27B0;
            margin: 3px;
        """)
        
        detalhes_layout.addWidget(self.label_etapa1)
        detalhes_layout.addWidget(self.label_etapa2)
        detalhes_layout.addWidget(self.label_etapa3)
        detalhes_layout.addWidget(self.label_etapa4)
        
        grupo_detalhes.setLayout(detalhes_layout)
        
        # Barra de progresso (MANTIDO ORIGINAL)
        self.barra_progresso = QProgressBar()
        self.barra_progresso.setRange(0, 50000)
        self.barra_progresso.setTextVisible(True)
        self.barra_progresso.setFormat("Capacidade: %v/%m kg")
        self.barra_progresso.setStyleSheet("""
            QProgressBar {
                border: 2px solid #1976D2;
                border-radius: 5px;
                text-align: center;
                background-color: #E3F2FD;
                height: 30px;
                font-weight: bold;
                font-size: 11pt;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 5px;
            }
        """)
        
        # Status das pesagens (MANTIDO ORIGINAL)
        self.label_status_pesagens = QLabel("🟡 Aguardando pesagens pendentes...")
        self.label_status_pesagens.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_status_pesagens.setStyleSheet("""
            QLabel {
                color: #FF8F00;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                background-color: #FFF3E0;
                border: 2px solid #FF9800;
                font-size: 11pt;
            }
        """)
        
        # NOVO: Status do WhatsApp
        self.label_status_whatsapp = QLabel("📱 WhatsApp: Pronto")
        self.label_status_whatsapp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_status_whatsapp.setStyleSheet("""
            QLabel {
                color: #25D366;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
                background-color: #E8F5E9;
                border: 2px solid #25D366;
                font-size: 10pt;
            }
        """)
        
        # Última leitura (MANTIDO ORIGINAL)
        self.label_ultima_leitura = QLabel("Última leitura: --/--/-- --:--:--")
        self.label_ultima_leitura.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_ultima_leitura.setStyleSheet("color: #0D47A1; font-weight: bold; font-size: 11pt;")
        
        status_layout.addWidget(self.label_status)
        status_layout.addWidget(self.label_peso)
        status_layout.addWidget(grupo_detalhes)
        status_layout.addWidget(self.barra_progresso)
        status_layout.addWidget(self.label_status_pesagens)
        status_layout.addWidget(self.label_status_whatsapp)  # NOVO
        status_layout.addWidget(self.label_ultima_leitura)
        
        grupo_status.setLayout(status_layout)
        col_esquerda.addWidget(grupo_status)
        
        # Controles (MANTIDO ORIGINAL)
        grupo_controle = QGroupBox("🔧 CONTROLES DO SISTEMA")
        grupo_controle.setStyleSheet(grupo_status.styleSheet())
        controle_layout = QFormLayout()
        
        self.btn_debug = QPushButton("🐛 Debug Banco de Dados")
        self.btn_debug.clicked.connect(self.debug_banco_dados)
        self.btn_debug.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #FF9800, stop:1 #F57C00);
                color: white;
                border: 2px solid #EF6C00;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #F57C00, stop:1 #E65100);
            }
        """)
        
        self.check_simulacao = QCheckBox("Modo Simulação")
        self.check_simulacao.setChecked(True)
        self.check_simulacao.setStyleSheet("""
            QCheckBox {
                color: #0D47A1;
                font-weight: bold;
                font-size: 11pt;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)
        
        controle_layout.addRow("", self.btn_debug)
        controle_layout.addRow("", self.check_simulacao)
        
        grupo_controle.setLayout(controle_layout)
        col_esquerda.addWidget(grupo_controle)
        
        # Sincronização com Pesagens (MANTIDO ORIGINAL)
        grupo_sincronizacao = QGroupBox("🔄 CONTROLE DE SINCRONIZAÇÃO")
        grupo_sincronizacao.setStyleSheet(grupo_status.styleSheet())
        sinc_layout = QVBoxLayout()
        
        hbox_botoes = QHBoxLayout()
        
        self.btn_sincronizar_agora = QPushButton("🔄 Sincronizar Agora")
        self.btn_sincronizar_agora.clicked.connect(self.sincronizar_com_pesagens)
        self.btn_sincronizar_agora.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
        """)
        
        self.btn_limpar_sincronizacao = QPushButton("🗑️ Limpar Indicador")
        self.btn_limpar_sincronizacao.clicked.connect(self.limpar_sincronizacao)
        self.btn_limpar_sincronizacao.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #D32F2F, stop:1 #B71C1C);
                color: white;
                border: 2px solid #C62828;
                border-radius: 5px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #C62828, stop:1 #8B0000);
            }
        """)
        
        hbox_botoes.addWidget(self.btn_sincronizar_agora)
        hbox_botoes.addWidget(self.btn_limpar_sincronizacao)
        
        sinc_layout.addLayout(hbox_botoes)
        
        # Tabela de pesagens sincronizadas (MANTIDO ORIGINAL)
        self.tabela_pesagens_sincronizadas = QTableWidget()
        self.tabela_pesagens_sincronizadas.setColumnCount(7)
        self.tabela_pesagens_sincronizadas.setHorizontalHeaderLabels([
            "Pesagem", "Traço", "Qtd (m³)", "Etapa 1", "Etapa 2", "Etapa 3", "Etapa 4"
        ])
        self.tabela_pesagens_sincronizadas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_pesagens_sincronizadas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_pesagens_sincronizadas.setMaximumHeight(120)
        
        self.tabela_pesagens_sincronizadas.setStyleSheet("""
            QTableWidget {
                border: 2px solid #1976D2;
                border-radius: 5px;
                background-color: white;
                gridline-color: #2196F3;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #BBDEFB;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #0D47A1;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 8pt;
            }
        """)
        
        sinc_layout.addWidget(self.tabela_pesagens_sincronizadas)
        
        grupo_sincronizacao.setLayout(sinc_layout)
        col_esquerda.addWidget(grupo_sincronizacao)
        
        # =============== NOVO GRUPO: WHATSAPP AUTOMÁTICO ===============
        grupo_whatsapp = QGroupBox("📱 ENVIO VIA WHATSAPP")
        grupo_whatsapp.setStyleSheet(grupo_status.styleSheet())
        whatsapp_layout = QVBoxLayout()
        
        # Botões WhatsApp
        hbox_whatsapp = QHBoxLayout()
        
        self.btn_config_whatsapp = QPushButton("⚙️ Configurar")
        self.btn_config_whatsapp.clicked.connect(self.abrir_config_whatsapp)
        self.btn_config_whatsapp.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #25D366, stop:1 #128C7E);
                color: white;
                border: 2px solid #0A7E5C;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #128C7E, stop:1 #0A7E5C);
            }
        """)
        
        self.btn_enviar_whatsapp = QPushButton("📤 Enviar Agora")
        self.btn_enviar_whatsapp.clicked.connect(self.enviar_whatsapp)
        self.btn_enviar_whatsapp.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #28A745, stop:1 #218838);
                color: white;
                border: 2px solid #1E7E34;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #218838, stop:1 #1C7430);
            }
        """)
        
        hbox_whatsapp.addWidget(self.btn_config_whatsapp)
        hbox_whatsapp.addWidget(self.btn_enviar_whatsapp)
        
        whatsapp_layout.addLayout(hbox_whatsapp)
        
        # Info do envio
        self.label_info_envio = QLabel("Último envio: Nunca")
        self.label_info_envio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_info_envio.setStyleSheet("color: #6C757D; font-size: 9pt;")
        whatsapp_layout.addWidget(self.label_info_envio)
        
        grupo_whatsapp.setLayout(whatsapp_layout)
        col_esquerda.addWidget(grupo_whatsapp)
        
        # Botões de controle do dispositivo (MANTIDO ORIGINAL)
        btn_controle_layout = QHBoxLayout()
        
        self.btn_conectar = QPushButton("🔗 Conectar Indicador")
        self.btn_conectar.clicked.connect(self.conectar_dispositivo)
        self.btn_conectar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #4CAF50, stop:1 #388E3C);
                color: white;
                border: 2px solid #2E7D32;
                border-radius: 5px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #388E3C, stop:1 #2E7D32);
            }
        """)
        
        self.btn_desconectar = QPushButton("🔴 Desconectar")
        self.btn_desconectar.clicked.connect(self.desconectar_dispositivo)
        self.btn_desconectar.setEnabled(False)
        self.btn_desconectar.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #D32F2F, stop:1 #B71C1C);
                color: white;
                border: 2px solid #C62828;
                border-radius: 5px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #C62828, stop:1 #8B0000);
            }
        """)
        
        btn_controle_layout.addWidget(self.btn_conectar)
        btn_controle_layout.addWidget(self.btn_desconectar)
        
        col_esquerda.addLayout(btn_controle_layout)
        
        hbox.addLayout(col_esquerda, 50)
        
        # Coluna direita: Log e Detalhes (MANTIDO ORIGINAL)
        col_direita = QVBoxLayout()
        
        # Log do sistema (MANTIDO ORIGINAL)
        grupo_log = QGroupBox("📝 LOG DO SISTEMA (DETALHADO)")
        grupo_log.setStyleSheet(grupo_status.styleSheet())
        log_layout = QVBoxLayout()
        
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMaximumHeight(250)
        self.text_log.setStyleSheet("""
            QTextEdit {
                background-color: #0D47A1;
                color: white;
                border: 2px solid #1976D2;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                padding: 5px;
            }
        """)
        
        log_layout.addWidget(self.text_log)
        
        btn_limpar_log = QPushButton("🧹 Limpar Log")
        btn_limpar_log.clicked.connect(self.limpar_log)
        btn_limpar_log.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1976D2, stop:1 #1565C0);
                color: white;
                border: 2px solid #0D47A1;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1565C0, stop:1 #0D47A1);
            }
        """)
        log_layout.addWidget(btn_limpar_log)
        
        grupo_log.setLayout(log_layout)
        col_direita.addWidget(grupo_log)
        
        # Tabela detalhada (MANTIDO ORIGINAL)
        grupo_detalhado = QGroupBox("📦 DETALHES POR PESAGEM")
        grupo_detalhado.setStyleSheet(grupo_status.styleSheet())
        detalhado_layout = QVBoxLayout()
        
        self.tabela_detalhada = QTableWidget()
        self.tabela_detalhada.setColumnCount(8)
        self.tabela_detalhada.setHorizontalHeaderLabels([
            "ID", "Traço", "Qtd", "B0", "B1", "Areia", "Pó", "Total"
        ])
        self.tabela_detalhada.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_detalhada.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_detalhada.setMaximumHeight(180)
        
        self.tabela_detalhada.setStyleSheet("""
            QTableWidget {
                border: 2px solid #1976D32;
                border-radius: 5px;
                background-color: white;
                gridline-color: #2196F3;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #BBDEFB;
            }
            QHeaderView::section {
                background-color: #0D47A1;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 7pt;
            }
        """)
        
        detalhado_layout.addWidget(self.tabela_detalhada)
        
        grupo_detalhado.setLayout(detalhado_layout)
        col_direita.addWidget(grupo_detalhado)
        
        # Status do sistema (MANTIDO ORIGINAL)
        self.label_status_sistema = QLabel("✅ Sistema pronto para sincronização")
        self.label_status_sistema.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_status_sistema.setStyleSheet("""
            QLabel {
                color: #0D47A1;
                font-weight: bold;
                padding: 12px;
                border: 2px solid #1976D2;
                border-radius: 5px;
                background-color: #E3F2FD;
                font-size: 11pt;
            }
        """)
        col_direita.addWidget(self.label_status_sistema)
        
        hbox.addLayout(col_direita, 50)
        
        layout.addLayout(hbox)
        
        # Informações do sistema (MANTIDO ORIGINAL)
        info = QLabel("💡 Sistema para operador da carregadeira. SOMA ACUMULADA: 1) BRITA 0  2) BRITA 0 + BRITA 1  3) BRITA 0 + BRITA 1 + AREIA  4) BRITA 0 + BRITA 1 + AREIA + PÓ DE BRITA")
        info.setWordWrap(True)
        info.setStyleSheet("""
            background-color: #E3F2FD;
            color: #0D47A1;
            padding: 12px;
            border-radius: 5px;
            border: 1px solid #1976D2;
            font-weight: bold;
            margin-top: 10px;
        """)
        layout.addWidget(info)
    
    # ==================== NOVOS MÉTODOS WHATSAPP ====================
    
    def abrir_config_whatsapp(self):
        """Abre a tela de configuração do WhatsApp"""
        dialog = TelaConfigWhatsApp(self)
        dialog.exec()
    
    def enviar_whatsapp(self):
        """Envia mensagem via WhatsApp"""
        try:
            # Carregar configurações
            config = ConfiguracaoWhatsApp.carregar_config()
            numeros = config.get("numeros", [])
            
            if not numeros:
                resposta = QMessageBox.question(
                    self,
                    "❓ Nenhum número configurado",
                    "Não há números cadastrados para envio.\nDeseja configurar agora?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if resposta == QMessageBox.StandardButton.Yes:
                    self.abrir_config_whatsapp()
                return
            
            # Obter dados atuais
            dados = SincronizadorPesagensAutomacao.calcular_soma_acumulada_total_pendentes()
            
            if dados['total_pesagens'] == 0:
                QMessageBox.warning(self, "⚠️ Atenção", "Não há pesagens pendentes para enviar!")
                return
            
            # Perguntar confirmação
            resposta = QMessageBox.question(
                self,
                "📤 Confirmar Envio WhatsApp",
                f"Deseja enviar para {len(numeros)} número(s)?\n\n"
                f"Total de pesagens: {dados['total_pesagens']}\n"
                f"Total geral: {dados['soma_etapa4']:,.0f} kg",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if resposta != QMessageBox.StandardButton.Yes:
                return
            
            # Gerar mensagem
            mensagem = self.gerar_mensagem_whatsapp(dados)
            
            # Enviar para cada número (em thread separada para não travar a interface)
            threading.Thread(target=self.enviar_whatsapp_thread, args=(numeros, mensagem), daemon=True).start()
            
            # Atualizar interface
            self.btn_enviar_whatsapp.setEnabled(False)
            self.btn_enviar_whatsapp.setText("⏳ Enviando...")
            self.label_status_whatsapp.setText("📱 WhatsApp: Enviando...")
            self.label_status_whatsapp.setStyleSheet("""
                QLabel {
                    color: #FFC107;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                    background-color: #FFF3CD;
                    border: 2px solid #FFC107;
                    font-size: 10pt;
                }
            """)
            
        except Exception as e:
            self.adicionar_log(f"Erro ao enviar WhatsApp: {str(e)}")
            QMessageBox.critical(self, "❌ Erro", f"Erro ao enviar mensagem:\n{str(e)}")
    
    def enviar_whatsapp_thread(self, numeros, mensagem):
        """Thread para envio de WhatsApp"""
        try:
            total_enviados = 0
            
            for numero in numeros:
                try:
                    # Formatar número
                    numero_formatado = ConfiguracaoWhatsApp.formatar_numero(numero)
                    
                    # Gerar link WhatsApp
                    mensagem_codificada = quote(mensagem)
                    link = f"https://web.whatsapp.com/send?phone={numero_formatado}&text={mensagem_codificada}"
                    
                    # Abrir no navegador
                    webbrowser.open(link)
                    
                    total_enviados += 1
                    
                    # Aguardar um pouco entre envios
                    time.sleep(2)
                    
                except Exception as e:
                    self.adicionar_log(f"Erro ao enviar para {numero}: {str(e)}")
            
            # Atualizar interface na thread principal
            self.btn_enviar_whatsapp.setText("📤 Enviar Agora")
            QTimer.singleShot(0, lambda: self.atualizar_status_envio(total_enviados, len(numeros)))
            
        except Exception as e:
            self.adicionar_log(f"Erro na thread WhatsApp: {str(e)}")
    
    def atualizar_status_envio(self, enviados, total):
        """Atualiza o status após envio"""
        self.btn_enviar_whatsapp.setEnabled(True)
        
        if enviados > 0:
            self.label_status_whatsapp.setText(f"📱 WhatsApp: {enviados}/{total} enviados")
            self.label_status_whatsapp.setStyleSheet("""
                QLabel {
                    color: #28A745;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                    background-color: #D4EDDA;
                    border: 2px solid #28A745;
                    font-size: 10pt;
                }
            """)
            
            # Atualizar último envio
            self.label_info_envio.setText(f"Último envio: {datetime.now().strftime('%H:%M %d/%m')}")
            
            self.adicionar_log(f"WhatsApp: {enviados} mensagem(ns) enviada(s)")
            QMessageBox.information(self, "✅ Sucesso", f"{enviados} mensagem(ns) enviada(s) com sucesso!")
        else:
            self.label_status_whatsapp.setText("📱 WhatsApp: Erro no envio")
            self.label_status_whatsapp.setStyleSheet("""
                QLabel {
                    color: #DC3545;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                    background-color: #F8D7DA;
                    border: 2px solid #DC3545;
                    font-size: 10pt;
                }
            """)
            
            QMessageBox.warning(self, "⚠️ Atenção", "Nenhuma mensagem foi enviada.")
    
    def gerar_mensagem_whatsapp(self, dados):
        """Gera mensagem formatada para WhatsApp"""
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        mensagem = f"""🚚 *PESAGENS PENDENTES - USINA DE CONCRETO* 🚚

📊 *SOMA ACUMULADA DOS AGREGADOS* 📊

*ETAPAS:*
1️⃣ BRITA 0: {dados['soma_etapa1']:,.0f} kg
2️⃣ BRITA 0 + BRITA 1: {dados['soma_etapa2']:,.0f} kg
3️⃣ BRITA 0 + BRITA 1 + AREIA: {dados['soma_etapa3']:,.0f} kg
4️⃣ TOTAL GERAL: {dados['soma_etapa4']:,.0f} kg

📋 *DETALHES:*
• Brita 0: {dados['brita0']:,.0f} kg
• Brita 1: {dados['brita1']:,.0f} kg
• Areia: {dados['areia']:,.0f} kg
• Pó de Brita: {dados['po_brita']:,.0f} kg

📦 *PESAGENS:* {dados['total_pesagens']}
⏰ *DATA/HORA:* {data_hora}
👷 *OPERADOR DA CARREGADEIRA*

⚠️ *SEGUIR ETAPAS NA SEQUÊNCIA INDICADA!*

✅ *INSTRUÇÕES:*
1. Carregue BRITA 0 até atingir: {dados['soma_etapa1']:,.0f} kg
2. Adicione BRITA 1 até totalizar: {dados['soma_etapa2']:,.0f} kg
3. Adicione AREIA até totalizar: {dados['soma_etapa3']:,.0f} kg
4. Complete com PÓ DE BRITA até: {dados['soma_etapa4']:,.0f} kg

🔔 *ATENÇÃO:* Verifique o indicador na tela durante o carregamento!"""
        
        return mensagem
    
    # ==================== MÉTODOS ORIGINAIS (MANTIDOS) ====================
    
    def iniciar_monitoramento_pesagens(self):
        """Inicia o monitoramento periódico de pesagens pendentes"""
        self.timer_monitoramento = QTimer()
        self.timer_monitoramento.timeout.connect(self.verificar_pesagens_pendentes)
        self.timer_monitoramento.start(15000)
        
        QTimer.singleShot(3000, self.verificar_pesagens_pendentes)
    
    def verificar_pesagens_pendentes(self):
        """Verifica se há pesagens pendentes e sincroniza automaticamente"""
        try:
            self.adicionar_log("Verificando pesagens pendentes...")
            
            resultado = SincronizadorPesagensAutomacao.calcular_soma_acumulada_total_pendentes()
            detalhes_pesagens = resultado["detalhes_pesagens"]
            
            if detalhes_pesagens:
                self.label_status_pesagens.setText(f"🟢 {len(detalhes_pesagens)} PESAGEM(NS) PENDENTE(S)")
                self.label_status_pesagens.setStyleSheet("""
                    QLabel {
                        color: #2E7D32;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 5px;
                        background-color: #E8F5E9;
                        border: 2px solid #4CAF50;
                        font-size: 11pt;
                    }
                """)
                
                # Atualizar tabela resumo
                self.tabela_pesagens_sincronizadas.setRowCount(len(detalhes_pesagens))
                for i, pesagem in enumerate(detalhes_pesagens):
                    # Calcular soma acumulada para esta pesagem
                    b0 = pesagem['agregados']['Brita 0']
                    b1 = pesagem['agregados']['Brita 1']
                    areia = pesagem['agregados']['Areia']
                    po = pesagem['agregados']['Pó de Brita']
                    
                    # Calcular as 4 etapas da soma acumulada
                    etapa1 = b0
                    etapa2 = b0 + b1
                    etapa3 = b0 + b1 + areia
                    etapa4 = b0 + b1 + areia + po
                    
                    self.tabela_pesagens_sincronizadas.setItem(i, 0, QTableWidgetItem(f"#{pesagem['id']}"))
                    self.tabela_pesagens_sincronizadas.setItem(i, 1, QTableWidgetItem(pesagem['traco_nome']))
                    self.tabela_pesagens_sincronizadas.setItem(i, 2, QTableWidgetItem(f"{pesagem['quantidade']:.2f}"))
                    self.tabela_pesagens_sincronizadas.setItem(i, 3, QTableWidgetItem(f"{etapa1:,.0f}"))
                    self.tabela_pesagens_sincronizadas.setItem(i, 4, QTableWidgetItem(f"{etapa2:,.0f}"))
                    self.tabela_pesagens_sincronizadas.setItem(i, 5, QTableWidgetItem(f"{etapa3:,.0f}"))
                    self.tabela_pesagens_sincronizadas.setItem(i, 6, QTableWidgetItem(f"{etapa4:,.0f}"))
                
                # Atualizar tabela detalhada
                self.tabela_detalhada.setRowCount(len(detalhes_pesagens))
                for i, pesagem in enumerate(detalhes_pesagens):
                    total_pesagem = (pesagem['agregados']['Brita 0'] + 
                                   pesagem['agregados']['Brita 1'] + 
                                   pesagem['agregados']['Areia'] + 
                                   pesagem['agregados']['Pó de Brita'])
                    
                    self.tabela_detalhada.setItem(i, 0, QTableWidgetItem(f"#{pesagem['id']}"))
                    self.tabela_detalhada.setItem(i, 1, QTableWidgetItem(pesagem['traco_nome']))
                    self.tabela_detalhada.setItem(i, 2, QTableWidgetItem(f"{pesagem['quantidade']:.2f}"))
                    self.tabela_detalhada.setItem(i, 3, QTableWidgetItem(f"{pesagem['agregados']['Brita 0']:,.0f}"))
                    self.tabela_detalhada.setItem(i, 4, QTableWidgetItem(f"{pesagem['agregados']['Brita 1']:,.0f}"))
                    self.tabela_detalhada.setItem(i, 5, QTableWidgetItem(f"{pesagem['agregados']['Areia']:,.0f}"))
                    self.tabela_detalhada.setItem(i, 6, QTableWidgetItem(f"{pesagem['agregados']['Pó de Brita']:,.0f}"))
                    self.tabela_detalhada.setItem(i, 7, QTableWidgetItem(f"{total_pesagem:,.0f}"))
                
                # Atualizar indicador com SOMA ACUMULADA (4 etapas)
                self.atualizar_indicador_acumulado(resultado)
                
                self.adicionar_log(f"Sincronização automática: {len(detalhes_pesagens)} pesagem(ns)")
                self.adicionar_log(f"Etapa 1 (B0): {resultado['soma_etapa1']:,.0f} kg")
                self.adicionar_log(f"Etapa 2 (B0+B1): {resultado['soma_etapa2']:,.0f} kg")
                self.adicionar_log(f"Etapa 3 (B0+B1+Areia): {resultado['soma_etapa3']:,.0f} kg")
                self.adicionar_log(f"Etapa 4 (Total): {resultado['soma_etapa4']:,.0f} kg")
                
                # Atualizar peso total no display principal
                self.peso_atual = resultado['soma_etapa4']
                self.atualizar_display()
                
            else:
                self.label_status_pesagens.setText("🟡 NENHUMA PESAGEM PENDENTE")
                self.label_status_pesagens.setStyleSheet("""
                    QLabel {
                        color: #FF8F00;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 5px;
                        background-color: #FFF3E0;
                        border: 2px solid #FF9800;
                        font-size: 11pt;
                    }
                """)
                self.tabela_pesagens_sincronizadas.setRowCount(0)
                self.tabela_detalhada.setRowCount(0)
                self.limpar_detalhes_indicador()
                self.peso_atual = 0
                self.atualizar_display()
                
        except Exception as e:
            self.adicionar_log(f"Erro ao verificar pesagens pendentes: {str(e)}")
    
    def atualizar_indicador_acumulado(self, resultado):
        """Atualiza o indicador com as 4 ETAPAS da SOMA ACUMULADA"""
        # Formatando os valores com separadores de milhar (ponto para milhar)
        etapa1_fmt = f"{resultado['soma_etapa1']:,.0f}".replace(",", ".")
        etapa2_fmt = f"{resultado['soma_etapa2']:,.0f}".replace(",", ".")
        etapa3_fmt = f"{resultado['soma_etapa3']:,.0f}".replace(",", ".")
        etapa4_fmt = f"{resultado['soma_etapa4']:,.0f}".replace(",", ".")
        
        # Atualizar labels das 4 ETAPAS da SOMA ACUMULADA
        self.label_etapa1.setText(f"1️⃣ BRITA 0 = {etapa1_fmt} kg")
        self.label_etapa2.setText(f"2️⃣ BRITA 0 + BRITA 1 = {etapa2_fmt} kg")
        self.label_etapa3.setText(f"3️⃣ BRITA 0 + BRITA 1 + AREIA = {etapa3_fmt} kg")
        self.label_etapa4.setText(f"4️⃣ BRITA 0 + BRITA 1 + AREIA + PÓ = {etapa4_fmt} kg")
        
        # Destacar se tiver valor
        if resultado['soma_etapa1'] > 0:
            self.label_etapa1.setStyleSheet("""
                color: #0D47A1;
                background-color: #BBDEFB;
                padding: 12px;
                border-radius: 5px;
                border: 3px solid #2196F3;
                margin: 3px;
                font-weight: bold;
                font-size: 14pt;
            """)
        
        if resultado['soma_etapa2'] > resultado['soma_etapa1']:
            self.label_etapa2.setStyleSheet("""
                color: #1565C0;
                background-color: #90CAF9;
                padding: 12px;
                border-radius: 5px;
                border: 3px solid #1976D2;
                margin: 3px;
                font-weight: bold;
                font-size: 14pt;
            """)
        
        if resultado['soma_etapa3'] > resultado['soma_etapa2']:
            self.label_etapa3.setStyleSheet("""
                color: #D84315;
                background-color: #FFCC80;
                padding: 12px;
                border-radius: 5px;
                border: 3px solid #FF9800;
                margin: 3px;
                font-weight: bold;
                font-size: 14pt;
            """)
        
        if resultado['soma_etapa4'] > resultado['soma_etapa3']:
            self.label_etapa4.setStyleSheet("""
                color: #6A1B9A;
                background-color: #E1BEE7;
                padding: 12px;
                border-radius: 5px;
                border: 3px solid #9C27B0;
                margin: 3px;
                font-weight: bold;
                font-size: 14pt;
            """)
    
    def limpar_detalhes_indicador(self):
        """Limpa os detalhes do indicador - SOMENTE AS 4 ETAPAS"""
        self.label_etapa1.setText("1️⃣ BRITA 0 = 0 kg")
        self.label_etapa2.setText("2️⃣ BRITA 0 + BRITA 1 = 0 kg")
        self.label_etapa3.setText("3️⃣ BRITA 0 + BRITA 1 + AREIA = 0 kg")
        self.label_etapa4.setText("4️⃣ BRITA 0 + BRITA 1 + AREIA + PÓ = 0 kg")
        
        # Resetar estilos
        self.label_etapa1.setStyleSheet("""
            color: #0D47A1;
            background-color: #BBDEFB;
            padding: 12px;
            border-radius: 5px;
            border: 2px solid #2196F3;
            margin: 3px;
        """)
        
        self.label_etapa2.setStyleSheet("""
            color: #1565C0;
            background-color: #90CAF9;
            padding: 12px;
            border-radius: 5px;
            border: 2px solid #1976D2;
            margin: 3px;
        """)
        
        self.label_etapa3.setStyleSheet("""
            color: #D84315;
            background-color: #FFCC80;
            padding: 12px;
            border-radius: 5px;
            border: 2px solid #FF9800;
            margin: 3px;
        """)
        
        self.label_etapa4.setStyleSheet("""
            color: #6A1B9A;
            background-color: #E1BEE7;
            padding: 12px;
            border-radius: 5px;
            border: 2px solid #9C27B0;
            margin: 3px;
        """)
    
    def sincronizar_com_pesagens(self):
        """Sincroniza manualmente com pesagens pendentes"""
        try:
            self.adicionar_log("=== INICIANDO SINCRONIZAÇÃO MANUAL ===")
            
            resultado = SincronizadorPesagensAutomacao.calcular_soma_acumulada_total_pendentes()
            detalhes_pesagens = resultado["detalhes_pesagens"]
            
            if detalhes_pesagens:
                # Atualizar tabelas
                self.tabela_pesagens_sincronizadas.setRowCount(len(detalhes_pesagens))
                self.tabela_detalhada.setRowCount(len(detalhes_pesagens))
                
                for i, pesagem in enumerate(detalhes_pesagens):
                    # Calcular soma acumulada para esta pesagem
                    b0 = pesagem['agregados']['Brita 0']
                    b1 = pesagem['agregados']['Brita 1']
                    areia = pesagem['agregados']['Areia']
                    po = pesagem['agregados']['Pó de Brita']
                    
                    # Calcular as 4 etapas da soma acumulada
                    etapa1 = b0
                    etapa2 = b0 + b1
                    etapa3 = b0 + b1 + areia
                    etapa4 = b0 + b1 + areia + po
                    total_pesagem = etapa4
                    
                    # Tabela resumo
                    self.tabela_pesagens_sincronizadas.setItem(i, 0, QTableWidgetItem(f"#{pesagem['id']}"))
                    self.tabela_pesagens_sincronizadas.setItem(i, 1, QTableWidgetItem(pesagem['traco_nome']))
                    self.tabela_pesagens_sincronizadas.setItem(i, 2, QTableWidgetItem(f"{pesagem['quantidade']:.2f}"))
                    self.tabela_pesagens_sincronizadas.setItem(i, 3, QTableWidgetItem(f"{etapa1:,.0f}"))
                    self.tabela_pesagens_sincronizadas.setItem(i, 4, QTableWidgetItem(f"{etapa2:,.0f}"))
                    self.tabela_pesagens_sincronizadas.setItem(i, 5, QTableWidgetItem(f"{etapa3:,.0f}"))
                    self.tabela_pesagens_sincronizadas.setItem(i, 6, QTableWidgetItem(f"{etapa4:,.0f}"))
                    
                    # Tabela detalhada
                    self.tabela_detalhada.setItem(i, 0, QTableWidgetItem(f"#{pesagem['id']}"))
                    self.tabela_detalhada.setItem(i, 1, QTableWidgetItem(pesagem['traco_nome']))
                    self.tabela_detalhada.setItem(i, 2, QTableWidgetItem(f"{pesagem['quantidade']:.2f}"))
                    self.tabela_detalhada.setItem(i, 3, QTableWidgetItem(f"{pesagem['agregados']['Brita 0']:,.0f}"))
                    self.tabela_detalhada.setItem(i, 4, QTableWidgetItem(f"{pesagem['agregados']['Brita 1']:,.0f}"))
                    self.tabela_detalhada.setItem(i, 5, QTableWidgetItem(f"{pesagem['agregados']['Areia']:,.0f}"))
                    self.tabela_detalhada.setItem(i, 6, QTableWidgetItem(f"{pesagem['agregados']['Pó de Brita']:,.0f}"))
                    self.tabela_detalhada.setItem(i, 7, QTableWidgetItem(f"{total_pesagem:,.0f}"))
                
                # Atualizar indicador
                self.atualizar_indicador_acumulado(resultado)
                
                # Atualizar peso total
                self.peso_atual = resultado['soma_etapa4']
                self.atualizar_display()
                
                # Atualizar status
                self.label_status_pesagens.setText(f"✅ {len(detalhes_pesagens)} PESAGEM(NS) SINCRONIZADA(S)")
                self.label_status_pesagens.setStyleSheet("""
                    QLabel {
                        color: #2E7D32;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 5px;
                        background-color: #E8F5E9;
                        border: 2px solid #4CAF50;
                        font-size: 11pt;
                    }
                """)
                
                # Criar mensagem detalhada
                mensagem = f"✅ SINCRONIZAÇÃO CONCLUÍDA!\n\n"
                mensagem += f"Total de pesagens: {len(detalhes_pesagens)}\n\n"
                mensagem += "SOMA ACUMULADA DOS AGREGADOS:\n"
                mensagem += f"1️⃣ BRITA 0 = {resultado['soma_etapa1']:,.0f} kg\n"
                mensagem += f"2️⃣ BRITA 0 + BRITA 1 = {resultado['soma_etapa2']:,.0f} kg\n"
                mensagem += f"3️⃣ BRITA 0 + BRITA 1 + AREIA = {resultado['soma_etapa3']:,.0f} kg\n"
                mensagem += f"4️⃣ BRITA 0 + BRITA 1 + AREIA + PÓ = {resultado['soma_etapa4']:,.0f} kg"
                
                self.adicionar_log(f"Sincronização manual: {len(detalhes_pesagens)} pesagem(ns)")
                self.adicionar_log(f"Etapa 1 (B0): {resultado['soma_etapa1']:,.0f} kg")
                self.adicionar_log(f"Etapa 2 (B0+B1): {resultado['soma_etapa2']:,.0f} kg")
                self.adicionar_log(f"Etapa 3 (B0+B1+Areia): {resultado['soma_etapa3']:,.0f} kg")
                self.adicionar_log(f"Etapa 4 (Total): {resultado['soma_etapa4']:,.0f} kg")
                
                QMessageBox.information(self, "✅ SINCRONIZAÇÃO CONCLUÍDA", mensagem)
            else:
                self.label_status_pesagens.setText("ℹ️ NENHUMA PESAGEM PENDENTE")
                self.label_status_pesagens.setStyleSheet("""
                    QLabel {
                        color: #757575;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 5px;
                        background-color: #F5F5F5;
                        border: 2px solid #BDBDBD;
                        font-size: 11pt;
                    }
                """)
                self.adicionar_log("Sincronização manual: Nenhuma pesagem pendente encontrada")
                QMessageBox.information(self, "ℹ️ INFORMAÇÃO", "Nenhuma pesagem pendente encontrada para sincronização.")
            
            self.adicionar_log("=== SINCRONIZAÇÃO CONCLUÍDA ===")
            
        except Exception as e:
            self.adicionar_log(f"Erro na sincronização manual: {str(e)}")
            QMessageBox.warning(self, "❌ ERRO", f"Erro na sincronização:\n{str(e)}")
    
    def adicionar_log(self, mensagem):
        """Adiciona uma mensagem ao log"""
        timestamp = QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm:ss")
        self.text_log.append(f"[{timestamp}] {mensagem}")
        
        # Rolar para o final
        scrollbar = self.text_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def limpar_log(self):
        """Limpa o log do sistema"""
        self.text_log.clear()
    
    def limpar_sincronizacao(self):
        """Limpa a sincronização atual"""
        self.tabela_pesagens_sincronizadas.setRowCount(0)
        self.tabela_detalhada.setRowCount(0)
        self.limpar_detalhes_indicador()
        self.label_status_pesagens.setText("🟡 NENHUMA PESAGEM PENDENTE")
        self.label_status_pesagens.setStyleSheet("""
            QLabel {
                color: #FF8F00;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                background-color: #FFF3E0;
                border: 2px solid #FF9800;
                font-size: 11pt;
            }
        """)
        self.peso_atual = 0
        self.atualizar_display()
        self.adicionar_log("Sincronização limpa - indicador zerado")
        QMessageBox.information(self, "✅ LIMPEZA CONCLUÍDA", "Indicador zerado com sucesso!")
    
    def debug_banco_dados(self):
        """Debug do banco de dados"""
        try:
            conn = sqlite3.connect('usina_concreto.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM pesagens WHERE status = 'PENDENTE'")
            count = cursor.fetchone()[0]
            
            cursor.execute("SELECT id, traco_id, quantidade FROM pesagens WHERE status = 'PENDENTE'")
            pesagens = cursor.fetchall()
            
            conn.close()
            
            self.adicionar_log(f"=== DEBUG BANCO DE DADOS ===")
            self.adicionar_log(f"Pesagens pendentes: {count}")
            
            for pesagem in pesagens:
                self.adicionar_log(f"Pesagem ID: {pesagem[0]}, Traço: {pesagem[1]}, Qtd: {pesagem[2]}")
                
                agregados = SincronizadorPesagensAutomacao.extrair_agregados_pesagem(pesagem[0])
                self.adicionar_log(f"  Brita 0: {agregados['Brita 0']:,.0f} kg")
                self.adicionar_log(f"  Brita 1: {agregados['Brita 1']:,.0f} kg")
                self.adicionar_log(f"  Areia: {agregados['Areia']:,.0f} kg")
                self.adicionar_log(f"  Pó de Brita: {agregados['Pó de Brita']:,.0f} kg")
            
            self.adicionar_log(f"=== FIM DEBUG ===")
            
            QMessageBox.information(self, "✅ DEBUG", f"Debug concluído. Verifique o log para detalhes.\nPesagens pendentes: {count}")
            
        except Exception as e:
            self.adicionar_log(f"Erro no debug: {str(e)}")
            QMessageBox.warning(self, "❌ ERRO", f"Erro no debug:\n{str(e)}")
    
    def iniciar_simulacao(self):
        """Inicia a simulação de leitura do dispositivo"""
        self.timer_simulacao = QTimer()
        self.timer_simulacao.timeout.connect(self.simular_leitura)
        self.timer_simulacao.start(1000)
    
    def simular_leitura(self):
        """Simula leitura do dispositivo"""
        if self.conectado and self.pesando:
            # Simular aumento gradual
            if self.peso_atual < self.peso_meta:
                incremento = random.uniform(10, 50)
                self.peso_atual += incremento
                
                if self.peso_atual > self.peso_meta:
                    self.peso_atual = self.peso_meta
                
                self.atualizar_display()
    
    def atualizar_display(self):
        """Atualiza o display do peso"""
        peso_formatado = f"{self.peso_atual:,.2f}".replace(",", ".")
        self.label_peso.setText(f"{peso_formatado} kg")
        self.barra_progresso.setValue(int(self.peso_atual))
        
        # Atualizar última leitura
        timestamp = QDateTime.currentDateTime().toString("dd/MM/yyyy hh:mm:ss")
        self.label_ultima_leitura.setText(f"Última leitura: {timestamp}")
    
    def conectar_dispositivo(self):
        """Conecta ao dispositivo"""
        if not self.conectado:
            self.conectado = True
            self.label_status.setText("🟢 CONECTADO")
            self.label_status.setStyleSheet("color: #2E7D32; font-weight: bold;")
            self.btn_conectar.setEnabled(False)
            self.btn_desconectar.setEnabled(True)
            self.adicionar_log("Dispositivo conectado (simulação)")
    
    def desconectar_dispositivo(self):
        """Desconecta do dispositivo"""
        if self.conectado:
            self.conectado = False
            self.label_status.setText("🔴 DESCONECTADO")
            self.label_status.setStyleSheet("color: #D32F2F; font-weight: bold;")
            self.btn_conectar.setEnabled(True)
            self.btn_desconectar.setEnabled(False)
            self.adicionar_log("Dispositivo desconectado")

# ==================== EXECUÇÃO PRINCIPAL ====================
def main():
    """Função principal para executar a aplicação"""
    app = QApplication(sys.argv)
    
    # Criar janela principal
    window = QMainWindow()
    window.setWindowTitle("Sistema de Automação - Usina de Concreto")
    window.setGeometry(100, 100, 1400, 800)
    
    # Centralizar na tela
    screen_geometry = app.primaryScreen().geometry()
    x = (screen_geometry.width() - 1400) // 2
    y = (screen_geometry.height() - 800) // 2
    window.move(x, y)
    
    # Criar widget central
    central_widget = TelaAutomacao(window)
    window.setCentralWidget(central_widget)
    
    # Mostrar janela
    window.show()
    
    # Executar aplicação
    sys.exit(app.exec())

if __name__ == "__main__":
    main()