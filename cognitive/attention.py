"""SPEACE Cognitive — Salience-based Attention Gating.

Implements UCB1 multi-armed bandit attention allocation and salience
filtering. Only salient, novel, or goal-relevant stimuli reach
conscious processing — the rest is filtered out.

BIOLOGICAL PRINCIPLE: The brain receives ~11 million bits/sec of sensory
input but consciousness processes ~50 bits/sec. Attention gating achieves
this 200,000:1 compression. SPEACE uses UCB1 (Upper Confidence Bound) for
optimal explore/exploit balancing — proven to minimize regret.
"""

import math
import random


class AttentionGate:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        self.attn_cfg = config.get("cognitive", {}).get("attention", {})
        self.exploration_weight = self.attn_cfg.get("ucb1_exploration_weight", 2.0)
        self.salience_threshold = self.attn_cfg.get("salience_threshold", 0.3)

        # UCB1 tracking per module
        self.module_rewards: dict[str, float] = {}
        self.module_pulls: dict[str, int] = {}
        self.current_focus: list[str] = []

    def compute_salience(self, user_input: str, emotional_state: dict) -> float:
        """Multi-factor salience score."""
        score = 0.3  # Base

        text = user_input.lower()

        # Novelty salience
        history = self.bus.get("recent_inputs", [])
        if history:
            words_now = set(text.split())
            for past in history[-5:]:
                words_past = set(past.split())
                overlap = len(words_now & words_past) / max(1, len(words_now | words_past))
                if overlap < 0.3:
                    score += 0.15  # Novel input
                    break

        # Emotional amplification (amygdala → attention)
        intensity = emotional_state.get("intensity", 0.1)
        valence = emotional_state.get("valence", "neutral")
        if valence == "negative":
            score += intensity * 0.3  # Threats prioritized
        elif valence == "positive":
            score += intensity * 0.15

        # Self-referential boost
        if any(w in text for w in ["speace", "cervello", "brain", "dna digitale"]):
            score += 0.1

        # Question boost
        if "?" in user_input:
            score += 0.1

        # Length normalization
        if len(user_input) > 50:
            score += 0.05

        return min(1.0, score)

    def ucb1_select(self, modules: list[str], context_relevance: dict[str, float]) -> list[str]:
        """Select top-k modules using UCB1 multi-armed bandit with context priors."""
        scores = {}
        total_pulls = sum(self.module_pulls.get(m, 0) for m in modules) + 1
        max_modules = self.attn_cfg.get("max_focus_modules", 5)

        for module in modules:
            # Prior from context relevance (keyword match)
            prior = context_relevance.get(module, 0.3)

            # UCB1 value
            pulls = self.module_pulls.get(module, 0)
            if pulls == 0:
                ucb = float("inf")  # Explore unseen modules
            else:
                mean_reward = self.module_rewards.get(module, 0) / pulls
                exploration_term = self.exploration_weight * math.sqrt(
                    math.log(total_pulls) / pulls
                )
                ucb = mean_reward + exploration_term

            # Blend UCB with context prior
            scores[module] = prior * 0.3 + (1.0 / (1.0 + math.exp(-ucb / 10))) * 0.7 \
                if ucb != float("inf") else 1.0

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        selected = [m for m, s in ranked[:max_modules]]

        # Update pulls
        for m in selected:
            self.module_pulls[m] = self.module_pulls.get(m, 0) + 1

        self.current_focus = selected
        return selected

    def update_reward(self, module: str, reward: float):
        """Feedback reward after module execution (dopaminergic signal)."""
        self.module_rewards[module] = self.module_rewards.get(module, 0) + reward

    def filter(self, user_input: str, emotional_state: dict, available_modules: list[str],
               context_relevance: dict[str, float]) -> tuple[list[str], float]:
        """Full attention cycle: compute salience → gate → UCB1 select."""
        salience = self.compute_salience(user_input, emotional_state)

        # Deep bypass: if salience too low, skip expensive processing
        if salience < self.salience_threshold:
            return [], salience

        modules = self.ucb1_select(available_modules, context_relevance)
        self.bus.set("attention_state", {
            "salience": round(salience, 3),
            "focus": modules,
            "threshold": self.salience_threshold,
        })

        return modules, salience
