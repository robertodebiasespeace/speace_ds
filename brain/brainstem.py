"""SPEACE Brain — Brainstem.

Autonomic regulation: heartbeat, sleep/wake, basic arousal.
Controls vital functions that must run 24/7 with minimal energy.

BIOLOGICAL PRINCIPLE: The brainstem is the oldest, most energy-efficient
part of the brain. It runs on autopilot via hardcoded neural circuits
(no learning needed = no plasticity overhead). SPEACE mimics this
with deterministic, lightweight cycle control.
"""

import time
from datetime import datetime


class Brainstem:

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.circadian_cfg = config.get("circadian", {})
        self.energy_cfg = config.get("energy", {})

        self.active_phase = self.circadian_cfg.get("active_phase_minutes", 16)
        self.consolidation_phase = self.circadian_cfg.get("consolidation_phase_minutes", 4)

        self.cycle_start = time.time()
        self.phase = "active"  # active or consolidation
        self.cycle_count = 0
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 10  # seconds

        self.graph.register_node(
            "BrainstemAutonomic",
            self._regulate_cycle,
            input_types={},
            output_types={"phase": str, "cycle_count": int, "next_switch_seconds": float},
            metadata={"region": "brainstem", "function": "autonomic_regulation"},
        )

    async def _regulate_cycle(self, inputs: dict = {}) -> dict:
        now = time.time()
        elapsed = now - self.cycle_start
        cycle_duration = (self.active_phase + self.consolidation_phase) * 60

        # Determine phase
        position_in_cycle = elapsed % cycle_duration
        active_seconds = self.active_phase * 60

        new_phase = "active" if position_in_cycle < active_seconds else "consolidation"

        if new_phase != self.phase:
            self.phase = new_phase
            self.cycle_count += 1
            self.bus.set("brainstem_phase", {"phase": self.phase, "cycle": self.cycle_count})

        # Heartbeat (basic system check)
        if now - self.last_heartbeat >= self.heartbeat_interval:
            self.last_heartbeat = now
            self.bus.set("heartbeat", {
                "timestamp": datetime.now().isoformat(),
                "phase": self.phase,
                "cycle": self.cycle_count,
            })

        next_switch = active_seconds - (position_in_cycle % active_seconds) \
            if self.phase == "active" else cycle_duration - position_in_cycle

        return {
            "phase": self.phase,
            "cycle_count": self.cycle_count,
            "next_switch_seconds": round(next_switch, 1),
        }

    def is_active(self) -> bool:
        return self.phase == "active"

    def should_consolidate(self) -> bool:
        return self.phase == "consolidation"

    async def regulate(self) -> dict:
        return await self._regulate_cycle()
