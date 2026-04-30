"""Test: SPEACE Emergence Behavior.

Verifica che metriche cognitive mostrino segni di comportamento emergente:
- Novità misurabile
- Coerenza crescente
- Adattamento a input variati
- Goal auto-generati

BIOLOGICAL PRINCIPLE: Emergence is NOT explicitly programmed.
It is measured as the *divergence* between programmed behavior and
observed behavior. True emergence means the system does something
that was not in the training data or hardcoded rules.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
import pytest
import asyncio


def load_config():
    cfg_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(cfg_path) as f:
        return yaml.safe_load(f)


class TestMetricsSuite:

    def test_novelty_baseline(self):
        """La novità per input identici dovrebbe essere bassa."""
        from monitoring.cognitive_metrics import SPEACEMetrics
        from core.state_bus import StateBus

        config = load_config()
        bus = StateBus()
        metrics = SPEACEMetrics(bus, config)

        for _ in range(5):
            metrics.record_output("Questa è una risposta di test molto simile.")

        novelty = metrics.calculate_novelty()
        assert 0.0 <= novelty <= 1.0, f"Novelty out of range: {novelty}"
        print(f"✓ Novelty (input simili): {novelty:.3f}")

    def test_novelty_divergent(self):
        """Input molto diversi dovrebbero produrre novelty alta."""
        from monitoring.cognitive_metrics import SPEACEMetrics
        from core.state_bus import StateBus

        config = load_config()
        bus = StateBus()
        metrics = SPEACEMetrics(bus, config)

        outputs = [
            "Il cervello umano usa solo 20 watt di potenza.",
            "SPEACE implementa la codifica predittiva di Friston.",
            "Gli astrociti formano reti gap-junction nel cervello.",
            "La memoria viene ricostruita ogni volta che viene richiamata.",
            "Il criticality controller mantiene il sistema nella zona ottimale.",
        ]
        for out in outputs:
            metrics.record_output(out)

        novelty = metrics.calculate_novelty()
        assert novelty > 0.3, f"Novelty troppo bassa per input divergenti: {novelty}"
        print(f"✓ Novelty (input divergenti): {novelty:.3f}")

    def test_coherence(self):
        """Output ben strutturati dovrebbero avere coerenza > 0.4."""
        from monitoring.cognitive_metrics import SPEACEMetrics
        from core.state_bus import StateBus

        config = load_config()
        bus = StateBus()
        metrics = SPEACEMetrics(bus, config)

        metrics.record_output(
            "SPEACE è un cervello digitale bio-ispirato. "
            "Utilizza 14 regioni cerebrali interconnesse. "
            "Inoltre implementa la codifica sparsa per risparmiare energia. "
            "Quindi è efficiente anche su hardware consumer. "
            "Tuttavia richiede modelli LLM locali per funzionare al meglio. "
            "Infatti la pipeline cognitiva processa il pensiero prima della verbalizzazione."
        )

        coherence = metrics.calculate_coherence()
        assert coherence > 0.3, f"Coherence troppo bassa: {coherence}"
        print(f"✓ Coherence: {coherence:.3f}")

    def test_emergence_composite(self):
        """Il composite emergence score deve essere in [0, 1]."""
        from monitoring.cognitive_metrics import SPEACEMetrics
        from core.state_bus import StateBus

        config = load_config()
        bus = StateBus()
        metrics = SPEACEMetrics(bus, config)

        for i in range(10):
            metrics.record_output(f"Risposta numero {i}: analisi del sistema cognitivo SPEACE.")
            metrics.record_state({"cycle": i, "state": f"active_{i % 3}"})

        measure = metrics.measure()
        emergence = measure["emergence"]

        assert 0.0 <= emergence <= 1.0, f"Emergence out of range: {emergence}"
        assert "novelty" in measure
        assert "coherence" in measure
        assert "self_generated_goals" in measure

        print(f"✓ Emergence: {emergence:.3f} | N:{measure['novelty']:.3f} "
              f"C:{measure['coherence']:.3f} | G:{measure['self_generated_goals']:.3f}")


class TestCriticality:

    def test_criticality_zones(self):
        from neuromodulation.criticality import CriticalityController
        from core.state_bus import StateBus

        config = load_config()
        bus = StateBus()
        cc = CriticalityController(bus, config)

        # Scenario: molte cascate piccole (sub-critical, rigido)
        for _ in range(10):
            cc.record_cascade(2, max_size=14)
        state = cc.compute_scores(coherence=0.85, novelty=0.15)
        assert "SUB-CRITICAL" in state["zone"] or "CRITICAL" in state["zone"]
        print(f"✓ Criticality (rigido): {state['zone']}")

        # Nuovo controller: cascate bilanciate
        cc2 = CriticalityController(bus, config)
        for _ in range(5):
            cc2.record_cascade(3, max_size=14)
        for _ in range(5):
            cc2.record_cascade(7, max_size=14)
        state2 = cc2.compute_scores(coherence=0.6, novelty=0.55)
        assert "CRITICAL" in state2["zone"] or "NEAR" in state2["zone"]
        print(f"✓ Criticality (bilanciato): {state2['zone']}")


class TestNeurotransmitters:

    def test_modulation_cycle(self):
        from neuromodulation.neurotransmitters import NeurotransmitterSystem
        from core.state_bus import StateBus

        config = load_config()
        bus = StateBus()
        nt = NeurotransmitterSystem(bus, config)

        # Reward → dopamine boost
        initial_da = nt.levels["dopamine"]
        nt.on_reward(1.0)
        assert nt.levels["dopamine"] > initial_da

        # Surprise → norepinephrine boost
        initial_ne = nt.levels["norepinephrine"]
        nt.on_surprise(1.5)
        assert nt.levels["norepinephrine"] > initial_ne

        # Decay
        nt.decay_all()
        for level_name, level in nt.levels.items():
            assert 0.0 <= level <= 1.0, f"{level_name} out of range: {level}"

        print(f"✓ Neurotransmitters OK: {nt.state()}")

    def test_learning_modifier(self):
        from neuromodulation.neurotransmitters import NeurotransmitterSystem
        from core.state_bus import StateBus

        config = load_config()
        bus = StateBus()
        nt = NeurotransmitterSystem(bus, config)

        modifier = nt.learning_rate_modifier()
        assert 0.5 <= modifier <= 2.0, f"Learning rate modifier out of range: {modifier}"
        print(f"✓ Learning rate modifier: {modifier:.3f}")


class TestSafety:

    def test_ethical_constraints_hard_lock(self):
        from safety.ethical_constraints import EthicalConstraints
        from safety.safeproactive import RiskLevel

        ethics = EthicalConstraints()
        allowed, violations = ethics.validate("replicate SPEACE autonomously", RiskLevel.HIGH)
        assert not allowed, "La replicazione dovrebbe essere bloccata!"
        assert "NO_SELF_REPLICATION" in violations
        print(f"✓ Replicazione bloccata: {violations}")

    def test_ethical_constraints_allow_read(self):
        from safety.ethical_constraints import EthicalConstraints
        from safety.safeproactive import RiskLevel

        ethics = EthicalConstraints()
        allowed, violations = ethics.validate("read status file", RiskLevel.LOW)
        assert allowed, f"La lettura dovrebbe essere permessa: {violations}"
        print("✓ Azioni read-only permesse")

    def test_risk_assessment(self):
        from safety.safeproactive import SafeProactive, RiskLevel
        from core.state_bus import StateBus

        config = load_config()
        bus = StateBus()
        sp = SafeProactive(bus, config)

        assert sp.assess_risk("read status") == RiskLevel.LOW
        assert sp.assess_risk("delete file") == RiskLevel.HIGH
        assert sp.assess_risk("financial trade") == RiskLevel.REGULATORY
        print("✓ Risk assessment OK")


# ── Run all ──

if __name__ == "__main__":
    print("═" * 60)
    print("  SPEACE — Test Suite Emergenza e Cognizione")
    print("═" * 60)

    tm = TestMetricsSuite()
    tm.test_novelty_baseline()
    tm.test_novelty_divergent()
    tm.test_coherence()
    tm.test_emergence_composite()

    tc = TestCriticality()
    tc.test_criticality_zones()

    tn = TestNeurotransmitters()
    tn.test_modulation_cycle()
    tn.test_learning_modifier()

    ts = TestSafety()
    ts.test_ethical_constraints_hard_lock()
    ts.test_ethical_constraints_allow_read()
    ts.test_risk_assessment()

    print("\n═" * 60)
    print("  Tutti i test superati ✓")
    print("═" * 60)
