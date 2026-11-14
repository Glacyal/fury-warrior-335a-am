# Class Warrior (Fury) — Handoff Tecnico

Manuale di riferimento tecnico per lo sviluppo, la manutenzione e l'estensione della suite **Class Warrior (Fury)** per World of Warcraft 3.3.5a (*WotLK Build 12340*).

---

## 1. Panoramica del Progetto

La suite è distribuita come **WeakAura autonoma** in formato compresso `!WA:1!` (serializzazione binaria `AceSerializer-3.0` + compressione Deflate RFC 1951 livello 9 + codifica di stampa `LibDeflate`).  
Include un simulatore web interattivo per la visualizzazione immediata del layout ospitato su GitHub Pages, una suite completa di test deterministici in Python con runner multi-core parallelo e una conformità nativa per motori classici e moderni.

| Proprietà | Dettaglio |
| :--- | :--- |
| **Piattaforma Target** | World of Warcraft 3.3.5a (WotLK Build 12340) |
| **Engine WeakAuras Target** | **WeakAuras 5.21.8+** (`internalVersion = 90`, `w = "5.21.8"`, Zero Warning nativa). |
| **File di Distribuzione** | [`IMPORT_STRING_v5.21.8.txt`](file:///d:/0Progetti/fury-warrior-335a-am/IMPORT_STRING_v5.21.8.txt) (stringa ufficiale pronta per l'importazione) |
| **Simulatore Web** | [`docs/index.html`](file:///d:/0Progetti/fury-warrior-335a-am/docs/index.html) |
| **Live Demo Online** | [GitHub Pages Live Showcase](https://glacyal.github.io/fury-warrior-335a-am/) |
| **Controllo Versione** | Git su GitHub: [Glacyal/fury-warrior-335a-am](https://github.com/Glacyal/fury-warrior-335a-am) (branch: `master`) |
| **Politica Documentazione** | `docs/*.md` esclusi dal controllo versione via `.gitignore` per preservare il contesto locale senza appesantire il repository Git. |

---

## 2. Struttura del Repository

```text
fury-warrior-335a-am/
├── IMPORT_STRING_v5.21.8.txt        # Stringa WeakAuras 5.21.8+ nativa (Zero warning, internalVersion: 90)
├── generate.py                      # Compilatore Python dell'albero WA (compila v5 nativo)
├── README.md                        # Documentazione utente, guida installazione e compatibilità
├── HANDOFF.md                       # Specifiche tecniche per sviluppatori e manutentori
│
├── builder/                         # Pacchetto Python modulare per la generazione dell'HUD
│   ├── tree.py                      # Assemblatore dell'albero gerarchico (38 aure, 20 nodi controllati)
│   ├── core/                        # Moduli core di serializzazione e codifica
│   │   ├── constants.py             # Load conditions (Warrior + Rampage 64), texture, font Expressway
│   │   ├── serializer.py            # Serializzatore AceSerializer-3.0 puro (^1...^^)
│   │   ├── deflate.py               # Compressione Deflate RFC 1951 + LibDeflate Print Encoding
│   │   ├── encoder.py               # Generatore stringa finale (!WA:1!...)
│   │   └── helpers.py               # Generatori di subtext e helper grafici
│   └── components/                  # Moduli dedicati ai singoli componenti dell'HUD
│       ├── rotational.py            # 15 - Rotational Bar (Dual Swing Timer MH/OH e HS/Cleave Queued glow)
│       ├── procs.py                 # 01 - Procs warDPS (gruppo dinamico orizzontale a 7 icone con SYNC)
│       ├── buffs.py                 # 02 - Battle Shout, 03 - Commanding Shout, 04 - Berserker Stance
│       ├── utility.py               # 05-13 - Utility Row (Monili, Anello, Mantello, Tier Set, Incanti, Guanti, DW, Reck, Stivali)
│       ├── bars.py                  # 14 - Rage Bar & 16 - Castbar warDPS
│       ├── alerts.py                # 17 - Alerts warDPS (avvisi testuali centrali Bloodsurge & Execute)
│       ├── stats.py                 # 18 - Stats Panel warDPS (AP, Crit, Haste, ArP con cap 1400, Hit/Exp)
│       └── sunder.py                # 19 - Sunder Armor Tracker (tracciamento cariche 1-5 ed Expose Armor)
│
├── docs/                            # Documentazione e anteprima interattiva per GitHub Pages
│   ├── index.html                   # Simulatore interattivo HTML/CSS/JS (proporzioni 1:1, tracciato in Git)
│   └── *.md                         # Documentazione interna (RULES, ARCHITECTURE, PRD, DECISIONS, ecc. - esclusa da Git)
│
├── scripts/
│   └── sync_docs.py                 # Sincronizzazione automatica della stringa v5 in docs/index.html
│
└── tests/                           # Suite di test automatici e paralleli
    ├── run_parallel_tests.py        # Test runner parallelo multi-processore (ProcessPoolExecutor)
    ├── test_buffs.py                # Test gestione Shout e Berserker Stance
    ├── test_components_integrity.py # Verifica integrità strutturale moduli (20 nodi sequenziali)
    ├── test_lua.py                  # Validazione sintassi codice Lua (98 blocchi, verifica script actions)
    ├── test_procs.py                # Test 01 - Procs warDPS e Weapon Desync Alert SYNC (Task 50)
    ├── test_rotational.py           # Test barra rotazionale, swing timer MH/OH e illuminazione cromatica HS/Cleave
    ├── test_stats_panel.py          # Verifica formule e moltiplicatori del pannello statistiche
    ├── test_string_sync.py          # Verifica corrispondenza tra builder e IMPORT_STRING_v5.21.8.txt
    ├── test_sunder_tracker.py       # Test Sunder Armor, conteggio cariche e allerta OFF
    ├── test_tree_layout.py          # Verifica gerarchia e proporzioni albero WA
    └── test_utility_row.py          # Test esaustivo su ICD, incanti arma x1/x2 e riga utility
```

---

## 3. Workflow di Sviluppo

Per apportare modifiche alla suite o estendere la logica:

1. **Modifica Componenti**:
   - Modifica i moduli Python in `builder/components/` o le librerie in `builder/core/`.
2. **Esecuzione Test Paralleli**:
   - Lancia la suite di test completa sfruttando tutti i core della CPU:
     ```bash
     python tests/run_parallel_tests.py
     ```
   - Tutti i 10 test devono risultare `[OK] PASSED` in meno di 0.5 secondi.
3. **Compilazione Stringa di Importazione**:
   - Ricompila la stringa nativa WA 5.21.8+ eseguendo:
     ```bash
     python generate.py
     ```
   - Questo aggiornerà deterministicamente [`IMPORT_STRING_v5.21.8.txt`](file:///d:/0Progetti/fury-warrior-335a-am/IMPORT_STRING_v5.21.8.txt).
4. **Sincronizzazione Simulatore Web**:
   - Sincronizza la stringa compilata all'interno del simulatore web:
     ```bash
     python scripts/sync_docs.py
     ```
5. **Commit & Push (`CP`)**:
   - Verifica lo stato Git con `git status` (assicurati che i file `docs/*.md` rimangano ignorati).
   - Esegui lo staging dei soli file di codice o documentazione pubblica (`git add <file>`).
   - Esegui commit e push sul branch `master`.

---

## 4. Specifiche Architetturali e Soluzioni WeakAuras 5+

### 4.1 Barra Rotazionale Dual Swing & HS/Cleave Queued (`15 - Rotational Bar`)
- **Doppio Swing Timer Speculare**:
  1. **OH Swing (Mezza Sinistra)**: Avanzamento dello swing per Mano Secondaria con etichetta `OH` e timing `%c` (es. `1.2s`).
  2. **MH Swing (Mezza Destra)**: Avanzamento dello swing per Mano Primaria con etichetta `MH` e timing `%c` (es. `1.8s`).
  3. **Colorazione Unificata**: Entrambe le barre condividono la medesima tonalità cromatica (`[0.85, 0.45, 0.15, 1.0]`) per massima armonia visiva.
- **Retroilluminazione Cromatica Additiva Dinamica**:
  - Quando **Heroic Strike** è accodato: retroilluminazione oro caldo (`[1.0, 0.84, 0.0, 0.40]`) con Pixel Glow dorato.
  - Quando **Cleave** è accodato: retroilluminazione verde smeraldo (`[0.1, 0.95, 0.2, 0.40]`) con Pixel Glow smeraldo.
  - Testo centrale azzerato (`return ""`) per garantire zero sovrapposizione visiva sui timer numerici di swing.
- **Isolamento Sandbox e Script Actions**:
  - Il frame listener dello swing timer è istanziato in modo anonimo (`CreateFrame("Frame")`) e salvato tramite `rawset(_G, "FWHUD_SwingFrame", f)` per evitare il warning di sovrascrittura di variabili globali (`checkGlobals`).
  - Nelle azioni `actions.start` e `actions.finish` di `Rotational Bar - HS Queued`, il codice Lua è configurato come script puro senza wrapper `function() ... end`, poiché WeakAuras vi applica automaticamente `return function() ... end`.

### 4.2 Gruppo Dinamico Procs & Weapon Desync Alert (`01 - Procs warDPS`)
- **Posizione**: Disposto orizzontalmente a $y = 52$ sopra la Castbar con riposizionamento automatico centrato.
- **7 Icone Reattive**:
  1. `Bloodsurge`: Slam istantaneo con swipe circolare e animazione dorata.
  2. `Victory Rush`: Proc *Victorious* post-uccisione con conto alla rovescia di 20s e glow dorato.
  3. `Flurry`: +25% attack speed (3 cariche).
  4. `Wrecking Crew`: +10% danno fisico per 12s da critico.
  5. `Rend`: Debuff sanguinamento applicato sul bersaglio corrente con timer al decimo.
  6. `Execute Usable`: Icona attiva con bordo luminoso ed etichetta `EXEC` sotto il 20% di salute del boss.
  7. `Weapon Desync Alert (SYNC)`: Icona di allerta (`Ability_DualWield`, 34x34px) collocata immediatamente a destra di *Execute Usable*.
- **Theorycrafting Weapon Desync**:
  - Se le armi MH e OH colpiscono contemporaneamente ($|\Delta t| < 0.30\text{s}$), l'OH non riesce a generare rabbia prima che l'MH consumi l'Heroic Strike accodato. L'allerta compare con **Pixel Glow rosso lampeggiante** ed etichetta rossa `SYNC`, avvisando il giocatore di resettare il ciclo d'attacco con la macro `/cleartarget /targetlasttarget /startattack`. Nascosta e impercettibile ($0$ px) in condizioni ottimali di sfasamento (Regola del 50%, $|\Delta t| \approx 1.1\text{s} - 1.4\text{s}$).

### 4.3 Buffs Anti-Clutter (`02 - Battle Shout`, `03 - Commanding Shout`, `04 - Berserker Stance`)
- **Filtri Overlap Raid**: Nascosti durante il combattimento se hanno più di 30 secondi residui o se l'effetto è coperto da buff equivalenti (*Blessing of Might / GBoM* del Paladino per Battle Shout, *Blood Pact* dell'Imp per Commanding Shout).
- **Allerta 'OFF'**: Mostrano un avviso desaturato solo se il buff manca completamente.
- **Berserker Stance**: Allerta ad alta visibilità con badge `STANCE` se il guerriero si trova fuori dalla postura da combattimento Berserker durante un incontro.

### 4.4 Centratura Dinamica Riga Utility (`05` - `13`, da 3 a 10 Icone)
- **Ordine rigoroso da sinistra a destra**:
  `[05 - Trinket 1] -> [06 - Trinket 2] -> [06b - Ring] -> [07 - Cloak] -> [08 - Tier Set] -> [09 - Enchants] -> [10 - Gloves] -> [11 - Death Wish] -> [12 - Recklessness] -> [13 - Boots]`
- **Smart Burst Advisor (`12 - Recklessness`)**:
  - Advisor reattivo per ottimizzare il lancio di Recklessness durante finestre di alto danno:
    - In combattimento contro un bersaglio vivente e attaccabile, con abilità pronta (`state == "READY"`).
    - Con Death Wish attivo: richiede almeno $\ge 2$ proc maggiori (Trinket 1, Trinket 2, Ashen Band, Berserking armi).
    - Senza Death Wish: richiede almeno $\ge 3$ proc maggiori simultanei.
    - Notifica visiva: **Pixel Glow Fuoco** arancione caldo (`[1.0, 0.35, 0.0, 1.0]`) senza testo o clutter invasivo.
    - All'attivazione: transizione istantanea a Pixel Glow giallo con conteggio cariche (`x3`, `x2`, `x1`).
    - In ricarica o out-of-combat: spegnimento totale del glow.
- **Safe Region Accessor (`getRegion`)**:
  - Sostituito l'accesso diretto a `WeakAuras.regions` con il safe accessor:
    ```lua
    local function getRegion(id)
        return (WeakAuras.GetRegion and WeakAuras.GetRegion(id)) or (WeakAuras.regions and WeakAuras.regions[id])
    end
    ```
  - Elimina al 100% il warning di deprecazione su tutti i moduli utility in WeakAuras 5.21.8+.
- **Eliminazione di `COMBAT_LOG_EVENT_UNFILTERED` Grezzo nei Trigger**:
  - Rimosso dall'array `events_list` del trigger custom. Il frame listener `FWHUD_CoreFrame` (creato anonimamente e registrato con `rawset`) intercetta il log di combattimento ed emette l'evento dedicato `FWHUD_ROW_UPDATE`.
- **Passo Adattivo e Geometria**:
  - Qualsiasi combinazione di icone attive viene centrata specularmente sotto la barra della rabbia senza alcun disallineamento orizzontale ($\sum x = 0$).

### 4.5 Pannello Statistiche in Tempo Reale (`18 - Stats Panel warDPS`)
- Aggiornato in tempo reale ad ogni variazione di equipaggiamento, buff, proc e debuff del bersaglio:
  - **AP**: Attack power totale calcolato con moltiplicatori e proc attivi.
  - **Crit**: Critico melee con debuff non duplicati (*Heart of the Crusader*, *Master Poisoner*, *Totem of Wrath*).
  - **Haste**: Melee Haste dinamica (*Windfury / Icy Talons* +20%, *Bloodlust* +30%, *Flurry* +25%, *Berserking Troll* +20%).
  - **ArP**: Rating e percentuale con badge verde **`(CAP)`** al raggiungimento di 1400.
  - **Hit & Exp**: Indicazione immediata dell'8% Special Hit cap e del soft cap 26 Expertise.

### 4.6 Sunder Armor Tracker (`19 - Sunder Armor Tracker`)
- Monitora cariche (1-5 con evidenziazione verde al cap), tempo residuo del debuff sul bersaglio ancorato alla base dell'icona, rilevamento automatico di *Expose Armor* del Ladro (`EA` in ciano) per prevenire sprechi di rabbia e allerta `OFF` rossa in assenza di debuff di riduzione armatura.

### 4.7 Architettura SubRegions & Dual-Key Text Anchoring
- In WeakAuras 5.x (`SubRegionTypes/SubText.lua`), l'ancoraggio nativo dei subtext legge rigorosamente il campo `anchor_point` (con underscore), mentre le definizioni classiche leggevano `anchorPoint` / `text_anchorPoint`.
- La funzione factory `make_subtext` in `builder/core/helpers.py` popola contemporaneamente sia i campi nativi che i relativi alias e offset (`anchor_point`, `anchorPoint`, `text_anchorPoint`, `anchorXOffset`, `anchorYOffset`, `text_anchorXOffset`, `text_anchorYOffset`, `text_xOffset`, `text_yOffset`), garantendo parità visiva al 100% senza collassi o disallineamenti del testo su entrambi gli engine.

---

## 5. Gestione dei File di Memoria DOCS

Come concordato e specificato nella configurazione `.gitignore`:
- I file markdown presenti in `docs/*.md` contengono la memoria persistente, gli ADR decisionali e l'architettura tecnica per gli assistenti AI e gli sviluppatori.
- **Questi file sono rigorosamente esclusi dal repository Git** e non compaiono nei commit.
- Il simulatore web `docs/index.html` fa eccezione ed è incluso nel versionamento Git per consentire il funzionamento della live demo su GitHub Pages.
