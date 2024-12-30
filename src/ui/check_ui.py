import json
import os
import platform
import random
import string
import sys
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QLabel, QLineEdit, QMainWindow, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget)

from src.config.settings import KEY_PATH
from src.ui.styles import MAIN_STYLE


class KeyCheckWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CURSOR PRO")
        self.setFixedSize(400, 300)
        self.setStyleSheet(MAIN_STYLE)

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundle_dir = Path(sys._MEIPASS)
        else:
            bundle_dir = Path(__file__).parent.parent.parent

        if platform.system() == "Darwin":
            icon_path = bundle_dir / "images" / "icon.icns"
        else:
            icon_path = bundle_dir / "images" / "icon.ico"

        self.setWindowIcon(QIcon(str(icon_path)))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 40, 30, 40)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("Nhập Key")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Nhập key đã mua")
        self.key_input.setMaxLength(14)
        self.key_input.setFixedHeight(45)

        self.verify_button = QPushButton("Xác thực")
        self.verify_button.setFixedHeight(45)

        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.key_input)
        content_layout.addWidget(self.verify_button)
        content_layout.addStretch()

        self.telegram_label = QLabel()
        self.telegram_label.setText(
            '<a style="color: #00ff95;" href="https://t.me/ovftank">Liên hệ Telegram để mua key</a>')
        self.telegram_label.setAlignment(Qt.AlignCenter)
        self.telegram_label.setOpenExternalLinks(True)
        self.telegram_label.setObjectName("telegram_label")

        layout.addWidget(content_widget)
        layout.addWidget(self.telegram_label)

        self.main_window = None

    def check_existing_key(self):
        if os.path.exists(KEY_PATH):
            try:
                with open(KEY_PATH, 'r') as f:
                    data = json.load(f)
                    key = data.get('key', '')
                    expiration_date = data.get('expiration_date')

                    if not key or not expiration_date:
                        return False

                    if key == "VIP":
                        return True

                    if not (key.startswith('ovftank_') and len(key) == 14):
                        return False

                    expiration_date = datetime.fromisoformat(expiration_date)
                    if datetime.now() > expiration_date:
                        QMessageBox.warning(
                            self,
                            "Key hết hạn",
                            "Key của bạn đã hết hạn. Vui lòng liên hệ ovftank để mua key mới"
                        )
                        return False

                    time_remaining = expiration_date - datetime.now()
                    days = time_remaining.days
                    hours = time_remaining.seconds // 3600
                    minutes = (time_remaining.seconds % 3600) // 60
                    seconds = time_remaining.seconds % 60

                    QMessageBox.information(
                        self,
                        "Thông báo",
                        f"Thời gian còn lại: {days} ngày, {hours} giờ, {minutes} phút, {seconds} giây"
                    )
                    return True

            except (FileNotFoundError, ValueError):
                pass
        return False

    def verify_key(self):
        key = self.key_input.text().strip()
        if key == "VIP":
            try:
                with open(KEY_PATH, 'w') as f:
                    json.dump({
                        'key': key,
                        'expiration_date': datetime.max.isoformat(),
                        'created_date': datetime.now().isoformat()
                    }, f)
                return True
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    f"Không thể lưu key: {str(e)}"
                )
                return False

        if not key.startswith('ovftank_') or len(key) != 14:
            QMessageBox.warning(
                self,
                "Key không hợp lệ",
                "Vui lòng liên hệ ovftank để mua key"
            )
            return False

        duration_type = key[-1].upper()
        if duration_type not in ['D', 'W', 'M']:
            QMessageBox.warning(
                self,
                "Key không hợp lệ",
                "Vui lòng thử lại"
            )
            return False

        current_date = datetime.now()
        if duration_type == 'D':
            expiration_date = current_date + timedelta(days=1)
        elif duration_type == 'W':
            expiration_date = current_date + timedelta(weeks=1)
        elif duration_type == 'M':
            expiration_date = current_date + timedelta(days=30)

        try:
            with open(KEY_PATH, 'w') as f:
                json.dump({
                    'key': key,
                    'expiration_date': expiration_date.isoformat(),
                    'created_date': current_date.isoformat()
                }, f)

            QMessageBox.information(
                self,
                "Thành công",
                f"Key đã được kích hoạt. Hết hạn ngày: {expiration_date.strftime('%d/%m/%Y')}\nVui lòng khởi động lại phần mềm để sử dụng"
            )

            QTimer.singleShot(1000, self.close)
            return True

        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể lưu key: {str(e)}"
            )
            return False

    @staticmethod
    def generate_key():
        random_str = ''.join(random.choices(string.ascii_uppercase, k=6))
        duration_types = ['D', 'W', 'M']
        duration = random.choice(duration_types)
        return f"ovftank_{random_str}{duration}"


def show_key_window():
    window = KeyCheckWindow()

    if not window.check_existing_key():
        window.show()
        return window, False
    return window, True
