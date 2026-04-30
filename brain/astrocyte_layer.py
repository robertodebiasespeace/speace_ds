"""SPEACE Brain — Astrocyte Layer.

Neuroglial support network. Regulates energy distribution, plasticity
modulation, and homeostasis across active brain regions.

BIOLOGICAL PRINCIPLE (Nature 2026 paper): Astrocytes form gap-junction
networks that monitor neural activity and dynamically redistribute
energy resources (glucose/glycogen) to active regions. They also modulate
synaptic plasticity — enabling/disabling learning based on energy availability.
SPEACE implements this as a resource-aware compute allocator.

Reference: Nature 2026, DOI: 10.1038/s41586-026-10426-6
"""

import threading


class AstrocyteLayer:
    """Energy gating and plasticity modulation inspired by astrocyte networks."""

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.energy_cfg = config.get("energy", {})
        self._lock = threading.RLock()

        # Per-region energy budgets
        self.energy_budget: dict[str, float] = {}
        self.support_levels: dict[str, float] = {}
        self.plasticity_boosts: dict[str, float] = {}

        # Gap junction network (who shares energy with whom)
        self.gap_junctions: dict[str, list[str]] = {}

        self.graph.register_node(
            "AstrocyteNetwork",
            self._astrocyte_regulate,
            input_types={"region_activations": dict, "neural_load": dict, "energy_budget": dict},
            output_types={"support_adjusted": dict, "plasticity_boosted": list, "energy_warnings": list},
            metadata={"region": "astrocyte", "function": "glial_support_energy"},
        )

    async def _astrocyte_regulate(self, inputs: dict) -> dict:
        with self._lock:
            activations = inputs.get("region_activations", {})
            neural_load = inputs.get("neural_load", {})
            energy_pool = inputs.get("energy_budget", {})

            warnings = []
            adjusted = {}
            plasticity_boosted = []

            total_load = sum(neural_load.values()) if neural_load else 1.0
            min_budget = 0.05  # Minimum energy per region

            for region, activation in activations.items():
                # Support level inversely proportional to load (restore function)
                load = neural_load.get(region, 0.5)
                support = max(0.1, 1.0 - load * 0.7)
                self.support_levels[region] = support

                # Energy allocation proportional to activation × support
                base_energy = energy_pool.get(region, 0.1)
                allocated = base_energy * activation * support
                adjusted[region] = max(min_budget, allocated)

                # Plasticity boost for active, well-supported regions
                if activation > 0.5 and support > 0.4:
                    boost = min(0.3, activation * support * 0.2)
                    self.plasticity_boosts[region] = boost
                    plasticity_boosted.append(region)

                # Warn if energy critically low
                if allocated < min_budget * 1.5:
                    warnings.append(f"Low energy: {region} ({allocated:.3f})")

            # Distribute via gap junctions: well-funded regions help neighbors
            for region, neighbors in self.gap_junctions.items():
                if self.energy_budget.get(region, 0) > 0.3:
                    for neighbor in neighbors:
                        if neighbor in adjusted and adjusted[neighbor] < 0.2:
                            transfer = 0.05
                            adjusted[region] = max(0.1, adjusted.get(region, 0.3) - transfer)
                            adjusted[neighbor] = min(0.5, adjusted[neighbor] + transfer)

            self.energy_budget = adjusted
            self.bus.set("astrocyte_state", {
                "support": dict(self.support_levels),
                "energy": dict(self.energy_budget),
                "plasticity": dict(self.plasticity_boosts),
            })

            return {
                "support_adjusted": dict(self.support_levels),
                "plasticity_boosted": plasticity_boosted,
                "energy_warnings": warnings,
            }

    def create_gap_junction(self, region_a: str, region_b: str):
        """Connect two regions to allow energy sharing."""
        for region, neighbor in [(region_a, region_b), (region_b, region_a)]:
            if region not in self.gap_junctions:
                self.gap_junctions[region] = []
            if neighbor not in self.gap_junctions[region]:
                self.gap_junctions[region].append(neighbor)

    async def regulate(self, activations: dict, neural_load: dict = {}) -> dict:
        if not neural_load:
            neural_load = {r: a * 0.8 for r, a in activations.items()}
        return await self._astrocyte_regulate({
            "region_activations": activations,
            "neural_load": neural_load,
            "energy_budget": dict(self.energy_budget),
        })

    def get_plasticity_boost(self, region: str) -> float:
        """Current plasticity boost factor for a brain region."""
        return self.plasticity_boosts.get(region, 0.0)
