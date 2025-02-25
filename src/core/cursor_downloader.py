import os
import subprocess
from pathlib import Path
from typing import Optional

import psutil
import requests
from tqdm import tqdm

from src.core.cursor_manager import CursorManager
from src.utils.colorful_logger import ColorfulLogger


class CursorDownloader:
    def __init__(self):
        self.logger = ColorfulLogger(__name__)
        self.cursor_manager = CursorManager()
        self.download_url = "https://downloader.cursor.sh/builds/250103fqxdt5u9z/windows/nsis/x64"
        self.version = "0.44.11"

    def should_download(self) -> bool:
        try:
            current_version = self.cursor_manager.get_version()
            if current_version == self.version:
                self.logger.info(f"Đã cài đặt Cursor v{self.version}")
                return False
            return True
        except Exception:
            return True

    def download(self, output_dir: Optional[str] = None) -> bool:
        if not self.should_download():
            return False

        if output_dir is None:
            output_dir = str(Path.home() / "Downloads")

        output_path = os.path.join(
            output_dir, f"Cursor-Setup-{self.version}.exe")

        try:
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            self.logger.info(f"Bắt đầu tải Cursor v{self.version}")

            with open(output_path, 'wb') as f, tqdm(
                desc="Đang tải",
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    pbar.update(size)

            self.logger.success(f"Đã tải xong: {output_path}")
            return self._install(output_path)

        except requests.RequestException as e:
            self.logger.error(f"Lỗi khi tải: {str(e)}")
            return False

    def _install(self, setup_path: str) -> bool:
        try:
            self.logger.info("Bắt đầu cài đặt Cursor...")

            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if proc.info['name'].lower() == 'cursor.exe':
                        psutil.Process(proc.info['pid']).terminate()
                        self.logger.info(
                            f"Đã tắt Cursor (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            process = subprocess.Popen(
                ['start', '/wait', setup_path],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            try:
                process.wait(timeout=120)
                if process.returncode == 0:
                    self.logger.success("Cài đặt Cursor thành công!")
                    os.remove(setup_path)
                    return True
                else:
                    self.logger.error(
                        f"Cài đặt thất bại với mã lỗi: {process.returncode}")
                    return False
            except subprocess.TimeoutExpired:
                process.kill()
                self.logger.error("Quá thời gian cài đặt")
                return False

        except Exception as e:
            self.logger.error(f"Lỗi trong quá trình cài đặt: {str(e)}")
            return False
