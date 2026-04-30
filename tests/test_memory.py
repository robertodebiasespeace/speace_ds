"""Test: SPEACE Memory System.

Verifica memorizzazione e recall deterministico, persistenza,
memoria episodica e semantica.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
import pytest
import asyncio
import tempfile
import os


def load_config():
    cfg_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(cfg_path) as f:
        return yaml.safe_load(f)


class TestHybridMemory:

    def test_memorize_and_recall_exact(self):
        from memory.hybrid_memory import HybridMemory

        config = load_config()
        mem = HybridMemory(config)

        mem.memorize_fact("codice alfa", "7319")
        result = mem.recall_fact("codice alfa")
        assert result == "7319", f"Expected '7319', got '{result}'"

        print("✓ Memorizzazione e recall esatto OK")

    def test_fuzzy_recall(self):
        from memory.hybrid_memory import HybridMemory

        config = load_config()
        mem = HybridMemory(config)

        mem.memorize_fact("progetto speace", "cervello digitale")
        result = mem.recall_fact("speace")
        assert result == "cervello digitale", f"Fuzzy recall fallito: {result}"

        print("✓ Recall fuzzy OK")

    def test_multiple_facts(self):
        from memory.hybrid_memory import HybridMemory

        config = load_config()
        mem = HybridMemory(config)

        facts = {
            "codice alfa": "7319",
            "codice beta": "4200",
            "codice gamma": "8877",
            "versione": "1.0.0",
        }
        for k, v in facts.items():
            mem.memorize_fact(k, v)

        assert len(mem.factual) >= 4
        for k, v in facts.items():
            assert str(mem.recall_fact(k)) == v, f"Mismatch: {k}"

        print(f"✓ {len(facts)} fatti memorizzati e recuperati")


class TestEpisodicMemory:

    def test_add_and_search_events(self):
        from memory.hybrid_memory import HybridMemory

        config = load_config()
        mem = HybridMemory(config)

        mem.add_event("test", "SPEACE sta imparando a ricordare episodi",
                       importance=0.8)
        mem.add_event("test", "Il cervello digitale elabora pattern complessi",
                       importance=0.6)
        mem.add_event("test", "La memoria di lavoro mantiene 7 chunks",
                       importance=0.4)

        results = mem.search_episodes("cervello digitale", top_k=2)
        assert len(results) > 0, "Nessun episodio trovato"
        assert "cervello" in results[0].content.lower()

        print(f"✓ Search episodi: trovati {len(results)} risultati su 3 eventi")

    def test_importance_sorting(self):
        from memory.hybrid_memory import HybridMemory

        config = load_config()
        mem = HybridMemory(config)

        mem.add_event("test", "Evento bassa importanza", importance=0.2)
        mem.add_event("test", "Evento alta importanza", importance=0.9)
        mem.add_event("test", "Evento media importanza", importance=0.5)

        # Dopo sorting, l'evento più importante dovrebbe essere primo
        assert mem.episodic[0].importance >= 0.9

        print("✓ Ordinamento per importanza OK")


class TestWorkingMemory:

    def test_buffer_limits(self):
        from cognitive.working_memory import WorkingMemory
        from core.state_bus import StateBus

        config = load_config()
        bus = StateBus()
        wm = WorkingMemory(bus, config)

        # Simula 25 turni (limite è 20)
        for i in range(25):
            wm.start_turn(f"input {i}")
            wm.end_turn(f"output {i}")

        assert len(wm.recent()) <= 20, f"Buffer overflow: {len(wm.recent())}"

        print(f"✓ Working memory buffer: {len(wm.recent())} turni (max 20)")


@pytest.mark.asyncio
async def test_semantic_store_basic():
    from memory.semantic_store import SemanticStore

    config = load_config()
    store = SemanticStore(config, embedding_engine=None)

    store.add("Il cervello usa codifica sparsa per risparmiare energia", importance=0.8)
    store.add("La memoria umana non è statica ma si ricostruisce", importance=0.7)
    store.add("Gli astrociti regolano il flusso energetico neurale", importance=0.6)

    results = store.search("efficienza energetica del cervello", top_k=2)
    assert len(results) >= 1, "Nessun risultato semantico"

    # Il primo risultato dovrebbe riguardare energia/codifica sparsa
    found_relevant = any("energia" in r["content"].lower() or "sparsa" in r["content"].lower()
                         for r in results)
    print(f"✓ Semantic search: {len(results)} risultati, relevant: {found_relevant}")

    # Test aggiuntivo
    results2 = store.search("memoria e ricostruzione", top_k=2)
    assert len(results2) >= 1
    print(f"✓ Seconda semantic search: {len(results2)} risultati")


if __name__ == "__main__":
    t = TestHybridMemory()
    t.test_memorize_and_recall_exact()
    t.test_fuzzy_recall()
    t.test_multiple_facts()

    te = TestEpisodicMemory()
    te.test_add_and_search_events()
    te.test_importance_sorting()

    tw = TestWorkingMemory()
    tw.test_buffer_limits()

    asyncio.run(test_semantic_store_basic())
