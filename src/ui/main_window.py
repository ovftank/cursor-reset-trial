import ctypes
import sys
from pathlib import Path

import psutil
from PyQt5.QtCore import Qt, QThread, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QLabel, QMainWindow,
                             QMessageBox, QPushButton, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)

from src.config.settings import CURSOR_PATHS
from src.config.translations import TRANSLATIONS
from src.ui.styles import MAIN_STYLE
from src.utils.block_update import (block_cursor_updates,
                                    download_and_install_cursor,
                                    get_cursor_version)
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


class InstallCursorThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, current_language):
        super().__init__()
        self.current_language = current_language

    def run(self):
        trans = TRANSLATIONS[self.current_language]
        try:
            success = download_and_install_cursor(
                progress_callback=self.progress_signal.emit,
                translations=trans
            )
            self.finished_signal.emit(success)
        except Exception as e:
            self.progress_signal.emit(str(e))
            self.finished_signal.emit(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_language = 'en'
        self.setWindowTitle("CURSOR RESET TRIAL")
        self.setFixedSize(700, 500)

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundle_dir = Path(sys._MEIPASS)
        else:
            bundle_dir = Path(__file__).parent.parent.parent

        icon_path = bundle_dir / "images" / "icon.ico"
        self.setWindowIcon(QIcon(str(icon_path)))

        self.setup_ui()
        self.setup_style()

        block_cursor_updates()
        self.check_cursor_version()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        trans = TRANSLATIONS[self.current_language]

        top_layout = QVBoxLayout()
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setAlignment(Qt.AlignRight)

        self.install_cursor_button = QPushButton(trans['install_cursor'])
        self.install_cursor_button.setFixedHeight(35)
        self.install_cursor_button.setCursor(Qt.PointingHandCursor)
        self.install_cursor_button.clicked.connect(self.install_cursor)
        self.install_cursor_button.hide()
        buttons_layout.addWidget(self.install_cursor_button)

        self.language_button = QPushButton(trans['language_button_en'])
        self.language_button.setFixedSize(70, 35)
        self.language_button.setCursor(Qt.PointingHandCursor)
        self.language_button.clicked.connect(self.toggle_language)
        self.language_button.setObjectName("language_button")
        buttons_layout.addWidget(self.language_button)

        buttons_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(buttons_container)

        layout.addLayout(top_layout)

        self.title_label = QLabel(trans['title_label'])
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFixedHeight(50)
        layout.addWidget(self.title_label)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.local_reset_tab = self.create_local_reset_tab()
        self.account_reset_tab = self.create_account_reset_tab()

        self.tab_widget.addTab(self.local_reset_tab, "Local Reset")
        self.tab_widget.addTab(self.account_reset_tab, "Account Reset")

        self.copyright_label = QLabel(trans['copyright_text'])
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

        trans = TRANSLATIONS[self.current_language]

        self.close_process_button = QPushButton(trans['close_processes'])
        self.close_process_button.setFixedHeight(45)
        self.close_process_button.setMinimumWidth(200)
        self.close_process_button.setCursor(Qt.PointingHandCursor)
        self.close_process_button.clicked.connect(self.close_cursor_processes)
        layout.addWidget(self.close_process_button)

        self.reset_button = QPushButton(trans['reset_trial'])
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

        trans = TRANSLATIONS[self.current_language]

        self.help_button = QPushButton(trans['instructions'])
        self.help_button.setFixedHeight(45)
        self.help_button.setMinimumWidth(200)
        self.help_button.setCursor(Qt.PointingHandCursor)
        self.help_button.clicked.connect(self.show_instructions)
        layout.addWidget(self.help_button)

        self.tampermonkey_button = QPushButton(trans['install_tampermonkey'])
        self.tampermonkey_button.setFixedHeight(45)
        self.tampermonkey_button.setMinimumWidth(200)
        self.tampermonkey_button.setCursor(Qt.PointingHandCursor)
        self.tampermonkey_button.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(trans['tampermonkey_url'])))
        layout.addWidget(self.tampermonkey_button)

        self.violentmonkey_button = QPushButton(trans['install_violentmonkey'])
        self.violentmonkey_button.setFixedHeight(45)
        self.violentmonkey_button.setMinimumWidth(200)
        self.violentmonkey_button.setCursor(Qt.PointingHandCursor)
        self.violentmonkey_button.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(trans['violentmonkey_url'])))
        layout.addWidget(self.violentmonkey_button)

        self.script_button = QPushButton(trans['install_script'])
        self.script_button.setFixedHeight(45)
        self.script_button.setMinimumWidth(200)
        self.script_button.setCursor(Qt.PointingHandCursor)
        self.script_button.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(trans['script_url'])))
        layout.addWidget(self.script_button)

        self.reset_account_button = QPushButton(trans['reset_account'])
        self.reset_account_button.setFixedHeight(45)
        self.reset_account_button.setMinimumWidth(200)
        self.reset_account_button.setCursor(Qt.PointingHandCursor)
        self.reset_account_button.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(trans['settings_url'])))
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
        trans = TRANSLATIONS[self.current_language]
        QDesktopServices.openUrl(QUrl(trans['telegram_url']))

    def close_cursor_processes(self):
        try:
            closed_count = 0
            current_pid = psutil.Process().pid

            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['pid'] == current_pid:
                    continue

                if proc.info['name'].lower() == 'cursor.exe':
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
        trans = TRANSLATIONS[self.current_language]
        self.language_button.setText(
            trans[f'language_button_{self.current_language}'])
        self.update_translations()

    def update_translations(self):
        trans = TRANSLATIONS[self.current_language]

        current_title = self.windowTitle()
        if " - Cursor " in current_title:
            version = current_title.split(" - Cursor ")[-1]
            self.setWindowTitle(f"{trans['window_title']} - Cursor {version}")
        else:
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
        self.install_cursor_button.setText(trans['install_cursor'])

    def check_cursor_version(self):
        trans = TRANSLATIONS[self.current_language]
        version_info = get_cursor_version()

        if version_info:
            version = version_info['version']
            self.setWindowTitle(f"{trans['window_title']} - Cursor {version}")

            if version != "0.44.11":
                self.install_cursor_button.show()
                QMessageBox.warning(
                    self,
                    trans['version_mismatch_title'],
                    trans['version_mismatch_message']
                )
            else:
                self.install_cursor_button.hide()
        else:
            self.setWindowTitle(
                f"{trans['window_title']} - {trans['version_error']}")
            self.install_cursor_button.show()

    def install_cursor(self):
        trans = TRANSLATIONS[self.current_language]
        self.install_cursor_button.setEnabled(False)
        self.close_process_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.help_button.setEnabled(False)
        self.tampermonkey_button.setEnabled(False)
        self.violentmonkey_button.setEnabled(False)
        self.script_button.setEnabled(False)
        self.reset_account_button.setEnabled(False)
        self.language_button.setEnabled(False)

        self.log_text.append(trans['installing'])

        self.install_thread = InstallCursorThread(self.current_language)
        self.install_thread.progress_signal.connect(self.log_text.append)
        self.install_thread.finished_signal.connect(self.install_finished)
        self.install_thread.start()

    def install_finished(self, success):
        trans = TRANSLATIONS[self.current_language]
        version_info = get_cursor_version()
        if version_info:
            version = version_info['version']
            self.setWindowTitle(f"{trans['window_title']} - Cursor {version}")
        if success:
            self.install_cursor_button.hide()
        else:
            self.log_text.append(trans['install_failed'])

        self.install_cursor_button.setEnabled(True)
        self.close_process_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.help_button.setEnabled(True)
        self.tampermonkey_button.setEnabled(True)
        self.violentmonkey_button.setEnabled(True)
        self.script_button.setEnabled(True)
        self.reset_account_button.setEnabled(True)
        self.language_button.setEnabled(True)
