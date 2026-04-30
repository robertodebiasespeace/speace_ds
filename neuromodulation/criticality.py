"""SPEACE Neuromodulation — Criticality Controller.

Monitors and maintains self-organized criticality (SOC) — the sweet spot
between rigid order and incoherent chaos where information processing
is optimal.

BIOLOGICAL PRINCIPLE: The brain operates at a second-order phase transition
between order and chaos. At this "critical point":
- Information transmission is maximized
- Dynamic range is widest
- Avalanches of neural activity follow power-law distributions
- Metastability enables rapid state switching

Too ordered = epileptic silence, can't respond. Too chaotic = seizure, noise.
Criticality = optimal information processing per watt.

Reference: Beggs & Plenz (2003), "Neuronal Avalanches in Neocortical Circuits."
"""

import math
from collections import deque


class CriticalityController:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        crit_cfg = config.get("criticality", {})
        self.target = crit_cfg.get("target_branching_ratio", 1.0)
        self.lower_bound = crit_cfg.get("lower_bound", 0.6)
        self.upper_bound = crit_cfg.get("upper_bound", 1.4)
        self.intervention_gain = crit_cfg.get("intervention_gain", 0.1)

        self.branching_history: deque[float] = deque(maxlen=30)
        self.cascade_sizes: deque[int] = deque(maxlen=50)
        self.zone = "UNKNOWN"
        self.order_score = 0.5
        self.chaos_score = 0.5

    def record_cascade(self, size: int, max_size: int = 14):
        """Record an activation cascade. Monitors branching ratio."""
        self.cascade_sizes.append(size)

        # Branching ratio: how many modules fire from 1 activation?
        if len(self.cascade_sizes) >= 5:
            ratio = sum(self.cascade_sizes) / max(1, len(self.cascade_sizes))
            self.branching_history.append(ratio)

    def compute_scores(self, coherence: float, novelty: float) -> dict:
        """Compute order/chaos from cognitive metrics."""
        self.order_score = coherence  # High coherence = ordered
        self.chaos_score = novelty  # High novelty = chaotic

        # Branching ratio from recent cascades
        avg_branching = 1.0
        if len(self.branching_history) >= 5:
            avg_branching = sum(self.branching_history) / len(self.branching_history)

        # Criticality zone
        if avg_branching < self.lower_bound:
            zone = "SUB-CRITICAL (rigid)"
            suggestion = "Aumentare temperatura, novelty, exploration"
        elif avg_branching > self.upper_bound:
            zone = "SUPER-CRITICAL (chaotic)"
            suggestion = "Aumentare inibizione, ridurre temperature, pruning"
        elif self.lower_bound + 0.1 <= avg_branching <= self.upper_bound - 0.1:
            zone = "CRITICAL (optimal)"
            suggestion = "Mantenere equilibrio corrente"
        else:
            zone = "NEAR-CRITICAL"
            suggestion = "Piccole correzioni"

        # Intervention
        delta = self.target - avg_branching
        intervention = delta * self.intervention_gain

        self.zone = zone

        state = {
            "zone": zone,
            "branching_ratio": round(avg_branching, 3),
            "order_score": round(self.order_score, 3),
            "chaos_score": round(self.chaos_score, 3),
            "suggestion": suggestion,
            "intervention": round(intervention, 3),
            "target": self.target,
        }
        self.bus.set("criticality", state)
        return state

    def get_zone(self) -> str:
        return self.zone

    def is_critical(self) -> bool:
        return "CRITICAL" in self.zone

    def recommend_temperature_shift(self) -> float:
        """How much to shift LLM temperature toward criticality."""
        if "SUB-CRITICAL" in self.zone:
            return 0.1  # Heat up
        elif "SUPER-CRITICAL" in self.zone:
            return -0.1  # Cool down
        return 0.0
