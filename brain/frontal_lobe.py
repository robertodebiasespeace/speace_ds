"""SPEACE Brain — Frontal Lobe.

Executive functions: planning, decision-making, action selection, inhibition.
Contains ExecutiveController + BrocaLanguagePlan nodes.

BIOLOGICAL PRINCIPLE: The frontal lobe is the last to activate and the
most energy-expensive — used only when deliberation is needed.
Automatic/habitual responses bypass it via cerebellum/basal ganglia.
"""

from __future__ import annotations

import time


class FrontalLobe:
    """Executive controller and language planning."""

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.cfg = config.get("brain_regions", {}).get("frontal", {})
        self.goals: list[dict] = []
        self.plans: list[dict] = []

        self.graph.register_node(
            "ExecutiveController",
            self._executive_process,
            input_types={"pattern": str, "recalled": dict, "bilateral_synthesis": str},
            output_types={"action": str, "priority": float, "risk": float, "rationale": str},
            metadata={"region": "frontal", "function": "executive_control"},
        )
        self.graph.register_node(
            "BrocaLanguagePlan",
            self._broca_process,
            input_types={"action": str, "style": str, "context": dict},
            output_types={"verbal_strategy": str, "fluency": float, "tone": str},
            metadata={"region": "frontal", "function": "language_production"},
        )
        self.graph.connect("ExecutiveController", "BrocaLanguagePlan",
                           {"action": "action", "rationale": "context"})

    async def _executive_process(self, inputs: dict) -> dict:
        """Select the action based on recognized pattern and context."""
        pattern = inputs.get("pattern", "general_reasoning")
        recalled = inputs.get("recalled", {})

        action_map = {
            "factual_memory_request": ("recall_fact", 0.9, 0.05),
            "self_improvement_request": ("self_improve", 0.7, 0.3),
            "planning_request": ("plan", 0.8, 0.15),
            "general_reasoning": ("answer", 0.6, 0.1),
        }
        action, priority, risk = action_map.get(pattern, ("answer", 0.5, 0.2))

        # Adjust priority if facts were recalled successfully
        if recalled and recalled.get("fact_text"):
            priority = min(1.0, priority + 0.15)
            risk = max(0.0, risk - 0.05)

        return {
            "action": action,
            "priority": priority,
            "risk": risk,
            "rationale": f"Azione '{action}' selezionata per pattern '{pattern}'",
        }

    async def _broca_process(self, inputs: dict) -> dict:
        """Plan language production: style, tone, fluency."""
        action = inputs.get("action", "answer")
        style_map = {
            "plan": "tecnico-operativo",
            "self_improve": "analitico-riflessivo",
            "recall_fact": "informativo-diretto",
            "answer": "conversazionale",
        }
        tone_map = {
            "plan": "determined",
            "self_improve": "hopeful",
            "recall_fact": "neutral",
            "answer": "friendly",
        }
        return {
            "verbal_strategy": style_map.get(action, "conversazionale"),
            "fluency": 0.75,
            "tone": tone_map.get(action, "neutral"),
        }

    async def process(self, pattern: str, recalled: dict, bilateral_synthesis: str) -> dict:
        """Run executive → Broca chain."""
        start = time.time()
        exec_result = await self._executive_process({
            "pattern": pattern,
            "recalled": recalled,
            "bilateral_synthesis": bilateral_synthesis,
        })
        broca_result = await self._broca_process({
            "action": exec_result["action"],
            "style": "default",
            "context": {"rationale": exec_result["rationale"]},
        })

        return {
            "action": exec_result["action"],
            "priority": exec_result["priority"],
            "risk": exec_result["risk"],
            "rationale": exec_result["rationale"],
            "verbal_style": broca_result["verbal_strategy"],
            "tone": broca_result["tone"],
            "latency_ms": (time.time() - start) * 1000,
        }
