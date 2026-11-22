import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QStackedWidget,
)

from .screens.main_menu import Main_menu
from .screens.settings import Settings

class Client(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Widgets App")

        self.main_menu = Main_menu()
        self.settings = Settings()
        self.camera_calibration = None
        self.robot_arm_calibration = None
        self.cluster_manager = None
        self.bin_manager = None

        self.main_menu.start_clicked.connect(self.start_sorting)
        self.main_menu.settings_clicked.connect(self.show_settings)
        self.main_menu.exit_clicked.connect(self.close)

        self.settings.return_clicked.connect(self.show_main_menu)

        self.stack = QStackedWidget()

        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.settings)

        self.setCentralWidget(self.stack)

    def start_sorting(self):
        print("Start sorting...")

    def show_main_menu(self):
        print("Show main menu...")
        self.stack.setCurrentWidget(self.main_menu)

    def show_settings(self):
        print("Show settings...")
        self.stack.setCurrentWidget(self.settings)

app = QApplication(sys.argv)
window = Client()

window.show()
#window.showFullScreen()

app.exec()
