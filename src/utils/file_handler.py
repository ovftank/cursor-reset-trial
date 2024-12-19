import json
import os
import shutil
from typing import Any, Dict

from src.config.settings import get_config_path
from src.utils.id_generator import (generate_dev_device_id,
                                    generate_mac_machine_id,
                                    generate_machine_id)


def secure_remove(file_path: str, passes: int = 3) -> bool:
    try:
        long_path = f"\\\\?\\{file_path}"
        if os.path.isfile(long_path):
            with open(long_path, 'ba+', buffering=0) as f:
                length = f.tell()
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(length))
            os.remove(long_path)
            return True
    except Exception:
        return False


def remove_directory(directory_path: str) -> bool:
    try:
        long_path = f"\\\\?\\{directory_path}"
        if os.path.exists(long_path):
            shutil.rmtree(long_path)
            return True
    except Exception:
        return False
    return False


def save_config() -> None:
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        os.chmod(config_path, 0o666)
        with open(config_path) as f:
            existing_config = json.load(f)
    else:
        existing_config = {}

    new_config: Dict[str, Any] = {
        "telemetry.sqmId": generate_mac_machine_id(),
        "telemetry.macMachineId": generate_mac_machine_id(),
        "telemetry.machineId": generate_machine_id(),
        "telemetry.devDeviceId": generate_dev_device_id()
    }

    existing_config.update(new_config)

    with open(config_path, 'w') as f:
        json.dump(existing_config, f, indent=4)

    os.chmod(config_path, 0o444)
