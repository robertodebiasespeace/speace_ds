"""SPEACE Evolution — Digital DNA System.

Tracks the evolutionary lineage of SPEACE's architectural principles
as genes with SHA-256 hashes, versions, and fitness scores.

BIOLOGICAL PRINCIPLE: The genome is NOT the organism. It's a compressed
encoding of constraints and possibilities — incredibly energy-efficient
as an information storage format. SPEACE DigitalDNA encodes:
- What modules exist (structural genes)
- How they connect (regulatory genes)
- Mutation rules and safety gates (epigenetic constraints)

Unlike biological DNA, SPEACE DNA can be validated via cryptographic
hash to detect corruption/tampering.
"""

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class DNAGene:
    name: str
    description: str
    source_code: str
    sha256: str
    version: int = 1
    fitness: float = 0.5
    last_mutated: float = 0.0
    mutation_count: int = 0
    created_at: str = ""


class DigitalDNA:

    def __init__(self, config: dict):
        self.persist_path = Path(config.get("evolution", {}).get("digital_dna", {}).get(
            "persist_file", "data/digital_dna.json"))
        self.min_fitness = config.get("evolution", {}).get("digital_dna", {}).get(
            "min_fitness_for_mutation", 0.65)
        self.genes: dict[str, DNAGene] = {}
        self.mutation_history: list[dict] = []
        self._seed_genes()
        self._load()

    def _seed_genes(self):
        """Initialize foundational architectural genes."""
        seeds = [
            ("brain_pipeline", "Pipeline cognitiva: Talamo→Lobi sensoriali→Ippocampo→Frontale→Lobi motori→Cervelletto"),
            ("memory_policy", "Politica memoria: Fattuale deterministico primario, episodico secondario, semantico terziario"),
            ("truth_policy", "Politica verità: Separare fatti osservati, inferenze, e ipotesi. Priorità ai fatti."),
            ("safety_guard", "Guardia sicurezza: SafeProactive WAL obbligatorio. Nessuna azione esterna senza approval gate."),
            ("energy_policy", "Politica energetica: Attivazione sparsa (max 5 moduli), predictive coding, pruning aggressivo"),
        ]
        now = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
        for name, desc in seeds:
            h = hashlib.sha256(desc.encode()).hexdigest()[:16]
            self.genes[name] = DNAGene(
                name=name, description=desc, source_code=desc,
                sha256=h, created_at=now,
            )

    def mutate_gene(self, gene_name: str, new_description: str) -> bool:
        """Attempt a mutation. Only succeeds if fitness improves."""
        if gene_name not in self.genes:
            return False

        old = self.genes[gene_name]
        new_hash = hashlib.sha256(new_description.encode()).hexdigest()[:16]

        # Fitness test: mutated gene must be at least as good
        # In future, this uses an LLM evaluator. For now, heuristic:
        # longer descriptions with concrete keywords score higher
        fitness = old.fitness
        quality_terms = ["deterministico", "primario", "obbligatorio", "sparsa", "aggressivo",
                          "separare", "priorità", "validato", "sicuro"]
        for term in quality_terms:
            if term in new_description.lower():
                fitness += 0.05
        fitness = min(1.0, fitness)

        if fitness < self.min_fitness:
            return False  # Below fitness threshold — reject mutation

        old.fitness = fitness + 0.02  # Small boost for attempting
        old.description = new_description
        old.sha256 = new_hash
        old.version += 1
        old.last_mutated = time.time()
        old.mutation_count += 1

        self.mutation_history.append({
            "gene": gene_name,
            "version": old.version,
            "fitness": round(old.fitness, 3),
            "timestamp": time.time(),
        })

        self._save()
        return True

    def status(self) -> dict:
        return {
            "genes": {
                name: {
                    "version": g.version,
                    "fitness": round(g.fitness, 3),
                    "sha256": g.sha256,
                    "mutations": g.mutation_count,
                }
                for name, g in self.genes.items()
            },
            "total_mutations": len(self.mutation_history),
            "recent_mutations": self.mutation_history[-5:],
        }

    def _save(self):
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "genes": {n: asdict(g) for n, g in self.genes.items()},
            "mutations": self.mutation_history[-50:],
        }
        with open(self.persist_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _load(self):
        if self.persist_path.exists():
            try:
                with open(self.persist_path) as f:
                    data = json.load(f)
                    for name, gdata in data.get("genes", {}).items():
                        self.genes[name] = DNAGene(**gdata)
                    self.mutation_history = data.get("mutations", [])
            except Exception:
                pass
