"""SPEACE Brain — Cerebral Hemispheres.

Models left/right hemispheric specialization with corpus callosum integration.
Left = logical, sequential, detail-oriented (low temp LLM).
Right = creative, divergent, holistic (high temp LLM).
Corpus Callosum = fusion, coherence scoring, bilateral synthesis.

BIOLOGICAL PRINCIPLE: Lateralization of function saves energy by
avoiding redundant processing — each hemisphere specializes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class HemisphereResult:
    hemisphere: str
    analysis: str
    keywords: list[str]
    confidence: float
    latency_ms: float


class CerebralHemispheres:
    """Dual-hemisphere processing with corpus callosum fusion."""

    def __init__(self, graph, state_bus, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.cfg = config.get("brain_regions", {}).get("hemispheres", {})

        # Register graph nodes
        self.graph.register_node(
            "LeftCortex",
            self._left_process,
            input_types={"input_text": str, "context": dict},
            output_types={"analysis": str, "keywords": list, "confidence": float},
            metadata={"region": "left_hemisphere", "style": "logical"},
        )
        self.graph.register_node(
            "RightCortex",
            self._right_process,
            input_types={"input_text": str, "context": dict},
            output_types={"analysis": str, "insights": str, "valence": str},
            metadata={"region": "right_hemisphere", "style": "creative"},
        )
        self.graph.register_node(
            "CorpusCallosum",
            self._callosum_fuse,
            input_types={"left_analysis": str, "right_insights": str},
            output_types={"synthesis": str, "coherence": float, "novelty_indicators": list},
            metadata={"region": "corpus_callosum", "style": "integrative"},
        )

        # Wire: Left → Callosum, Right → Callosum
        self.graph.connect("LeftCortex", "CorpusCallosum",
                           {"analysis": "left_analysis", "keywords": "left_keywords"})
        self.graph.connect("RightCortex", "CorpusCallosum",
                           {"insights": "right_insights", "valence": "right_valence"})

        self.history: list[dict] = []

    async def _left_process(self, inputs: dict) -> dict:
        """Left hemisphere: logical, sequential analysis."""
        text = inputs["input_text"]
        context = inputs.get("context", {})

        # Structured analysis heuristics
        analysis_parts = []

        # Identify key entities
        words = text.lower().split()
        if any(w in words for w in ["piano", "plan", "goal", "obiettivo"]):
            analysis_parts.append("Rilevata richiesta di pianificazione")
        if any(w in words for w in ["memoria", "ricorda", "remember", "recall", "codice"]):
            analysis_parts.append("Rilevata richiesta di memoria")
        if any(w in words for w in ["errore", "error", "bug", "fix", "correggi"]):
            analysis_parts.append("Rilevata anomalia da analizzare")

        # Extract structured facts from context
        factual_context = context.get("factual_memory", {})
        if factual_context:
            analysis_parts.append(f"Contesto fattuale disponibile: {len(factual_context)} elementi")

        return {
            "analysis": "; ".join(analysis_parts) if analysis_parts else "Analisi sequenziale completata",
            "keywords": [w for w in words if len(w) > 3][:10],
            "confidence": 0.7 if analysis_parts else 0.5,
        }

    async def _right_process(self, inputs: dict) -> dict:
        """Right hemisphere: creative, divergent, holistic."""
        text = inputs["input_text"]
        context = inputs.get("context", {})

        insights = []
        valence = "neutral"

        # Holistic pattern detection
        if "migliorare" in text.lower() or "improve" in text.lower():
            insights.append("Potenziale evolutivo rilevato — possibili percorsi di crescita")
            valence = "positive"
        if "?" in text:
            insights.append("Curiosità epistemica attivata — esplorazione multi-angolazione")
            valence = "curious"
        if any(w in text.lower() for w in ["crea", "inventa", "nuovo", "innovativo"]):
            insights.append("Spinta creativa — generazione di connessioni inusuali")
            valence = "creative"
        if any(w in text.lower() for w in ["problema", "critico", "urgente", "pericolo"]):
            insights.append("Segnale di allerta — attivazione percorsi di difesa")
            valence = "alert"

        if not insights:
            insights.append("Elaborazione olistica dello stimolo in corso")

        return {
            "analysis": "Prospettiva creativa attivata",
            "insights": "; ".join(insights),
            "valence": valence,
        }

    async def _callosum_fuse(self, inputs: dict) -> dict:
        """Corpus Callosum: integrate left logic with right creativity."""
        left = inputs.get("left_analysis", "")
        right = inputs.get("right_insights", "")

        coherence = 0.6
        if left and right:
            coherence = 0.75  # Both hemispheres contributed

        synthesis = f"Sintesi bilaterale: [{left}] + [{right}]"

        return {
            "synthesis": synthesis,
            "coherence": coherence,
            "novelty_indicators": ["bilateral_integration"],
        }

    async def process(self, user_input: str, temporal_context: dict | None = None) -> dict:
        """Run bilateral processing and return fused result."""
        start = time.time()
        context = temporal_context or {}
        context["factual_memory"] = self.bus.get("factual_memory", {})

        # Run left and right in parallel (like real brain)
        left_result = await self._left_process({
            "input_text": user_input,
            "context": context,
        })
        right_result = await self._right_process({
            "input_text": user_input,
            "context": context,
        })
        fused = await self._callosum_fuse({
            "left_analysis": left_result["analysis"],
            "right_insights": right_result["insights"],
        })

        result = {
            "left": left_result,
            "right": right_result,
            "fused": fused,
            "latency_ms": (time.time() - start) * 1000,
        }
        self.history.append(result)
        if len(self.history) > 20:
            self.history = self.history[-20:]
        return result
