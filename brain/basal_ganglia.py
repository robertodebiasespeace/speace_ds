"""SPEACE Brain — Basal Ganglia.

Action selection and inhibition. Chooses one action while inhibiting
competing alternatives — the "winner-takes-all" circuit.

BIOLOGICAL PRINCIPLE: The basal ganglia implement a direct (Go) and
indirect (No-Go) pathway. Go promotes action; No-Go inhibits it.
This opponent process ensures only one action at a time, preventing
costly parallel action conflicts. Energy saved by NOT executing N-1 actions.
"""


class BasalGanglia:

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus

        self.graph.register_node(
            "StriatumActionSelector",
            self._select_action,
            input_types={"candidates": list, "priorities": dict, "context": dict},
            output_types={"selected_action": str, "inhibited": list, "confidence": float},
            metadata={"region": "basal_ganglia", "function": "action_selection"},
        )

    async def _select_action(self, inputs: dict) -> dict:
        candidates = inputs.get("candidates", ["answer"])
        priorities = inputs.get("priorities", {c: 0.5 for c in candidates})

        # Sort by priority (Direct pathway = high priority, Indirect = inhibition)
        ranked = sorted(candidates, key=lambda c: priorities.get(c, 0.5), reverse=True)
        selected = ranked[0] if ranked else "answer"
        inhibited = ranked[1:] if len(ranked) > 1 else []

        # Confidence = ratio between winner and runner-up
        runner_up_priority = priorities.get(inhibited[0], 0) if inhibited else 0
        winner_priority = priorities.get(selected, 0.5)
        confidence = min(1.0, winner_priority / max(0.01, runner_up_priority + winner_priority))

        return {
            "selected_action": selected,
            "inhibited": inhibited,
            "confidence": round(confidence, 3),
        }

    async def select(self, candidates: list[str], priorities: dict[str, float] | None = None) -> dict:
        return await self._select_action({
            "candidates": candidates,
            "priorities": priorities or {},
            "context": {},
        })
