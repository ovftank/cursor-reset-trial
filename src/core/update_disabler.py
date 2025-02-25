import os
import shutil
from pathlib import Path

import psutil

from src.utils.colorful_logger import ColorfulLogger


class CursorAutoUpdateDisabler:
    def __init__(self) -> None:
        self.local_app_data = Path(os.environ.get('LOCALAPPDATA', ''))
        self.updater_path = self.local_app_data / 'cursor-updater'
        self.logger = ColorfulLogger(__name__)

    def _kill_cursor_processes(self) -> bool:
        try:
            killed = False
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == 'cursor.exe':
                    try:
                        proc.kill()
                        killed = True
                        self.logger.success('Đã kill cursor.exe')
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        self.logger.warning('Không thể kill cursor.exe')
            if not killed:
                self.logger.info('Không tìm thấy cursor.exe')
            return True
        except Exception as e:
            self.logger.error(f'Lỗi: {e}')
            return False

    def _safely_remove_directory(self) -> bool:
        try:
            if self.updater_path.is_dir():
                shutil.rmtree(self.updater_path)
                self.logger.success('Đã xóa updater')
            return True
        except OSError as e:
            self.logger.error(f'Lỗi: {e}')
            return False

    def _create_blocking_file(self) -> bool:
        try:
            self.updater_path.touch()
            self.logger.success('Đã chặn update')
            return True
        except OSError as e:
            self.logger.error(f'Lỗi: {e}')
            return False

    def disable_auto_update(self) -> bool:
        if self.updater_path.is_file():
            self.logger.info('Đã disable auto-update từ trước')
            return True

        if not self._kill_cursor_processes():
            self.logger.error('Không kill được cursor.exe')
            return False

        if not self.updater_path.parent.exists():
            self.logger.error('Thư mục không tồn tại')
            return False

        if not self._safely_remove_directory():
            self.logger.warning('Xóa updater thất bại')
            return False

        success = self._create_blocking_file()
        if success:
            self.logger.success('Hoàn tất')
        else:
            self.logger.error('Thất bại')

        return success
