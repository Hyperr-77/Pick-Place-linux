from ..resources import ASSETS_DIR

from PySide6.QtGui import QColor, QPalette, QPainter, QPixmap, QFont
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class Live_sorting(QWidget):
    start_clicked = Signal(bool)
    settings_clicked = Signal(bool)
    exit_clicked = Signal(bool)

    background_path = ASSETS_DIR / "main_menu_background.jpg"

    def __init__(self, color):
        super().__init__()
        layout = QVBoxLayout(self)