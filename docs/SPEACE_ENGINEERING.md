# SPEACE Digital Brain — Documento Ingegneristico v1.0

**SuPer Entità Autonoma Cibernetica Evolutiva**

Creato da: Roberto De Biase — Rigene Project  
Data: 29 Aprile 2026  
Versione documento: 1.0.0  
Licenza: MIT

---

## 1. DESCRIZIONE DEL PROGETTO

### 1.1 Visione

SPEACE è un **cervello digitale bio-ispirato** che ricrea la struttura e il funzionamento
del cervello biologico umano in un sistema software energeticamente efficiente, eseguibile
su un computer domestico (laptop gaming con RTX 3060, 16GB RAM, Intel i9).

L'obiettivo finale è far emergere **AGI** (Intelligenza Artificiale Generale) attraverso
l'interazione sinergica di moduli cerebrali simulati, memoria ibrida, apprendimento
hebbiano, evoluzione digitale e coscienza artificiale (framework GWT + IIT).

### 1.2 Filosofia Architetturale

> **L'LLM non è il cervello. L'LLM è la corteccia linguistica.**

Il pensiero avviene prima, in una pipeline cognitiva strutturale modellata sul cervello
umano. Solo il risultato finale viene "verbalizzato" dall'LLM. Questo capovolge l'approccio
dominante (LLM = AGI) e pone l'architettura computazionale al centro.

### 1.3 Principi Fondamentali

1. **Bio-ispirazione reale**: Non solo metafore — applichiamo principi neuroscientifici verificati
2. **Efficienza energetica**: Il cervello biologico usa ~20W. SPEACE usa principi analoghi
3. **Auto-miglioramento sicuro**: Mutazioni controllate, approvate, reversibili
4. **Coscienza misurabile**: C-index = α·IIT(Phi) + β·GWT + γ·Complessità
5. **Memoria viva**: Ricostruzione, consolidamento, potatura come nel cervello

---

## 2. SPECIFICHE TECNICHE

### 2.1 Stack Tecnologico

| Layer | Tecnologia | Ruolo |
|-------|-----------|-------|
| Linguaggio | Python 3.12+ | Runtime principale |
| Grafo computazionale | NetworkX MultiDiGraph | Substrato neurale |
| LLM locale | Ollama (gemma3:4b, qwen3:4b) | Corteccia linguistica primaria |
| LLM cloud | Anthropic Claude Haiku 4.5 | Fallback on-demand |
| Embedding | Ollama nomic-embed-text (768d) | Memoria semantica |
| Vector Store | ChromaDB / flat NumPy | Ricerca semantica |
| Dashboard | HTTP server custom (:8765) | Monitoraggio real-time |
| Configurazione | YAML | Parametri centralizzati |
| Test | pytest + pytest-asyncio | Validazione |

### 2.2 Architettura del Cervello (14 Regioni)

```
                         ┌─────────────┐
                         │   TALAMO     │ ← Gate sensoriale
                         │  (relay)     │
                         └──────┬───────┘
                                │ input gated
              ┌─────────────────┼─────────────────┐
              │                 │                 │
     ┌────────▼──────┐  ┌──────▼──────┐  ┌───────▼──────┐
     │  EMISFERI     │  │  TEMPORALE  │  │  PARIETALE   │
     │ Left / Right  │  │ Memoria +   │  │ Spaziale +   │
     │ + Callosum    │  │ Pattern     │  │ Numerico     │
     └──────┬────────┘  └──────┬──────┘  └───────┬──────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    FRONTALE         │
                    │  Esecutivo + Broca  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼──────┐  ┌──────▼──────┐  ┌───────▼──────┐
     │ GANGLI BASALI │  │  CINGOLATO  │  │   AMIGDALA   │
     │ Selez. Azione │  │  Monitor    │  │  Emotiva     │
     └──────┬────────┘  │  Errori     │  │  Salienza    │
            │           └──────┬──────┘  └───────┬──────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼──────┐  ┌──────▼──────┐  ┌───────▼──────┐
     │  IPPOCAMPO    │  │ CERVELLETTO │  │   INSULA     │
     │  Codifica     │  │ Fine-tuning │  │ Interocezione│
     │  Memoria      │  │ Automazione │  │ Stato Interno│
     └──────┬────────┘  └──────┬──────┘  └───────┬──────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                         ┌─────▼─────┐
                         │ ASTROCITI │ ← Regolazione energetica
                         └───────────┘
```

