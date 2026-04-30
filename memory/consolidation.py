"""SPEACE Memory — Consolidation Engine.

Mimics hippocampal-neocortical memory consolidation during "sleep" phase.
During consolidation:
1. Recent important episodes are replayed (strengthened)
2. Low-importance memories decay
3. Factual index is rebuilt for faster recall
4. Semantic store redundancies are pruned

BIOLOGICAL PRINCIPLE: During sleep, the hippocampus replays recent
experiences at 10-20× speed (sharp-wave ripples). This drives
neocortical plasticity, transferring episodic memories into stable
semantic/factual knowledge. Without consolidation, memory capacity
would saturate in hours instead of lasting decades.

SPEACE uses consolidation phase (4min every 20min cycle) for this.
"""

import time


class ConsolidationEngine:

    def __init__(self, config: dict):
        cons_cfg = config.get("memory", {}).get("consolidation", {})
        self.replay_ratio = cons_cfg.get("replay_ratio", 0.3)
        self.strengthen_factor = cons_cfg.get("strengthen_factor", 1.2)
        self.prune_below = cons_cfg.get("prune_below_importance", 0.1)

    def run(self, hybrid_memory, semantic_store, working_memory) -> dict:
        """Execute one consolidation cycle."""
        start = time.time()
        stats = {}

        # 1. Replay recent important episodes
        if hybrid_memory.episodic:
            num_replay = max(1, int(len(hybrid_memory.episodic) * self.replay_ratio))
            replayed = hybrid_memory.episodic[:num_replay]
            for event in replayed:
                event.importance = min(1.0, event.importance * self.strengthen_factor)
            stats["replayed"] = num_replay
        else:
            stats["replayed"] = 0

        # 2. Prune low-importance episodes
        before_prune = len(hybrid_memory.episodic)
        hybrid_memory.episodic = [
            e for e in hybrid_memory.episodic
            if e.importance > self.prune_below
        ]
        stats["pruned_episodes"] = before_prune - len(hybrid_memory.episodic)
        hybrid_memory._save_episodic()

        # 3. Clean working memory stale chunks
        if hasattr(working_memory, 'clear_stale'):
            cleared = working_memory.clear_stale()
            stats["cleared_wm_chunks"] = cleared

        # 4. Decay old semantic items
        if hasattr(semantic_store, 'items'):
            for item in semantic_store.items:
                age_hours = (time.time() - item.timestamp) / 3600
                if age_hours > 24:
                    item.importance = max(0.05, item.importance * 0.95)

        # 5. Rebuild factual index (compact keys)
        if hasattr(hybrid_memory, 'factual'):
            dead_keys = [k for k, v in hybrid_memory.factual.items()
                         if v is None or v == ""]
            for k in dead_keys:
                del hybrid_memory.factual[k]
            stats["cleaned_facts"] = len(dead_keys)
            if dead_keys:
                hybrid_memory._save_factual()

        stats["duration_ms"] = round((time.time() - start) * 1000, 1)
        return stats
