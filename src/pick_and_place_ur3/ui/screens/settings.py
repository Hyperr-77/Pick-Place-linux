from ..resources import ASSETS_DIR

from PySide6.QtGui import QColor, QPalette, QPainter, QPixmap, QFont
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class Settings(QWidget):
    camera_configurator_clicked = Signal(bool)
    robotarm_configurator_clicked = Signal(bool)
    cluster_manager_clicked = Signal(bool)
    bin_manager_clicked = Signal(bool)
    return_clicked = Signal(bool)

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

        self.title = QLabel("Settings")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont(self.font().family(), 24, QFont.Weight.Bold))

        self.camera_configurator_button = QPushButton("Camera configuration")
        self.robotarm_configurator_button = QPushButton("Robot arm configuration")
        self.cluster_manager_button = QPushButton("Manage cluster")
        self.bin_manager_button = QPushButton("Manage bins")
        self.return_button = QPushButton("Return")

        self.camera_configurator_button.clicked.connect(self.camera_configurator_clicked)
        self.robotarm_configurator_button.clicked.connect(self.robotarm_configurator_clicked)
        self.cluster_manager_button.clicked.connect(self.cluster_manager_clicked)
        self.bin_manager_button.clicked.connect(self.bin_manager_clicked)
        self.return_button.clicked.connect(self.return_clicked)

        for button in (self.camera_configurator_button, self.robotarm_configurator_button, self.cluster_manager_button, self.bin_manager_button, self.return_button):
            button.setFixedHeight(56)

        self.menu_layout.addWidget(self.title)
        self.menu_layout.addWidget(self.camera_configurator_button)
        self.menu_layout.addWidget(self.robotarm_configurator_button)
        self.menu_layout.addWidget(self.cluster_manager_button)
        self.menu_layout.addWidget(self.bin_manager_button)
        self.menu_layout.addWidget(self.return_button)

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
        