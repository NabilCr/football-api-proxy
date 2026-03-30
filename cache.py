import time
from typing import Any


class TTLCache:
    """Simple in-memory cache with per-entry TTL (seconds)."""

    def __init__(self):
        self._store: dict[str, dict] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() - entry["ts"] > entry["ttl"]:
            del self._store[key]
            return None
        return entry["data"]

    def set(self, key: str, data: Any, ttl: int) -> None:
        self._store[key] = {"data": data, "ts": time.time(), "ttl": ttl}

    def clear(self) -> None:
        self._store.clear()


cache = TTLCache()
