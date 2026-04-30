"""SPEACE Neuromodulation — Circadian Rhythm Oscillator.

Implements the sleep-wake cycle that governs energy management.
During active phase: full processing. During consolidation: memory
replay, pruning, energy recovery.

BIOLOGICAL PRINCIPLE: The suprachiasmatic nucleus (SCN) generates a ~24h
circadian rhythm that synchronizes every cell in the body. SPEACE uses
a shorter cycle (configurable, default 16min/4min) appropriate for digital
timescales. The principle is identical: active processing ↔ maintenance cycling.

Energy savings:
- Consolidation phase uses ~30% of active phase energy (no LLM calls,
  only local memory operations)
- Deep consolidation (once per "day") does full index rebuild + pruning
"""

import time
from datetime import datetime


class CircadianOscillator:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        circ_cfg = config.get("circadian", {})
        self.active_minutes = circ_cfg.get("active_phase_minutes", 16)
        self.consolidation_minutes = circ_cfg.get("consolidation_phase_minutes", 4)
        self.deep_consolidation_hour = circ_cfg.get("deep_consolidation_hour", 3)

        self.cycle_start = time.time()
        self.cycle_count = 0
        self.phase = "active"
        self.phase_start = time.time()

    @property
    def cycle_duration_minutes(self) -> float:
        return self.active_minutes + self.consolidation_minutes

    def tick(self) -> str:
        """Advance the oscillator. Return current phase."""
        now = time.time()
        elapsed = now - self.cycle_start
        cycle_s = self.cycle_duration_minutes * 60
        active_s = self.active_minutes * 60

        position = elapsed % cycle_s
        new_phase = "active" if position < active_s else "consolidation"

        if new_phase != self.phase:
            self.phase = new_phase
            self.phase_start = now
            if new_phase == "active":
                self.cycle_count += 1

        # Deep consolidation trigger
        now_dt = datetime.now()
        is_deep = (now_dt.hour == self.deep_consolidation_hour and
                   new_phase == "consolidation")

        state = {
            "phase": self.phase,
            "cycle": self.cycle_count,
            "is_deep_consolidation": is_deep,
            "time_in_phase_s": round(now - self.phase_start, 1),
            "next_phase": "consolidation" if self.phase == "active" else "active",
            "next_phase_in_s": round((active_s if self.phase != "active" else cycle_s) -
                                     (position % active_s if self.phase == "active" else
                                      position % (cycle_s - active_s) if self.phase != "active" else 0), 1),
        }
        self.bus.set("circadian", state)
        return self.phase

    def should_process(self) -> bool:
        return self.phase == "active"

    def should_consolidate(self) -> bool:
        return self.phase == "consolidation"

    def is_deep_consolidation(self) -> bool:
        now_dt = datetime.now()
        return (now_dt.hour == self.deep_consolidation_hour and
                self.phase == "consolidation")
