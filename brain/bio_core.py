"""SPEACE Brain — Central Bio-Inspired Orchestrator.

Coordinates all 14 brain regions through the adaptive graph and state bus.
Implements sparse activation: only 3-5 regions fire per input cycle.
"""

from __future__ import annotations

import asyncio
import random
from typing import Any

from core.graph_engine import SPEACEAdaptiveGraph
from core.state_bus import StateBus


class BioCore:
    """Central brain orchestrator with dynamic needs and sparse activation."""

    def __init__(self, graph: SPEACEAdaptiveGraph, state_bus: StateBus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.config = config
        self.regions: dict[str, Any] = {}

        # Dynamic needs vector (biological drives)
        self.needs = {
            "energy": 0.80,
            "stability": 0.78,
            "novelty": 0.70,
            "self_improvement": 0.65,
            "coherence": 0.75,
        }

        # Lobe activation levels (0.0 — 1.0)
        self.activation = {
            "frontal": 0.5,
            "temporal": 0.5,
            "parietal": 0.3,
            "occipital": 0.3,
            "cingulate": 0.4,
            "insula": 0.3,
            "thalamus": 0.6,
            "basal_ganglia": 0.4,
            "amygdala": 0.3,
            "hippocampus": 0.5,
            "cerebellum": 0.3,
            "brainstem": 0.5,
            "left_hemisphere": 0.5,
            "right_hemisphere": 0.5,
        }

        # Phase tracking
        self.total_thoughts = 0
        self.emergence_history: list[float] = []
        self.module_usage: dict[str, int] = {k: 0 for k in self.activation}

    def register_region(self, name: str, region_instance: Any):
        self.regions[name] = region_instance

    # ── Sparse Activation Heuristic ──
    # Mimics biological brain: not all regions fire; relevance is computed
    # via keyword/concept association + current needs state.

    REGION_KEYWORDS = {
        "temporal": ["memoria", "ricorda", "memorizza", "passato", "apprendimento", "codice",
                      "remember", "recall", "fact", "memory"],
        "parietal": ["spazio", "quantità", "numeri", "coordinate", "logica", "calcola",
                     "spatial", "number", "math", "calculate"],
        "occipital": ["immagine", "visivo", "pattern", "schema", "disegno",
                      "visual", "pattern", "image", "chart"],
        "frontal": ["piano", "goal", "obiettivo", "decidi", "pianifica", "strategia",
                    "plan", "goal", "strategy", "decide", "execute"],
        "cingulate": ["errore", "conflitto", "correggi", "monitor", "sbagliato",
                      "error", "conflict", "monitor", "correct"],
        "amygdala": ["paura", "rischio", "pericolo", "emotivo", "urgente",
                     "fear", "danger", "risk", "emotional", "urgent"],
        "hippocampus": ["episodio", "esperienza", "passato", "contesto",
                        "episode", "experience", "context", "navigate"],
        "cerebellum": ["automatico", "procedura", "abitudine", "routine",
                       "automate", "procedure", "habit", "routine"],
        "insula": ["corpo", "fame", "dolore", "stato interno", "omeostasi",
                   "body", "pain", "hunger", "homeostasis"],
    }

    def compute_sparse_activation(self, user_input: str) -> list[str]:
        """Return the top 3-5 brain regions relevant to this input."""
        text_lower = user_input.lower()
        scores: dict[str, float] = {}

        for region, keywords in self.REGION_KEYWORDS.items():
            score = 0.0
            for kw in keywords:
                if kw in text_lower:
                    score += 0.25
            # Blend with current needs
            if region == "temporal":
                score += self.needs["stability"] * 0.1
            elif region == "frontal":
                score += self.needs["self_improvement"] * 0.15
            elif region == "amygdala":
                score += (1.0 - self.needs["stability"]) * 0.1
            elif region == "hippocampus":
                score += self.needs["coherence"] * 0.1
            elif region == "insula":
                score += (1.0 - self.needs["energy"]) * 0.1

            scores[region] = min(1.0, score)

        # Always include thalamus (relay) and hemispheres (processing)
        scores["thalamus"] = max(scores.get("thalamus", 0.0), 0.5)
        scores["left_hemisphere"] = max(scores.get("left_hemisphere", 0.0), 0.4)
        scores["right_hemisphere"] = max(scores.get("right_hemisphere", 0.0), 0.4)

        # Sort and take top 5
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        max_regions = self.config.get("cognitive", {}).get("attention", {}).get("max_focus_modules", 5)
        active = [r for r, s in ranked[:max_regions] if s > 0.1]

        # Track usage for pruning
        for r in active:
            self.module_usage[r] = self.module_usage.get(r, 0) + 1

        return active

    def update_activation(self, active_regions: list[str]):
        """Boost activation of used regions, decay others. Hebbian principle."""
        for region in self.activation:
            if region in active_regions:
                self.activation[region] = min(1.0, self.activation[region] + 0.05)
            else:
                self.activation[region] = max(0.1, self.activation[region] - 0.01)

    def adjust_needs(self, metrics: dict):
        """Homeostatic needs adjustment based on cognitive metrics."""
        emergence = metrics.get("emergence", 0.5)
        novelty = metrics.get("novelty", 0.5)
        coherence = metrics.get("coherence", 0.5)

        self.needs["novelty"] = max(0.3, 1.0 - novelty)
        self.needs["coherence"] = max(0.3, 1.0 - coherence)
        self.needs["stability"] = 0.5 + (coherence - 0.5) * 0.5
        self.needs["self_improvement"] = 0.3 + emergence * 0.5
        self.needs["energy"] = max(0.2, self.needs["energy"] - 0.02)

        self.emergence_history.append(emergence)
        if len(self.emergence_history) > 50:
            self.emergence_history = self.emergence_history[-50:]

    def get_prunable_regions(self, min_usage: int = 3) -> list[str]:
        """Identify regions that could be offloaded to save energy."""
        return [r for r, u in self.module_usage.items() if u < min_usage and r in self.activation]

    def status(self) -> dict:
        return {
            "needs": dict(self.needs),
            "activation": dict(self.activation),
            "total_thoughts": self.total_thoughts,
            "active_regions_count": sum(1 for v in self.activation.values() if v > 0.3),
            "emergence_mean": round(sum(self.emergence_history[-10:]) / max(1, len(self.emergence_history[-10:])), 3),
            "graph": self.graph.get_introspection(),
        }
