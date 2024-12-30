import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from src.ui.check_ui import KeyCheckWindow
from src.ui.main_window import MainWindow


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setFont(QFont("Segoe UI", 10))
        self.main_window = None
        self.key_window = None

    def show_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()

    def run(self):
        self.key_window = KeyCheckWindow()

        self.key_window.verify_button.clicked.connect(self.handle_verification)

        if self.key_window.check_existing_key():
            self.show_main_window()
        else:
            self.key_window.show()

        return self.app.exec_()

    def handle_verification(self):
        if self.key_window.verify_key():
            self.key_window.close()
            QTimer.singleShot(100, self.show_main_window)


def main():
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
