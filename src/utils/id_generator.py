import hashlib
import secrets
import uuid


def generate_machine_id() -> str:
    prefix = "auth0|user_"
    sequence = f"{secrets.randbelow(100):02d}"
    charset = "0123456789ABCDEFGHJKLMNPQRSTVWXYZ"
    unique_id = ''.join(secrets.choice(charset) for _ in range(23))
    full_id = prefix + sequence + unique_id
    return full_id.encode().hex()


def generate_mac_machine_id() -> str:
    data = secrets.token_bytes(32)
    return hashlib.sha256(data).hexdigest()


def generate_dev_device_id() -> str:
    return str(uuid.uuid4())
