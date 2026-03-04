from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class TelaEstoque(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        titulo = QLabel("Controle de Estoque")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")

        layout.addWidget(titulo)
        self.setLayout(layout)
