"""SPEACE Monitoring — Cognitive Metrics Suite.

Tracks: novelty, coherence, adaptation speed, memory continuity,
and self-generated goals to compute an overall emergence score.

BIOLOGICAL PRINCIPLE: The brain doesn't compute these metrics explicitly,
but they emerge from the dynamics. SPEACE makes them explicit for:
- Introspection (the system knows its own cognitive state)
- Criticality control (needs novelty & coherence as inputs)
- Fitness evaluation (emergence is a fitness component)
- Dashboard display (human-readable system health)
"""

import time
from collections import deque


class SPEACEMetrics:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        mon_cfg = config.get("monitoring", {}).get("metrics", {})
        self.history_window = mon_cfg.get("history_window", 5)
        self.weights = mon_cfg.get("emergence_weights", {
            "novelty": 0.20, "coherence": 0.25, "adaptation": 0.15,
            "memory_continuity": 0.20, "self_generated_goals": 0.20,
        })

        self.output_history: deque[str] = deque(maxlen=self.history_window)
        self.state_history: list[dict] = []
        self.goal_history: deque[str] = deque(maxlen=20)

    def record_output(self, output: str):
        self.output_history.append(output)

    def record_state(self, state: dict):
        self.state_history.append(state)
        if len(self.state_history) > 50:
            self.state_history = self.state_history[-50:]

    # ── Individual Metrics ──

    def calculate_novelty(self) -> float:
        """Jaccard distance of word sets between current and recent outputs."""
        if len(self.output_history) < 2:
            return 0.5

        current_words = set(self.output_history[-1].lower().split())
        past_words = set()
        for out in list(self.output_history)[:-1]:
            past_words.update(out.lower().split())

        union = len(current_words | past_words)
        intersection = len(current_words & past_words)
        if union == 0:
            return 0.5

        novelty = 1.0 - (intersection / union)
        return min(1.0, max(0.0, novelty))

    def calculate_coherence(self) -> float:
        """Sentence count + connector presence + output length scoring."""
        if not self.output_history:
            return 0.5

        last = self.output_history[-1]
        sentences = [s.strip() for s in last.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        n_sentences = max(1, len(sentences))

        connectors = ["quindi", "perché", "inoltre", "tuttavia", "dunque", "infatti",
                       "therefore", "because", "however", "thus", "indeed", "furthermore"]
        conn_count = sum(1 for c in connectors if c in last.lower())

        length_score = min(1.0, len(last.split()) / 100)

        coherence = (min(1.0, n_sentences / 5) * 0.3 +
                     min(1.0, conn_count / 3) * 0.5 +
                     length_score * 0.2)

        return min(1.0, max(0.1, coherence))

    def calculate_adaptation_speed(self) -> float:
        """Proportion of changed state keys between consecutive states."""
        if len(self.state_history) < 2:
            return 0.3

        a = self.state_history[-2]
        b = self.state_history[-1]

        changes = sum(1 for k in set(list(a.keys()) + list(b.keys()))
                      if a.get(k) != b.get(k))
        total = max(1, len(set(list(a.keys()) + list(b.keys()))))
        return min(1.0, changes / total)

    def calculate_long_term_continuity(self) -> float:
        """Time span coverage of recent thoughts vs. session duration."""
        return min(1.0, len(self.output_history) / max(1, self.history_window * 2))

    def calculate_self_generated_goals(self) -> float:
        """Keyword detection for goal-oriented language in recent outputs."""
        goal_keywords = [
            "goal", "obiettivo", "piano", "migliorare", "ottimizzare", "evolvere",
            "raggiungere", "completare", "target", "milestone", "task",
        ]
        if not self.output_history:
            return 0.3

        recent = " ".join(list(self.output_history)[-3:]).lower()
        hits = sum(1 for kw in goal_keywords if kw in recent)

        self.goal_history.append(f"{hits} hits")
        return min(1.0, hits / max(3, len(goal_keywords) * 0.3))

    # ── Composite Emergence Score ──

    def measure(self) -> dict:
        """Full metrics cycle."""
        novelty = self.calculate_novelty()
        coherence = self.calculate_coherence()
        adaptation = self.calculate_adaptation_speed()
        memory_cont = self.calculate_long_term_continuity()
        goals = self.calculate_self_generated_goals()

        emergence = (
            novelty * self.weights.get("novelty", 0.20) +
            coherence * self.weights.get("coherence", 0.25) +
            adaptation * self.weights.get("adaptation", 0.15) +
            memory_cont * self.weights.get("memory_continuity", 0.20) +
            goals * self.weights.get("self_generated_goals", 0.20)
        )

        result = {
            "emergence": round(emergence, 4),
            "novelty": round(novelty, 3),
            "coherence": round(coherence, 3),
            "adaptation": round(adaptation, 3),
            "memory_continuity": round(memory_cont, 3),
            "self_generated_goals": round(goals, 3),
            "timestamp": time.time(),
        }

        self.bus.set("cognitive_metrics", result)
        return result
