import base64
import hashlib
import json
import os
import re
import shutil
import sqlite3
import tempfile
import uuid
import winreg
from dataclasses import dataclass
from typing import Dict, Optional

import requests

from src.core.cursor_cleaner import CursorCleaner
from src.utils.colorful_logger import ColorfulLogger


@dataclass
class CursorPaths:
    package_path: str
    main_path: str
    state_path: str
    db_path: str


class CursorManager:
    def __init__(self):
        self.logger = ColorfulLogger(__name__)
        self._paths = self._initialize_paths()
        self._version: Optional[str] = None
        self.cleaner = CursorCleaner()

    def _initialize_paths(self) -> CursorPaths:
        base_path = os.path.join(
            os.getenv("LOCALAPPDATA", ""),
            "Programs",
            "Cursor",
            "resources",
            "app"
        )

        appdata = os.getenv("APPDATA", "")
        cursor_storage = os.path.join(
            appdata, "Cursor", "User", "globalStorage")

        return CursorPaths(
            package_path=os.path.join(base_path, "package.json"),
            main_path=os.path.join(base_path, "out/main.js"),
            state_path=os.path.join(cursor_storage, "state.vscdb"),
            db_path=os.path.join(cursor_storage, "storage.json")
        )

    @property
    def package_path(self) -> str:
        return self._paths.package_path

    @property
    def main_path(self) -> str:
        return self._paths.main_path

    @property
    def state_path(self) -> str:
        return self._paths.state_path

    @property
    def db_path(self) -> str:
        return self._paths.db_path

    def _generate_telemetry_ids(self) -> Dict[str, str]:
        device_id = str(uuid.uuid4())
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()
        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

        return {
            "telemetry.devDeviceId": device_id,
            "telemetry.macMachineId": mac_machine_id,
            "telemetry.machineId": machine_id,
            "telemetry.sqmId": sqm_id,
            "storage.serviceMachineId": device_id,
        }

    def get_version(self) -> str:
        if self._version is None:
            try:
                with open(self.package_path, 'r', encoding='utf-8') as f:
                    self._version = json.load(f)['version']
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Không tìm thấy package.json tại {self.package_path}")
            except json.JSONDecodeError:
                raise json.JSONDecodeError(
                    f"JSON không hợp lệ tại {self.package_path}", doc="", pos=0)
            except KeyError:
                raise KeyError(
                    f"Không tìm thấy trường version trong {self.package_path}")
        return self._version

    def reset_machine_id(self) -> bool:
        try:
            backup_path = f"{self.main_path}.backup"
            if not os.path.exists(backup_path):
                shutil.copy2(self.main_path, backup_path)
                self.logger.success("Đã backup")
            with open(self.main_path, "r", encoding="utf-8") as main_file:
                content = main_file.read()
            patterns = {
                r"async getMachineId\(\)\{return [^??]+\?\?([^}]+)\}":
                    r"async getMachineId(){return \1}",
                r"async getMacMachineId\(\)\{return [^??]+\?\?([^}]+)\}":
                    r"async getMacMachineId(){return \1}",
            }
            for pattern, replacement in patterns.items():
                content = re.sub(pattern, replacement, content)
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            shutil.move(tmp_path, self.main_path)
            self.logger.success("Đã reset ID")
            return True

        except Exception as e:
            if 'tmp_path' in locals():
                os.unlink(tmp_path)
            self.logger.error(f"Lỗi reset ID: {e}")
            return False

    def _update_file_permissions(self, file_path: str, mode: int) -> None:
        if os.path.exists(file_path):
            try:
                current_mode = os.stat(file_path).st_mode & 0o777
                if current_mode != mode:
                    os.chmod(file_path, mode)
                    action = "mở quyền ghi" if mode == 0o666 else "đặt chế độ chỉ đọc"
                    self.logger.info(
                        f"Đã {action} cho {os.path.basename(file_path)}")
            except PermissionError:
                action = "mở quyền ghi" if mode == 0o666 else "đặt chế độ chỉ đọc"
                self.logger.error(
                    f"Không thể {action} cho {os.path.basename(file_path)}")
                raise

    def _update_state_database(self, new_ids: Dict[str, str]) -> None:
        if self._version != "0.44.11":
            conn = sqlite3.connect(self.state_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ItemTable (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            for key, value in new_ids.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO ItemTable (key, value)
                    VALUES (?, ?)
                """, (key, value))
                self.logger.info(f"Cập nhật {key} trong state DB")

            conn.commit()
            conn.close()

    def _update_storage_database(self, new_ids: Dict[str, str]) -> None:
        storage_data = {}
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    storage_data = json.load(f)

                    update_keys = [
                        "telemetry.devDeviceId",
                        "telemetry.macMachineId",
                        "telemetry.machineId",
                        "telemetry.sqmId",
                        "storage.serviceMachineId"
                    ]

                    for key in update_keys:
                        if key in new_ids:
                            storage_data[key] = new_ids[key]
                            self.logger.info(
                                f"Cập nhật {key} trong storage DB")

            except json.JSONDecodeError:
                self.logger.warning("File storage.json không hợp lệ, tạo mới")
                storage_data = new_ids
        else:
            storage_data = new_ids

        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(storage_data, f, indent=4)

    def update_state_db(self) -> bool:
        new_ids = self._generate_telemetry_ids()
        try:
            self.logger.info("Đang cập nhật state DB...")

            for file_path in [self.state_path, self.db_path]:
                self._update_file_permissions(file_path, 0o666)

            self._update_state_database(new_ids)
            self.logger.success("Đã cập nhật state DB")

            self.logger.info("Đang cập nhật storage DB...")
            self._update_storage_database(new_ids)
            self.logger.success("Đã cập nhật storage DB")

            for file_path in [self.db_path]:
                self._update_file_permissions(file_path, 0o444)

            return True

        except PermissionError as e:
            self.logger.error(f"Lỗi quyền truy cập: {e}")
            self.logger.info(
                "Thử chạy với quyền admin để có thể cập nhật files")
            return False
        except Exception as e:
            self.logger.error(f"Lỗi cập nhật DB: {e}")
            return False

    def update_machine_guid(self) -> bool:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SOFTWARE\\Microsoft\\Cryptography",
                0,
                winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
            )
            new_guid = str(uuid.uuid4())
            winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
            winreg.CloseKey(key)
            self.logger.success("Đã cập nhật MachineGuid")
            return True
        except PermissionError:
            self.logger.error("Cần quyền admin để cập nhật MachineGuid")
            return False
        except Exception as e:
            self.logger.error(f"Lỗi cập nhật MachineGuid: {e}")
            return False

    def reset_cursor(self) -> bool:
        self.logger.info("Bắt đầu reset Cursor...")

        if self.cleaner._is_cursor_running():
            self.logger.info("Đang tắt Cursor...")
            self.cleaner._kill_cursor_processes()

        self.logger.info("Đang xóa cache...")
        if not self.cleaner.clear_cache():
            self.logger.warning("Có lỗi khi xóa cache, nhưng vẫn tiếp tục reset")

        if not self.reset_machine_id():
            self.logger.error("Lỗi reset ID")
            return False
        if not self.update_state_db():
            self.logger.error("Lỗi cập nhật DB")
            return False
        if not self.update_machine_guid():
            self.logger.error("Lỗi cập nhật GUID")
            return False
        self.logger.success("Reset thành công!")
        return True

    def reset_account(self) -> bool:
        try:
            if self.cleaner._is_cursor_running():
                self.logger.info("Đang tắt Cursor...")
                self.cleaner._kill_cursor_processes()

            self.logger.info("Đang reset thông số tài khoản Cursor...")

            conn = sqlite3.connect(self.state_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT value FROM ItemTable
                WHERE key = 'cursorAuth/accessToken'
            """)

            result = cursor.fetchone()
            conn.close()

            if not result:
                self.logger.error("Không tìm thấy access token")
                return False

            access_token = result[0]

            try:
                payload = access_token.split('.')[1]
                padding = 4 - (len(payload) % 4)
                if padding != 4:
                    payload += '=' * padding

                decoded = base64.b64decode(payload)
                token_data = json.loads(decoded)

                user_id = token_data['sub'].split(
                    '|')[1] if '|' in token_data['sub'] else token_data['sub']
            except Exception as e:
                self.logger.error(f"Lỗi parse token: {str(e)}")
                return False

            headers = {
                'accept': '*/*',
                'accept-language': 'en,vi;q=0.9',
                'content-type': 'application/json',
                'authorization': f'Bearer {access_token}',
                'origin': 'https://www.cursor.com',
                'referer': 'https://www.cursor.com/settings',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin'
            }

            cookies = {
                'WorkosCursorSessionToken': f'{user_id}::{access_token}'
            }

            response = requests.post(
                'https://www.cursor.com/api/dashboard/delete-account',
                headers=headers,
                cookies=cookies,
                json={},
                timeout=10
            )

            if response.status_code == 200:
                self.logger.success("Đã reset thông số tài khoản thành công!")
                return True
            else:
                self.logger.error(
                    f"Lỗi khi reset thông số tài khoản: HTTP {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Lỗi reset thông số tài khoản: {str(e)}")
            self.logger.error(f"Chi tiết lỗi: {repr(e)}")
            return False
