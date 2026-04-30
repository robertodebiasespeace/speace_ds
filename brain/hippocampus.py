"""SPEACE Brain — Hippocampus.

Memory encoding, consolidation, and context-rich episodic storage.
Converts active neural patterns into stable long-term memory traces.

BIOLOGICAL PRINCIPLE: The hippocampus performs "pattern separation" (making
similar experiences distinct) and "pattern completion" (reconstructing a
full memory from a partial cue). Replay during sleep/consolidation
strengthens important memories and weakens noise — extremely energy-efficient
because it reuses existing circuits instead of storing redundant copies.
"""

import time


class Hippocampus:

    def __init__(self, graph, state_bus, memory_system, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.memory = memory_system
        self.index: dict[str, list[str]] = {}  # context_tag → memory_ids

        self.graph.register_node(
            "HippocampalEncoding",
            self._encode_event,
            input_types={"content": str, "context": dict, "importance": float},
            output_types={"memory_id": str, "tags": list, "encoded": bool},
            metadata={"region": "hippocampus", "function": "memory_encoding"},
        )

    async def _encode_event(self, inputs: dict) -> dict:
        content = inputs.get("content", "")
        context = inputs.get("context", {})
        importance = inputs.get("importance", 0.5)

        tags = []
        # Auto-tagging
        text_lower = content.lower()
        if any(w in text_lower for w in ["memoria", "memory", "ricorda", "recall"]):
            tags.append("memory_operation")
        if any(w in text_lower for w in ["piano", "plan", "goal", "obiettivo"]):
            tags.append("planning")
        if any(w in text_lower for w in ["errore", "error", "bug", "problema"]):
            tags.append("error")
        if any(w in text_lower for w in ["speace", "brain", "cervello"]):
            tags.append("self_referential")
        if not tags:
            tags.append("general")

        memory_id = f"ep-{int(time.time())}-{len(self.index)}"

        # Store in memory
        if hasattr(self.memory, 'add_event'):
            self.memory.add_event(
                event_type="hippocampal",
                content=content,
                data={"context": context, "tags": tags, "importance": importance},
                importance=importance,
            )

        # Index by tags
        for tag in tags:
            if tag not in self.index:
                self.index[tag] = []
            self.index[tag].append(memory_id)

        self.bus.set(f"hippocampus_last", {"memory_id": memory_id, "tags": tags})

        return {"memory_id": memory_id, "tags": tags, "encoded": True}

    async def encode(self, content: str, context: dict = {}, importance: float = 0.5) -> dict:
        return await self._encode_event({
            "content": content,
            "context": context,
            "importance": importance,
        })

    def contextual_recall(self, tags: list[str]) -> list[str]:
        """Retrieve memory IDs matching given context tags."""
        matches = set()
        for tag in tags:
            if tag in self.index:
                matches.update(self.index[tag])
        return list(matches)
