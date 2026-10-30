# Class Warrior (Fury) — WeakAuras Suite

[![WoW Version](https://img.shields.io/badge/World%20of%20Warcraft-3.3.5a%20(12340)-orange.svg)](https://github.com/Glacyal/fury-warrior-335a-am)
[![WeakAuras](https://img.shields.io/badge/WeakAuras-4.0.0-blue.svg)](https://github.com/Glacyal/fury-warrior-335a-am)
[![Class](https://img.shields.io/badge/Class-Warrior%20(Fury%20TG)-red.svg)](https://github.com/Glacyal/fury-warrior-335a-am)
[![GitHub Pages](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen.svg)](https://glacyal.github.io/fury-warrior-335a-am/)
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-gray.svg?logo=paypal&logoColor=white&labelColor=0079c1)](https://www.paypal.me/AMantmar)

Suite WeakAuras completa, modulare e ordinata per **Warrior Fury (Titan's Grip) Livello 80** in World of Warcraft 3.3.5a (*Wrath of the Lich King - Build 12340*).  
Progettata per garantire la massima efficacia in combattimento, un consumo ridotto di risorse CPU, un monitoraggio chiaro e affidabile dei proc, gestione millisecondo-precisa del **Dual-Wield Swing Timer (MH/OH)** e della coda **Heroic Strike / Cleave**, e un'interfaccia pulita senza elementi superflui (*Zero Clutter*), orientata all'ottimizzazione del DPS.

---

## 🌐 Anteprima Online (Live Simulator)

Visualizza e interagisci con l'HUD direttamente dal browser senza installare nulla:  
👉 **[Apri il Simulatore Web su GitHub Pages](https://glacyal.github.io/fury-warrior-335a-am/)**  
- **Test Interattivo Equip/Unequip**: simula l'indossamento o la rimozione di Monili, Anello Ashen, Mantello, Guanti e Incanti con contrazione ed espansione automatica dell'HUD.
- **Dual Swing Timer & Queueing**: visualizza l'avanzamento speculare dello swing per Mano Primaria e Mano Secondaria con evidenziazione in tempo reale della coda per Heroic Strike e Cleave.
- **Precision Timers & Radial Cooldown Clock**: tutti i proc e gli ICD presentano conto alla rovescia al secondo e animazione circolare clock swipe autentica.  

---

## 🌟 Caratteristiche Principali

Tutti i componenti del pacchetto sono organizzati con una numerazione sequenziale ordinata (da **01** a **19**):

### 1. Barra Rotazionale & Dual Swing Timer (`15 - Rotational Bar`)
Posizionata visivamente a centro schermo subito sopra la barra della rabbia, gestisce il monitoraggio del ritmo di attacco e della priorità in combattimento:
- **Doppio Swing Timer Speculare con Timing Numerico Live**:
  - **Mezza Barra Sinistra (MH)**: Avanzamento dello swing per la Mano Primaria con etichetta MH e conto alla rovescia numerico live.
  - **Mezza Barra Destra (OH)**: Avanzamento dello swing per la Mano Secondaria con etichetta OH e conto alla rovescia numerico live.
- **Rilevamento ed Evidenziazione Differenziata HS vs Cleave Queued**:
  - Quando **Heroic Strike** è in coda: La barra si illumina con bordo dorato e mostra la scritta centrale `[HS QUEUED]`.
  - Quando **Cleave** è in coda: La barra si illumina con bordo verde smeraldo e mostra la scritta centrale `[CLEAVE QUEUED]`.
  - Consente di distinguere istantaneamente la coda per bersaglio singolo rispetto all'AoE, garantendo che il colpo elimini i colpi di striscio (*glancing blow*) sulla mano primaria e rimuova la penalità del 27% miss sull'arma secondaria.

### 2. Gruppo Dinamico Procs (`01 - Procs warDPS`)
Posizionato nella parte superiore dell'HUD, gestisce fino a 6 icone con riposizionamento orizzontale automatico, riservato ai proc attivi e debuff chiave:
1. **Bloodsurge**: Slam istantaneo con animazione luminosa dorata e conto alla rovescia di 5 secondi.
2. **Victory Rush**: Proc *Victorious* post-uccisione nemico con conto alla rovescia di 20 secondi e animazione dorata.
3. **Rend**: Debuff sanguinamento applicato sul bersaglio corrente con durata di 15 secondi, timer al decimo e swipe circolare.
4. **Flurry**: +25% attack speed (3 cariche) dopo un colpo critico in mischia.
5. **Wrecking Crew / Enrage**: +10% danno fisico per 12s da critico.
6. **Execute Usable**: Icona attiva con bordo luminoso ed etichetta `EXEC` quando il bersaglio scende sotto il 20% di salute.

### 3. Schermo Pulito ("Zero Clutter")
- **02 - Battle Shout & 03 - Commanding Shout**: Rimangono nascosti durante il combattimento se hanno più di 30 secondi residui o se l'effetto è già coperto dai buff di raid equivalenti (*Blessing of Might* del Paladino per Battle Shout, *Blood Pact* dell'Imp del Warlock per Commanding Shout); mostrano l'icona con swipe e timer numerico solo se in scadenza, oppure un avviso "OFF" desaturato se il buff manca completamente.
- **04 - Berserker Stance**: Allerta immediata ad alta visibilità con etichetta `STANCE` se durante il combattimento il guerriero si trova fuori dalla Berserker Stance.
- **Caricamento Specifico su [Rampage]**: Il talento passivo *Rampage* è utilizzato come condizione di caricamento esclusiva dell'intero pacchetto: la suite si carica solo se il guerriero è specializzato Fury con Rampage attivo, evitando qualsiasi occupazione di memoria per altre classi o specializzazioni.

### 4. Barre Centrali & Avvisi
- **14 - Rage Bar**: Barra orizzontale con visualizzazione della percentuale numerica e cambio cromatico a 3 stadi: rosso scuro sotto i 25 punti (starvation), rosso pieno tra 25 e 44 punti (pronto per Bloodthirst/Whirlwind) e ambra/oro sopra i 45 punti (via libera allo scarico sicuro con Heroic Strike o Cleave).
- **15 - Rotational Bar**: Barra centrale con swing timer dual-wield posizionata subito sopra la barra della rabbia.
- **16 - Castbar warDPS**: Barra di lancio con icona dell'incantesimo attivo, nome e tempo residuo per lanci di Slam non-proc e cannellature.
- **17 - Alerts warDPS**: Avviso testuale centrale `SLAM READY!` ad alta visibilità con notifica acustica ("Tamburi di Guerra" su canale Master) all'attivazione di Bloodsurge.

### 5. Riga Utility Adattiva (`05` - `13`, da 3 a 10 Icone)
La riga inferiore si adatta in tempo reale con centratura automatica in base all'equipaggiamento indossato:
- **05 - Trinket 1 warDPS** e **06 - Trinket 2 warDPS**: Visibili solo se gli slot sono equipaggiati, con riconoscimento automatico di tutti i monili da mischia DPS e Tank di WotLK 3.3.5a con ICD reali verificati (*Deathbringer's Will*, *Sharpened Twilight Scale*, *Death's Choice/Verdict*, *Whispering Fanged Skull*, *Needle-Encrusted Scorpion*, *Dark-Matter*, *Mjolnir Runestone*, *Comet's Trail*, *Darkmoon Card: Greatness*, monili da tank e On-Use a 120s), animazione cooldown clock swipe radiale e bordo luminoso su proc attivo.
- **06b - Ring warDPS**: Compare solo se è equipaggiato nello slot anello un anello con proc attivo da mischia (*Ashen Band of Endless Vengeance* del Verdetto Cinereo, con proc *Frostforged Champion* +480 AP per 10s e 60s ICD).
- **07 - Cloak warDPS**: Compare solo con incanti da mischia attivi (*Swordguard Embroidery* +400 AP, o paracadute/flexweave di Ingegneria).
- **08 - Tier Set warDPS**: Rilevamento automatico dell'armatura Tier equipaggiata (T7, T8, T9, T10 e combinazioni ibride multi-set), tracciando bonus 2P/4P attivi (*Siegebreaker*, *Advantage*, *Spirits of the Lost*).
- **09 - Enchants warDPS**: Monitoraggio unificato degli incanti arma (Mano Primaria e Secondaria), presente esclusivamente se almeno un'arma possiede un incanto con proc (*Berserking*, *Mongoose*, *Executioner*, *Crusader*, *Blade Ward*, *Blood Draining*, *Black Magic*). Mostra il badge `x2` in alto in caso di doppio proc simultaneo (+800 AP con doppio Berserking) e timer FIFO alla base con durata residua del primo incanto in scadenza.
- **10 - Gloves warDPS**: Compare solo se i guanti possiedono gli *Acceleratori Ipersonici* di Ingegneria (+340 Haste per 12s, 60s CD).
- **11 - Death Wish**: Monitora durata attiva (+20% danno) e tempo di recupero.
- **12 - Recklessness**: Tracciamento delle cariche di critico garantito e tempo di recupero.
- **13 - Boots warDPS**: Compare solo se gli stivali possiedono gli *Acceleratori a Nitro* di Ingegneria (5s sprint, 180s CD), nascondendosi automaticamente in presenza di incanti con statistiche passive.
- **Centratura Automatica Dinamica**: Qualsiasi combinazione di icone attive (fino a 10 icone con passo adattivo) viene allineata in modo perfettamente simmetrico ed equilibrato sotto la barra della rabbia senza alcun disallineamento.

### 6. Pannello Statistiche in Tempo Reale (`18 - Stats Panel warDPS`)
Aggiorna in tempo reale i valori effettivi tenendo conto di equipaggiamento, talenti, consumabili e sinergie di raid:
- **AP**: Attack power totale calcolato in tempo reale con buff e proc (*Battle Shout*, *GBoM*, *Berserking MH/OH*, *Ashen Band*, *DBW*, *STS*, *T10 2P*).
- **Crit**: Critico in mischia con debuff *Heart of the Crusader*, *Master Poisoner* e *Totem of Wrath* (+3%) sul bersaglio senza conteggi duplicati.
- **Haste**: Melee Haste dinamica calcolata combinando rating e moltiplicatori raid (*Windfury Totem / Improved Icy Talons* +20%, *Swift Retribution / Improved Moonkin* +3%, *Bloodlust* +30%, *Flurry* +25%, *Berserking Troll* +20%).
- **ArP**: Percentuale e rating di Armor Penetration, con indicatore verde **`(CAP)`** al raggiungimento del cap di 1400 rating.
- **Hit & Exp**: Verifica visiva istantanea del cap 8% Special Hit (con aura Draenei *Heroic Presence* +1%) e del soft cap 26 Expertise.

### 7. Sunder Armor Tracker (`19 - Sunder Armor Tracker`)
Icona dinamica posizionata a destra della barra rotazionale:
- **Cariche in Alto al Centro**: Visualizzazione numerica delle cariche applicate (da 1 a 5) con evidenziazione in verde al raggiungimento del cap massimo di 5 cariche.
- **Timer di Scadenza**: Durata residua del debuff sul bersaglio ancorata alla base dell'icona per un rinnovo ottimale senza sovrapposizione visiva.
- **Riconoscimento Expose Armor**: Rilevamento automatico di *Expose Armor* del Ladro con indicatore `EA` in ciano per evitare di sprecare rabbia sul debuff.
- **Allerta 'OFF'**: Se il debuff manca completamente sul bersaglio ostile, mostra l'indicazione `OFF` in rosso.

---

## ⚙️ Struttura Modulare del Progetto (`builder/`)

Il codice sorgente separa la compilazione della stringa dalla definizione di ciascun componente dell'interfaccia:

```text
Fury Warrior 3.3.5a AM/
├── builder/
│   ├── core/                        # Compressione e codifica stringa WeakAuras
│   │   ├── constants.py             # Costanti, condizioni di caricamento e texture
│   │   ├── serializer.py            # Serializzazione compatibile AceSerializer-3.0
│   │   ├── deflate.py               # Compressione Deflate e codifica LibDeflate
│   │   ├── encoder.py               # Generatore del formato !WA:1!
│   │   └── helpers.py               # Funzioni di supporto per testi e formattazione
│   ├── components/                  # Moduli funzionali dell'HUD
│   │   ├── rotational.py            # 15 - Rotational Bar (Dual Swing Timer MH/OH & Queueing HS/Cleave)
│   │   ├── procs.py                 # 01 - Procs warDPS (gruppo dinamico superiore)
│   │   ├── buffs.py                 # 02/03/04 - Battle Shout, Commanding Shout, Berserker Stance
│   │   ├── utility.py               # 05-13 - Monili, Anello, Mantello, Tier Set, Incanti, Guanti, DW, Reck, Stivali
│   │   ├── bars.py                  # 14 - Rage Bar & 16 - Castbar warDPS
│   │   ├── alerts.py                # 17 - Alerts warDPS (avvisi testuali centrali)
│   │   ├── stats.py                 # 18 - Stats Panel warDPS (pannello statistiche in tempo reale)
│   │   └── sunder.py                # 19 - Sunder Armor Tracker (tracciamento cariche e Expose Armor)
│   └── tree.py                      # Albero complessivo del gruppo (20 nodi principali, 38 sotto-aure)
├── docs/
│   └── index.html                   # Simulatore web interattivo
├── tests/                           # Suite di test automatici
│   ├── run_parallel_tests.py        # Esecutore parallelo multi-core
│   ├── test_buffs.py                # Test gestione Shout e Berserker Stance
│   ├── test_components_integrity.py # Verifica integrità strutturale e numerazione 01-19
│   ├── test_lua.py                  # Controllo sintassi dei blocchi Lua inclusi
│   ├── test_rotational.py           # Test barra rotazionale, swing timer MH/OH e coda HS/Cleave
│   ├── test_stats_panel.py          # Verifica formule e moltiplicatori del pannello statistiche
│   ├── test_string_sync.py          # Verifica corrispondenza tra builder e IMPORT_STRING.txt
│   ├── test_sunder_tracker.py       # Test Sunder Armor, conteggio cariche e allerta OFF
│   ├── test_tree_layout.py          # Verifica gerarchia e ordinamento dell'albero
│   └── test_utility_row.py          # Test esaustivo su ICD, incanti arma x1/x2 e riga utility
├── generate.py                      # Script di compilazione della stringa finale
├── IMPORT_STRING.txt                # Stringa WeakAuras pronta per l'importazione
└── scripts/
    └── sync_docs.py                 # Sincronizzazione automatica di IMPORT_STRING.txt in docs/index.html
```

---

## 🚀 Installazione in Gioco (3 Passaggi)

1. **Copia la Stringa**: Apri il file **[`IMPORT_STRING.txt`](IMPORT_STRING.txt)** e copia l'intero contenuto (`Ctrl+A`, poi `Ctrl+C`).
2. **Apri WeakAuras**: In gioco, digita il comando `/wa` nella chat.
3. **Importa**: Clicca su **Import** in alto a sinistra, incolla il testo con `Ctrl+V` e conferma l'importazione.

---

## 📌 Compatibilità Addon & Client

| Client / Piattaforma | Versione WeakAuras | Compatibilità | Note |
| :--- | :--- | :---: | :--- |
| **WotLK 3.3.5a (Build 12340)** | **WeakAuras 4.0.0** | ✅ **100% Nativa** | Sviluppata e collaudata su WeakAuras 4.0.0 (`internalVersion: 52`). Importazione rapida e priva di blocchi (~82 KB). |

---

## 🧪 Validazione & Test Suite

Il progetto include una suite di 9 test automatici eseguibili sia in parallelo per una verifica rapida, sia in modalità standard:

```bash
# Esecuzione parallela multi-core della suite completa (9/9 PASS)
python tests/run_parallel_tests.py

# Esecuzione standard tramite unittest
python -m unittest discover tests

# Ricompilazione della stringa di importazione
python generate.py
```

---

## 📄 Licenza

Distribuito sotto licenza **MIT**.  
Repository: [Glacyal/fury-warrior-335a-am](https://github.com/Glacyal/fury-warrior-335a-am)
