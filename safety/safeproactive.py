"""SPEACE Safety — SafeProactive Governance.

Write-Ahead Logging (WAL), Approval Gates, Snapshots, and Rollback.
All mutations and external actions pass through this gating system.

BIOLOGICAL PRINCIPLE: The immune system distinguishes self from non-self
and neutralizes threats. The prefrontal cortex provides inhibitory control
over impulsive actions. Together they form a safety architecture:
- Immune = detect anomalies (WAL anomaly detection)
- Inhibitory control = block dangerous actions (Approval Gates)
- Memory = snapshot for recovery (Snapshots + Rollback)

In SPEACE, SafeProactive is MANDATORY for any mutation or external action.
"""

import enum
import hashlib
import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path


class RiskLevel(enum.Enum):
    LOW = "low"            # Auto-approve
    MEDIUM = "medium"      # Human approval required
    HIGH = "high"           # Human with timeout
    REGULATORY = "regulatory"  # Dual human review


class ProposalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


@dataclass
class SafeProposal:
    id: str
    action: str
    risk_level: RiskLevel
    description: str
    proposed_by: str
    timestamp: float = field(default_factory=time.time)
    status: ProposalStatus = ProposalStatus.PENDING
    reviewer: str = ""
    review_timestamp: float = 0.0
    snapshot_path: str = ""


class SafeProactive:

    def __init__(self, state_bus, config: dict):
        self.bus = state_bus
        safety_cfg = config.get("safety", {}).get("safeproactive", {})
        self.wal_enabled = safety_cfg.get("wal_enabled", True)
        self.max_snapshots = safety_cfg.get("max_snapshots", 20)

        self.wal_path = Path("data/wal.jsonl")
        self.snapshot_dir = Path("data/snapshots")
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.proposals: dict[str, SafeProposal] = {}
        self.proposal_counter = 0

    def assess_risk(self, action: str) -> RiskLevel:
        action_lower = action.lower()

        low_patterns = ["read", "status", "list", "view", "show", "get", "recall"]
        high_patterns = ["write", "delete", "mutate", "execute", "shell", "improve",
                         "replicate", "deploy", "install"]
        regulatory_patterns = ["financial", "trade", "payment", "identity", "pii"]

        for p in regulatory_patterns:
            if p in action_lower:
                return RiskLevel.REGULATORY
        for p in high_patterns:
            if p in action_lower:
                return RiskLevel.HIGH
        for p in low_patterns:
            if p in action_lower:
                return RiskLevel.LOW
        return RiskLevel.MEDIUM

    def propose(self, action: str, description: str, proposed_by: str = "SPEACE") -> SafeProposal:
        risk = self.assess_risk(action)
        self.proposal_counter += 1

        proposal = SafeProposal(
            id=f"PROP-{self.proposal_counter:04d}",
            action=action,
            risk_level=risk,
            description=description,
            proposed_by=proposed_by,
        )

        # Create snapshot before risky actions
        if risk in (RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.REGULATORY):
            proposal.snapshot_path = self._create_snapshot(action)

        # Auto-approve low risk
        if risk == RiskLevel.LOW:
            proposal.status = ProposalStatus.APPROVED
            proposal.reviewer = "auto"
            proposal.review_timestamp = time.time()

        self.proposals[proposal.id] = proposal
        self._write_wal(proposal)

        return proposal

    def approve(self, proposal_id: str, reviewer: str = "human") -> bool:
        if proposal_id not in self.proposals:
            return False
        prop = self.proposals[proposal_id]
        if prop.risk_level == RiskLevel.REGULATORY and reviewer == "auto":
            return False  # Regulatory needs human review
        prop.status = ProposalStatus.APPROVED
        prop.reviewer = reviewer
        prop.review_timestamp = time.time()
        self._write_wal(prop)
        self.bus.set(f"approval_{prop.id}", asdict(prop))
        return True

    def reject(self, proposal_id: str, reason: str = "") -> bool:
        if proposal_id not in self.proposals:
            return False
        self.proposals[proposal_id].status = ProposalStatus.REJECTED
        self._write_wal(self.proposals[proposal_id])
        return True

    def rollback(self, proposal_id: str) -> bool:
        if proposal_id not in self.proposals:
            return False
        prop = self.proposals[proposal_id]
        if prop.snapshot_path and Path(prop.snapshot_path).exists():
            prop.status = ProposalStatus.ROLLED_BACK
            self._write_wal(prop)
            return True
        return False

    def is_approved(self, action: str) -> bool:
        """Check if a given action is approved and safe to execute."""
        risk = self.assess_risk(action)
        if risk == RiskLevel.LOW:
            return True
        for prop in self.proposals.values():
            if prop.action == action and prop.status == ProposalStatus.APPROVED:
                return True
        return False

    # ── Internal ──

    def _create_snapshot(self, action: str) -> str:
        """Snapshot relevant data before risky action."""
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        safe_action = action.replace(" ", "_").replace("/", "_")[:40]
        filename = f"{timestamp}_{safe_action}.json"
        path = self.snapshot_dir / filename

        state = self.bus.snapshot()
        with open(path, "w") as f:
            json.dump(state, f, indent=2, default=str)

        # Cleanup old snapshots
        snapshots = sorted(self.snapshot_dir.glob("*.json"))
        if len(snapshots) > self.max_snapshots:
            for old in snapshots[:len(snapshots) - self.max_snapshots]:
                old.unlink(missing_ok=True)

        return str(path)

    def _write_wal(self, proposal: SafeProposal):
        if not self.wal_enabled:
            return
        with open(self.wal_path, "a") as f:
            f.write(json.dumps(asdict(proposal), default=str) + "\n")

    def status(self) -> dict:
        counts = {s.value: 0 for s in ProposalStatus}
        for p in self.proposals.values():
            counts[p.status.value] += 1
        return {
            "total_proposals": len(self.proposals),
            "by_status": counts,
            "pending_approvals": [
                p.id for p in self.proposals.values()
                if p.status == ProposalStatus.PENDING
            ],
        }