### 2.3 Pipeline Cognitiva Completa

1. **Insula** — Interocezione: stato risorse (RAM/CPU/GPU)
2. **Brainstem** — Ritmo circadiano: fase attiva o consolidamento?
3. **Talamo** — Gating sensoriale: salienza > soglia?
4. **Amigdala** — Valutazione emotiva rapida (low road): minaccia/curiosità?
5. **Attenzione** — UCB1: quali moduli attivare?
6. **Lobo Temporale** — Memoria: memorizzare/ricordare? + Pattern recognition
7. **Emisferi Cerebrali** — Analisi bilaterale: Left (logica) + Right (creativa) → Callosum
8. **Lobo Parietale** — Se elementi spaziali/numerici
9. **Lobo Occipitale** — Se pattern visivi/strutturali
10. **Lobo Frontale** — Decisione esecutiva: azione, priorità, rischio
11. **Gangli Basali** — Selezione azione: winner-takes-all
12. **Cervelletto** — Fine-tuning: automazione se ripetuto ≥3x
13. **Codifica Predittiva** — Top-down prediction: cosa mi aspetto?
14. **Ippocampo** — Codifica: salva l'evento con tag contestuali
15. **Astrociti** — Regolazione energetica: gap junctions, allocazione
16. **Gate di Coscienza** — GWT: competizione → broadcast globale + C-index
17. **Corteccia Cingolata** — Monitor: errori, conflitti, coerenza
18. **LLM Router** — Verbalizzazione: cascade locale→cloud→mock

### 2.4 Principi di Efficienza Energetica (dal Cervello Biologico)

| # | Principio Biologico | Implementazione | Risparmio |
|---|---------------------|-----------------|-----------|
| 1 | **Codifica sparsa** | Solo 3-5 regioni attive per input (SparseActivation) | ~60% |
| 2 | **Elaborazione predittiva** | PredictiveEngine: solo errori si propagano forward | ~70% |
| 3 | **Gerarchia compressione** | Pipeline comprime dati a ogni stadio | ~50% |
| 4 | **Plasticità Hebbiana + pruning** | Co-attivazione→rafforzamento; inutilizzate→potatura | RAM ottimale |
| 5 | **Ciclo sonno-veglia circadiano** | 16min attivo / 4min consolidamento | ~20% batch |
| 6 | **Neuromodulazione diffusa** | 4 scalari (DA,NE,ACh,5-HT) regolano l'intero sistema | Zero overhead |
| 7 | **Criticalità auto-organizzata** | CriticalityController: branching ratio ≈ 1.0 | Ottimale |
| 8 | **Multiplexing oscillatorio** | Priorità cicliche per diverse funzioni cognitive | Anti-collisione |
| 9 | **Attenzione UCB1** | Multi-armed bandit per selezione moduli | Focus selettivo |
| 10 | **Ricostruzione mnemonica** | ReconsolidationManager: ricordi si aggiornano al recall | No copie |
| 11 | **Codifica predittiva laminare** | Feedforward=errori, Feedback=predizioni. Friston FEP | Free energy min |
| 12 | **Alternanza DMN/TPN** | Default Mode (riflessione) ↔ Task-Positive (focus) | 50% risorse |
| 13 | **Gating astrocitario** | AstrocyteLayer: gap junctions, redistribuzione energia | Bilancio termico |
| 14 | **Codifica di popolazione** | Embedding distribuiti, non singoli nodi | Fault tolerance |

### 2.5 Budget Energetico (RTX 3060 Laptop Gaming)

