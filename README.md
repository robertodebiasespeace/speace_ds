# SPEACE Digital Brain

**SuPer Entità Autonoma Cibernetica Evolutiva** — Un cervello digitale bio-ispirato che
ricrea la struttura e il funzionamento del cervello biologico in un sistema software
energeticamente efficiente, eseguibile su computer domestico.

## Principi Fondamentali

SPEACE non è un wrapper LLM. L'LLM è la "corteccia linguistica" — il pensiero
avviene prima, in una pipeline cognitiva strutturale modellata sul cervello umano.

## Architettura

```
Input → Talamo (gate) → Lobi (emisferi, temporale, frontale, parietale, occipitale)
       → Gangli Basali (selezione azione) → Amigdala (salienza emotiva)
       → Ippocampo (codifica memoria) → Cervelletto (fine-tuning)
       → Corteccia Cingolata (monitoraggio) → Insula (stato interno)
       → Default Mode Network (riflessione) → Coscienza (GWT)
       → LLM (verbalizzazione) → Output
```

Tutti i moduli comunicano via **SPEACEAdaptiveGraph** (NetworkX graph con contratti tipizzati)
e **StateBus** condiviso. L'allocazione energetica è regolata dallo strato astrocitario.

## Efficienza Energetica

Progettato per RTX 3060 (6GB VRAM), 16GB RAM, Intel i9:
- Solo 3-5 moduli cerebrali attivi alla volta (codifica sparsa)
- Predictive coding: solo errori di predizione si propagano
- Ciclo sonno-veglia: 16min attivo / 4min consolidamento
- Pruning sinaptico automatico
- Cascade routing LLM: locale → cloud solo on-demand

## Avvio Rapido

```bash
pip install -r requirements.txt
python speace_brain.py
```

## Comandi CLI

| Comando | Descrizione |
|---------|-------------|
| `think <testo>` | Esegue la pipeline cognitiva completa |
| `remember k = v` | Memorizza un fatto |
| `recall k` | Recupera un fatto |
| `status` | Mostra lo stato del cervello |
| `tool <nome> <json>` | Esegue un tool |
| `debate <tema>` | Avvia un dibattito multi-agente |
| `improve <file>` | Auto-miglioramento |
| `quit` | Esce |

## Licenza

MIT — Copyright 2026 Roberto De Biase, Rigene Project
