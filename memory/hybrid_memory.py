"""SPEACE Memory — Hybrid Memory System.

Three-tier memory with automatic persistence:
1. Working: sliding window of recent turns
2. Factual: deterministic key-value with fuzzy recall (no embeddings needed)
3. Episodic: timestamped events with importance scoring

BIOLOGICAL PRINCIPLE: The brain has multiple memory systems with different
energy profiles. Factual/semantic memory (cortical) is cheap to store but
slow to form. Episodic memory (hippocampal) is fast to encode but requires
active consolidation. Working memory (prefrontal) is the most expensive
per item — hence the strict 7±2 capacity limit.

SPEACE mirrors this: facts are cheap JSON key-values, episodes are
importance-sorted JSONL that gets pruned, and working memory is a tight
ring buffer that auto-decays.
"""

import json
import re
import time
from collections import deque
from pathlib import Path
from typing import Any


class EpisodicEvent:
    def __init__(self, event_type: str, content: str, data: dict, importance: float = 0.5):
        self.event_type = event_type
        self.content = content
        self.data = data
        self.importance = importance
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "type": self.event_type,
            "content": self.content,
            "data": self.data,
            "importance": self.importance,
            "timestamp": self.timestamp,
            "iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.timestamp)),
        }


class HybridMemory:
    """Three-tier memory: working + factual + episodic."""

    def __init__(self, config: dict):
        mem_cfg = config.get("memory", {})
        self.factual: dict[str, Any] = {}
        self.episodic: list[EpisodicEvent] = []
        self.working: deque[dict] = deque(maxlen=mem_cfg.get("working", {}).get("max_turns", 20))

        self.max_episodes = mem_cfg.get("episodic", {}).get("max_events", 500)
        self.fuzzy_threshold = mem_cfg.get("factual", {}).get("fuzzy_match_threshold", 0.6)
        self.factual_path = Path(mem_cfg.get("factual", {}).get("persist_file", "data/factual_memory.json"))
        self.episodic_path = Path(mem_cfg.get("episodic", {}).get("persist_file", "data/episodic_memory.jsonl"))

        self._load()

    # ── Factual Memory (Deterministic, No LLM) ──

    def memorize_fact(self, key: str, value: Any):
        self.factual[key.lower()] = value
        self._save_factual()

    def recall_fact(self, key: str) -> str | None:
        # Exact match
        key_lower = key.lower().strip()
        if key_lower in self.factual:
            return str(self.factual[key_lower])
        # Substring match
        for k, v in self.factual.items():
            if key_lower in k or k in key_lower:
                return str(v)
        return None

    def get_all_facts(self) -> dict:
        return dict(self.factual)

    # ── Episodic Memory ──

    def add_event(self, event_type: str, content: str, data: dict = {},
                   importance: float = 0.5):
        event = EpisodicEvent(event_type, content, data, importance)
        self.episodic.append(event)
        self.episodic.sort(key=lambda e: e.importance, reverse=True)
        if len(self.episodic) > self.max_episodes:
            self.episodic = self.episodic[:self.max_episodes]
        self._save_episodic()

    def search_episodes(self, query: str, top_k: int = 5) -> list[EpisodicEvent]:
        terms = set(query.lower().split())
        scored = []
        for event in self.episodic:
            content_terms = set(event.content.lower().split())
            overlap = len(terms & content_terms)
            if overlap > 0:
                score = overlap * event.importance
                scored.append((score, event))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:top_k]]

    # ── Working Memory ──

    def add_turn(self, user_input: str, assistant_response: str):
        self.working.append({
            "user": user_input,
            "assistant": assistant_response,
            "timestamp": time.time(),
        })

    def recent_turns(self, n: int = 5) -> list[dict]:
        return list(self.working)[-n:]

    # ── Context Assembly ──

    def context_block(self, query: str) -> dict:
        """Assemble memory context for downstream processing."""
        facts = self.recall_fact(query) or ""
        episodes = self.search_episodes(query, top_k=3)
        recent = self.recent_turns(5)

        return {
            "factual_context": facts,
            "relevant_episodes": [e.to_dict() for e in episodes],
            "recent_turns": recent,
            "total_facts": len(self.factual),
            "total_episodes": len(self.episodic),
        }

    # ── Persistence ──

    def _save_factual(self):
        self.factual_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.factual_path, "w") as f:
            json.dump(self.factual, f, indent=2, default=str)

    def _save_episodic(self):
        self.episodic_path.parent.mkdir(parents=True, exist_ok=True)
        recent = self.episodic[:self.max_episodes]
        with open(self.episodic_path, "w") as f:
            for event in recent:
                f.write(json.dumps(event.to_dict(), default=str) + "\n")

    def _load(self):
        if self.factual_path.exists():
            try:
                with open(self.factual_path) as f:
                    self.factual = json.load(f)
            except Exception:
                pass
        if self.episodic_path.exists():
            try:
                with open(self.episodic_path) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            d = json.loads(line)
                            self.episodic.append(EpisodicEvent(
                                event_type=d.get("type", ""),
                                content=d.get("content", ""),
                                data=d.get("data", {}),
                                importance=d.get("importance", 0.5),
                            ))
            except Exception:
                pass

    def clear_old_episodes(self, max_age_hours: float = 48.0):
        now = time.time()
        cutoff = now - max_age_hours * 3600
        self.episodic = [e for e in self.episodic if e.timestamp > cutoff]
        self._save_episodic()
