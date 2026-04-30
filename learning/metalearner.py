"""SPEACE Learning — Meta-Learner.

Learns how to learn: tunes hyperparameters, selects strategies, and
optimizes the learning process itself based on performance history.

BIOLOGICAL PRINCIPLE: Meta-cognition in the prefrontal cortex enables
"learning to learn." Instead of optimizing one task, the brain develops
general strategies (working memory chunking, attention allocation, sleep
consolidation scheduling) that improve ALL tasks. This is the key to
the brain's remarkable sample efficiency vs. deep learning.

SPEACE meta-learner adjusts: learning rate, exploration weight, pruning
thresholds, consolidation replay ratio, and LLM routing preferences.
"""

import json
import time
from pathlib import Path


class MetaLearner:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        self.state_path = Path("data/metalearner_state.json")

        self.params = {
            "learning_rate": 0.05,
            "exploration_weight": 2.0,
            "prune_threshold": 0.1,
            "consolidation_replay_ratio": 0.3,
            "gate_salience_threshold": 0.3,
            "llm_temperature": 0.65,
            "batch_size": 1,
        }

        self.param_history: list[dict] = []
        self.performance_history: list[float] = []
        self._load()

    def observe_outcome(self, metrics: dict):
        """Record performance and adjust hyperparameters."""
        emergence = metrics.get("emergence", 0.5)
        coherence = metrics.get("coherence", 0.5)
        novelty = metrics.get("novelty", 0.3)
        self.performance_history.append(emergence)
        if len(self.performance_history) > 50:
            self.performance_history = self.performance_history[-50:]

        # Simple gradient-free meta-optimization
        trend = self._performance_trend()

        if trend > 0.01:  # Improving
            # Reinforce current params
            pass
        elif trend < -0.01:  # Degrading
            # Perturb params
            self.params["learning_rate"] = max(0.01, min(0.2, self.params["learning_rate"] * 1.1))
            self.params["exploration_weight"] = max(0.5, min(5.0, self.params["exploration_weight"] * 1.05))
            self.params["prune_threshold"] = max(0.05, min(0.3, self.params["prune_threshold"] * 1.05))

        # Coherence-based adjustments
        if coherence < 0.4:
            self.params["llm_temperature"] = max(0.1, self.params["llm_temperature"] - 0.05)
        if novelty < 0.3:
            self.params["llm_temperature"] = min(0.95, self.params["llm_temperature"] + 0.05)
            self.params["exploration_weight"] = min(5.0, self.params["exploration_weight"] * 1.1)

        snapshot = {
            "timestamp": time.time(),
            "params": dict(self.params),
            "emergence": emergence,
            "coherence": coherence,
            "novelty": novelty,
        }
        self.param_history.append(snapshot)
        if len(self.param_history) > 30:
            self.param_history = self.param_history[-30:]

        self.bus.set("metalearner_params", dict(self.params))
        self._save()

    def _performance_trend(self, window: int = 5) -> float:
        if len(self.performance_history) < window:
            return 0.0
        recent = self.performance_history[-window:]
        return (recent[-1] - recent[0]) / max(0.01, window)

    def recommend(self) -> dict:
        """Return current recommended hyperparameters for other modules."""
        return dict(self.params)

    def _save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w") as f:
            json.dump({
                "params": self.params,
                "history": self.param_history[-20:],
                "performance": self.performance_history[-30:],
            }, f, indent=2, default=str)

    def _load(self):
        if self.state_path.exists():
            try:
                with open(self.state_path) as f:
                    data = json.load(f)
                    if "params" in data:
                        self.params.update(data["params"])
                    if "performance" in data:
                        self.performance_history = data["performance"]
            except Exception:
                pass
