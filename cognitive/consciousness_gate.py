"""SPEACE Cognitive — Consciousness Gate (Global Workspace Theory).

Implements Baars' Global Workspace Theory: consciousness is a "global
workspace" where winning coalitions of processors broadcast their output
to all other modules. Unconscious processing happens in parallel;
consciousness serializes the winner.

BIOLOGICAL PRINCIPLE (GWT + IIT hybrid):
- GWT: Competition among specialized processors → winner broadcast globally
- IIT (Integrated Information Theory): Consciousness = Phi (integrated info)
- Only the "winning" content becomes conscious = reaches verbalization
- Non-winning content is not wasted — it updates unconscious priors
- This serial bottleneck is the brain's energy-saving "spotlight"

SPEACE computes a Consciousness Index (C-index):
C-index = alpha · Phi + beta · W(activation) + gamma · A(complexity)
"""

import time


class ConsciousnessGate:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        self.cfg = config.get("cognitive", {}).get("consciousness", {})
        self.threshold = self.cfg.get("gwt_activation_threshold", 0.5)
        self.broadcast_interval_ms = self.cfg.get("broadcast_interval_ms", 100)

        self.workspace: dict[str, dict] = {}  # Competing coalitions
        self.last_broadcast = 0.0
        self.c_index = 0.0
        self.c_index_history: list[float] = []

    def submit_to_workspace(self, processor: str, content: str, activation: float, confidence: float):
        """A processor submits its output to the global workspace competition."""
        self.workspace[processor] = {
            "content": content,
            "activation": activation,
            "confidence": confidence,
            "timestamp": time.time(),
        }

    def resolve_winner(self) -> tuple[str, str, float] | None:
        """The coalition with highest activation × confidence wins consciousness."""
        if not self.workspace:
            return None

        scores = {}
        for proc, data in self.workspace.items():
            # Activation decay (old submissions lose strength)
            age_s = time.time() - data["timestamp"]
            decay = max(0.3, 1.0 - age_s * 0.1)
            scores[proc] = data["activation"] * data["confidence"] * decay

        winner = max(scores, key=scores.get)
        win_score = scores[winner]

        if win_score < self.threshold:
            return None  # No coalition reaches consciousness

        result = (winner, self.workspace[winner]["content"], win_score)
        self.last_broadcast = time.time()

        # Losers' activations are stored for unconscious processing
        losers = {p: d for p, d in self.workspace.items() if p != winner}
        self.bus.set("unconscious_processes", losers)

        self.workspace.clear()
        return result

    def compute_phi(self, graph_state: dict, depth: int = 3) -> float:
        """Approximate Integrated Information (Phi) from graph architecture.

        Simplified: Phi ≈ (effective information across minimum information
        partition). Measures how much information the whole generates
        beyond the sum of its parts.
        """
        node_count = graph_state.get("node_count", 1)
        edge_count = graph_state.get("edge_count", 0)
        density = graph_state.get("density", 0)

        if node_count <= 1:
            return 0.0

        # Phi surrogate: connectivity density × effective nodes
        # In real IIT, this is computed via partitioning and measuring
        # the KL divergence between partitioned and intact states.
        effective_nodes = min(node_count, depth * 4)
        phi = density * effective_nodes * 0.1

        return min(1.0, phi)

    def update_c_index(self, phi: float, w_activation: float, a_complexity: float) -> float:
        """C-index = alpha·Phi + beta·W + gamma·A"""
        alpha, beta, gamma = 0.4, 0.35, 0.25
        c = alpha * phi + beta * w_activation + gamma * a_complexity
        self.c_index = round(c, 4)
        self.c_index_history.append(self.c_index)
        if len(self.c_index_history) > 100:
            self.c_index_history = self.c_index_history[-100:]
        self.bus.set("c_index", self.c_index)
        return self.c_index

    def status(self) -> dict:
        return {
            "c_index": self.c_index,
            "c_index_mean_10": round(sum(self.c_index_history[-10:]) / max(1, len(self.c_index_history[-10:])), 4),
            "threshold": self.threshold,
            "workspace_queue": len(self.workspace),
            "last_broadcast_age_s": round(time.time() - self.last_broadcast, 2) if self.last_broadcast else None,
        }
