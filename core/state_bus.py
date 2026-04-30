"""SPEACE Core — Shared State Bus for inter-module communication."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path


class StateBus:
    """Thread-safe in-memory state with optional persistence.

    All brain modules read/write through this bus, ensuring a single
    source of truth accessible to monitoring, safety, and introspection.
    """

    def __init__(self, persist_path: str | None = None):
        self._lock = threading.RLock()
        self._state: dict = {}
        self._history: list[dict] = []
        self._max_history = 50
        self._persist_path = Path(persist_path) if persist_path else None
        if self._persist_path and self._persist_path.exists():
            self._load()

    def get(self, key: str, default=None):
        with self._lock:
            return self._state.get(key, default)

    def set(self, key: str, value):
        with self._lock:
            old = self._state.get(key)
            self._state[key] = value
            self._history.append({
                "timestamp": time.time(),
                "key": key,
                "old": str(old)[:200],
                "new": str(value)[:200],
            })
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

    def update(self, d: dict):
        with self._lock:
            for k, v in d.items():
                self._state[k] = v

    def snapshot(self) -> dict:
        with self._lock:
            return dict(self._state)

    def recent_changes(self, n: int = 20) -> list[dict]:
        with self._lock:
            return list(self._history[-n:])

    def changed_keys_between(self, state_a: dict, state_b: dict) -> set[str]:
        """Return keys that differ between two state snapshots."""
        keys = set(state_a.keys()) | set(state_b.keys())
        return {k for k in keys if state_a.get(k) != state_b.get(k)}

    def save(self):
        if not self._persist_path:
            return
        with self._lock:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._persist_path, "w") as f:
                json.dump(self._state, f, indent=2, default=str)

    def _load(self):
        try:
            with open(self._persist_path) as f:
                self._state = json.load(f)
        except Exception:
            pass
