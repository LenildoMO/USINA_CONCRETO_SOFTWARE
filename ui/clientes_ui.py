from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class TelaClientes(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        titulo = QLabel("Cadastro de Clientes")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")

        layout.addWidget(titulo)
        self.setLayout(layout)
