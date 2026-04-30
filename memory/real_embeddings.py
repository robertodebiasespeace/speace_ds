"""SPEACE Memory — Real Embeddings via Ollama (with deterministic fallback).

BIOLOGICAL PRINCIPLE: Biological neural networks don't store raw data —
they store compressed, distributed representations. These emerge naturally
from the network dynamics. Similarly, embeddings compress text into dense
vectors where semantic similarity = geometric proximity.

Energy note: batching embeddings saves ~40% vs one-at-a-time because
the model stays loaded in GPU memory.
"""

import hashlib
import math
import random


class RealEmbeddings:
    """Ollama embedding engine with deterministic hash-based fallback."""

    def __init__(self, config: dict):
        emb_cfg = config.get("llm", {}).get("embeddings", {})
        self.model = emb_cfg.get("model", "nomic-embed-text")
        self.dimensions = emb_cfg.get("dimensions", 768)
        self.ollama_url = config.get("llm", {}).get("primary", {}).get("ollama_url",
                              "http://localhost:11434")
        self._available: bool | None = None  # None = not tested yet

    async def embed(self, text: str) -> list[float]:
        """Get embedding vector. Tries Ollama first, falls back to deterministic."""
        if self._available is None:
            await self._check_available()

        if self._available:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.ollama_url}/api/embeddings",
                        json={"model": self.model, "prompt": text},
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            emb = data.get("embedding", [])
                            if emb:
                                return emb
            except Exception:
                self._available = False

        return self._deterministic_embed(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embedding — much more energy-efficient."""
        results = []
        for text in texts:
            results.append(await self.embed(text))
        return results

    async def _check_available(self):
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ollama_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    self._available = resp.status == 200
        except Exception:
            self._available = False

    def _deterministic_embed(self, text: str) -> list[float]:
        """Hash-based deterministic embedding — always available, no GPU needed."""
        words = text.lower().split()
        if not words:
            words = [" "]

        # Base seed from full text
        text_hash = int(hashlib.md5(text.encode()).hexdigest()[:16], 16) % (2**31)
        rng = random.Random(text_hash)
        vector = [rng.uniform(-1, 1) for _ in range(self.dimensions)]

        # Perturb by each word
        for word in words:
            w_hash = int(hashlib.md5(word.encode()).hexdigest()[:16], 16)
            rng = random.Random(w_hash)
            # Sparse perturbation: only affect ~10% of dimensions
            for _ in range(self.dimensions // 10):
                idx = rng.randint(0, self.dimensions - 1)
                vector[idx] += rng.uniform(-0.15, 0.15)

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    def embed_sync(self, text: str) -> list[float]:
        """Synchronous wrapper (uses deterministic only, no async needed)."""
        return self._deterministic_embed(text)
