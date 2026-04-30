"""SPEACE LLM — Cascade Router.

Energy-optimized LLM routing:
1. Local Ollama (gemma3:4b, qwen3:4b) — default, ~0 cost
2. Anthropic cloud (claude-haiku) — on-demand, requires approval
3. Mock/deterministic — offline fallback

BIOLOGICAL PRINCIPLE: The brain has a similar cascade:
- Reflex arcs (brainstem/spinal) — fast, automatic, no cortex
- Procedural (cerebellum/basal ganglia) — learned, efficient
- Deliberative (prefrontal cortex) — slow, expensive, used sparingly

SPEACE mirrors this: most responses use tiny local models (reflex),
cloud is only for complex reasoning that benefits from larger models.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any


class LLMRouter:
    """Cascade routing with energy budgeting."""

    def __init__(self, config: dict, state_bus):
        self.cfg = config.get("llm", {})
        self.bus = state_bus

        self.ollama_url = "http://localhost:11434"
        self.primary_model = self.cfg.get("primary", {}).get("model", "gemma3:4b")
        self.secondary_model = self.cfg.get("secondary", {}).get("model", "qwen3:4b")
        self.cloud_model = self.cfg.get("cloud_fallback", {}).get("model", "claude-haiku-4-5-20251001")
        self.require_cloud_approval = self.cfg.get("cloud_fallback", {}).get("require_approval", True)

        self.cloud_available = False  # Set to True if Anthropic key exists
        self.stats: dict[str, int] = {"ollama_calls": 0, "cloud_calls": 0, "mock_calls": 0}

    # ── Tier 1: Local Ollama ──

    async def _ollama_generate(self, prompt: str, system: str = "",
                                model: str = "", temperature: float = 0.65,
                                max_tokens: int = 512) -> dict:
        start = time.time()
        model = model or self.primary_model

        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                }
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.stats["ollama_calls"] += 1
                        return {
                            "content": data.get("response", ""),
                            "model": model,
                            "provider": "ollama",
                            "latency_ms": round((time.time() - start) * 1000, 1),
                        }
        except Exception:
            pass

        # Fallback: try secondary model
        if model != self.secondary_model:
            try:
                return await self._ollama_generate(
                    prompt, system, self.secondary_model, temperature, max_tokens
                )
            except Exception:
                pass

        return {"content": "", "model": model, "provider": "ollama",
                "error": "Ollama unavailable", "latency_ms": round((time.time() - start) * 1000, 1)}

    # ── Tier 2: Cloud Anthropic ──

    async def _cloud_generate(self, prompt: str, system: str = "",
                               temperature: float = 0.5, max_tokens: int = 1024) -> dict:
        if self.require_cloud_approval:
            self.bus.set("cloud_request_pending", {"prompt": prompt[:200], "timestamp": time.time()})
            return {"content": "", "provider": "anthropic",
                    "error": "Cloud approval required. Use 'approve-cloud' command."}

        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic()
            msg = await client.messages.create(
                model=self.cloud_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "Sei SPEACE, un cervello digitale bio-ispirato. Rispondi in italiano.",
                messages=[{"role": "user", "content": prompt}],
            )
            self.stats["cloud_calls"] += 1
            return {
                "content": msg.content[0].text,
                "model": self.cloud_model,
                "provider": "anthropic",
                "latency_ms": 0,  # Will be set by caller
            }
        except Exception as e:
            return {"content": "", "provider": "anthropic", "error": str(e)}

    # ── Tier 3: Mock (deterministic, always available) ──

    def _mock_generate(self, prompt: str) -> dict:
        self.stats["mock_calls"] += 1
        words = prompt.split()
        response = (
            f"[SPEACE — Risposta deterministica]\n"
            f"Il cervello digitale ha analizzato l'input ({len(words)} parole) "
            f"e risponde in modalità offline.\n"
            f"Prompt ricevuto: '{prompt[:150]}...'"
        )
        return {
            "content": response,
            "model": "mock/deterministic",
            "provider": "mock",
            "latency_ms": 0.5,
        }

    # ── Cascade Logic ──

    async def generate(self, prompt: str, system: str = "", role: str = "verbalizer",
                        temperature: float | None = None, max_tokens: int = 512) -> dict:
        """Cascade: local → cloud → mock."""
        temp = temperature or self.cfg.get("primary", {}).get("temperature", 0.65)

        model_map = {
            "verbalizer": self.primary_model,
            "planner": self.secondary_model,
            "executor": self.secondary_model,
            "critic": self.primary_model,
            "reflector": self.primary_model,
        }
        model = model_map.get(role, self.primary_model)

        # Tier 1: Local
        result = await self._ollama_generate(prompt, system, model, temp, max_tokens)
        if result.get("content"):
            return result

        # Tier 2: Cloud
        cloud_result = await self._cloud_generate(prompt, system, temp, max_tokens)
        if cloud_result.get("content"):
            return cloud_result

        # Tier 3: Mock
        return self._mock_generate(prompt)

    def enable_cloud(self):
        self.cloud_available = True

    def get_stats(self) -> dict:
        return dict(self.stats)
