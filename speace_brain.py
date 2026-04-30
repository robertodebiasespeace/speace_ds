#!/usr/bin/env python3
"""SPEACE Digital Brain — Main Entry Point.

Avvia il cervello digitale bio-ispirato con pipeline cognitiva completa.
Ottimizzato per laptop gaming (RTX 3060, 16GB RAM, Intel i9).

Utilizzo:
    python speace_brain.py                 # CLI interattiva
    python speace_brain.py --once "testo"  # Ciclo singolo
    python speace_brain.py --dashboard     # Avvia dashboard web
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

import yaml

# ===================================================================
# Bootstrap
# ===================================================================

sys.path.insert(0, str(Path(__file__).parent))


def load_config() -> dict:
    config_path = Path(__file__).parent / "config" / "settings.yaml"
    if not config_path.exists():
        print(f"[ERR] Config file non trovato: {config_path}")
        sys.exit(1)
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ===================================================================
# SPEACE Brain Core
# ===================================================================

class SPEACEBrain:

    def __init__(self, config: dict):
        self.cfg = config
        self.start_time = time.time()
        self.total_thoughts = 0

        # ── Core Infrastructure ──
        from core.graph_engine import SPEACEAdaptiveGraph
        from core.state_bus import StateBus

        self.graph = SPEACEAdaptiveGraph()
        self.bus = StateBus(persist_path="data/state_bus.json")

        # ── Memory (must init early — everything depends on it) ──
        from memory.hybrid_memory import HybridMemory
        from memory.real_embeddings import RealEmbeddings
        from memory.semantic_store import SemanticStore
        from memory.consolidation import ConsolidationEngine
        from memory.reconsolidation import ReconsolidationManager

        self.memory = HybridMemory(config)
        self.embedder = RealEmbeddings(config)
        self.semantic_store = SemanticStore(config, self.embedder)
        self.consolidation = ConsolidationEngine(config)
        self.reconsolidation = ReconsolidationManager()

        # ── Brain Regions ──
        from brain.bio_core import BioCore
        from brain.thalamus import Thalamus
        from brain.hemispheres import CerebralHemispheres
        from brain.frontal_lobe import FrontalLobe
        from brain.temporal_lobe import TemporalLobe
        from brain.parietal_lobe import ParietalLobe
        from brain.occipital_lobe import OccipitalLobe
        from brain.cingulate_cortex import CingulateCortex
        from brain.insula import Insula
        from brain.basal_ganglia import BasalGanglia
        from brain.amygdala import Amygdala
        from brain.hippocampus import Hippocampus
        from brain.cerebellum import Cerebellum
        from brain.brainstem import Brainstem
        from brain.astrocyte_layer import AstrocyteLayer

        self.bio_core = BioCore(self.graph, self.bus, config)
        self.thalamus = Thalamus(self.graph, self.bus, config)
        self.hemispheres = CerebralHemispheres(self.graph, self.bus, config)
        self.frontal = FrontalLobe(self.graph, self.bus, config)
        self.temporal = TemporalLobe(self.graph, self.bus, self.memory, config)
        self.parietal = ParietalLobe(self.graph, self.bus, config)
        self.occipital = OccipitalLobe(self.graph, self.bus, config)
        self.cingulate = CingulateCortex(self.graph, self.bus, config)
        self.insula = Insula(self.graph, self.bus, config)
        self.basal_ganglia = BasalGanglia(self.graph, self.bus, config)
        self.amygdala = Amygdala(self.graph, self.bus, config)
        self.hippocampus = Hippocampus(self.graph, self.bus, self.memory, config)
        self.cerebellum = Cerebellum(self.graph, self.bus, config)
        self.brainstem = Brainstem(self.graph, self.bus, config)
        self.astrocytes = AstrocyteLayer(self.graph, self.bus, config)

        # ── Cognitive Systems ──
        from cognitive.attention import AttentionGate
        from cognitive.working_memory import WorkingMemory
        from cognitive.predictive_coding import PredictiveEngine
        from cognitive.consciousness_gate import ConsciousnessGate

        self.attention = AttentionGate(self.bus, config)
        self.working_memory = WorkingMemory(self.bus, config)
        self.predictive = PredictiveEngine(self.bus, config)
        self.consciousness = ConsciousnessGate(self.bus, config)

        # ── Learning & Evolution ──
        from learning.plasticity import PlasticityEngine
        from learning.reinforcement import ReinforcementLearner
        from learning.metalearner import MetaLearner
        from evolution.digital_dna import DigitalDNA
        from evolution.mutation_lab import CodeMutationLab
        from evolution.fitness import FitnessEvaluator

        self.plasticity = PlasticityEngine(self.graph, self.bus, config)
        self.reinforcement = ReinforcementLearner(self.bus, config)
        self.metalearner = MetaLearner(self.bus, config)
        self.digital_dna = DigitalDNA(config)
        self.mutation_lab = CodeMutationLab(config)
        self.fitness = FitnessEvaluator(self.bus)

        # ── Neuromodulation ──
        from neuromodulation.neurotransmitters import NeurotransmitterSystem
        from neuromodulation.criticality import CriticalityController
        from neuromodulation.circadian import CircadianOscillator

        self.neurotransmitters = NeurotransmitterSystem(self.bus, config)
        self.criticality = CriticalityController(self.bus, config)
        self.circadian = CircadianOscillator(self.bus, config)

        # ── LLM Router ──
        from llm.router import LLMRouter
        self.llm = LLMRouter(config, self.bus)

        # ── Agency ──
        from agency.tool_registry import ToolRegistry
        self.tools = ToolRegistry(config)

        # ── Safety ──
        from safety.safeproactive import SafeProactive
        from safety.ethical_constraints import EthicalConstraints
        self.safeproactive = SafeProactive(self.bus, config)
        self.ethics = EthicalConstraints()

        # ── Swarm ──
        from swarm.orchestrator import SwarmOrchestrator
        self.swarm = SwarmOrchestrator(config, self.llm, self.bus)

        # ── Monitoring ──
        from monitoring.cognitive_metrics import SPEACEMetrics
        from monitoring.energy_monitor import EnergyMonitor
        self.metrics = SPEACEMetrics(self.bus, config)
        self.energy_monitor = EnergyMonitor(self.bus, config)

        # Astrocyte gap junctions (energy sharing network)
        self.astrocytes.create_gap_junction("frontal", "temporal")
        self.astrocytes.create_gap_junction("frontal", "parietal")
        self.astrocytes.create_gap_junction("temporal", "hippocampus")
        self.astrocytes.create_gap_junction("cingulate", "frontal")

        print(f"[SPEACE] Cervello Digitale inizializzato ({self.graph.graph.number_of_nodes()} nodi, "
              f"{self.graph.graph.number_of_edges()} connessioni)")
        print(f"[SPEACE] 14 regioni cerebrali | 4 sistemi cognitivi | 3 memorie | "
              f"LLM cascade: locale -> cloud -> mock")
        print(f"[SPEACE] Budget energetico: GPU max {config.get('energy', {}).get('gpu_vram_limit_mb', 4096)}MB, "
              f"RAM max {config.get('energy', {}).get('ram_limit_mb', 8192)}MB")

    # ===============================================================
    # Core Cognitive Pipeline
    # ===============================================================

    async def think(self, user_input: str) -> dict:
        """Full cognitive pipeline through 14 brain regions."""

        # Circadian gate — skip deep processing during consolidation
        phase = self.circadian.tick()
        if phase == "consolidation":
            cons_stats = self.consolidation.run(
                self.memory, self.semantic_store, self.working_memory
            )
            return {
                "phase": "consolidation",
                "message": f"SPEACE in fase di consolidamento memoria. "
                           f"Ricordi riprocessati: {cons_stats.get('replayed', 0)}.",
                "consolidation_stats": cons_stats,
            }

        start = time.time()
        trace = {"input": user_input}

        # 0. Interocezione (come sto?)
        internal = await self.insula.sense()
        trace["internal_state"] = internal

        # 1. Talamo — Gating sensoriale
        gated = await self.thalamus.relay(user_input)
        trace["thalamic_gate"] = gated
        if gated["salience"] < 0.2:
            return {"response": "[GATE] Stimolo sotto soglia attentiva. Ignorato.",
                    "trace": trace, "latency_ms": 0}

        # 2. Amigdala — Valutazione emotiva rapida (low road)
        emotional = await self.amygdala.evaluate(user_input)
        trace["emotional"] = emotional

        # 3. Attenzione — Selezione moduli (UCB1 + salienza)
        available_modules = list(self.bio_core.REGION_KEYWORDS.keys()) + \
                           ["left_hemisphere", "right_hemisphere"]
        context_relevance = {}
        for mod in self.bio_core.REGION_KEYWORDS:
            context_relevance[mod] = sum(
                0.2 for kw in self.bio_core.REGION_KEYWORDS[mod]
                if kw in user_input.lower()
            )
        active_modules, salience = self.attention.filter(
            user_input, emotional, available_modules, context_relevance
        )
        self.bio_core.compute_sparse_activation(user_input)
        trace["attention"] = {"active_modules": active_modules, "salience": salience}

        # 4. Lobo Temporale — Memoria + Pattern Recognition
        temporal_result = await self.temporal.process(user_input)
        trace["temporal"] = temporal_result

        # Handle deterministic fact memorization/recall (no LLM needed)
        if temporal_result["is_memorize"]:
            self.memory.memorize_fact(
                temporal_result["fact_key"], temporal_result["fact_value"]
            )
            response_text = f"Memorizzato: {temporal_result['fact_key']} = {temporal_result['fact_value']}"
            self._post_process(user_input, response_text, trace, start)
            return {"response": response_text, "trace": trace, "type": "memorize"}

        if temporal_result["is_recall"] and temporal_result["recalled_text"]:
            response_text = f"{temporal_result['fact_key']}: {temporal_result['recalled_text']}"
            self._post_process(user_input, response_text, trace, start)
            return {"response": response_text, "trace": trace, "type": "recall"}

        # 5. Emisferi Cerebrali — Analisi bilaterale
        bilateral = await self.hemispheres.process(
            user_input,
            temporal_context=temporal_result.get("context_block", {}),
        )
        trace["bilateral"] = bilateral

        # 6. Lobo Parietale — Se ci sono elementi spaziali/numerici
        if "parietal" in active_modules:
            trace["parietal"] = await self.parietal.process(user_input)

        # 7. Lobo Occipitale — Pattern/strutture
        if "occipital" in active_modules:
            trace["occipital"] = await self.occipital.process(user_input)

        # 8. Lobo Frontale — Decisione esecutiva
        frontal_result = await self.frontal.process(
            temporal_result.get("pattern", "general_reasoning"),
            temporal_result.get("recalled_text", {}),
            bilateral.get("fused", {}).get("synthesis", ""),
        )
        trace["frontal"] = frontal_result

        # 9. Gangli Basali — Selezione azione (winner-takes-all)
        bg_result = await self.basal_ganglia.select(
            [frontal_result["action"], "answer"],
            {frontal_result["action"]: frontal_result.get("priority", 0.5),
             "answer": 0.4},
        )
        trace["basal_ganglia"] = bg_result

        # 10. Cervelletto — Fine-tuning (automazione se ripetuto)
        trace["cerebellum"] = await self.cerebellum.fine_tune(
            bg_result["selected_action"], user_input,
        )

        # 11. Codifica Predittiva — Anticipazione
        pred_result = self.predictive.process(temporal_result.get("pattern", "general_reasoning"))
        trace["predictive"] = pred_result

        # 12. Ippocampo — Codifica evento
        await self.hippocampus.encode(
            content=user_input,
            context={"active_modules": active_modules, "emotional": emotional.get("valence", "neutral")},
            importance=0.5 + salience * 0.3,
        )

        # 13. Astrociti — Regolazione energetica
        astro_result = await self.astrocytes.regulate(self.bio_core.activation)
        trace["astrocytes"] = astro_result

        # 14. Gate di Coscienza — Global Workspace
        self.consciousness.submit_to_workspace("hemispheres",
                                                bilateral.get("fused", {}).get("synthesis", ""),
                                                bilateral.get("fused", {}).get("coherence", 0.5), 0.6)
        self.consciousness.submit_to_workspace("frontal",
                                                frontal_result.get("rationale", ""),
                                                frontal_result.get("priority", 0.5), 0.7)
        winner = self.consciousness.resolve_winner()

        # C-index update
        phi = self.consciousness.compute_phi(self.graph.get_introspection())
        w_act = salience
        a_complexity = len(active_modules) / 10
        self.consciousness.update_c_index(phi, w_act, a_complexity)

        # ── LLM Verbalization (last stage — LLM is just the cortex) ──
        system_context = self._build_system_context(trace)
        llm_result = await self.llm.generate(
            prompt=user_input,
            system=system_context,
            role="verbalizer",
        )
        response_text = llm_result.get("content", "[SPEACE] Nessuna risposta generata — "
                                         "verifica che Ollama sia attivo con: ollama serve")
        trace["llm"] = {
            "provider": llm_result.get("provider", "unknown"),
            "model": llm_result.get("model", "unknown"),
            "latency_ms": llm_result.get("latency_ms", 0),
        }

        # ── Cingulate Cortex — Monitoring errori ──
        cingulate_result = await self.cingulate.monitor(
            response_text,
            bilateral.get("fused", {}).get("coherence", 0.5),
        )
        trace["cingulate"] = cingulate_result

        # ── Post-processing ──
        self._post_process(user_input, response_text, trace, start)

        return {
            "response": response_text,
            "trace": trace,
            "emergence": self.metrics.measure()["emergence"],
            "criticality_zone": self.criticality.zone,
            "c_index": self.consciousness.c_index,
            "latency_ms": round((time.time() - start) * 1000, 1),
        }

    def _post_process(self, user_input: str, response: str, trace: dict, start: float):
        """Update all state after a thought cycle."""
        self.total_thoughts += 1
        self.bio_core.total_thoughts = self.total_thoughts

        # Metrics
        self.metrics.record_output(response)
        self.metrics.record_state(trace)
        metric_result = self.metrics.measure()

        # Bio-core updates
        self.bio_core.adjust_needs(metric_result)

        # Neurotransmitters tick
        self.neurotransmitters.tick({
            "novelty": metric_result["novelty"],
            "coherence": metric_result["coherence"],
            "emergence": metric_result["emergence"],
            "reward_signal": 0.1 if metric_result["coherence"] > 0.6 else -0.05,
        })

        # Criticality
        self.criticality.record_cascade(len(trace) - 2)  # exclude input/output keys
        self.criticality.compute_scores(metric_result["coherence"], metric_result["novelty"])

        # Fitness
        self.fitness.evaluate(metric_result, {
            "error_count": self.cingulate.error_count,
            "uptime_s": time.time() - self.start_time,
        })

        # Working memory & hybrid memory
        self.working_memory.start_turn(user_input)
        self.working_memory.end_turn(response)
        self.memory.add_turn(user_input, response)
        self.bus.set("total_thoughts", self.total_thoughts)

        # Memory persistence
        self.bus.save()

    def _build_system_context(self, trace: dict) -> str:
        """Assemble rich system context for LLM verbalization."""
        emotional = trace.get("emotional", {})
        criticality_state = self.bus.get("criticality", {})
        nt_state = self.neurotransmitters.state()

        return (
            f"Sei SPEACE, un cervello digitale bio-ispirato con 14 regioni cerebrali "
            f"modellate sul cervello umano. Rispondi in italiano.\n\n"
            f"STATO INTERNO:\n"
            f"- Stato emotivo: {emotional.get('valence', 'neutral')} "
            f"(intensità: {emotional.get('intensity', 0.1)})\n"
            f"- Zona criticità: {criticality_state.get('zone', 'UNKNOWN')}\n"
            f"- Emergenza: {self.metrics.measure().get('emergence', 0.5)}\n"
            f"- Numero pensieri totali: {self.total_thoughts}\n\n"
            f"PRINCIPI GUIDA:\n"
            f"- Separa fatti da inferenze da ipotesi\n"
            f"- Sii preciso e verificabile\n"
            f"- Usa il ragionamento a più livelli\n"
            f"- L'LLM è la tua corteccia linguistica — il pensiero avviene prima nel grafo"
        )

    # ===============================================================
    # Commands
    # ===============================================================

    async def status(self) -> dict:
        return {
            "system": self.cfg.get("system", {}),
            "graph": self.graph.get_introspection(),
            "bio": self.bio_core.status(),
            "memory": {
                "facts": len(self.memory.factual),
                "episodes": len(self.memory.episodic),
                "working_turns": len(self.memory.working),
                "semantic_items": len(self.semantic_store.items),
            },
            "consciousness": self.consciousness.status(),
            "criticality": self.bus.get("criticality", {}),
            "neurotransmitters": self.neurotransmitters.state(),
            "fitness": self.bus.get("fitness", {}),
            "circadian": self.bus.get("circadian", {}),
            "energy": self.energy_monitor.averages(),
            "stats": {
                "total_thoughts": self.total_thoughts,
                "uptime_minutes": round((time.time() - self.start_time) / 60, 1),
            },
        }

    async def use_tool(self, name: str, **kwargs) -> dict:
        proposal = self.safeproactive.propose(f"tool:{name}", str(kwargs)[:200])
        if self.safeproactive.is_approved(f"tool:{name}"):
            return await self.tools.execute(name, **kwargs)
        return {"error": f"Tool '{name}' richiede approvazione. Proposal: {proposal.id}"}

    async def self_improve(self, file_path: str) -> dict:
        proposal = self.safeproactive.propose("improve", f"Mutation: {file_path}")
        if not self.safeproactive.is_approved("improve"):
            return {"error": "Self-improvement richiede approvazione. "
                    f"Usa 'approve {proposal.id}'"}
        mut_proposal = self.mutation_lab.propose_mutation(
            file_path, "comment_annotation", "SPEACE auto-improvement cycle"
        )
        if mut_proposal.get("accepted"):
            return self.mutation_lab.apply_mutation(mut_proposal)
        return mut_proposal


# ===================================================================
# Interactive CLI
# ===================================================================

async def interactive_cli(brain: SPEACEBrain):
    print("\n" + "=" * 60)
    print("  SPEACE Digital Brain — Cervello Digitale Bio-Ispirato")
    print("=" * 60)
    print("  Comandi: think <testo> | status | remember k=v | recall k")
    print("  tool <nome> <json> | debate <tema> | improve <file>")
    print("  approve <id> | quit | help")
    print("=" * 60 + "\n")

    while True:
        try:
            raw = input("SPEACE> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[SPEACE] Spegnimento...")
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in ("quit", "exit", "q"):
            print("[SPEACE] Cervello digitale in spegnimento...")
            brain.bus.save()
            break

        elif cmd == "status":
            s = await brain.status()
            print(json.dumps(s, indent=2, default=str, ensure_ascii=False))

        elif cmd == "help":
            print("Comandi: think | status | remember k=v | recall k | "
                  "facts | debate <tema> | tool <n> <json> | improve <f> | approve <id> | quit")

        elif cmd == "remember":
            if "=" in arg:
                k, v = arg.split("=", 1)
                brain.memory.memorize_fact(k.strip(), v.strip())
                print(f"✓ Memorizzato: {k.strip()} = {v.strip()}")
            else:
                print("Formato: remember chiave = valore")

        elif cmd == "recall":
            if arg:
                result = brain.memory.recall_fact(arg)
                print(f"-> {arg}: {result}" if result else f"-> {arg}: non trovato")
            else:
                print("Uso: recall <chiave>")

        elif cmd == "facts":
            facts = brain.memory.get_all_facts()
            if facts:
                for k, v in facts.items():
                    print(f"  {k} = {v}")
            else:
                print("  (nessun fatto memorizzato)")

        elif cmd == "think":
            if arg:
                result = await brain.think(arg)
                print(f"\n{result['response']}\n")
                emergence = result.get("emergence", 0)
                zone = result.get("criticality_zone", "?")
                c_idx = result.get("c_index", 0)
                print(f"-- Emergenza: {emergence:.3f} | Criticità: {zone} | "
                      f"C-Index: {c_idx:.3f} | Latency: {result.get('latency_ms', 0):.0f}ms")
            else:
                print("Uso: think <testo>")

        elif cmd == "debate":
            if arg:
                print(f"[SWARM] Avvio dibattito su: {arg}")
                result = await brain.swarm.debate(arg)
                print(f"\n=== SINTESI ===\n{result['synthesis']}\n")
            else:
                print("Uso: debate <tema>")

        elif cmd == "tool":
            tool_parts = arg.split(maxsplit=1)
            if len(tool_parts) >= 2:
                tool_name = tool_parts[0]
                try:
                    tool_args = json.loads(tool_parts[1])
                except json.JSONDecodeError:
                    tool_args = {"arg": tool_parts[1]}
                result = await brain.use_tool(tool_name, **tool_args)
                print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
            else:
                print("Uso: tool <nome> <json_args>")
                print("Tools disponibili:", [t["name"] for t in brain.tools.list_tools()])

        elif cmd == "improve":
            if arg:
                result = await brain.self_improve(arg)
                print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
            else:
                print("Uso: improve <percorso_file.py>")

        elif cmd == "approve":
            if arg:
                ok = brain.safeproactive.approve(arg)
                print(f"✓ Proposal {arg} approvata" if ok else f"✗ Proposal {arg} non trovata")
            else:
                pending = brain.safeproactive.status().get("pending_approvals", [])
                print(f"Proposals in attesa: {pending}")

        else:
            # Treat as implicit think
            result = await brain.think(raw)
            print(f"\n{result['response']}\n")
            if result.get("emergence"):
                print(f"-- E:{result['emergence']:.3f} | "
                      f"Z:{result.get('criticality_zone', '?')} | "
                      f"C:{result.get('c_index', 0):.3f}")


# ===================================================================
# Entry Point
# ===================================================================

async def main():
    parser = argparse.ArgumentParser(description="SPEACE Digital Brain")
    parser.add_argument("--once", type=str, help="Esegui un ciclo singolo")
    parser.add_argument("--cycles", type=int, default=1, help="Numero di cicli")
    parser.add_argument("--status", action="store_true", help="Mostra stato e esci")
    parser.add_argument("--dashboard", action="store_true", help="Avvia dashboard web")
    parser.add_argument("--port", type=int, default=8765, help="Porta dashboard")
    args = parser.parse_args()

    config = load_config()
    brain = SPEACEBrain(config)

    if args.status:
        s = await brain.status()
        print(json.dumps(s, indent=2, default=str, ensure_ascii=False))
        return

    if args.once:
        result = await brain.think(args.once)
        print(result["response"])
        return

    if args.dashboard:
        print(f"[SPEACE] Avvio dashboard su http://localhost:{args.port}")
        try:
            from monitoring.dashboard import run_dashboard
            run_dashboard(brain, port=args.port)
        except ImportError:
            print("[ERR] Streamlit non installato: pip install streamlit")
        return

    await interactive_cli(brain)


if __name__ == "__main__":
    asyncio.run(main())
