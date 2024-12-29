import ctypes
import sys
from pathlib import Path
import platform

import psutil
from PyQt5.QtCore import Qt, QThread, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import (QDialog, QLabel, QMainWindow, QMessageBox,
                             QPushButton, QTabWidget, QTextEdit, QVBoxLayout,
                             QWidget, QProgressDialog)
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

from src.config.settings import CURSOR_PATHS
from src.config.translations import TRANSLATIONS
from src.ui.styles import MAIN_STYLE
from src.utils.file_handler import remove_directory, save_config, secure_remove


class ResetThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, current_language):
        super().__init__()
        self.current_language = current_language

    def run(self):
        trans = TRANSLATIONS[self.current_language]
        for path in CURSOR_PATHS:
            if secure_remove(path):
                self.progress_signal.emit(
                    trans['securely_removed'].format(path))
            elif remove_directory(path):
                self.progress_signal.emit(
                    trans['removed_directory'].format(path))
        try:
            save_config()
            self.progress_signal.emit(trans['config_updated'])
            self.progress_signal.emit(trans['restart_required'])
        except Exception as e:
            self.progress_signal.emit(trans['error_config'].format(str(e)))

        self.finished_signal.emit()


class CallbackHandler(BaseHTTPRequestHandler):
    callback_signal = None

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))
            if self.callback_signal:
                self.callback_signal.emit(data)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))


