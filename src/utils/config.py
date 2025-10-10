import os
from typing import Optional

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def get_env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def get_env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def get_env_str(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


def get_env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default
