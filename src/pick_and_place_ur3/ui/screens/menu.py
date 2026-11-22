from pathlib import Path

from PySide6.QtGui import QColor, QPalette, QPainter, QPixmap, QFont
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class Menu(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.menu_layout = QVBoxLayout(self)
        self.menu_layout.addStretch()

        self.name = QLabel()
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name.setFont(QFont(self.font().family(), 24, QFont.Weight.Bold))
        self.menu_layout.addWidget(self.name)

        self.background = None
        self.painter = QPainter(self)

        self.options: dict[str, QPushButton] = {}

    def set_name(self, name: str) -> None:
        self.name.setText(name)

    def set_background(self, path: Path) -> None:
         self.background = QPixmap(path)

    def set_dimensions(self, width: int, button_height: int, spacing: int) -> None:
        self.setFixedWidth(width)
        self.menu_layout.setSpacing(spacing)
        for button in self.options.values():
            button.setFixedHeight(button_height)
    
    def add_option(self, name: str, object: object) -> QPushButton:
        button = QPushButton(name)
        button.clicked.connect(object)

        self.options[name] = button

        self.menu_layout.addWidget(button)

        return button

    def paintEvent(self, event):
        if self.background is None: return
        self.painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        image = self.background.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (self.width() - image.width()) // 2
        y = (self.height() - image.height()) // 2
        self.painter.drawPixmap(x, y, image)