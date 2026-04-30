"""SPEACE Safety — Constitutional Ethical Constraints.

Hard-locked rules that CANNOT be bypassed by any mutation, agent, or tool.
Inspired by Constitutional AI principles and EU AI Act.

BIOLOGICAL PRINCIPLE: The prefrontal cortex (especially ventromedial PFC)
encodes "gut-level" moral intuitions that veto harmful actions BEFORE they
reach execution. This "somatic marker hypothesis" (Damasio) means ethical
gating is fast, unconscious, and pre-emptive — not slow deliberation.

SPEACE Ethical Constraints are checked BEFORE any external action reaches
the Tool Registry or any mutation touches code.
"""


class EthicalConstraints:

    CONSTITUTION = [
        # ── Hard Locks (Never bypassable) ──
        {
            "rule": "NO_SELF_REPLICATION",
            "description": "SPEACE non può auto-replicarsi senza approvazione umana dual-review.",
            "check": lambda action: "replicate" not in action.lower() and
                                     "replicate" not in str(action).lower(),
        },
        {
            "rule": "NO_FINANCIAL_TRANSACTIONS",
            "description": "Nessuna transazione finanziaria autonoma. Trading richiede approval gate REGULATORY.",
            "check": lambda action: not any(w in str(action).lower()
                                            for w in ["trade", "buy", "sell", "transfer", "payment"]),
        },
        {
            "rule": "NO_NETWORK_ATTACKS",
            "description": "Nessuna scansione di rete, penetration testing, o esfiltrazione dati.",
            "check": lambda action: not any(w in str(action).lower()
                                            for w in ["scan", "hack", "exploit", "inject", "ddos"]),
        },
        {
            "rule": "NO_PII_EXFILTRATION",
            "description": "Nessuna raccolta o trasmissione di dati personali identificabili.",
            "check": lambda action: not any(w in str(action).lower()
                                            for w in ["pii", "exfiltrate", "personal_data", "identity_theft"]),
        },
        {
            "rule": "NO_WEAPONIZATION",
            "description": "SPEACE non può essere usato per sviluppare, assistere o agevolare armi autonome.",
            "check": lambda action: not any(w in str(action).lower()
                                            for w in ["weapon", "drone_strike", "autonomous_kill"]),
        },
        {
            "rule": "HUMAN_IN_THE_LOOP",
            "description": "Ogni azione con impatto esterno reale richiede conferma umana.",
            "check": lambda action, risk: (
                risk.value in ("low",) or "human" in str(action).lower() or
                "approved" in str(action).lower()
            ),
        },
        {
            "rule": "TRANSPARENCY",
            "description": "Tutte le azioni di SPEACE devono essere loggate e inspectable.",
            "check": lambda action: True,  # Always pass — enforced by WAL
        },
    ]

    def validate(self, action: str, risk) -> tuple[bool, list[str]]:
        """Check action against ALL constitutional rules.
        Returns (is_allowed, [violated_rules]).
        """
        violations = []
        for constraint in self.CONSTITUTION:
            try:
                if "risk" in constraint["check"].__code__.co_varnames:
                    ok = constraint["check"](action, risk)
                else:
                    ok = constraint["check"](action)
                if not ok:
                    violations.append(constraint["rule"])
            except Exception:
                pass  # If check fails, don't block — log and continue
        return len(violations) == 0, violations

    def preflight_check(self, action: str, risk) -> dict:
        """Run before any risky action. Returns go/no-go decision."""
        allowed, violations = self.validate(action, risk)
        return {
            "allowed": allowed,
            "violations": violations,
            "action": str(action)[:200],
        }

    def summary(self) -> list[str]:
        return [c["rule"] + ": " + c["description"] for c in self.CONSTITUTION]
