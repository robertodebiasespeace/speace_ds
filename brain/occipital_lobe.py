"""SPEACE Brain — Occipital Lobe.

Pattern and structure recognition. Detects schemas, templates, and
recurring configurations in input data.

BIOLOGICAL PRINCIPLE: The visual cortex uses hierarchical feature detection
(simple edges → complex shapes → objects) — each level compresses information,
reducing the data volume passed upward by ~10× per level.
"""


class OccipitalLobe:

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.graph.register_node(
            "OccipitalCortex",
            self._process,
            input_types={"input_text": str, "history": list},
            output_types={"patterns_detected": list, "templates": list, "structure_type": str},
            metadata={"region": "occipital", "function": "pattern_detection"},
        )

    async def _process(self, inputs: dict) -> dict:
        text = inputs.get("input_text", "").lower()

        schema_indicators = {
            "list": ["elenco", "lista", "punti", "bullet", "items", "steps"],
            "hierarchy": ["sotto", "sopra", "principale", "sub", "parent", "child", "tree"],
            "sequence": ["primo", "secondo", "poi", "dopo", "infine", "first", "then", "next", "finally"],
            "comparison": ["rispetto", "rispetto a", "confronto", "vs", "versus", "compared", "differenza"],
            "template": ["template", "modello", "schema", "pattern", "boilerplate", "scaffold"],
        }

        detected = []
        for schema_type, keywords in schema_indicators.items():
            if any(kw in text for kw in keywords):
                detected.append(schema_type)

        return {
            "patterns_detected": detected,
            "templates": detected,
            "structure_type": detected[0] if detected else "unstructured",
        }

    async def process(self, user_input: str) -> dict:
        return await self._process({"input_text": user_input, "history": []})
