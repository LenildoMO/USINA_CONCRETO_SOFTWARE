 # ===============================
# OCULTAR CONSOLE (SEGURANÇA)
# ===============================
import ctypes
try:
    ctypes.windll.user32.ShowWindow(
        ctypes.windll.kernel32.GetConsoleWindow(), 0
    )
except:
    pass


# ===============================
# IMPORTAÇÕES BÁSICAS
# ===============================
import os
import sys
import subprocess


# ===============================
# CONFIGURAÇÃO BASE (SCRIPT / EXE)
# ===============================
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    IS_EXE = True
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IS_EXE = False

sys.path.insert(0, BASE_DIR)
if not IS_EXE:
    sys.path.insert(0, os.path.join(BASE_DIR, 'ui'))


# ===============================
# PYQT6
# ===============================
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QPushButton,
    QStackedWidget, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon


# ===============================
# IMPORTAÇÃO DAS TELAS
# ===============================
try:
    from ui.pages.tela_dashboard import TelaDashboard
except:
    TelaDashboard = None

try:
    from ui.pages.tela_clientes import TelaClientes
except:
    TelaClientes = None

try:
    from ui.pages.tela_estoque import TelaEstoque
except:
    TelaEstoque = None

try:
    from ui.pages.tela_tracos import TelaTracos
except:
    TelaTracos = None

try:
    from ui.pages.tela_pesagens import TelaPesagens
except:
    TelaPesagens = None

try:
    from ui.pages.tela_notas import TelaNotas
except:
    TelaNotas = None

try:
    from ui.pages.tela_relatorios import TelaRelatorios
except:
    TelaRelatorios = None

try:
    from ui.pages.tela_automacao import TelaAutomacao
except:
    TelaAutomacao = None


# ===============================
# JANELA PRINCIPAL (LAYOUT ORIGINAL)
# ===============================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 🔵 ÍCONE DA JANELA (SEM ALTERAR LAYOUT)
        icon_path = os.path.join(
            BASE_DIR, "Ícone profissional Betto Mix Concretos.png"
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle("Usina Betto Mix Concreto - Sistema de Gestão")
        self.setGeometry(100, 50, 1200, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # CABEÇALHO AZUL (ORIGINAL)
        header = QLabel("USINA BETTO MIX CONCRETO - SISTEMA DE GESTÃO")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            "background-color: #003366; color: white; padding: 10px;"
        )
        main_layout.addWidget(header)

        # BARRA DE BOTÕES
        self.button_bar = QHBoxLayout()
        self.button_bar.setSpacing(5)
        main_layout.addLayout(self.button_bar)

        # ÁREA DE CONTEÚDO
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # STATUS
        self.status_label = QLabel("Sistema inicializando...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            "background-color: #f0f0f0; padding: 5px;"
        )
        main_layout.addWidget(self.status_label)

        self.inicializar_sistema()

    def inicializar_sistema(self):
        telas = [
            ("🏠 Dashboard", TelaDashboard, self.abrir_dashboard),
            ("👥 Clientes", TelaClientes, self.abrir_clientes),
            ("📦 Estoque", TelaEstoque, self.abrir_estoque),
            ("📐 Traços", TelaTracos, self.abrir_tracos),
            ("⚖️ Pesagens", TelaPesagens, self.abrir_pesagens),
            ("📄 Notas", TelaNotas, self.abrir_notas),
            ("📊 Relatórios", TelaRelatorios, self.abrir_relatorios),
            ("⚙️ Automação", TelaAutomacao, self.abrir_automacao)
        ]

        self.telas_instancias = {}

        for texto, Classe, funcao in telas:
            btn = QPushButton(texto)
            btn.setFixedHeight(40)
            btn.clicked.connect(funcao)
            self.button_bar.addWidget(btn)

            if Classe:
                try:
                    instancia = Classe(self)
                except:
                    instancia = QWidget()
            else:
                instancia = QWidget()

            self.stacked_widget.addWidget(instancia)
            self.telas_instancias[texto] = instancia

        self.abrir_dashboard()
        self.status_label.setText("Sistema carregado com sucesso!")

    def mostrar_tela(self, nome, titulo):
        self.stacked_widget.setCurrentWidget(self.telas_instancias[nome])
        self.setWindowTitle(titulo)
        self.status_label.setText(nome)

    def abrir_dashboard(self):
        self.mostrar_tela("🏠 Dashboard", "Dashboard - Usina Betto Mix Concreto")

    def abrir_clientes(self):
        self.mostrar_tela("👥 Clientes", "Clientes - Usina Betto Mix Concreto")

    def abrir_estoque(self):
        self.mostrar_tela("📦 Estoque", "Estoque - Usina Betto Mix Concreto")

    def abrir_tracos(self):
        self.mostrar_tela("📐 Traços", "Traços - Usina Betto Mix Concreto")

    def abrir_pesagens(self):
        self.mostrar_tela("⚖️ Pesagens", "Pesagens - Usina Betto Mix Concreto")

    def abrir_notas(self):
        self.mostrar_tela("📄 Notas", "Notas Fiscais - Usina Betto Mix Concreto")

    def abrir_relatorios(self):
        self.mostrar_tela("📊 Relatórios", "Relatórios - Usina Betto Mix Concreto")

    def abrir_automacao(self):
        self.mostrar_tela("⚙️ Automação", "Automação - Usina Betto Mix Concreto")


# ===============================
# MAIN
# ===============================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 🔵 IDENTIDADE DO APLICATIVO (CORRIGE ÍCONE DO PYTHON NO WINDOWS)
    app.setApplicationName("Betto Mix Concreto")
    app.setOrganizationName("Betto Mix")

    # 🔵 ÍCONE GLOBAL DO SISTEMA
    icon_path = os.path.join(
        BASE_DIR, "Ícone profissional Betto Mix Concretos.png"
    )
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # TEMA AZUL ORIGINAL (INALTERADO)
    app.setStyleSheet("""
        QMainWindow { background-color: #f5f5f5; }
        QPushButton {
            background-color: #003366;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #004080; }
        QPushButton:pressed { background-color: #00264d; }
    """)

    janela = MainWindow()
    janela.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()