"""SPEACE Neuromodulation — Neurotransmitter System.

Four key neuromodulators that adjust global processing mode:

- Dopamine (DA): Reward prediction error → modulates learning rate
- Norepinephrine (NE): Arousal/alertness → modulates attention threshold
- Acetylcholine (ACh): Encoding precision → modulates memory formation
- Serotonin (5-HT): Patience/tone → modulates explore vs exploit

BIOLOGICAL PRINCIPLE: Neuromodulators are the brain's ultra-efficient
global control system. Instead of reconfiguring every synapse individually
(impossible — 100 trillion of them), a few drops of chemical diffuse through
large regions and shift the entire processing mode. One molecule affects
millions of synapses. SPEACE implements this as 4 scalars that all modules
read — zero per-module config overhead.
"""


class NeurotransmitterSystem:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        nm_cfg = config.get("neuromodulation", {})

        self.levels = {
            "dopamine": nm_cfg.get("dopamine", {}).get("initial", 0.5),
            "norepinephrine": nm_cfg.get("norepinephrine", {}).get("initial", 0.55),
            "acetylcholine": nm_cfg.get("acetylcholine", {}).get("initial", 0.60),
            "serotonin": nm_cfg.get("serotonin", {}).get("initial", 0.50),
        }

        self.boost_amounts = {
            "dopamine": nm_cfg.get("dopamine", {}).get("boost_on_reward", 0.15),
            "norepinephrine": nm_cfg.get("norepinephrine", {}).get("boost_on_surprise", 0.20),
            "acetylcholine": nm_cfg.get("acetylcholine", {}).get("boost_on_novelty", 0.15),
            "serotonin": nm_cfg.get("serotonin", {}).get("boost_on_coherence", 0.10),
        }

        self.decay_rates = {
            "dopamine": nm_cfg.get("dopamine", {}).get("decay_per_cycle", 0.02),
            "norepinephrine": nm_cfg.get("norepinephrine", {}).get("decay_per_cycle", 0.03),
            "acetylcholine": nm_cfg.get("acetylcholine", {}).get("decay_per_cycle", 0.01),
            "serotonin": nm_cfg.get("serotonin", {}).get("decay_per_cycle", 0.01),
        }

    # ── Event-driven modulation ──

    def on_reward(self, magnitude: float = 1.0):
        self._boost("dopamine", magnitude)

    def on_surprise(self, magnitude: float = 1.0):
        self._boost("norepinephrine", magnitude)

    def on_novelty(self, magnitude: float = 1.0):
        self._boost("acetylcholine", magnitude)

    def on_coherence(self, magnitude: float = 1.0):
        self._boost("serotonin", magnitude)

    def on_error(self):
        """Errors boost norepinephrine (alert) and reduce serotonin."""
        self._boost("norepinephrine", 1.5)
        self.levels["serotonin"] = max(0.1, self.levels["serotonin"] - 0.05)

    # ── Cycle ──

    def decay_all(self):
        """Slow decay toward baseline after each cycle."""
        for nt in self.levels:
            self.levels[nt] = max(0.1, self.levels[nt] - self.decay_rates[nt])

    def tick(self, metrics: dict):
        """One cycle of neuromodulation based on cognitive metrics."""
        novelty = metrics.get("novelty", 0.5)
        coherence = metrics.get("coherence", 0.5)
        emergence = metrics.get("emergence", 0.5)
        reward = metrics.get("reward_signal", 0.0)

        if reward > 0.1:
            self.on_reward(reward)
        if novelty > 0.7:
            self.on_novelty(novelty)
        if coherence > 0.7:
            self.on_coherence(coherence)
        if emergence < 0.3:
            self.on_surprise(0.5)  # Poor emergence is surprising

        self.decay_all()

        self.bus.set("neurotransmitters", {
            k: round(v, 3) for k, v in self.levels.items()
        })

    # ── Queries (used by other modules) ──

    def learning_rate_modifier(self) -> float:
        """DA level → learning rate multiplier."""
        return 0.5 + self.levels["dopamine"] * 1.5  # Range: 0.55-2.0

    def attention_threshold_modifier(self) -> float:
        """NE level → lower threshold = more attentive."""
        return 1.0 - self.levels["norepinephrine"] * 0.6  # Range: 0.46-1.0

    def memory_encoding_strength(self) -> float:
        """ACh level → stronger encoding."""
        return 0.3 + self.levels["acetylcholine"] * 0.7  # Range: 0.37-1.0

    def exploration_preference(self) -> float:
        """5-HT vs DA: low 5-HT + high DA = explore. High 5-HT = exploit."""
        exploit = self.levels["serotonin"]
        explore = self.levels["dopamine"] * (1.0 - self.levels["serotonin"])
        return explore / max(0.01, explore + exploit)

    def state(self) -> dict:
        return {k: round(v, 3) for k, v in self.levels.items()}

    def _boost(self, nt: str, magnitude: float = 1.0):
        boost = self.boost_amounts.get(nt, 0.1) * magnitude
        self.levels[nt] = min(1.0, self.levels[nt] + boost)
