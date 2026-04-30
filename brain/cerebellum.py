"""SPEACE Brain — Cerebellum.

Fine-tuning, procedural learning, and automation of repeated patterns.
Once a behavior is learned, the cerebellum handles it efficiently
without engaging the expensive frontal cortex.

BIOLOGICAL PRINCIPLE: The cerebellum contains ~80% of the brain's neurons
but operates unconsciously and automatically. It uses a remarkably
regular architecture (cristalline repeating microcircuits) that enables
fast, energy-efficient procedural execution once patterns are learned.
"""


class Cerebellum:

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.procedures: dict[str, callable] = {}
        self.automation_patterns: dict[str, dict] = {}

        self.graph.register_node(
            "CerebellarFineTuner",
            self._fine_tune,
            input_types={"action": str, "output": str, "expected_pattern": dict},
            output_types={"refined_action": str, "automation_candidate": bool, "confidence": float},
            metadata={"region": "cerebellum", "function": "procedural_learning_fine_tuning"},
        )

    async def _fine_tune(self, inputs: dict) -> dict:
        action = inputs.get("action", "")
        output = inputs.get("output", "")
        expected = inputs.get("expected_pattern", {})

        # Detect if this is a repeated pattern (candidate for automation)
        action_sig = f"{action}|{str(expected)}"
        if action_sig in self.automation_patterns:
            self.automation_patterns[action_sig]["count"] += 1
        else:
            self.automation_patterns[action_sig] = {"count": 1, "outputs": []}

        self.automation_patterns[action_sig]["outputs"].append(output)
        if len(self.automation_patterns[action_sig]["outputs"]) > 10:
            self.automation_patterns[action_sig]["outputs"] = \
                self.automation_patterns[action_sig]["outputs"][-10:]

        count = self.automation_patterns[action_sig]["count"]
        automation_candidate = count >= 3  # 3 repeats = ready for automation

        return {
            "refined_action": f"{action}_optimized" if automation_candidate else action,
            "automation_candidate": automation_candidate,
            "confidence": min(0.95, 0.5 + count * 0.15),
        }

    async def fine_tune(self, action: str, output: str, expected: dict = {}) -> dict:
        return await self._fine_tune({
            "action": action,
            "output": output,
            "expected_pattern": expected,
        })

    def register_procedure(self, name: str, func: callable):
        """Register an automated procedure to bypass cortical processing."""
        self.procedures[name] = func

    def execute_procedure(self, name: str, *args, **kwargs):
        if name in self.procedures:
            return self.procedures[name](*args, **kwargs)
        raise KeyError(f"Procedura '{name}' non registrata")
