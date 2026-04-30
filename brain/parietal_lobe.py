"""SPEACE Brain — Parietal Lobe.

Spatial processing, numerical cognition, sensorimotor integration.
Processes quantities, spatial relationships, and logical structures.

BIOLOGICAL PRINCIPLE: The parietal lobe integrates multimodal information
(sight, touch, proprioception) into a coherent spatial map — doing with
one unified representation what would otherwise require N separate ones.
"""


class ParietalLobe:

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.graph.register_node(
            "ParietalCortex",
            self._process,
            input_types={"input_text": str, "pattern": str},
            output_types={"spatial_analysis": str, "numerical_elements": list, "logic_structure": str},
            metadata={"region": "parietal", "function": "spatial_numerical"},
        )
        self.history: list[dict] = []

    async def _process(self, inputs: dict) -> dict:
        text = inputs.get("input_text", "")
        words = text.lower().split()

        numerical = [w for w in words if w.replace(".", "").replace("-", "").isdigit()]
        spatial_terms = [w for w in words if w in {
            "sopra", "sotto", "destra", "sinistra", "vicino", "lontano",
            "spazio", "coordinate", "mappa", "direzione", "above", "below",
            "left", "right", "near", "far", "space", "map", "direction",
        }]
        logical_ops = [w for w in words if w in {
            "se", "allora", "quindi", "perché", "causa", "effetto",
            "if", "then", "therefore", "because", "cause", "effect",
        }]

        analysis = []
        if numerical:
            analysis.append(f"Elementi numerici: {numerical}")
        if spatial_terms:
            analysis.append(f"Relazioni spaziali: {spatial_terms}")

        return {
            "spatial_analysis": "; ".join(analysis) if analysis else "Nessuna dimensione spaziale/quantitativa rilevata",
            "numerical_elements": numerical,
            "logic_structure": "deductive" if logical_ops else "associative",
        }

    async def process(self, user_input: str) -> dict:
        return await self._process({"input_text": user_input, "pattern": "auto"})
