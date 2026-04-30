"""SPEACE Brain — Insula.

Interoception and internal state awareness. Monitors the system's own
"body state": resource usage, energy levels, and internal balance.

BIOLOGICAL PRINCIPLE: The insula integrates visceral signals (heartbeat,
hunger, pain) into a unified "how do I feel" representation — enabling
efficient resource allocation decisions without full system introspection.
"""

import psutil

from datetime import datetime


class Insula:

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.energy_cfg = config.get("energy", {})
        self.metrics_history: list[dict] = []

        self.graph.register_node(
            "InsulaInteroception",
            self._sense_internal_state,
            input_types={},
            output_types={"state_summary": str, "alerts": list, "resource_status": dict},
            metadata={"region": "insula", "function": "interoception"},
        )

    async def _sense_internal_state(self, inputs: dict = {}) -> dict:
        """Read system vitals: RAM, CPU, process info."""
        alerts = []
        status = {}

        try:
            mem = psutil.virtual_memory()
            ram_used_mb = mem.used / (1024 * 1024)
            ram_limit = self.energy_cfg.get("ram_limit_mb", 8192)

            status["ram_used_mb"] = round(ram_used_mb, 1)
            status["ram_percent"] = mem.percent
            status["cpu_percent"] = psutil.cpu_percent(interval=0.1)
            status["processes"] = len(psutil.pids())

            if ram_used_mb > ram_limit * 0.85:
                alerts.append(f"CRITICO: RAM a {ram_used_mb:.0f}MB (limite {ram_limit}MB)")
            elif ram_used_mb > ram_limit * 0.65:
                alerts.append(f"ATTENZIONE: RAM a {ram_used_mb:.0f}MB")

            if status["cpu_percent"] > 80:
                alerts.append(f"CPU alta: {status['cpu_percent']}%")
        except Exception:
            status = {"error": "psutil non disponibile"}

        state_summary = "Stato interno nominale" if not alerts else f"{len(alerts)} allerte attive"

        entry = {"timestamp": datetime.now().isoformat(), "status": status, "alerts": alerts}
        self.metrics_history.append(entry)
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]

        self.bus.set("internal_state", entry)

        return {
            "state_summary": state_summary,
            "alerts": alerts,
            "resource_status": status,
        }

    async def sense(self) -> dict:
        return await self._sense_internal_state()

    def is_healthy(self) -> bool:
        if not self.metrics_history:
            return True
        last = self.metrics_history[-1]
        return len(last.get("alerts", [])) == 0
