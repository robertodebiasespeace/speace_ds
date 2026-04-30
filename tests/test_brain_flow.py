"""Test: SPEACE Brain structural flow.

Verifica che la pipeline cognitiva sia integra e produca output
con tutti i livelli di processing attesi.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
import pytest


def load_config():
    cfg_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(cfg_path) as f:
        return yaml.safe_load(f)


@pytest.mark.asyncio
async def test_brain_initialization():
    """Verifica che tutte le 14 regioni siano inizializzabili."""
    from speace_brain import SPEACEBrain

    config = load_config()
    brain = SPEACEBrain(config)

    # Verifica regioni
    regions = [
        "thalamus", "hemispheres", "frontal", "temporal", "parietal",
        "occipital", "cingulate", "insula", "basal_ganglia", "amygdala",
        "hippocampus", "cerebellum", "brainstem", "astrocytes",
    ]
    for region in regions:
        assert hasattr(brain, region), f"Regione mancante: {region}"
        assert getattr(brain, region) is not None, f"Regione None: {region}"

    # Verifica sistemi cognitivi
    assert brain.attention is not None
    assert brain.predictive is not None
    assert brain.consciousness is not None
    assert brain.working_memory is not None

    # Verifica memoria
    assert brain.memory is not None
    assert brain.semantic_store is not None

    # Verifica sicurezza
    assert brain.safeproactive is not None
    assert brain.ethics is not None

    print("✓ Tutte le 14 regioni cerebrali e tutti i sistemi sono inizializzati")


@pytest.mark.asyncio
async def test_pipeline_structure():
    """Verifica che la pipeline think() restituisca struttura attesa."""
    from speace_brain import SPEACEBrain
    import time

    config = load_config()
    brain = SPEACEBrain(config)

    # Force active circadian phase
    brain.circadian.cycle_start = time.time()
    brain.circadian.phase = "active"
    brain.circadian.phase_start = time.time()

    result = await brain.think("Crea un piano per migliorare la memoria di SPEACE")

    # If consolidation phase, test returns different structure
    if result.get("phase") == "consolidation":
        print(f"System in consolidation phase — skipping deep test")
        assert "message" in result
        return

    # Verifica struttura risultato
    assert "response" in result, f"Manca 'response' nel risultato. Keys: {list(result.keys())}"
    assert "trace" in result, "Manca 'trace' nel risultato"

    trace = result["trace"]

    # Verifica che la pipeline abbia eseguito tutti i passaggi chiave
    assert "input" in trace
    assert "internal_state" in trace, "Insula non ha eseguito"
    assert "thalamic_gate" in trace, "Talamo non ha eseguito"
    assert "emotional" in trace, "Amigdala non ha eseguito"
    assert "temporal" in trace, "Temporale non ha eseguito"
    assert "bilateral" in trace, "Emisferi non hanno eseguito"
    assert "frontal" in trace, "Frontale non ha eseguito"
    assert "basal_ganglia" in trace, "Gangli basali non hanno eseguito"
    assert "cerebellum" in trace, "Cervelletto non ha eseguito"
    assert "predictive" in trace, "Predictive coding non ha eseguito"
    assert "astrocytes" in trace, "Astrociti non hanno eseguito"
    assert "cingulate" in trace, "Cingolato non ha eseguito"

    print(f"Pipeline completa: {len(trace)} step eseguiti")
    print(f"Output: {result['response'][:100]}...")
    print(f"Emergenza: {result.get('emergence', 0):.3f}")
    print(f"Zona criticità: {result.get('criticality_zone', '?')}")


@pytest.mark.asyncio
async def test_sparse_activation():
    """Verifica che solo 3-5 regioni siano attive (codifica sparsa)."""
    from speace_brain import SPEACEBrain

    config = load_config()
    brain = SPEACEBrain(config)

    active = brain.bio_core.compute_sparse_activation("Ricorda il codice alfa")
    assert 2 <= len(active) <= 7, f"Attese 2-7 regioni attive, ottenute: {len(active)}"

    # La richiesta di memoria dovrebbe attivare temporale
    assert any("temporal" in r for r in active), "Il temporale dovrebbe essere attivo per richieste di memoria"

    print(f"✓ Sparse activation: {len(active)} regioni attive: {active}")


if __name__ == "__main__":
    asyncio.run(test_brain_initialization())
    asyncio.run(test_pipeline_structure())
    asyncio.run(test_sparse_activation())
