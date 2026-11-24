from ..resources import ASSETS_DIR

from .menu_screen import Menu_screen

from PySide6.QtGui import QColor, QPalette, QPainter, QPixmap, QFont
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class Main_menu(Menu_screen):
    start_clicked = Signal(bool)
    settings_clicked = Signal(bool)
    exit_clicked = Signal(bool)

    background_path = ASSETS_DIR / "main_menu_background.jpg"

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addStretch()

        self.background = QPixmap(self.background_path)

        self.menu = QWidget(self)
        self.menu.setFixedWidth(360)
        self.menu_layout = QVBoxLayout(self.menu)
        self.menu_layout.setSpacing(16)

        self.title = QLabel("Pick & Place Client")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont(self.font().family(), 24, QFont.Weight.Bold))

        self.start_button = QPushButton("Start sorting")
        self.settings_button = QPushButton("Settings")
        self.exit_button = QPushButton("Exit")

        self.start_button.clicked.connect(self.start_clicked)
        self.settings_button.clicked.connect(self.settings_clicked)
        self.exit_button.clicked.connect(self.exit_clicked)

        for button in (self.start_button, self.settings_button, self.exit_button):
            button.setFixedHeight(56)

        self.menu_layout.addWidget(self.title)
        self.menu_layout.addWidget(self.start_button)
        self.menu_layout.addWidget(self.settings_button)
        self.menu_layout.addWidget(self.exit_button)

        layout.addWidget(self.menu, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
    
    # Triggers automatically when window is resized
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        image = self.background.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (self.width() - image.width()) // 2
        y = (self.height() - image.height()) // 2
        painter.drawPixmap(x, y, image)
        