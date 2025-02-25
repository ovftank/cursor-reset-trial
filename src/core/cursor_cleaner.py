import os
import shutil
import sqlite3
from pathlib import Path

import psutil

from src.utils.colorful_logger import ColorfulLogger


class CursorCleaner:
    def __init__(self):
        self.logger = ColorfulLogger(__name__)
        self._initialize_paths()

    def _initialize_paths(self) -> None:
        appdata = os.getenv("APPDATA", "")
        temp = os.getenv("TEMP", "")
        cursor_appdata = os.path.join(appdata, "Cursor")

        self.state_db_path = os.path.join(
            cursor_appdata, "User", "globalStorage", "state.vscdb")

        self.cache_paths = [
            (temp, "Cursor*"),
            (os.path.join(cursor_appdata, "Cache", "Cache_Data"), "*"),
            (os.path.join(cursor_appdata, "CachedData"), "*"),
            (os.path.join(cursor_appdata, "CachedExtensionVSIXs"), "*"),
            (os.path.join(cursor_appdata, "CachedProfilesData"), "*"),
            (os.path.join(cursor_appdata, "logs"), "*"),
            (os.path.join(cursor_appdata, "User", "History"), "*"),
            (os.path.join(cursor_appdata, "User", "workspaceStorage"), "*"),
            (os.path.join(cursor_appdata, "Backups"), "*"),
            (os.path.join(cursor_appdata, "Service Worker"), "*"),
        ]

    def _is_cursor_running(self) -> bool:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == 'cursor.exe':
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def _kill_cursor_processes(self) -> None:
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'].lower() == 'cursor.exe':
                    psutil.Process(proc.info['pid']).terminate()
                    self.logger.info(
                        f"Đã tắt Cursor (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def _remove_path(self, path: str, pattern: str) -> None:
        try:
            if not os.path.exists(path):
                return

            for item in Path(path).glob(pattern):
                try:
                    if item.is_file():
                        item.unlink(missing_ok=True)
                        self.logger.info(f"Đã xóa {item.name}")
                    elif item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                        self.logger.info(f"Đã xóa {item.name}")
                except OSError as e:
                    self.logger.warning(f"{item.name}: {e}")
        except Exception as e:
            self.logger.error(f"Lỗi: {e}")

    def clear_disk_kv(self) -> bool:
        try:
            if not os.path.exists(self.state_db_path):
                self.logger.warning("Không tìm thấy file database")
                return False

            if self._is_cursor_running():
                self.logger.warning("Đang tắt Cursor...")
                self._kill_cursor_processes()

            conn = sqlite3.connect(self.state_db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM cursorDiskKV")
            conn.commit()

            cursor.close()
            conn.close()

            self.logger.success("Đã xóa dữ liệu từ cursorDiskKV")
            return True

        except sqlite3.Error as e:
            self.logger.error(f"Lỗi SQL: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Lỗi: {e}")
            return False

    def clear_cache(self) -> bool:
        try:
            self.logger.info("Bắt đầu dọn dẹp...")

            self.clear_disk_kv()

            if self._is_cursor_running():
                self.logger.warning("Đang tắt Cursor...")
                self._kill_cursor_processes()

            for path, pattern in self.cache_paths:
                self._remove_path(path, pattern)

            self.logger.success("Hoàn tất!")
            return True
        except Exception as e:
            self.logger.error(f"Lỗi: {e}")
            return False
