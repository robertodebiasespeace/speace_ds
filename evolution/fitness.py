"""SPEACE Evolution — Multi-Component Fitness Function.

Evaluates system "health" across 5 weighted dimensions to gate evolution.

BIOLOGICAL PRINCIPLE: Fitness in nature is multi-dimensional (survival,
reproduction, energy efficiency, adaptability). A single scalar "fitness"
hides trade-offs. SPEACE uses weighted multi-component fitness so the
mutation system can understand WHY something is fit/unfit.
"""

import time


class FitnessEvaluator:

    WEIGHTS = {
        "alignment": 0.30,       # Alignment with Rigene objectives / constitution
        "performance": 0.25,     # Task success, response quality
        "stability": 0.20,       # System uptime, error-free cycles
        "efficiency": 0.15,      # Energy per operation, memory usage
        "emergence": 0.10,       # Novelty, coherence, self-generated goals
    }

    def __init__(self, state_bus):
        self.bus = state_bus
        self.scores: dict[str, float] = {k: 0.5 for k in self.WEIGHTS}

    def evaluate(self, metrics: dict, system_status: dict) -> dict:
        """Compute multi-dimensional fitness from current system state."""
        # Alignment score
        dna = self.bus.get("digital_dna", {})
        mutations = len(dna.get("mutations", [])) if isinstance(dna, dict) else 0
        self.scores["alignment"] = min(1.0, 0.5 + mutations * 0.02)

        # Performance score
        self.scores["performance"] = metrics.get("emergence", 0.5)

        # Stability score
        error_count = system_status.get("error_count", 0)
        self.scores["stability"] = max(0.1, 1.0 - error_count * 0.05)

        # Efficiency score
        internal = self.bus.get("internal_state", {})
        ram_pct = internal.get("status", {}).get("ram_percent", 50) if isinstance(internal, dict) else 50
        self.scores["efficiency"] = max(0.1, 1.0 - (ram_pct / 100) * 0.7)

        # Emergence score
        self.scores["emergence"] = metrics.get("emergence", 0.5)

        # Weighted composite
        composite = sum(self.scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)

        result = {
            "composite": round(composite, 4),
            "components": {k: round(self.scores[k], 3) for k in self.WEIGHTS},
            "weights": dict(self.WEIGHTS),
            "timestamp": time.time(),
        }

        self.bus.set("fitness", result)
        return result

    def is_healthy(self, threshold: float = 0.5) -> bool:
        composite = sum(self.scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)
        return composite >= threshold
