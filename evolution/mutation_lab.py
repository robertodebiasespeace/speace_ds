"""SPEACE Evolution — Safe Mutation Lab.

Conservative code self-modification with backup/rollback safety.
Only applies safe, validated mutations (parameter tuning, annotations).

BIOLOGICAL PRINCIPLE: Biological mutations are (a) random, (b) mostly neutral
or harmful, (c) rarely beneficial. Evolution's genius is the SELECTION step,
not the mutation step. SPEACE inverts this: mutations are constrained to be
safe, validated, and reversible. The fitness function gates acceptance.
This is "Lamarckian" evolution (guided by intelligence) — far faster than
blind Darwinian search for software systems.
"""

import ast
import shutil
import time
from datetime import datetime
from pathlib import Path


class CodeMutationLab:

    def __init__(self, config: dict):
        mut_cfg = config.get("evolution", {}).get("mutation_lab", {})
        self.backup_dir = Path("data/backups")
        self.validate_with_ast = mut_cfg.get("validate_with_ast", True)
        self.rollback_on_failure = mut_cfg.get("rollback_on_failure", True)
        self.allowed_types = mut_cfg.get("allowed_mutation_types", [
            "parameter_tuning", "comment_annotation",
        ])
        self.audit_log: list[dict] = []

    def create_backup(self, file_path: Path) -> Path:
        """Timestamped backup before mutation."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(file_path, backup_path)
        return backup_path

    def validate_syntax(self, code: str) -> tuple[bool, str]:
        """AST parse to verify Python syntax validity."""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, str(e)

    def propose_mutation(self, file_path: str, mutation_type: str, description: str = "") -> dict:
        """Propose a safe mutation. Validates before returning proposal."""
        path = Path(file_path)
        if not path.exists():
            return {"accepted": False, "error": f"File {file_path} non trovato"}

        if mutation_type not in self.allowed_types:
            return {"accepted": False, "error": f"Mutazione '{mutation_type}' non consentita"}

        original = path.read_text(encoding="utf-8")

        # Validate original
        ok, err = self.validate_syntax(original)
        if not ok:
            return {"accepted": False, "error": f"Originale invalido: {err}"}

        # Create backup
        backup = self.create_backup(path)

        # Apply mutation
        mutated = self._apply_mutation(original, mutation_type, description)

        # Validate mutated
        ok, err = self.validate_syntax(mutated)
        if not ok:
            return {"accepted": False, "error": f"Mutazione invalida: {err}", "backup": str(backup)}

        proposal = {
            "accepted": True,
            "file": str(path),
            "backup": str(backup),
            "original_hash": str(hash(original)),
            "mutated_code": mutated,
            "mutation_type": mutation_type,
            "description": description,
            "timestamp": time.time(),
        }

        self.audit_log.append({
            "action": "proposed",
            "file": str(path),
            "type": mutation_type,
            "timestamp": time.time(),
        })

        return proposal

    def apply_mutation(self, proposal: dict) -> dict:
        """Write mutated code to disk. Rolls back on failure."""
        if not proposal.get("accepted"):
            return {"success": False, "error": "Proposta non accettata"}

        path = Path(proposal["file"])
        backup_path = Path(proposal["backup"])

        try:
            path.write_text(proposal["mutated_code"], encoding="utf-8")

            # Re-validate after write
            written = path.read_text(encoding="utf-8")
            ok, err = self.validate_syntax(written)
            if not ok:
                # Rollback
                shutil.copy2(backup_path, path)
                return {"success": False, "error": f"Post-write validation failed: {err}", "rolled_back": True}

            self.audit_log.append({
                "action": "applied",
                "file": str(path),
                "type": proposal["mutation_type"],
                "timestamp": time.time(),
            })

            return {"success": True, "file": str(path), "backup": str(backup_path)}

        except Exception as e:
            if backup_path.exists():
                shutil.copy2(backup_path, path)
            return {"success": False, "error": str(e), "rolled_back": True}

    def _apply_mutation(self, code: str, mutation_type: str, description: str) -> str:
        """Apply specific mutation type."""
        if mutation_type == "parameter_tuning":
            return code  # Parameters live in YAML, not code — no code mutation needed
        elif mutation_type == "comment_annotation":
            header = (
                f"# ── SPEACE Mutation Annotation ──\n"
                f"# Date: {datetime.now().isoformat()}\n"
                f"# Description: {description}\n"
                f"#\n"
            )
            # Insert after module docstring or at top
            lines = code.split("\n")
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("#") or line.strip().startswith('"""'):
                    continue
                insert_pos = i
                break
            lines.insert(insert_pos, header)
            return "\n".join(lines)

        return code

    def history(self, n: int = 20) -> list[dict]:
        return self.audit_log[-n:]