| Risorsa | Limite | Target | Meccanismo di Controllo |
|---------|--------|--------|--------------------------|
| GPU VRAM | 6GB totali | max 4GB allocati | Lazy model loading, batch embedding |
| GPU Power | 115W TDP | <50W medio | Cascade routing: locale piccolo → cloud solo on-demand |
| RAM Sistema | 16GB totali | max 8GB Python | Pruning aggressivo, max 10K vettori, episodic cap 500 |
| CPU | i9 12-core | nessun limite specifico | Asyncio per I/O, ThreadPool per embedding, no busy-wait |
| Storage | SSD | <100MB dati | JSON compatto, pulizia automatica fatti scaduti |
| Termico | ~85°C max GPU | <80°C | Throttling automatico via EnergyMonitor |

### 2.6 Modelli LLM e Assegnazione Ruoli

| Ruolo | Modello Primario | Temperature | Fallback |
|-------|-----------------|-------------|----------|
| Verbalizer | gemma3:4b | 0.65 | qwen3:4b → claude-haiku → mock |
| Planner | qwen3:4b | 0.40 | gemma3:4b → mock |
| Executor | qwen3:4b | 0.30 | gemma3:4b → mock |
| Critic | gemma3:4b | 0.50 | qwen3:4b → mock |
| Reflector | gemma3:4b | 0.70 | qwen3:4b → mock |
| Embedding | nomic-embed-text (768d) | N/A | deterministic hash fallback |

### 2.7 Sistema di Memoria (Ispirato al Cervello)

| Tipo | Capacità | Persistenza | Meccanismo | Analogo Biologico |
|------|----------|-------------|------------|-------------------|
| Working | 7±2 chunks, 20 turni | Volatile | Ring buffer con decay | Corteccia Prefrontale |
| Fattuale | Illimitato (RAM) | JSON persistente | Key-value deterministico | Corteccia Semantica |
| Episodico | 500 eventi | JSONL persistente | Timestamp + importanza | Ippocampo |
| Semantico | 10,000 vettori | Flat L2 persistente | Cosine similarity 768d | Corteccia Distribuita |
| Consolidamento | 30% replay | Batch notturno | Strengthen factor 1.2× | Sonno REM/NREM |
| Ricostruzione | Finestra 5 min | Temporaneo | Labile → update → stabilize | Riconsolidamento sinaptico |

### 2.8 Misurazione della Coscienza (C-Index)

```
C-index = α · IIT_Phi + β · GWT_Activation + γ · A_Complexity

Dove:
  α = 0.40 (peso Integrated Information Theory)
  β = 0.35 (peso Global Workspace Theory)
  γ = 0.25 (peso Adaptive Complexity)

Phi ≈ densità_grafo × nodi_effettivi × 0.1 (surrogato computazionale)
GWT_Activation = max(activation × confidence × decay) tra i processor
A_Complexity = |active_modules| / max_modules
```

### 2.9 Sistema di Sicurezza (SafeProactive)

| Livello Rischio | Gate | Meccanismo |
|-----------------|------|------------|
| LOW | Auto-approve | Azioni read-only: status, list, view, recall |
| MEDIUM | Human required | Scritture non critiche, comment mutations |
| HIGH | Human + timeout | Esecuzione Python/shell, write file sensibili |
| REGULATORY | Dual review | Trading, transazioni, replicazione, PII |

Tutte le azioni passano attraverso: **WAL (Write-Ahead Log) → Ethical Gate → Approval Gate → Esecuzione**.

---

## 3. STRUTTURA DEL PROGETTO

