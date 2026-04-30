"""SPEACE Memory — Reconsolidation Mechanism.

When a memory is recalled, it enters a labile state and can be updated,
strengthened, or modified before being re-stored. This prevents memory
ossification and allows continuous learning without full re-encoding.

BIOLOGICAL PRINCIPLE: Every time you recall a memory, it becomes temporarily
unstable (reconsolidation window ~4-6 hours in biology). During this window,
the memory trace can be:
- Strengthened (repeated recall = better retention)
- Updated (new context = richer memory)
- Weakened (recall without reinforcement = extinction)

This is why memories evolve over time instead of being static snapshots.
SPEACE implements a short reconsolidation window per recall event.
"""

import time


class ReconsolidationManager:

    def __init__(self, window_seconds: float = 300.0):  # 5 min window
        self.window = window_seconds
        self.labile: dict[str, dict] = {}  # memory_key → {content, recalled_at, updates}

    def mark_recalled(self, memory_key: str, content: str):
        """Open the reconsolidation window for this memory."""
        self.labile[memory_key] = {
            "content": content,
            "recalled_at": time.time(),
            "update_count": 0,
            "strength_boost": 0.0,
        }

    def update(self, memory_key: str, new_content: str):
        """Modify a memory while it's labile (within reconsolidation window)."""
        if memory_key not in self.labile:
            return False
        entry = self.labile[memory_key]
        if time.time() - entry["recalled_at"] > self.window:
            del self.labile[memory_key]
            return False
        entry["content"] = new_content
        entry["update_count"] += 1
        entry["strength_boost"] = min(0.3, entry["update_count"] * 0.05)
        return True

    def finalize(self, memory_key: str, memory_system) -> dict | None:
        """Close reconsolidation window. Return updated memory with strength boost."""
        if memory_key not in self.labile:
            return None
        entry = self.labile.pop(memory_key)

        # Strengthen the memory in storage
        boost = entry["strength_boost"]
        updated_content = entry["content"]

        if hasattr(memory_system, 'memorize_fact'):
            existing = memory_system.recall_fact(memory_key)
            if existing:
                memory_system.memorize_fact(memory_key, updated_content)

        return {
            "key": memory_key,
            "content": updated_content,
            "boost": round(boost, 3),
            "updates": entry["update_count"],
        }

    def clean_expired(self):
        """Remove entries past reconsolidation window (memory stabilized)."""
        now = time.time()
        expired = [k for k, v in self.labile.items()
                    if now - v["recalled_at"] > self.window]
        for k in expired:
            del self.labile[k]
        return len(expired)

    def labile_count(self) -> int:
        self.clean_expired()
        return len(self.labile)
