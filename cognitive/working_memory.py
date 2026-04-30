"""SPEACE Cognitive — Working Memory with Dynamic Chunking.

Maintains a limited-capacity active buffer (Miller's Law: 7±2 chunks)
that holds currently relevant information for manipulation.

BIOLOGICAL PRINCIPLE: Working memory in the prefrontal cortex relies on
persistent neural firing (not synaptic storage). This means:
- Very fast read/write (no weight updates needed)
- Automatically clears when activity stops (no cleanup cost)
- Energy cost proportional to items held × time held

SPEACE implements this as a bounded ring buffer with automatic decay.
"""

import time
from collections import deque


class WorkingMemory:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        mem_cfg = config.get("memory", {}).get("working", {})
        self.chunk_size = mem_cfg.get("chunk_size", 7)
        self.max_turns = mem_cfg.get("max_turns", 20)

        self._buffer: deque[dict] = deque(maxlen=self.max_turns)
        self._active_chunks: dict[str, dict] = {}  # keyed by chunk id
        self._current_turn: dict = {}

    def start_turn(self, user_input: str):
        self._current_turn = {
            "user_input": user_input,
            "timestamp": time.time(),
            "chunks_held": len(self._active_chunks),
        }

    def hold(self, key: str, content: str, ttl_seconds: float = 120.0):
        """Keep an item in active buffer. Auto-evicts after TTL."""
        self._active_chunks[key] = {
            "content": content,
            "created": time.time(),
            "ttl": ttl_seconds,
            "accessed": 1,
        }

    def access(self, key: str) -> str | None:
        """Retrieve item, refreshing its access count."""
        chunk = self._active_chunks.get(key)
        if chunk:
            if time.time() - chunk["created"] > chunk["ttl"]:
                del self._active_chunks[key]
                return None
            chunk["accessed"] += 1
            self._strengthen(key)
            return chunk["content"]
        return None

    def _strengthen(self, key: str):
        """Increase TTL for frequently accessed items (attention boost)."""
        chunk = self._active_chunks.get(key)
        if chunk:
            chunk["ttl"] = min(300.0, chunk["ttl"] * 1.15)

    def clear_stale(self):
        """Remove expired chunks. Called during consolidation phase."""
        now = time.time()
        expired = [
            k for k, v in self._active_chunks.items()
            if now - v["created"] > v["ttl"]
        ]
        for k in expired:
            del self._active_chunks[k]
        return len(expired)

    def compress_to_chunks(self, long_text: str) -> list[str]:
        """Break long text into ~7-chunk-sized pieces (Miller chunking)."""
        sentences = [s.strip() for s in long_text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        if len(sentences) <= self.chunk_size:
            return [long_text]
        chunks = []
        for i in range(0, len(sentences), self.chunk_size):
            chunks.append(". ".join(sentences[i:i + self.chunk_size]) + ".")
        return chunks

    def end_turn(self, assistant_response: str):
        """Commit turn to buffer."""
        self._current_turn["assistant_response"] = assistant_response
        self._current_turn["duration_ms"] = (time.time() - self._current_turn["timestamp"]) * 1000
        self._buffer.append(self._current_turn)
        self.bus.set("working_memory", self.snapshot())
        self._current_turn = {}

    def recent(self, n: int | None = None) -> list[dict]:
        n = n or self.max_turns
        return list(self._buffer)[-n:]

    def active_chunks(self) -> dict[str, str]:
        return {k: v["content"] for k, v in self._active_chunks.items()}

    def snapshot(self) -> dict:
        return {
            "buffer_size": len(self._buffer),
            "active_chunks": len(self._active_chunks),
            "active_keys": list(self._active_chunks.keys()),
            "recent_turns": len(self._buffer),
            "oldest_turn_age_s": round(time.time() - self._buffer[0]["timestamp"], 1) if self._buffer else 0,
        }
