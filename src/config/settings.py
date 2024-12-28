import os
import platform
from pathlib import Path


def get_config_path() -> Path:
    system = platform.system()
    if system == "Windows":
        return Path(os.environ["APPDATA"]) / "Cursor" / "User" / "globalStorage" / "storage.json"
    elif system == "Darwin":  # macOS
        username = os.getlogin()
        return Path("/Users") / username / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "storage.json"
    elif system == "Linux":
        return Path.home() / ".config" / "Cursor" / "User" / "globalStorage" / "storage.json"
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")


CURSOR_PATHS = []
system = platform.system()

if system == "Windows":
    CURSOR_PATHS = [
        Path(os.environ["APPDATA"]) / "Cursor",
        Path(os.environ["LOCALAPPDATA"]) / "Programs" / "Cursor",
        Path(os.environ["LOCALAPPDATA"]) / "Cursor",
        Path(os.environ["TEMP"]) / "Cursor",
        Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Cursor",
    ]
elif system == "Darwin":  # macOS
    username = os.getlogin()
    CURSOR_PATHS = [
        Path("/Users") / username / "Library" / "Application Support" / "Cursor",
        Path("/Users") / username / "Applications" / "Cursor",
        Path("/Users") / username / "Library" / "Caches" / "Cursor",
        Path("/Users") / username / "Library" / "Logs" / "Cursor",
        Path("/Users") / username / "Desktop" / "Cursor",
    ]
elif system == "Linux":
    CURSOR_PATHS = [
        Path.home() / ".config" / "Cursor",
        Path.home() / "Cursor",
        Path("/tmp/Cursor"),
        Path.home() / ".local/share/Cursor",
    ]
else:
    raise RuntimeError(f"Unsupported operating system: {system}")