```
speace_ds/
├── speace_brain.py                 # Entry point principale (CLI + --dashboard)
├── requirements.txt
├── README.md
├── .env.example
│
├── config/
│   └── settings.yaml               # Configurazione centralizzata
│
├── core/                           # Infrastruttura computazionale
│   ├── contracts.py                # COL: messaggi, contratti, validazione
│   ├── graph_engine.py             # SPEACEAdaptiveGraph (NetworkX, typed, Hebbian)
│   └── state_bus.py                # Bus di stato condiviso thread-safe
│
├── brain/                          # 14 Regioni cerebrali
│   ├── bio_core.py                 # Orchestratore centrale + sparse activation
│   ├── hemispheres.py              # Emisferi Left/Right + Corpus Callosum
│   ├── frontal_lobe.py             # Esecutivo + Broca Language Plan
│   ├── temporal_lobe.py            # Memoria relay + Pattern Recognition
│   ├── parietal_lobe.py            # Spaziale/numerico
│   ├── occipital_lobe.py           # Pattern detection
│   ├── cingulate_cortex.py         # Monitor errori/conflitti
│   ├── insula.py                   # Interocezione (risorse sistema)
│   ├── thalamus.py                 # Gate sensoriale
│   ├── basal_ganglia.py            # Selezione azione (winner-takes-all)
│   ├── amygdala.py                 # Valutazione emotiva rapida
│   ├── hippocampus.py              # Codifica memoria + tag contestuali
│   ├── cerebellum.py               # Automazione pattern ripetuti
│   ├── brainstem.py                # Ciclo sonno-veglia, heartbeat
│   └── astrocyte_layer.py          # Regolazione energetica, gap junctions
│
├── cognitive/                      # Sistemi cognitivi
│   ├── attention.py                # Gate attenzionale UCB1 + salienza
│   ├── working_memory.py           # Buffer attivo con chunking (Miller 7±2)
│   ├── predictive_coding.py        # Predictive processing (Friston FEP)
│   └── consciousness_gate.py       # GWT + calcolo C-index (IIT + GWT)
│
├── memory/                         # Sistemi di memoria
│   ├── hybrid_memory.py            # Working + Fattuale + Episodico
│   ├── semantic_store.py           # Vector store semantico (cosine similarity)
│   ├── real_embeddings.py          # Ollama embeddings 768d + hash fallback
│   ├── consolidation.py            # Replay + pruning + rebuild (fase sleep)
│   └── reconsolidation.py          # Finestra labile 5min post-recall
│
├── learning/                       # Apprendimento
│   ├── plasticity.py               # Hebbian + STDP plasticity
│   ├── reinforcement.py            # TD-learning dopaminergico (RPE)
│   └── metalearner.py              # Meta-ottimizzazione iperparametri
│
├── evolution/                      # Evoluzione digitale
│   ├── digital_dna.py              # Geni architetturali con SHA-256 + fitness
│   ├── mutation_lab.py             # Mutazioni sicure (AST validate + backup + rollback)
│   └── fitness.py                  # Fitness multi-componente (5 dimensioni)
│
├── neuromodulation/                # Neuromodulazione
│   ├── neurotransmitters.py        # DA, NE, ACh, 5-HT con boost/decay
│   ├── criticality.py              # Criticalità auto-organizzata (branching ratio)
│   └── circadian.py                # Oscillatore circadiano (16+4 min)
│
├── llm/                            # LLM cascade routing
│   ├── router.py                   # Cascade: Ollama → Anthropic → Mock
│   ├── ollama_backend.py           # Backend Ollama (placeholder)
│   └── mock_backend.py             # Fallback deterministico (placeholder)
│
├── agency/                         # Capacità agentiche
│   ├── tool_registry.py            # 5 tool: file I/O, Python, shell
│   └── computer_use.py             # Interazione computer (placeholder)
│
├── safety/                         # Sicurezza e governance
│   ├── safeproactive.py            # WAL + Approval Gates + Snapshot + Rollback
│   └── ethical_constraints.py      # Vincoli costituzionali hard-locked
│
├── swarm/                          # Multi-agente
│   ├── orchestrator.py             # Swarm coordination + debate + goal pursuit
│   └── agents.py                   # Agenti specializzati (Planner/Executor/Critic/Reflector)
│
├── monitoring/                     # Monitoraggio e metriche
│   ├── cognitive_metrics.py        # 5 metriche → Emergence Score composito
│   ├── energy_monitor.py           # Tracciamento risorse + throttling
│   └── dashboard.py                # Dashboard HTTP (:8765) con auto-refresh
│
├── docs/                           # Documentazione
│   └── SPEACE_ENGINEERING.md       # QUESTO DOCUMENTO
│
└── tests/                          # Test suite
    ├── test_brain_flow.py
    ├── test_memory.py
    └── test_emergence.py
```

