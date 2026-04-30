"""SPEACE Cognitive — Predictive Coding Engine.

Implements bidirectional predictive processing inspired by Karl Friston's
Free Energy Principle. The brain constantly generates top-down predictions;
only prediction errors propagate bottom-up.

BIOLOGICAL PRINCIPLE: Predictive coding explains why the brain uses ~20W:
most sensory input IS predicted and cancelled out. Only the unexpected
(surprise / prediction error) requires energy to process. Without this,
the brain would need kilowatts to process the full sensory stream.

SPEACE applies this to textual/conceptual processing:
- Feedforward: carries prediction errors (surprise = what was unexpected)
- Feedback: carries predictions (expectations = what should happen next)
"""

import math
from collections import deque


class PredictiveEngine:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        pc_cfg = config.get("cognitive", {}).get("predictive_coding", {})
        self.horizon = pc_cfg.get("prediction_horizon", 3)
        self.error_threshold = pc_cfg.get("error_threshold", 0.15)
        self.learning_rate = pc_cfg.get("learning_rate", 0.05)

        # State transition model: (state_pattern, next_pattern) → weight
        self.transition_weights: dict[tuple[str, str], float] = {}
        self.recent_states: deque[str] = deque(maxlen=20)

    def predict(self, current_state: str) -> list[tuple[str, float]]:
        """Predict top-k likely next states given current state."""
        candidates = []
        for (src, dst), weight in self.transition_weights.items():
            if src == current_state:
                candidates.append((dst, weight))

        if not candidates:
            return [("general_reasoning", 0.5)]  # Default prediction

        total = sum(w for _, w in candidates)
        return [(dst, w / total) for dst, w in sorted(candidates, key=lambda x: x[1], reverse=True)[:self.horizon]]

    def compute_prediction_error(self, predicted: str, actual: str) -> float:
        """How wrong was the prediction? 0 = perfect, 1 = completely wrong."""
        if predicted == actual:
            return 0.0
        # Simple categorical error — could be extended with semantic distance
        return 0.7

    def update_model(self, current: str, actual_next: str):
        """Strengthen correct transitions, weaken incorrect ones."""
        key = (current, actual_next)
        old_weight = self.transition_weights.get(key, 0.3)
        self.transition_weights[key] = min(1.0, old_weight + self.learning_rate)

        # Normalize outgoing weights
        outgoing = [(k, v) for k, v in self.transition_weights.items() if k[0] == current]
        if outgoing:
            total = sum(v for _, v in outgoing)
            for k, _ in outgoing:
                self.transition_weights[k] /= total

    def process(self, current_pattern: str) -> dict:
        """Run one predictive cycle: predict → compute error → update."""
        self.recent_states.append(current_pattern)

        predictions = self.predict(current_pattern)

        # Surprise = weighted expected error (placeholder until actual next is known)
        expected_surprise = 1.0 - predictions[0][1] if predictions else 0.5

        # Suppress propagation if predictions are confident (low error)
        propagate = expected_surprise > self.error_threshold

        self.bus.set("predictive_state", {
            "current": current_pattern,
            "predictions": predictions,
            "surprise": round(expected_surprise, 3),
            "propagate": propagate,
        })

        return {
            "predictions": predictions,
            "surprise": round(expected_surprise, 3),
            "should_propagate": propagate,
            "free_energy_estimate": round(-math.log(max(0.01, predictions[0][1])) if predictions else 1.0, 3),
        }
