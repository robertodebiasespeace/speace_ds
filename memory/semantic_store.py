"""SPEACE Memory — Semantic/Vector Store.

Cosine-similarity semantic search with persistent storage.
Wrapper around ChromaDB for production or flat NumPy index for lightweight use.

BIOLOGICAL PRINCIPLE: Semantic memory in the cortex uses distributed
representations — each concept is a pattern of activity across many neurons.
No single neuron "stores" a concept; it emerges from the ensemble. This is:
- Robust (damage to some neurons doesn't destroy the memory)
- Energy-efficient (reuses the same neurons for multiple memories)
- Generalizing (similar concepts share overlapping patterns)

SPEACE uses vector embeddings (nomic-embed-text, 768d) for the same purpose.
"""

import json
import math
import time
from pathlib import Path
from typing import Any


class MemoryItem:
    def __init__(self, item_id: str, content: str, embedding: list[float],
                 metadata: dict | None = None, importance: float = 0.5):
        self.id = item_id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata or {}
        self.importance = importance
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "importance": self.importance,
            "timestamp": self.timestamp,
        }


class SemanticStore:
    """Flat cosine-similarity vector store. ChromaDB optional upgrade path."""

    def __init__(self, config: dict, embedding_engine=None):
        sem_cfg = config.get("memory", {}).get("semantic", {})
        self.max_items = sem_cfg.get("max_items", 10000)
        self.persist_dir = Path(sem_cfg.get("persist_dir", "data/vector_store"))
        self.embedder = embedding_engine
        self.items: list[MemoryItem] = []
        self.embeddings: list[list[float]] = []
        self._load()

    def add(self, content: str, metadata: dict | None = None, importance: float = 0.5) -> str:
        embedding = self.embedder.embed(content) if self.embedder else self._fallback_embed(content)
        item_id = f"vec-{int(time.time())}-{len(self.items)}"
        item = MemoryItem(item_id, content, embedding, metadata, importance)
        self.items.append(item)
        self.embeddings.append(embedding)

        # Prune if over limit
        if len(self.items) > self.max_items:
            self.items.sort(key=lambda x: x.importance, reverse=True)
            self.items = self.items[:self.max_items]
            self.embeddings = [i.embedding for i in self.items]

        self._save_index()
        return item_id

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self.items:
            return []
        query_emb = self.embedder.embed(query) if self.embedder else self._fallback_embed(query)

        scores = []
        for i, emb in enumerate(self.embeddings):
            sim = self._cosine_similarity(query_emb, emb)
            weighted = sim * self.items[i].importance
            scores.append((weighted, i))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, idx in scores[:top_k]:
            if score > 0.1:
                item = self.items[idx]
                results.append({
                    "id": item.id,
                    "content": item.content,
                    "similarity": round(score, 4),
                    "metadata": item.metadata,
                    "importance": item.importance,
                })
        return results

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _fallback_embed(self, text: str, dims: int = 768) -> list[float]:
        """Deterministic hash-based embedding when no embedder is available."""
        import hashlib
        import random
        words = text.lower().split()
        seed = int(hashlib.md5(text.encode()).hexdigest()[:16], 16) % (2**31)
        rng = random.Random(seed)
        base = [rng.uniform(-1, 1) for _ in range(dims)]
        for w in words:
            w_hash = int(hashlib.md5(w.encode()).hexdigest()[:16], 16)
            rng = random.Random(w_hash)
            for i in range(min(50, dims)):
                base[i] += rng.uniform(-0.1, 0.1)
        norm = math.sqrt(sum(x * x for x in base))
        return [x / norm for x in base] if norm > 0 else base

    def _save_index(self):
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        index = [i.to_dict() for i in self.items]
        with open(self.persist_dir / "index.json", "w") as f:
            json.dump(index, f, indent=2, default=str)

    def _load(self):
        index_file = self.persist_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file) as f:
                    data = json.load(f)
                    for d in data:
                        content = d.get("content", "")
                        # Recompute embedding via fallback if no embedder
                        emb = self._fallback_embed(content) if not self.embedder else []
                        if not emb and self.embedder:
                            emb = []  # Will need lazy embedding on search
                        item = MemoryItem(
                            item_id=d["id"],
                            content=content,
                            embedding=emb,
                            metadata=d.get("metadata", {}),
                            importance=d.get("importance", 0.5),
                        )
                        item.timestamp = d.get("timestamp", time.time())
                        self.items.append(item)
                        if emb:
                            self.embeddings.append(emb)
            except Exception:
                pass
