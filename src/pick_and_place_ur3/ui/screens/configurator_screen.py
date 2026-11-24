
from PySide6.QtGui import QColor, QPalette, QPainter, QPixmap, QFont
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLayout

class Screen(QWidget):
    def __init__(self):
        super().__init__()
        layout: QLayout | None = None
        layout = QVBoxLayout()