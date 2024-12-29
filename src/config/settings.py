import os
from pathlib import Path


def get_config_path() -> Path:
    return Path(os.environ["APPDATA"]) / "Cursor" / "User" / "globalStorage" / "storage.json"


CURSOR_PATHS = [
    os.path.expandvars(r"%APPDATA%\\Cursor"),
    os.path.expandvars(r"%LOCALAPPDATA%\\Programs\\Cursor"),
    os.path.expandvars(r"%LOCALAPPDATA%\\Cursor"),
    os.path.expandvars(r"%TEMP%\\Cursor"),
    os.path.expandvars(
        r"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Cursor")
]