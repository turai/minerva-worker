import json
from typing import Any, Self
from urllib.parse import unquote
import socket

from minerva.constants import CACHE_FILE


class JobCache:
    _instance: Self | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}
        if CACHE_FILE.exists():
            try:
                self._data = json.loads(CACHE_FILE.read_text(encoding="utf8"))
            except Exception:
                self._data = {}

    def _save(self) -> None:
        CACHE_FILE.write_text(json.dumps(self._data), encoding="utf8")

    def list(self) -> list[dict[str, Any]]:
        return list(self._data.values())

    def get(self, job: dict[str, Any]) -> dict[str, Any]:
        key = unquote(job["url"])
        return self._data.get(key) or {}

    def set(self, job: dict[str, Any]) -> None:
        key = unquote(job["url"])
        self._data[key] = {**job, "is_cached": True}
        self._save()

    def remove(self, job: dict[str, Any]) -> None:
        key = unquote(job["url"])
        if key in self._data:
            del self._data[key]
            self._save()


def cache_dns() -> None:
    dns_cache: dict[tuple[str, int], list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int] | tuple[str, int, int, int] | tuple[int, bytes]]]] = {}

    _orig_getaddrinfo = socket.getaddrinfo

    def cached_getaddrinfo(host: str, port: int, *args: Any, **kwargs: Any) -> list:
        key = (host, port)

        if key not in dns_cache:
            dns_cache[key] = _orig_getaddrinfo(host, port, *args, **kwargs)

        return dns_cache[key]

    socket.getaddrinfo = cached_getaddrinfo  # type: ignore


job_cache = JobCache()


__all__ = ["job_cache"]
