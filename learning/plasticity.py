"""SPEACE Learning — Hebbian and STDP Plasticity.

Implements biologically-plausible synaptic plasticity rules.

BIOLOGICAL PRINCIPLE:
- Hebbian: "Neurons that fire together wire together." Co-activation → strengthening.
- STDP (Spike-Timing-Dependent Plasticity): The ORDER of firing matters.
  Pre-before-post → LTP (strengthening). Post-before-pre → LTD (weakening).
  This temporal asymmetry is the brain's key to learning sequences and causality.

Energy efficiency: Hebbian/STDP learning is local (only depends on pre+post
activity at a single synapse — no global backpropagation needed). Biological
brains learn with ~20W; backprop through millions of parameters needs GPUs.
SPEACE uses local Hebbian updates on the graph where possible and reserves
gradient-based learning only for embedding fine-tuning.
"""

import math


class PlasticityEngine:

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.hebbian_rate = 0.05  # Base Hebbian strengthening rate
        self.stdp_ltp_window_ms = 20.0  # Pre-before-post window for LTP
        self.stdp_ltd_window_ms = 40.0  # Post-before-pre window for LTD

    def hebbian_step(self, coactive_pairs: list[tuple[str, str]]):
        """Strengthen edges between co-active neurons."""
        for src, dst in coactive_pairs:
            if self.graph.graph.has_edge(src, dst):
                self.graph.strengthen_edge(src, dst, self.hebbian_rate)
            else:
                # Form new connection (structural plasticity)
                self.graph.connect(src, dst)

    def stdp_step(self, pre_spike_times: dict[str, float],
                  post_spike_times: dict[str, float]):
        """Apply STDP rule: delta_w = f(delta_t) where delta_t = t_post - t_pre."""
        for pre, t_pre in pre_spike_times.items():
            for post, t_post in post_spike_times.items():
                if pre == post:
                    continue
                dt = t_post - t_pre  # ms

                if dt > 0 and dt < self.stdp_ltp_window_ms:
                    # Pre-then-post → LTP (causal)
                    delta_w = 0.01 * math.exp(-dt / self.stdp_ltp_window_ms)
                    self.graph.strengthen_edge(pre, post, delta_w)
                elif dt < 0 and abs(dt) < self.stdp_ltd_window_ms:
                    # Post-then-pre → LTD (acausal)
                    delta_w = -0.005 * math.exp(-abs(dt) / self.stdp_ltd_window_ms)
                    self.graph.weaken_edge(pre, post, abs(delta_w))

    def prune_cycle(self):
        """Remove weak edges to free graph memory."""
        self.graph.prune_weak_edges(threshold=0.1)

    def homeostatic_scaling(self, target_activity: float = 0.3):
        """Global scaling to maintain target average activity (stability)."""
        activations = {}
        for name, node in self.graph._nodes.items():
            activations[name] = node.performance_score

        if not activations:
            return

        mean_act = sum(activations.values()) / len(activations)
        scale_factor = target_activity / max(0.01, mean_act)

        for u, v, key, data in self.graph.graph.edges(keys=True, data=True):
            data["plasticity"] = min(1.0, max(0.05, data.get("plasticity", 0.5) * scale_factor))
