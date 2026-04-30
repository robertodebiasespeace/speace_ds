"""SPEACE Monitoring — Energy Budget Tracker.

Tracks resource usage against configured limits for the RTX 3060 laptop.
Alerts and throttles when approaching energy/thermal limits.

BIOLOGICAL PRINCIPLE: The hypothalamus monitors body temperature, blood
glucose, and hydration — automatically triggering corrective responses
(sweating, hunger, thirst) without conscious intervention.

SPEACE energy monitor does the same: automatic throttling when GPU/RAM
usage exceeds budget, before the OS OOM-killer or thermal throttle kicks in.
"""

import time
from datetime import datetime


class EnergyMonitor:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        energy_cfg = config.get("energy", {})
        mon_cfg = config.get("monitoring", {}).get("energy_monitor", {})

        self.gpu_vram_limit = energy_cfg.get("gpu_vram_limit_mb", 4096)
        self.ram_limit = energy_cfg.get("ram_limit_mb", 8192)
        self.target_gpu_power = energy_cfg.get("target_gpu_power_w", 50)
        self.sample_interval = mon_cfg.get("sample_interval_seconds", 10)
        self.alert_gpu = mon_cfg.get("alert_on_gpu_exceed", 70)
        self.alert_ram = mon_cfg.get("alert_on_ram_exceed_mb", 7000)

        self.samples: list[dict] = []
        self.last_sample = 0.0
        self.throttle_active = False

    async def sample(self):
        """Take one resource measurement. Called periodically."""
        now = time.time()
        if now - self.last_sample < self.sample_interval:
            return
        self.last_sample = now

        try:
            import psutil
            mem = psutil.virtual_memory()
            ram_used = mem.used / (1024 * 1024)

            sample = {
                "timestamp": datetime.now().isoformat(),
                "ram_used_mb": round(ram_used, 1),
                "ram_percent": mem.percent,
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "processes": len(psutil.pids()),
            }

            # GPU (if available via nvidia-smi)
            try:
                import subprocess
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,power.draw,temperature.gpu",
                     "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    parts = [x.strip() for x in result.stdout.split(",")]
                    if len(parts) >= 4:
                        sample["gpu_util_percent"] = float(parts[0])
                        sample["gpu_vram_mb"] = float(parts[1])
                        sample["gpu_power_w"] = float(parts[2])
                        sample["gpu_temp_c"] = float(parts[3])
            except Exception:
                pass

            # Check limits
            alerts = []
            if sample.get("gpu_power_w", 0) > self.alert_gpu:
                alerts.append(f"GPU power alert: {sample['gpu_power_w']}W > {self.alert_gpu}W")
            if sample.get("ram_used_mb", 0) > self.alert_ram:
                alerts.append(f"RAM alert: {sample['ram_used_mb']:.0f}MB > {self.alert_ram}MB")
            if sample.get("gpu_temp_c", 0) > 85:
                alerts.append(f"GPU thermal alert: {sample['gpu_temp_c']}°C")

            sample["alerts"] = alerts

        except Exception:
            sample = {"timestamp": datetime.now().isoformat(), "error": "psutil unavailable"}

        self.samples.append(sample)
        if len(self.samples) > 200:
            self.samples = self.samples[-200:]

        self.bus.set("energy_sample", sample)

        # Auto-throttle
        if sample.get("alerts"):
            self.throttle_active = True
            self.bus.set("throttle", {"active": True, "reason": sample["alerts"]})
        elif self.throttle_active:
            self.throttle_active = False
            self.bus.set("throttle", {"active": False, "reason": ""})

    def recent(self, n: int = 10) -> list[dict]:
        return self.samples[-n:]

    def averages(self, n: int = 10) -> dict:
        recent = self.samples[-n:] if self.samples else []
        if not recent:
            return {}

        avg = {}
        for key in ["ram_used_mb", "gpu_power_w", "gpu_temp_c"]:
            vals = [s[key] for s in recent if key in s]
            if vals:
                avg[key] = round(sum(vals) / len(vals), 1)

        return avg

    def should_throttle(self) -> bool:
        return self.throttle_active
