"""SPEACE Brain — Cingulate Cortex.

Error monitoring, conflict detection, and performance optimization.
The "anterior cingulate" signals when something is wrong or unexpected.

BIOLOGICAL PRINCIPLE: Error monitoring is a sparse signal — the brain
doesn't verify every operation, it only flags anomalies. This is the
predictive coding error signal: unexpected = forward propagation.
"""


class CingulateCortex:

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.error_count = 0
        self.conflict_log: list[dict] = []

        self.graph.register_node(
            "CingulateMonitor",
            self._monitor,
            input_types={"output": str, "expected": str, "coherence": float},
            output_types={"error_detected": bool, "conflict_type": str, "correction_suggestion": str},
            metadata={"region": "cingulate", "function": "error_conflict_monitor"},
        )

    async def _monitor(self, inputs: dict) -> dict:
        coherence = inputs.get("coherence", 0.5)
        output = inputs.get("output", "")

        error = False
        conflict = "none"
        suggestion = ""

        if coherence < 0.4:
            error = True
            conflict = "low_coherence"
            suggestion = "Rivedere la coerenza dell'output. Possibile conflitto logico."
            self.error_count += 1
        elif not output.strip():
            error = True
            conflict = "empty_output"
            suggestion = "Nessun output generato. Ricalibrare la pipeline."
            self.error_count += 1
        elif len(output.split()) < 3:
            conflict = "low_verbosity"
            suggestion = "Output minimo — verificare se appropriato al contesto."

        if error or conflict != "none":
            self.conflict_log.append({
                "conflict": conflict,
                "coherence": coherence,
                "suggestion": suggestion,
            })
            if len(self.conflict_log) > 50:
                self.conflict_log = self.conflict_log[-50:]

        return {
            "error_detected": error,
            "conflict_type": conflict,
            "correction_suggestion": suggestion,
        }

    async def monitor(self, output: str, coherence: float) -> dict:
        return await self._monitor({
            "output": output,
            "expected": "",
            "coherence": coherence,
        })
