"""Thread-safe JSON-file cache, atomic writes (tmp file + rename)."""
from __future__ import annotations
import json
import os
import threading
import time

_lock = threading.Lock()
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _path(name: str) -> str:
    return os.path.join(_DATA_DIR, name)


def write(payload: dict, name: str = "cache.json") -> None:
    with _lock:
        os.makedirs(_DATA_DIR, exist_ok=True)
        payload = dict(payload)
        payload["updated_at"] = time.time()
        tmp = _path(name) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        os.replace(tmp, _path(name))


def read(name: str = "cache.json") -> dict | None:
    try:
        with open(_path(name), "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