class ServerThread(QThread):
    def __init__(self, callback_signal):
        super().__init__()
        CallbackHandler.callback_signal = callback_signal
        self.server = None

    def run(self):
        try:
            self.server = HTTPServer(('localhost', 8765), CallbackHandler)
            self.server.serve_forever()
        except Exception as e:
            print(f"Server error: {str(e)}")

    def quit(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        super().quit()


class MainWindow(QMainWindow):
    callback_received = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.current_language = 'en'
        self.setWindowTitle("CURSOR RESET TRIAL")
        self.setFixedSize(700, 500)

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundle_dir = Path(sys._MEIPASS)
        else:
            bundle_dir = Path(__file__).parent.parent.parent

        if platform.system() == "Darwin":
            icon_path = bundle_dir / "images" / "icon.icns"
        else:
            icon_path = bundle_dir / "images" / "icon.ico"

        self.setWindowIcon(QIcon(str(icon_path)))

        self.setup_ui()
        self.setup_style()

        self.callback_received.connect(self.handle_callback)
        self.server_thread = ServerThread(self.callback_received)
        self.server_thread.start()

        # Create a progress dialog for showing status
        self.progress_dialog = None

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        self.language_button = QPushButton("VI")
        self.language_button.setFixedSize(70, 35)
        self.language_button.setCursor(Qt.PointingHandCursor)
        self.language_button.clicked.connect(self.toggle_language)
        self.language_button.setObjectName("language_button")

        top_layout = QVBoxLayout()
        language_container = QWidget()
        language_layout = QVBoxLayout(language_container)
        language_layout.setAlignment(Qt.AlignRight)
        language_layout.addWidget(self.language_button)
        language_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(language_container)

        layout.addLayout(top_layout)

        self.title_label = QLabel("CURSOR RESET TRIAL")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFixedHeight(50)
        layout.addWidget(self.title_label)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.local_reset_tab = self.create_local_reset_tab()
        self.account_reset_tab = self.create_account_reset_tab()

        self.tab_widget.addTab(self.local_reset_tab, "Local Reset")
        self.tab_widget.addTab(self.account_reset_tab, "Account Reset")

        self.copyright_label = QLabel("Made by ovftank")
        self.copyright_label.setAlignment(Qt.AlignCenter)
        self.copyright_label.setFixedHeight(25)
        self.copyright_label.setCursor(Qt.PointingHandCursor)
        self.copyright_label.mousePressEvent = self.open_github
        layout.addWidget(self.copyright_label)

    def create_local_reset_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 10, 40, 10)
        layout.setSpacing(20)

        layout.addStretch(1)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(192)
        self.log_text.setMaximumHeight(192)
        layout.addWidget(self.log_text)

        self.close_process_button = QPushButton("CLOSE ALL CURSOR PROCESSES")
        self.close_process_button.setFixedHeight(45)
        self.close_process_button.setMinimumWidth(200)
        self.close_process_button.setCursor(Qt.PointingHandCursor)
        self.close_process_button.clicked.connect(self.close_cursor_processes)
        layout.addWidget(self.close_process_button)

        self.reset_button = QPushButton("RESET TRIAL")
        self.reset_button.setFixedHeight(45)
        self.reset_button.setMinimumWidth(200)
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.clicked.connect(self.start_reset)
        self.reset_button.hide()
        layout.addWidget(self.reset_button)

        layout.addStretch(1)

        return tab

    def create_account_reset_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 10, 40, 10)
        layout.setSpacing(7)

        layout.addStretch(1)

        self.help_button = QPushButton("Instructions")
        self.help_button.setFixedHeight(45)
        self.help_button.setMinimumWidth(200)
        self.help_button.setCursor(Qt.PointingHandCursor)
        self.help_button.clicked.connect(self.show_instructions)
        layout.addWidget(self.help_button)

        self.tampermonkey_button = QPushButton(
            "Install Tampermonkey for Chrome")
        self.tampermonkey_button.setFixedHeight(45)
        self.tampermonkey_button.setMinimumWidth(200)
        self.tampermonkey_button.setCursor(Qt.PointingHandCursor)
        self.tampermonkey_button.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo")))
        layout.addWidget(self.tampermonkey_button)

        self.violentmonkey_button = QPushButton(
            "Install Violentmonkey for Chrome")
        self.violentmonkey_button.setFixedHeight(45)
        self.violentmonkey_button.setMinimumWidth(200)
        self.violentmonkey_button.setCursor(Qt.PointingHandCursor)
        self.violentmonkey_button.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://chromewebstore.google.com/detail/violentmonkey/jinjaccalgkegednnccohejagnlnfdag")))
        layout.addWidget(self.violentmonkey_button)

        self.script_button = QPushButton("Install Script from Greasyfork")
        self.script_button.setFixedHeight(45)
        self.script_button.setMinimumWidth(200)
        self.script_button.setCursor(Qt.PointingHandCursor)
        self.script_button.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://update.greasyfork.org/scripts/521244/Cursor%20Reset%20Trial.user.js")))
        layout.addWidget(self.script_button)

        self.reset_account_button = QPushButton("RESET ACCOUNT TRIAL")
        self.reset_account_button.setFixedHeight(45)
        self.reset_account_button.setMinimumWidth(200)
        self.reset_account_button.setCursor(Qt.PointingHandCursor)
        self.reset_account_button.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://cursor.com/settings?reset=true")))
        layout.addWidget(self.reset_account_button)

        layout.addStretch(1)

        return tab

    def setup_style(self):
        self.setStyleSheet(MAIN_STYLE)
        self.copyright_label.setObjectName("copyright_label")
        self.close_process_button.setObjectName("close_process_button")
        self.reset_button.setObjectName("reset_button")

        self.tab_widget.setObjectName("tab_widget")
        self.local_reset_tab.setObjectName("tab")
        self.account_reset_tab.setObjectName("tab")

    def is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    def start_reset(self):
        if not self.is_admin():
            QMessageBox.warning(
                self, "Error", TRANSLATIONS[self.current_language]['admin_error'])
            return

        self.reset_button.setEnabled(False)
        self.log_text.clear()
        self.log_text.append(TRANSLATIONS[self.current_language]['resetting'])

        self.reset_thread = ResetThread(self.current_language)
        self.reset_thread.progress_signal.connect(self.update_log)
        self.reset_thread.finished_signal.connect(self.reset_finished)
        self.reset_thread.start()

    def update_log(self, message: str):
        self.log_text.append(message)

    def reset_finished(self):
        self.log_text.append(
            TRANSLATIONS[self.current_language]['reset_complete'])
        self.reset_button.setEnabled(True)

    def open_github(self, _):
        QDesktopServices.openUrl(
            QUrl("https://github.com/ovftank/cursor-reset-trial"))

    def close_cursor_processes(self):
        try:
            closed_count = 0
            current_pid = psutil.Process().pid

            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['pid'] == current_pid:
                    continue

                if 'cursor' in proc.info['name'].lower():
                    proc.kill()
                    closed_count += 1

            if closed_count > 0:
                self.log_text.append(
                    TRANSLATIONS[self.current_language]['processes_closed'].format(closed_count))
                self.reset_button.show()
                self.close_process_button.hide()
            else:
                self.log_text.append(
                    TRANSLATIONS[self.current_language]['no_processes'])
                self.reset_button.show()
                self.close_process_button.hide()
        except Exception as e:
            self.log_text.append(
                TRANSLATIONS[self.current_language]['process_error'].format(str(e)))

    def show_instructions(self):
        help_dialog = QDialog(self)
        trans = TRANSLATIONS[self.current_language]
        help_dialog.setWindowTitle(trans['help_title'])
        help_dialog.setFixedSize(500, 400)
        help_dialog.setWindowFlags(
            help_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(help_dialog)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(trans['help_content'])
        layout.addWidget(text)

        close_button = QPushButton(trans['close'])
        close_button.clicked.connect(help_dialog.close)
        layout.addWidget(close_button)

        help_dialog.setStyleSheet(MAIN_STYLE)
        help_dialog.exec_()

    def toggle_language(self):
        self.current_language = 'vi' if self.current_language == 'en' else 'en'
        self.language_button.setText(
            "EN" if self.current_language == 'vi' else "VI")
        self.update_translations()

    def update_translations(self):
        trans = TRANSLATIONS[self.current_language]

        self.setWindowTitle(trans['window_title'])
        self.title_label.setText(trans['title_label'])
        self.tab_widget.setTabText(0, trans['local_reset_tab'])
        self.tab_widget.setTabText(1, trans['account_reset_tab'])
        self.close_process_button.setText(trans['close_processes'])
        self.reset_button.setText(trans['reset_trial'])
        self.help_button.setText(trans['instructions'])
        self.tampermonkey_button.setText(trans['install_tampermonkey'])
        self.violentmonkey_button.setText(trans['install_violentmonkey'])
        self.script_button.setText(trans['install_script'])
        self.reset_account_button.setText(trans['reset_account'])

    def show_status_dialog(self, title, message):
        """Show a non-blocking status dialog"""
        if not self.progress_dialog:
            self.progress_dialog = QProgressDialog(self)
            self.progress_dialog.setWindowTitle(title)
            self.progress_dialog.setLabelText(message)
            self.progress_dialog.setCancelButton(None)
            self.progress_dialog.setRange(0, 0)  # Infinite progress bar
            self.progress_dialog.setWindowModality(Qt.WindowModal)
        else:
            self.progress_dialog.setLabelText(message)

        self.progress_dialog.show()

    def hide_status_dialog(self):
        """Hide the status dialog"""
        if self.progress_dialog:
            self.progress_dialog.hide()

    @pyqtSlot(dict)
    def handle_callback(self, data):
        """Handle callbacks received from the web"""
        try:
            action = data.get('action')
            if action == 'reset_loading':
                self.reset_account_button.setEnabled(False)
                self.show_status_dialog(
                    TRANSLATIONS[self.current_language]['window_title'],
                    TRANSLATIONS[self.current_language]['web_reset_loading']
                )
            elif action == 'reset_complete':
                self.reset_account_button.setEnabled(True)
                self.hide_status_dialog()
                QMessageBox.information(
                    self,
                    TRANSLATIONS[self.current_language]['window_title'],
                    TRANSLATIONS[self.current_language]['web_reset_complete']
                )
            elif action == 'reset_failed':
                error = data.get('error', 'Unknown error')
                self.reset_account_button.setEnabled(True)
                self.hide_status_dialog()
                QMessageBox.warning(
                    self,
                    TRANSLATIONS[self.current_language]['window_title'],
                    TRANSLATIONS[self.current_language]['web_reset_failed'].format(error)
                )
        except Exception as e:
            self.reset_account_button.setEnabled(True)
            self.hide_status_dialog()
            QMessageBox.critical(
                self,
                TRANSLATIONS[self.current_language]['window_title'],
                TRANSLATIONS[self.current_language]['callback_error'].format(str(e))
            )

    def closeEvent(self, event):
        """Handle application closing"""
        try:
            # Hide any open dialogs first
            if self.progress_dialog:
                self.progress_dialog.hide()

            # Stop the server thread properly
            if hasattr(self, 'server_thread'):
                # Create a new HTTPServer instance just to send a shutdown request
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect(('localhost', 8765))
                    sock.close()
                except Exception:
                    pass  # Server might already be closed

                self.server_thread.quit()
                self.server_thread.wait(1000)  # Wait up to 1 second

                # Force terminate if still running
                if self.server_thread.isRunning():
                    self.server_thread.terminate()
                    self.server_thread.wait()

            event.accept()
        except Exception as e:
            print(f"Error during closing: {str(e)}")
            event.accept()  # Always close even if there's an error