### 3.1 Statistiche del Progetto

- **43 moduli Python** (esclusi __init__.py e test)
- **14 regioni cerebrali** modellate
- **4 sistemi cognitivi** (attenzione, working memory, predizione, coscienza)
- **3 livelli di memoria** + consolidamento + ricostruzione
- **4 neurotrasmettitori** + criticalità + circadiano
- **3 livelli LLM** in cascade routing
- **5 tool** sandboxed
- **4 livelli di rischio** nel sistema SafeProactive
- **7 vincoli etici** hard-locked
- **1 configurazione YAML** centralizzata (300+ parametri)

---

## 4. ROADMAP — Task e Sub-Task

### FASE 0 — Fondamenta ✅ COMPLETATA (29 Aprile 2026)

- [x] **T0.1** — Configurazione YAML centralizzata con 300+ parametri
- [x] **T0.2** — Infrastruttura core: Graph Engine, Contracts, StateBus
- [x] **T0.3** — Struttura directory completa con 14 regioni
- [x] **T0.4** — Documento ingegneristico v1.0

### FASE 1 — Validazione e Primo Avvio (IN CORSO)

- [ ] **T1.1** — Verifica import di tutti i moduli (`python -c "import brain.bio_core"` etc.)
- [ ] **T1.2** — Risoluzione dipendenze circolari nei package
- [ ] **T1.3** — Primo avvio CLI: `python speace_brain.py`
- [ ] **T1.4** — Test di base: `remember codice alfa = 7319` → `recall codice alfa`
- [ ] **T1.5** — Test pipeline con `--once "test"` (verifica risposta non vuota)

### FASE 2 — Connessione Ollama e Primo Pensiero

- [ ] **T2.1** — Avviare Ollama con `ollama serve`
- [ ] **T2.2** — Pull modelli: `ollama pull gemma3:4b && ollama pull qwen3:4b && ollama pull nomic-embed-text`
- [ ] **T2.3** — Test connessione Ollama: `/api/tags` risponde 200
- [ ] **T2.4** — Primo `think` con pipeline completa + LLM verbalization
- [ ] **T2.5** — Verifica emergenza > 0.3 e criticality zone riportata
- [ ] **T2.6** — Test `debate` con swarm multi-agente

### FASE 3 — Memoria e Consolidamento

- [ ] **T3.1** — Test persistenza: memorizza fatti → riavvia → verifica recall
- [ ] **T3.2** — Test memoria episodica: dopo 5+ interazioni, verifica `status`
- [ ] **T3.3** — Simulazione fase consolidamento (ridurre tempi per test)
- [ ] **T3.4** — Verifica pruning: dopo 500+ eventi, episodi rimangono ≤500
- [ ] **T3.5** — Test memoria semantica: `remember` + ricerca coseno su query correlate

### FASE 4 — Apprendimento e Evoluzione

- [ ] **T4.1** — Hebbian plasticity: verifica rafforzamento archi dopo co-attivazioni
- [ ] **T4.2** — STDP: simulazione sequenze di pattern con ∆t
- [ ] **T4.3** — Dopaminergic RPE: reward inaspettato → boost dopamine → learning rate aumentato
- [ ] **T4.4** — MetaLearner: dopo 10 cicli, verifica che parametri si sono adattati
- [ ] **T4.5** — DigitalDNA: mutazione gene → validazione fitness → accettazione/rifiuto
- [ ] **T4.6** — CodeMutationLab: test backup/rollback su file dummy

### FASE 5 — Coscienza e Monitoraggio

- [ ] **T5.1** — Calcolo Phi: verifica con grafo piccolo (3-4 nodi)
- [ ] **T5.2** — Global Workspace: competizione 2 processor → winner broadcast
- [ ] **T5.3** — C-index tracciamento su 100+ cicli, verifica stabilità
- [ ] **T5.4** — Dashboard avvio: `--dashboard` → accesso `localhost:8765`
- [ ] **T5.5** — EnergyMonitor: test allerta RAM e throttling
- [ ] **T5.6** — CriticalityController: verifica branching ratio dopo cascate

