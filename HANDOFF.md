# Class Warrior (Fury) — Handoff Tecnico

Manuale di riferimento tecnico per lo sviluppo, la manutenzione e l'estensione della suite **Class Warrior (Fury)** per World of Warcraft 3.3.5a (*WotLK Build 12340*).

---

## 1. Panoramica del Progetto

La suite è distribuita come **WeakAura autonoma** in formato compresso `!WA:1!` (serializzazione `AceSerializer-3.0` + compressione `LibDeflate`). Include un simulatore web interattivo per la visualizzazione immediata del layout ospitato su GitHub Pages e una suite completa di test deterministici in Python.

| Proprietà | Dettaglio |
| :--- | :--- |
| **Piattaforma Target** | World of Warcraft 3.3.5a (WotLK Build 12340) |
| **Engine WeakAuras** | WeakAuras 4.0.0 (`internalVersion = 52`, header `!WA:1!`). |
| **File di Distribuzione** | [`IMPORT_STRING.txt`](file:///d:/0Progetti/fury-warrior-335a-am/IMPORT_STRING.txt) |
| **Simulatore Web** | [`docs/index.html`](file:///d:/0Progetti/fury-warrior-335a-am/docs/index.html) |
| **Live Demo Online** | [GitHub Pages Live Showcase](https://glacyal.github.io/fury-warrior-335a-am/) |
| **Controllo Versione** | Git su GitHub: [Glacyal/fury-warrior-335a-am](https://github.com/Glacyal/fury-warrior-335a-am) |

---

## 2. Struttura del Repository

```text
fury-warrior-335a-am/
├── IMPORT_STRING.txt                # Stringa WeakAuras pronta all'uso per il comando /wa
├── generate.py                      # Compilatore Python dell'albero WA
├── README.md                        # Documentazione utente, guida installazione e compatibilità
├── HANDOFF.md                       # Specifiche tecniche per sviluppatori e manutentori
│
├── builder/                         # Pacchetto Python modulare per la generazione dell'HUD
│   ├── tree.py                      # Assemblatore dell'albero gerarchico (39 nodi, 19 di primo livello)
│   ├── core/                        # Moduli core di serializzazione e codifica
│   │   ├── constants.py             # Load conditions (Warrior 84), texture, font Expressway
│   │   ├── serializer.py            # Serializzatore AceSerializer-3.0 puro (^1...^^)
│   │   ├── deflate.py               # Compressione Deflate RFC 1951 + LibDeflate Print Encoding
│   │   ├── encoder.py               # Generatore stringa finale (!WA:1!...)
│   │   └── helpers.py               # Generatori di subtext e glow helper
│   └── components/                  # Moduli dedicati ai singoli componenti dell'HUD
│       ├── rotational.py            # 15 - Rotational Bar (Dual Swing Timer e HS Queued glow)
│       ├── procs.py                 # 01 - Procs (gruppo dinamico con Victory Rush, Bloodsurge, T10, DBW, ecc.)
│       ├── buffs.py                 # 02 - Battle Shout, 03 - Commanding Shout, 04 - Berserker Stance (con filtri overlap raid)
│       ├── utility.py               # 05-13 - Utility Row (Monili, Mantello, CD maggiori, Stivali)
│       ├── bars.py                  # 14 - Rage Bar & 16 - Castbar
│       ├── alerts.py                # 17 - Alerts (Bloodsurge & Execute Phase)
│       ├── stats.py                 # 18 - Stats Panel (AP, Crit, ArP con Cap, Hit/Exp)
│       └── sunder.py                # 19 - Sunder Armor Tracker (1-5 cariche su boss)
│
├── docs/                            # Documentazione e anteprima interattiva per GitHub Pages
│   ├── index.html                   # Simulatore interattivo HTML/CSS/JS (proporzioni 1:1)
│   ├── ARCHITECTURE.md              # [Escluso da git] Architettura di sistema
│   ├── MEMORY.md                    # [Escluso da git] Registro memoria viva
│   ├── TASKS.md                     # [Escluso da git] Piano operativo task
│   ├── PRD.md                       # [Escluso da git] Specifiche di prodotto
│   ├── RULES.md                     # [Escluso da git] Guardrails operativi
│   ├── DESIGN.md                    # [Escluso da git] Design system e token
│   ├── DECISIONS.md                 # [Escluso da git] Registro decisioni ADR
│   ├── TEST_PLAN.md                 # [Escluso da git] Piano di collaudo
│   └── WORKFLOW.md                  # [Escluso da git] Flusso di lavoro standard
│
├── scripts/                         # Script di supporto e manutenzione
│   └── sync_docs.py                 # Sincronizza IMPORT_STRING.txt con docs/index.html
│
└── tests/                           # Suite di test automatici e paralleli
    ├── run_parallel_tests.py        # Test runner parallelo multi-processore (ProcessPoolExecutor)
    ├── test_components_integrity.py # Verifica integrità strutturale moduli (19 sequenziali)
    ├── test_tree_layout.py          # Verifica gerarchia e proporzioni albero WA
    ├── test_lua.py                  # Validazione sintassi codice Lua (29 blocchi)
    ├── test_string_sync.py          # Verifica sincronizzazione stringa WA e simulatore
    ├── test_stats_panel.py          # Verifica calcolo statistiche guerriero (AP, Crit, ArP, Hit/Exp)
    ├── test_utility_row.py          # Verifica riga utility da 3 a 9 elementi
    ├── test_procs.py                # Verifica 01 - Procs warDPS e Weapon Desync Alert (Task 50)
    ├── test_rotational.py           # Verifica Dual Swing Timer e Heroic Strike Queued
    └── test_sunder_tracker.py       # Verifica debuff Sunder Armor e Expose Armor
```

---

## 3. Gestione dei File di Memoria DOCS

Come concordato e specificato nella configurazione `.gitignore`:
- I file markdown presenti in `docs/*.md` contengono la memoria persistente e l'architettura tecnica per gli assistenti AI e gli sviluppatori.
- **Questi file sono esclusi dal repository Git** e non compaiono nei commit.
- Il simulatore web `docs/index.html` fa eccezione ed è incluso nel versionamento Git per consentire il funzionamento della live demo su GitHub Pages.

