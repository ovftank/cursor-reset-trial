import ctypes
import hashlib
import json
import os
import secrets
import shutil
import sys
import uuid
from pathlib import Path
from typing import List

import psutil
from PyQt5.QtCore import QByteArray, Qt, QThread, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QMessageBox,
                             QPushButton, QTextEdit, QVBoxLayout, QWidget)


def get_config_path() -> Path:
    return Path(os.environ["APPDATA"]) / "Cursor" / "User" / "globalStorage" / "storage.json"


def generate_machine_id() -> str:
    prefix = "auth0|user_"
    sequence = f"{secrets.randbelow(100):02d}"
    charset = "0123456789ABCDEFGHJKLMNPQRSTVWXYZ"
    unique_id = ''.join(secrets.choice(charset) for _ in range(23))
    full_id = prefix + sequence + unique_id
    return full_id.encode().hex()


def generate_mac_machine_id() -> str:
    data = secrets.token_bytes(32)
    return hashlib.sha256(data).hexdigest()


def generate_dev_device_id() -> str:
    return str(uuid.uuid4())


def save_config() -> None:
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        os.chmod(config_path, 0o666)
        with open(config_path) as f:
            existing_config = json.load(f)
    else:
        existing_config = {}

    existing_config.update({
        "telemetry.sqmId": generate_mac_machine_id(),
        "telemetry.macMachineId": generate_mac_machine_id(),
        "telemetry.machineId": generate_machine_id(),
        "telemetry.devDeviceId": generate_dev_device_id()
    })

    with open(config_path, 'w') as f:
        json.dump(existing_config, f, indent=4)

    os.chmod(config_path, 0o444)


class ResetThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

    def secure_remove(self, file_path: str, passes: int = 3) -> None:
        try:
            long_path = f"\\\\?\\{file_path}"
            if os.path.isfile(long_path):
                with open(long_path, 'ba+', buffering=0) as f:
                    length = f.tell()
                    for _ in range(passes):
                        f.seek(0)
                        f.write(os.urandom(length))
                os.remove(long_path)
                self.progress_signal.emit(f"Đã xóa an toàn: {file_path}")
        except Exception as e:
            self.progress_signal.emit(f"Lỗi khi xóa {file_path}: {e}")

    def remove_directory(self, directory_path: str) -> None:
        try:
            long_path = f"\\\\?\\{directory_path}"
            if os.path.exists(long_path):
                shutil.rmtree(long_path)
                self.progress_signal.emit(
                    f"Đã xóa thư mục: {directory_path}")
        except Exception as e:
            self.progress_signal.emit(
                f"Lỗi khi xóa thư mục {directory_path}: {e}")

    def reset_cursor_trial(self) -> None:
        cursor_paths: List[str] = [
            os.path.expandvars(r"%APPDATA%\\Cursor"),
            os.path.expandvars(r"%LOCALAPPDATA%\\Programs\\Cursor"),
            os.path.expandvars(r"%LOCALAPPDATA%\\Cursor"),
            os.path.expandvars(r"%TEMP%\\Cursor"),
            os.path.expandvars(
                r"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Cursor")
        ]

        for path in cursor_paths:
            if os.path.isdir(path):
                self.remove_directory(path)
            elif os.path.isfile(path):
                self.secure_remove(path)

    def run(self):
        self.reset_cursor_trial()
        try:
            save_config()
            self.progress_signal.emit(
                "Cập nhật file cấu hình thành công!")
            self.progress_signal.emit(
                "Vui lòng khởi động lại Cursor để áp dụng thay đổi")
        except Exception as e:
            self.progress_signal.emit(f"Lỗi khi tạo cấu hình mới: {e}")
        self.finished_signal.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cursor Reset Trial")
        self.setFixedSize(600, 400)
        self.setup_ui()
        self.setup_style()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.title_label = QLabel("CURSOR RESET TRIAL")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFixedHeight(50)
        layout.addWidget(self.title_label)

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(50, 0, 50, 0)
        main_layout.setSpacing(25)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(150)
        self.log_text.setMaximumHeight(150)
        main_layout.addWidget(self.log_text)

        self.close_process_button = QPushButton("CLOSE ALL CURSOR PROCESSES")
        self.close_process_button.setFixedHeight(45)
        self.close_process_button.setCursor(Qt.PointingHandCursor)
        self.close_process_button.clicked.connect(self.close_cursor_processes)
        main_layout.addWidget(self.close_process_button)

        self.reset_button = QPushButton("RESET TRIAL")
        self.reset_button.setFixedHeight(45)
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.clicked.connect(self.start_reset)
        self.reset_button.hide()
        main_layout.addWidget(self.reset_button)

        layout.addWidget(main_container)

        self.copyright_label = QLabel("Made by ovftank")
        self.copyright_label.setAlignment(Qt.AlignCenter)
        self.copyright_label.setFixedHeight(20)
        self.copyright_label.setCursor(Qt.PointingHandCursor)
        self.copyright_label.mousePressEvent = self.open_github
        layout.addWidget(self.copyright_label)

    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
            }
            QLabel {
                color: #00ff95;
                font-size: 24px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
            }
            QTextEdit {
                background-color: rgba(26, 26, 46, 0.8);
                color: #00ff95;
                border: 2px solid #00ff95;
                border-radius: 10px;
                padding: 15px;
                font-family: 'Consolas';
                font-size: 13px;
                selection-background-color: #00ff95;
                selection-color: #1a1a2e;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff95, stop:1 #00b8ff);
                color: #1a1a2e;
                padding: 12px;
                border: none;
                border-radius: 22px;
                font-size: 16px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00b8ff, stop:1 #00ff95);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #008c67, stop:1 #0081b3);
                padding-left: 14px;
            }
            QPushButton:disabled {
                background: #2c3e50;
                color: #516170;
            }
            QLabel#copyright_label {
                color: #00ff95;
                font-size: 12px;
                font-weight: normal;
                padding: 5px;
                background: transparent;
            }
            QLabel#copyright_label:hover {
                color: #00b8ff;
                text-decoration: underline;
            }
            QPushButton#close_process_button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4757, stop:1 #ff6b81);
                color: white;
            }
            QPushButton#close_process_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6b81, stop:1 #ff4757);
            }
            QPushButton#close_process_button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff1f30, stop:1 #ff4757);
            }

            QPushButton#reset_button {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff95, stop:0.5 #00b8ff, stop:1 #7d2ae8);
                color: white;
            }
            QPushButton#reset_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7d2ae8, stop:0.5 #00b8ff, stop:1 #00ff95);
            }
            QPushButton#reset_button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a1ea8, stop:0.5 #0081b3, stop:1 #008c67);
            }
        """)
        self.copyright_label.setObjectName("copyright_label")
        self.close_process_button.setObjectName("close_process_button")
        self.reset_button.setObjectName("reset_button")

    def is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    def start_reset(self):
        if not self.is_admin():
            QMessageBox.warning(
                self, "Lỗi", "Ứng dụng này yêu cầu quyền quản trị viên.")
            return

        self.reset_button.setEnabled(False)
        self.log_text.clear()
        self.log_text.append("Đang reset Cursor trial...")

        self.reset_thread = ResetThread()
        self.reset_thread.progress_signal.connect(self.update_log)
        self.reset_thread.finished_signal.connect(self.reset_finished)
        self.reset_thread.start()

    def update_log(self, message: str):
        self.log_text.append(message)

    def reset_finished(self):
        self.log_text.append("Reset hoàn tất thành công.")
        self.reset_button.setEnabled(True)

    def open_github(self, _):
        QDesktopServices.openUrl(QUrl("https://github.com/ovftank"))

    def close_cursor_processes(self):
        try:
            closed_count = 0
            for proc in psutil.process_iter(['name']):
                if 'cursor' in proc.info['name'].lower():
                    proc.kill()
                    closed_count += 1

            if closed_count > 0:
                self.log_text.append(
                    f"Đã đóng {closed_count} tiến trình Cursor")
                self.reset_button.show()
                self.close_process_button.hide()
            else:
                self.log_text.append(
                    "Không tìm thấy tiến trình Cursor nào đang chạy")
        except Exception as e:
            self.log_text.append(f"Lỗi khi đóng tiến trình: {str(e)}")


def main():
    app = QApplication(sys.argv)
    image_base64 = b''
    icon = icon_from_base64(image_base64)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec_())


def icon_from_base64(base64):
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray.fromBase64(base64))
    icon = QIcon(pixmap)
    return icon


if __name__ == "__main__":
    main()
