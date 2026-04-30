"""SPEACE Brain — Amygdala.

Emotional salience detector. Evaluates input for affective significance:
threat, reward, novelty, urgency. Biases downstream processing.

BIOLOGICAL PRINCIPLE: The amygdala provides a "low road" (fast, crude,
energy-efficient) emotional evaluation BEFORE the slower cortical "high road."
This enables rapid resource allocation to threats without full cognitive analysis.
"""


class Amygdala:

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.valence_history: list[dict] = []

        self.graph.register_node(
            "AmygdalaSalience",
            self._evaluate,
            input_types={"input_text": str, "context": dict},
            output_types={"valence": str, "intensity": float, "action_bias": str},
            metadata={"region": "amygdala", "function": "emotional_salience"},
        )

    async def _evaluate(self, inputs: dict) -> dict:
        text = inputs.get("input_text", "").lower()

        threat_keywords = {
            "pericolo", "attacco", "virus", "hacker", "cancella", "distruggi",
            "danger", "attack", "virus", "delete", "destroy", "breach",
        }
        reward_keywords = {
            "successo", "ottimo", "migliora", "evolvi", "cresci",
            "success", "great", "improve", "evolve", "grow", "achieve",
        }
        curiosity_keywords = {
            "nuovo", "scopri", "esplora", "crea", "inventa",
            "new", "discover", "explore", "create", "invent",
        }

        threat = sum(1 for kw in threat_keywords if kw in text)
        reward = sum(1 for kw in reward_keywords if kw in text)
        curiosity = sum(1 for kw in curiosity_keywords if kw in text)

        if threat > reward and threat > curiosity:
            valence, intensity, bias = "negative", min(1.0, threat * 0.3), "conservative"
        elif reward > curiosity:
            valence, intensity, bias = "positive", min(1.0, reward * 0.25), "approach"
        elif curiosity > 0:
            valence, intensity, bias = "curious", min(1.0, curiosity * 0.2), "explore"
        else:
            valence, intensity, bias = "neutral", 0.1, "balanced"

        result = {"valence": valence, "intensity": intensity, "action_bias": bias}
        self.valence_history.append(result)
        if len(self.valence_history) > 30:
            self.valence_history = self.valence_history[-30:]
        self.bus.set("emotional_state", result)

        return result

    async def evaluate(self, user_input: str) -> dict:
        return await self._evaluate({"input_text": user_input, "context": {}})

    def recent_valence(self, n: int = 5) -> str:
        if not self.valence_history:
            return "neutral"
        recent = [v["valence"] for v in self.valence_history[-n:]]
        return max(set(recent), key=recent.count)  # Most frequent
