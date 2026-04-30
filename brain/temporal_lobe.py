"""SPEACE Brain — Temporal Lobe.

Memory processing, pattern recognition, and language comprehension.
Routes between recall (memory retrieval) and memorize (encoding) modes.

BIOLOGICAL PRINCIPLE: The temporal lobe uses sparse pattern completion —
a partial cue reactivates the full memory via attractor dynamics,
which is far more efficient than exhaustive search.
"""

from __future__ import annotations

import re
import time


class TemporalLobe:
    """Memory input processing with pattern recognition."""

    def __init__(self, graph, state_bus, memory_system, config: dict):
        self.graph = graph
        self.bus = state_bus
        self.memory = memory_system
        self.cfg = config.get("brain_regions", {}).get("temporal", {})

        self.graph.register_node(
            "TemporalMemory",
            self._memory_process,
            input_types={"query": str, "user_input": str},
            output_types={"is_memorize": bool, "is_recall": bool, "fact_key": str,
                          "fact_value": str, "recalled_text": str, "context_block": dict},
            metadata={"region": "temporal", "function": "memory_relay"},
        )
        self.graph.register_node(
            "TemporalPatternRecognition",
            self._pattern_process,
            input_types={"query": str, "recalled_text": str},
            output_types={"pattern": str, "confidence": float, "keywords": list},
            metadata={"region": "temporal", "function": "pattern_recognition"},
        )
        self.graph.connect("TemporalMemory", "TemporalPatternRecognition",
                           {"recalled_text": "recalled_text"})

    # ── Fact extraction regex (Italian + English) ──
    FACT_MEMORIZE_RE = re.compile(
        r"(?:memorizza|ricorda|remember|memorize)\s+"
        r"(?:che\s+)?(?:il\s+)?(?:la\s+)?"
        r"([\w\sàèìòù\-\+]+?)\s*(?:è|e'|è|is|=|:)\s*(.+)",
        re.IGNORECASE,
    )
    FACT_KEYVALUE_RE = re.compile(
        r"([\w\sàèìòù\-\+]+?)\s*=\s*(.+)"
    )
    RECALL_RE = re.compile(
        r"(?:qual(?:'è|e'| è|è|e)\s+(?:il|la|lo|l')\s+)?"
        r"(?:ricorda|recall|recupera|retrieve|dimmi|qual è il)\s+"
        r"([\w\sàèìòù\-\+]+)",
        re.IGNORECASE,
    )
    QUESTION_RE = re.compile(
        r"(?:qual(?:'è|e'| è|è|e)\s+|cos(?:'è|e'| è|è|a\s+(?:è|e'))\s+|"
        r"chi\s+(?:è|e'|ha)\s+|come\s+|perché|perche'|quando\s+|dove\s+|"
        r"what\s+is\s+|who\s+is\s+|how\s+|why\s+|when\s+|where\s+)",
        re.IGNORECASE,
    )

    async def _memory_process(self, inputs: dict) -> dict:
        """Detect memorize/recall commands and route accordingly."""
        user_input = inputs.get("user_input", inputs.get("query", ""))
        text = user_input.strip()

        result = {
            "is_memorize": False,
            "is_recall": False,
            "fact_key": "",
            "fact_value": "",
            "recalled_text": "",
            "context_block": {},
        }

        # 1. Check for explicit memorize command
        m = self.FACT_MEMORIZE_RE.search(text)
        if not m and not self.QUESTION_RE.search(text):
            m = self.FACT_KEYVALUE_RE.search(text)
        if m:
            result["is_memorize"] = True
            result["fact_key"] = m.group(1).strip()
            result["fact_value"] = m.group(2).strip()

        # 2. Check for recall command
        if not result["is_memorize"]:
            r = self.RECALL_RE.search(text)
            if r:
                key_candidate = r.group(1).strip()
                fact = self.memory.recall_fact(key_candidate) if hasattr(self.memory, 'recall_fact') else None
                result["is_recall"] = True
                result["fact_key"] = key_candidate
                result["recalled_text"] = fact if fact else ""

        # 3. Try direct recall even without explicit command (for question-like input)
        if not result["is_memorize"] and not result["is_recall"]:
            for key, value in (getattr(self.memory, 'factual_memory', {}) or {}).items():
                if key.lower() in text.lower():
                    result["is_recall"] = True
                    result["fact_key"] = key
                    result["recalled_text"] = str(value)
                    break

        # 4. Build context block
        if hasattr(self.memory, 'context_block'):
            result["context_block"] = self.memory.context_block(text)

        return result

    async def _pattern_process(self, inputs: dict) -> dict:
        """Classify the input into a cognitive pattern type using keyword analysis."""
        query = inputs.get("query", "")
        recalled = inputs.get("recalled_text", "")
        text = f"{query} {recalled}".lower()

        patterns = {
            "factual_memory_request": ["memoria", "ricorda", "memorizza", "codice", "fact",
                                        "remember", "recall", "store", "save"],
            "self_improvement_request": ["migliora", "ottimizza", "evolvi", "mutazione",
                                          "improve", "optimize", "evolve", "enhance", "fix"],
            "planning_request": ["piano", "pianifica", "goal", "obiettivo", "strategia",
                                 "plan", "schedule", "organize", "roadmap"],
            "general_reasoning": ["spiega", "analizza", "pensa", "ragiona",
                                  "explain", "analyze", "think", "reason", "why", "how"],
        }

        scores = {}
        for pattern, keywords in patterns.items():
            score = sum(1.0 for kw in keywords if kw in text)
            scores[pattern] = score

        best = max(scores, key=scores.get)
        confidence = min(1.0, scores[best] / max(3, len(patterns[best])))

        # Extract keywords from input
        words = [w for w in query.lower().split() if len(w) > 3 and w.isalpha()]

        return {
            "pattern": best if scores[best] > 0 else "general_reasoning",
            "confidence": confidence,
            "keywords": words[:10],
        }

    async def process(self, user_input: str) -> dict:
        """Run memory → pattern chain."""
        start = time.time()
        mem_result = await self._memory_process({
            "query": user_input,
            "user_input": user_input,
        })
        pat_result = await self._pattern_process({
            "query": user_input,
            "recalled_text": mem_result.get("recalled_text", ""),
        })

        return {
            "is_memorize": mem_result["is_memorize"],
            "is_recall": mem_result["is_recall"],
            "fact_key": mem_result["fact_key"],
            "fact_value": mem_result["fact_value"],
            "recalled_text": mem_result.get("recalled_text", ""),
            "context_block": mem_result.get("context_block", {}),
            "pattern": pat_result["pattern"],
            "pattern_confidence": pat_result["confidence"],
            "keywords": pat_result.get("keywords", []),
            "latency_ms": (time.time() - start) * 1000,
        }
