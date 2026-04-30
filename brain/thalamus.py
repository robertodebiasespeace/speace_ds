"""SPEACE Brain — Thalamus.

Sensory gating and relay. All input passes through the thalamus first,
which filters and routes it to the appropriate cortical regions.

BIOLOGICAL PRINCIPLE: The thalamus acts as a "gate" that blocks ~90% of
sensory input from reaching consciousness. Only salient, novel, or
attended stimuli pass through — this sparse gating saves enormous energy.
"""


class Thalamus:

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.gate_threshold = config.get("cognitive", {}).get("attention", {}).get("salience_threshold", 0.3)

        self.graph.register_node(
            "ThalamicRelay",
            self._gate_input,
            input_types={"input_text": str, "internal_state": dict},
            output_types={"gated_input": str, "salience": float, "routing_hints": list},
            metadata={"region": "thalamus", "function": "sensory_gate"},
        )

    async def _gate_input(self, inputs: dict) -> dict:
        text = inputs.get("input_text", "")
        internal = inputs.get("internal_state", {})

        # Compute salience
        salience = 0.5  # Base
        if len(text) > 20:
            salience += 0.1
        if "?" in text:
            salience += 0.1  # Questions are salient
        if any(w in text.lower() for w in ["urgente", "importante", "critico", "alert"]):
            salience += 0.25
        if any(w in text.lower() for w in ["speace", "cervello", "brain", "dna"]):
            salience += 0.15  # Self-referential

        # Check for resource alerts
        if internal.get("alerts"):
            salience -= 0.15  # Reduce processing when system is stressed

        salience = min(1.0, max(0.1, salience))

        # Routing hints for downstream regions
        routing = []
        if "memoria" in text.lower() or "ricorda" in text.lower():
            routing.extend(["temporal_lobe", "hippocampus"])
        if "piano" in text.lower() or "strategia" in text.lower():
            routing.append("frontal_lobe")
        if any(w in text.lower() for w in ["errore", "problema", "bug"]):
            routing.append("cingulate_cortex")

        # Gate: if salience below threshold, signal to skip deep processing
        gated = text if salience >= self.gate_threshold else ""

        return {
            "gated_input": gated,
            "salience": round(salience, 3),
            "routing_hints": routing if salience >= self.gate_threshold else [],
        }

    async def relay(self, user_input: str) -> dict:
        internal = self.bus.get("internal_state", {})
        return await self._gate_input({"input_text": user_input, "internal_state": internal})