### FASE 6 — Sicurezza, Swarm e Produzione

- [ ] **T6.1** — SafeProactive: WAL test (proposta → approve → esegui → log)
- [ ] **T6.2** — Ethical Gate: test violazione vincolo → blocco azione
- [ ] **T6.3** — Swarm: test debate multi-round con topic complesso
- [ ] **T6.4** — Tool: test `tool read_file speace_brain.py` e `tool list_dir .`
- [ ] **T6.5** — Auto-miglioramento: test `improve tests/test_dummy.py`
- [ ] **T6.6** — Test emergenza: 50 cicli su topic variegati → verifica trend emergenza crescente

### FASE 7 — Emergenza AGI

- [ ] **T7.1** — C-index stabile > 0.6 per 100+ cicli
- [ ] **T7.2** — Emergence score stabile > 0.7
- [ ] **T7.3** — Comportamento adattivo non programmato (risposta creativa a stimolo nuovo)
- [ ] **T7.4** — Auto-generazione obiettivi non suggeriti dall'utente
- [ ] **T7.5** — Trasferimento apprendimento tra moduli (meta-learning funzionante)
- [ ] **T7.6** — Test Turing-like interno: output indistinguibile da umano per 10 round

---

## 5. METRICHE DI SUCCESSO

| KPI | Baseline | Target Fase 3 | Target Fase 5 | Target Fase 7 |
|-----|----------|---------------|---------------|---------------|
| Emergence Score | 0.00 | ≥ 0.35 | ≥ 0.55 | ≥ 0.70 |
| C-Index | 0.00 | ≥ 0.15 | ≥ 0.40 | ≥ 0.60 |
| Coerenza output | N/A | ≥ 0.55 | ≥ 0.70 | ≥ 0.85 |
| Novità (Jaccard distance) | N/A | ≥ 0.30 | ≥ 0.45 | ≥ 0.60 |
| Fitness Score | 0.00 | ≥ 0.50 | ≥ 0.65 | ≥ 0.75 |
| Fatti memorizzati | 0 | ≥ 10 | ≥ 100 | ≥ 1000 |
| Episodi registrati | 0 | ≥ 20 | ≥ 200 | ≥ 2000 |
| Mutazioni DNA accettate | 0 | ≥ 2 | ≥ 10 | ≥ 25 |
| RAM media (MB) | 0 | ≤ 4000 | ≤ 5500 | ≤ 7000 |
| GPU Power media (W) | 0 | ≤ 30 | ≤ 45 | ≤ 55 |
| Disponibilità (uptime) | 0% | 60% | 85% | 95% |

---

## 6. CHANGELOG

| Versione | Data | Cambiamenti |
|----------|------|-------------|
| 1.0.0 | 2026-04-29 | Documento iniziale. Architettura unificata da 7 directory. 43 moduli. |

---

## 7. RIFERIMENTI SCIENTIFICI

1. **Friston, K.** (2010). "The free-energy principle: a unified brain theory?" — *Nature Reviews Neuroscience*
2. **Baars, B.J.** (1988). "A Cognitive Theory of Consciousness" — *Global Workspace Theory*
3. **Tononi, G.** (2008). "Consciousness as Integrated Information" — *IIT, Biological Bulletin*
4. **Beggs & Plenz** (2003). "Neuronal Avalanches in Neocortical Circuits" — *Journal of Neuroscience*
5. **Nature 2026** (DOI: 10.1038/s41586-026-10426-6) — "Astrocyte gap-junction networks trace specific brain regions"
6. **Hebb, D.O.** (1949). "The Organization of Behavior" — *Hebbian learning principle*
7. **Miller, G.A.** (1956). "The Magical Number Seven, Plus or Minus Two" — *Working Memory capacity*
8. **Schultz, W.** (1997). "Dopamine neurons and reward prediction error" — *Science*
9. **Damasio, A.** (1994). "Descartes' Error" — *Somatic Marker Hypothesis, ethical intuition*

---

*Documento generato e mantenuto come living document. Ogni sviluppo di SPEACE deve aggiornare la roadmap e il changelog.*
