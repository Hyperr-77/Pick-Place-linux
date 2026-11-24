import sys

from .resources import ASSETS_DIR

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QStackedWidget,
)

from.screens.menu_screen import Menu_screen

class Client(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Widgets App")

        self.camera_calibration = None
        self.robot_arm_calibration = None
        self.cluster_manager = None
        self.bin_manager = None

        self.main_menu = Menu_screen()
        self.main_menu.set_name("Pick & Place Client")
        self.main_menu.set_background(ASSETS_DIR / "main_menu_background.jpg")
        self.main_menu.add_option("Start sorting", self.start_sorting)
        self.main_menu.add_option("Options", self.show_settings)
        self.main_menu.add_option("Exit", self.close)
        self.main_menu.set_dimensions(360, 56, 16)

        self.settings = Menu_screen()
        self.settings.set_name("Settings")
        self.main_menu.set_background(ASSETS_DIR / "main_menu_background.jpg")
        self.settings.add_option("Camera configuration", self.show_camera_configurator)
        self.settings.add_option("Robot arm configuration", self.show_robotarm_configurator)
        self.settings.add_option("Manage cluster", self.show_cluster_manager)
        self.settings.add_option("Manage bins", self.show_bin_manager)
        self.settings.add_option("Return", self.show_main_menu)
        self.settings.set_dimensions(360, 56, 16)

        self.stack = QStackedWidget()

        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.settings)

        self.setCentralWidget(self.stack)

    def start_sorting(self):
        print("Start sorting...")

    def show_camera_configurator(self):
        print("Show camera configurator...")

    def show_robotarm_configurator(self):
        print("Show robot arm configurator...")

    def show_cluster_manager(self):
        print("Show cluster manager...")

    def show_bin_manager(self):
        print("Show bin manager...")

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
