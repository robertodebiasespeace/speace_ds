"""SPEACE Learning — Reinforcement / Reward-Based (Dopaminergic).

Implements TD-learning-like reinforcement modulated by dopamine signal.

BIOLOGICAL PRINCIPLE: Dopamine neurons encode reward prediction error (RPE):
- Better than expected → dopamine burst → strengthen preceding actions (LTP)
- Worse than expected → dopamine dip → weaken preceding actions (LTD)
- As expected → no change → stable behavior

This is the brain's core "credit assignment" mechanism, operating on
timescales of seconds and without backpropagation. Extremely efficient:
one global signal (dopamine) tunes plasticity everywhere simultaneously.
"""


class ReinforcementLearner:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        self.dopa_cfg = config.get("neuromodulation", {}).get("dopamine", {})
        self.dopamine = self.dopa_cfg.get("initial", 0.5)
        self.value_predictions: dict[str, float] = {}  # state → expected reward
        self.action_values: dict[str, float] = {}  # action → learned value

    def predict_value(self, state_key: str) -> float:
        """Expected reward given current state."""
        return self.value_predictions.get(state_key, 0.5)

    def update(self, state_key: str, actual_reward: float, learning_rate: float = 0.1):
        """TD update: V(s) += alpha * (R - V(s))."""
        predicted = self.value_predictions.get(state_key, 0.5)
        rpe = actual_reward - predicted  # Reward Prediction Error

        # Update state value
        self.value_predictions[state_key] = predicted + learning_rate * rpe

        # Update global dopamine level
        if rpe > 0:
            self.dopamine = min(1.0, self.dopamine + self.dopa_cfg.get("boost_on_reward", 0.15))
        else:
            self.dopamine = max(0.1, self.dopamine - 0.05)

        # Decay
        self.dopamine = max(0.1, self.dopamine - self.dopa_cfg.get("decay_per_cycle", 0.02))

        self.bus.set("dopamine", {
            "level": round(self.dopamine, 3),
            "rpe": round(rpe, 3),
            "state": state_key,
        })

        return rpe

    def reinforce_action(self, action: str, reward: float):
        """Boost action value based on outcome. DA burst = strengthen."""
        current = self.action_values.get(action, 0.5)
        self.action_values[action] = min(1.0, current + reward * self.dopamine * 0.15)

    def select_action(self, candidates: list[str], explore: bool = False) -> str:
        """Select action with highest learned value (or explore)."""
        if explore and candidates:
            import random
            return random.choice(candidates)
        values = {c: self.action_values.get(c, 0.5) for c in candidates}
        return max(values, key=values.get) if values else "answer"

    def get_dopamine_level(self) -> float:
        return self.dopamine
