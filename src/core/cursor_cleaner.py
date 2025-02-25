import os
import shutil
from pathlib import Path

from src.utils.colorful_logger import ColorfulLogger


class CursorCleaner:
    def __init__(self):
        self.logger = ColorfulLogger(__name__)
        self._initialize_paths()

    def _initialize_paths(self) -> None:
        appdata = os.getenv("APPDATA", "")
        temp = os.getenv("TEMP", "")
        cursor_appdata = os.path.join(appdata, "Cursor")

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
        ]

    def _remove_path(self, path: str, pattern: str) -> None:
        try:
            if not os.path.exists(path):
                return

            for item in Path(path).glob(pattern):
                if item.is_file():
                    item.unlink()
                    self.logger.info(f"Đã xóa file: {item}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    self.logger.info(f"Đã xóa thư mục: {item}")
        except Exception as e:
            self.logger.error(f"Lỗi khi xóa {path}: {e}")

    def clear_cache(self) -> bool:
        try:
            self.logger.info("Bắt đầu xóa cache...")
            for path, pattern in self.cache_paths:
                self._remove_path(path, pattern)
            self.logger.success("Đã xóa cache thành công!")
            return True
        except Exception as e:
            self.logger.error(f"Lỗi khi xóa cache: {e}")
            return False
