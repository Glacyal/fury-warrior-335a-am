# Class Warrior (Fury) — WeakAuras Suite

[![WoW Version](https://img.shields.io/badge/World%20of%20Warcraft-3.3.5a%20(12340)-orange.svg)](https://github.com/Glacyal/fury-warrior-335a-am)
[![WeakAuras](https://img.shields.io/badge/WeakAuras-4.0.0-blue.svg)](https://github.com/Glacyal/fury-warrior-335a-am)
[![Class](https://img.shields.io/badge/Class-Warrior%20(Fury%20TG)-red.svg)](https://github.com/Glacyal/fury-warrior-335a-am)
[![GitHub Pages](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen.svg)](https://glacyal.github.io/fury-warrior-335a-am/)
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-gray.svg?logo=paypal&logoColor=white&labelColor=0079c1)](https://www.paypal.me/AMantmar)

Suite WeakAuras completa, modulare e ad altissime prestazioni per **Warrior Fury (Titan's Grip) Livello 80** in World of Warcraft 3.3.5a (*Wrath of the Lich King - Build 12340*).  
Progettata per garantire la massima efficacia in combattimento, un consumo CPU trascurabile (< 0.1% in raid 25), un monitoraggio millisecondo-preciso di **Heroic Strike Queueing**, **Swing Timer Dual-Wield (MH/OH)**, proc di **Bloodsurge**, gestione completa di **tutti i Tier Set WotLK (T7, T8, T9, T10)**, catalogo esaustivo di **tutti i monili da mischia 3.3.5a**, incanti armi (**Berserking MH/OH x1/x2 fino a +800 AP**) e una visuale perfettamente pulita (*Zero Clutter*).

---

## 🌐 Anteprima Online (Live Simulator)

Visualizza e interagisci con l'HUD direttamente dal browser senza installare nulla:  
👉 **[Apri il Simulatore Web su GitHub Pages](https://glacyal.github.io/fury-warrior-335a-am/)**  

---

## 🌟 Caratteristiche Principali

Tutti i componenti del pacchetto sono organizzati con una numerazione sequenziale rigorosa da **01** a **19**:

### 1. Gruppo Dinamico Procs Rotazionali (`01 - Procs warDPS`)
Barra orizzontale superiore (y = 52) con riposizionamento dinamico centrato, riservata **esclusivamente ai proc di combattimento attivi**:
1. **Bloodsurge**: Slam istantaneo con pixel glow dorato e conto alla rovescia di 5 secondi.
2. **Victory Rush**: Proc *Victorious* (Spell 34428 / Buff 32216) con conto alla rovescia di 20 secondi e pixel glow verde.
3. **Flurry**: +25% attack speed (3 cariche) dopo un critico in mischia.
4. **Wrecking Crew / Enrage**: +10% danno fisico per 12s da critico.
5. **Execute Usable**: Icona attiva con bordo luminoso ed etichetta `EXEC` quando il boss scende sotto il 20% di salute.

### 2. Zero Clutter & Intelligenza Overlap di Raid
- **02 - Battle Shout**: Gruppo genitore con architettura Active/OFF a zero sfarfallio (icone guerriero esclusive `Ability_Warrior_BattleShout` con `auto: False`): mostra l'icona con swipe e timer numerico se in scadenza (<= 30s); se mancano sia Battle Shout che BoM/GBoM del Paladino mostra l'avviso "OFF" desaturato pilotato da eventi `UNIT_AURA` con untrigger immediato; è completamente nascosto se attivo e sano (> 30s) o coperto da Paladino.
- **03 - Commanding Shout**: Gruppo genitore con architettura Active/OFF a zero sfarfallio (icone guerriero esclusive `Ability_Warrior_CommandingShout` con `auto: False` per tutti i Rank 1-3): mostra l'icona con swipe e timer numerico se in scadenza (<= 30s); se mancano sia Commanding Shout che Blood Pact dell'Imp del Warlock mostra l'avviso "OFF" desaturato pilotato da eventi `UNIT_AURA` con untrigger immediato; è completamente nascosto se attivo e sano (> 30s) o coperto dal Warlock.
- **04 - Berserker Stance**: Allerta immediata ad alta visibilità se durante il combattimento il guerriero si trova fuori dalla Berserker Stance (con scritta compatta 'STANCE', font 8).
- **Caricamento Specifico su [Rampage]**: Il talento passivo *Rampage* (Tab 2, Posizione 24 -> ID WeakAuras 64) è utilizzato come condizione di caricamento esclusiva dell'intero pacchetto: la suite si carica solo se il guerriero è specializzato Fury con Rampage attivo, e non occupa spazio visivo superfluo a schermo.

### 3. Riga Utility Adattiva (`05` - `13`, da 3 a 11 Icone a y = -45)
Fila orizzontale inferiore a y = -45 con riposizionamento e ricentratura automatica naturale (espansione e contrazione dinamica identica a fire-mage-335a-am, con proporzioni geometriche auto-calibrate per rimanere contenuta entro i 278px della Rage Bar):
- **05 - Trinket 1 warDPS & 06 - Trinket 2 warDPS**: Riconoscimento automatico slot 13 & 14 (suffisso `warDPS` anti-collisione). Catalogo esaustivo di **tutti i monili da mischia DPS e Tank 3.3.5a con ICD reali verificati online**:
  - *Deathbringer's Will*: proc 30s, ICD reale **105s** (trasformazioni Vrykul, Taunka, Iron Dwarf con icone dinamiche).
  - *Sharpened Twilight Scale*: proc 15s, ICD reale **45s** (+1472 / +1304 AP).
  - *Death's Choice / Verdict*: proc 15s, ICD reale **45s** (+510 / +450 Strength).
  - *Whispering Fanged Skull*: proc 15s, ICD reale **45s** (+1250 / +1100 AP).
  - *Mirror of Truth*, *Anvil of Titans*, *Coren's Chromium Coaster*: proc *Reflection of Torment* (+1000 AP per 10s, ICD reale **45s**, Spell 60065).
  - *Needle-Encrusted Scorpion*: proc *Now is the Time!* (+678 ArP per 10s, ICD reale **45s**).
  - *Dark-Matter*: proc critico (+612 Crit per 10s, ICD reale **45s**).
  - *Mjolnir Runestone* & *Comet's Trail*: proc 10s, ICD reale **45s** (+665 ArP / +722 Haste).
  - *Darkmoon Card: Greatness*, *Grim Toll*, *Banner of Victory*, *Meteorite Whetstone*, *Vestige of Haldor*: ICD reale **45s**.
  - *Wrathstone*, *Mark of Supremacy*, *Incisor Fragment*, *Loatheb's Shadow*, *Shard of Crystal Heart*: On-Use 20s, Cooldown **120s**.
  - *Herkuml War Token*: accumulo cariche (1-20) e durata 10s, nessun ICD.
  - **Monili Tank Supportati**: *Juggernaut's Vitality* / *Satrina's Impeding Scarab* (+4610/+5186 Max HP, 180s CD), *Corroded Skeleton Key* (Hardened Skin assorbe 6400 danni, 120s CD), *Unidentifiable Organ* (stacking armor fino a 10 cariche), *Sindragosa's Flawless Fang* (Aegis of Dalaran, 60s CD), *Glyph of Indomitability* (Dodge +512, 120s CD), *The Black Heart* (+705 Armor, 45s ICD), *Essence of Gossamer* (absorb, 45s ICD), *Lavanthor's Talisman*, *Heart of Iron*, *Ick's Rotting Thumb*, *Purified Onyxia Blood Talisman*, *Royal Seal of King Llane*, *The General's Heart*, *Monarch Crab*, *Ruby Hare*, *Brawler's Souvenir*, *Seal of the Pantheon* e Medaglioni PvP / Battlemaster's.
  - Tre stati visivi in tempo reale a 60+ FPS: **READY** (pronto, icona dell'oggetto senza swipe né testo), **PROC ATTIVO** (icona specifica del buff, swipe di durata attiva, testo giallo `|cFFFFFF00%.1fs|r` e Pixel Glow dorato) e **ICD** (icona dell'oggetto, swipe di ricarica residua e timer numerico rosso `|cFFFF4444%d:%02d|r` o `|cFFFF4444%.0fs|r` fino a 0s).
  - Motore di aggiornamento reattivo ad alte prestazioni con trigger `check: "update"` e cache temporale frame-by-frame (`_G.FWHUD_SlotCache`), con fallback euristico per nome monile e parsing CLEU `SPELL_AURA_APPLIED` / `SPELL_AURA_REMOVED`.
- **06b - Ring warDPS**: Monitoraggio dell'anello con proc nello slot 11 o 12 (sul modello di fire-mage-335a-am):
  - *Ashen Band of Endless Vengeance* (Item 50402/50401): Proc *Frostforged Champion* (+480 AP per 10s, ICD **60s**).
  - *Band of the Eternal Champion* (Item 29301): Proc (+160 AP per 10s, ICD **60s**).
  - Compare solo se equipaggiato, con Pixel Glow dorato su proc e timer di ICD.
- **07 - Cloak warDPS**: Attivo con incanti da mischia (Swordguard Embroidery +400 AP o paracadute/flexweave).
- **08 - Tier Set warDPS (T7 - T10 & Combinazioni Multi-Set)**: Rilevamento automatico dell'armatura Tier equipaggiata (>= 2 o >= 4 pezzi) e tracciamento proc intelligente con supporto combinazioni (es. 2P T10 + 2P T8, 2P T10 + 2P T9, 2P T8 + 2P T7):
  - **Tier 10 (Ymirjar Lord)**: 4P Siegebreaker (2 cariche e -0.5s GCD su Slam/Execute) e 2P Advantage (+16% AP per 10s da Deep Wounds/Rend).
  - **Tier 8 (Siegebreaker)**: 2P proc (+150 Haste per 5s da critici di Heroic Strike e Slam); 4P passivo (+10% crit Bloodthirst e Mortal Strike).
  - **Tier 7 (Heroes' / Valorous Dreadnaught)**: 4P proc **Spirits of the Lost** (Spell 60176 - riduce di 5 il costo in rabbia della prossima abilità con timer e Pixel Glow); 2P passivo (+10% danno a Slam).
  - **Tier 9 (Hellscream/Wrynn)**: Bonus passivi di stance e critico.
  - **Combinazioni Multi-Set Ibride**: Valutazione dinamica in priorità di esecuzione; se più proc si attivano contemporaneamente, viene evidenziata la finestra più urgente/breve passando istantaneamente all'altro proc al consumo del primo.
- **09 - Enchants warDPS**: Monitoraggio unificato ed ergonomico degli incanti arma (Slot 16 MH e Slot 17 OH):
  - **Meccanica PPM & Assenza di ICD**: In WotLK 3.3.5a, *Berserking* (così come *Mongoose* ed *Executioner*) è regolato dal sistema **PPM (~1.0 PPM)** e **NON possiede alcun Cooldown Interno (ICD = 0s)**. Può riattivarsi back-to-back, eseguire refresh continuativo dei 15s e tornare subito in stato READY senza blocchi né countdown rossi di lockout.
  - **Badge Cariche `x2` in Alto**: Ciascuna arma (MH e OH) calcola il proc in modo indipendente. Se entrambe le armi attivano l'incanto contemporaneamente (doppio Berserking per **+800 AP complessivi**), compare il badge `x2` in alto in giallo (`INNER_TOP`, font 11). Quando è attivo 1 solo proc, il badge è vuoto.
  - **Timer FIFO alla Base**: Mostra sempre la durata residua del proc che scadrà per primo (`INNER_BOTTOM`, font 10). Alla sua scadenza, transiziona istantaneamente al secondo proc residuo azzerando contemporaneamente il badge `x2`.
  - **Swipe e Glow**: Swipe radiale coordinato sulla durata del proc FIFO e Pixel Glow dorato attivo su qualsiasi proc attivo. Supporta anche *Executioner*, *Mongoose* e *Black Magic*.
- **10 - Gloves warDPS**: Acceleratori Ipersonici Ingegneria (+340 Haste per 12s, 60s CD).
- **11 - Death Wish**: Durata attiva 30s (+20% danno) e cooldown.
- **12 - Recklessness**: Tracciamento delle 3 cariche di critico garantito e cooldown.
- **13 - Boots warDPS**: Stivali a nitro (Nitro Boosts) o incanti velocità con stato pronto e ricarica.
- **Standard Cromatico & Formattazione Tempi (Allineato 1:1 a Fire Mage)**:
  - **Proc Attivo**: testo in giallo brillante al decimo di secondo (`|cFFFFFF00%.1fs|r`) con animazione circolare e contorno Pixel Glow dorato.
  - **ICD / Cooldown di Ricarica**: testo bianco standard (senza tag di colore e senza la lettera `s`), formattato in minuti:secondi (`%d:%02d`, es. `1:15`) se $\ge 60\text{s}$ oppure in secondi interi (`%.0f`, es. `45`, `30`, `12`) se $< 60\text{s}$, garantendo una visualizzazione sobria e pulita identica a quella nativa di WoW e di Fire Mage.
  - **Stato Pronto (Ready)**: testo vuoto `""` e icona statica a colori naturali pronta per il prossimo proc.

### 4. Barra della Rabbia Dinamica (`14 - Rage Bar`)
Barra orizzontale di precisione (278x14px a y = -20) con lettura numerica (%p) e cambio cromatico a 3 stadi:
- **< 25 Rage**: Rosso scuro attenuato (allerta starvation).
- **25 - 44 Rage**: Rosso sangue pieno (capacità di lanciare Bloodthirst/Whirlwind).
- **>= 45 Rage**: Transizione istantanea ad **Ambra/Oro** per indicare il via libera allo scarico sicuro con Heroic Strike/Cleave!

### 5. Barra Rotazionale & Dual Swing Timer (15 - Rotational Bar)
Posizionata visivamente a centro schermo subito sopra la barra della rabbia (278x7px):
- **Doppio Swing Timer Speculare con Timing Numerico Live**:
  - **Mezza Barra Sinistra (MH)**: Avanzamento dello swing per la Mano Primaria con etichetta MH a sinistra e countdown numerico centrato nella barretta (es. 1.8s durante l'animazione di swing, velocità arma da fermo).
  - **Mezza Barra Destra (OH)**: Avanzamento dello swing per la Mano Secondaria con countdown numerico centrato nella barretta (es. 1.2s durante l'animazione di swing, velocità arma da fermo) ed etichetta OH a destra.
- **Rilevamento ed Evidenziazione Differenziata HS vs Cleave Queued**:
  - Quando **Heroic Strike** è in coda: La barra si illumina con bordo e bagliore dorato e mostra la scritta centrale |cFFFFD700[HS QUEUED]|r.
  - Quando **Cleave** è in coda: La barra si illumina con bordo e bagliore verde smeraldo e mostra la scritta centrale |cFF00FF00[CLEAVE QUEUED]|r.
  - Consente di distinguere istantaneamente la coda per single target rispetto all'AoE, garantendo che il colpo elimini i glancing blow sulla mano primaria e rimuova la penalità del 27% miss sull'arma secondaria!

### 6. Castbar Centrale (`16 - Castbar warDPS`)
Barra sincronizzata (278x20px a y = 8) per lanci di Slam non-proc e cannellature, con icona incantesimo a sinistra, nome al centro e tempo a destra.

### 7. Avviso Testuale ad Alta Visibilità (`17 - Alerts warDPS`)
Avviso singolo centrato compatto posizionato appena sopra la riga dei proc (y = 78):
- `SLAM READY!` in giallo brillante (`|cFFFFFF00`) quando Bloodsurge procca, indicando all'istante la disponibilità di Slam istantaneo senza alcun clutter o distrazione visiva.

### 8. Pannello Statistiche in Tempo Reale (`18 - Stats Panel warDPS`)
Pannello compatto (88x60px a x = -190, y = -45) con aggiornamento throttled a 10 Hz e 5 righe dinamiche:
- **AP**: Attack power totale con buff e moltiplicatori (Battle Shout, GBoM, Berserking MH/OH, Ashen Band, DBW, STS, T10 2P).
- **Crit**: Critico in mischia con debuff Heart of the Crusader / Master Poisoner / Totem of Wrath (+3%) sul bersaglio.
- **Haste**: Melee Haste dinamica calcolata con moltiplicatori raid: Windfury Totem / Improved Icy Talons (+20%), Swift Retribution / Improved Moonkin (+3%), Bloodlust (+30%), Flurry (+25%), Berserking Troll (+20%) e Power Infusion (+20%).
- **ArP**: Percentuale e rating, con dicitura **CAP in verde** al raggiungimento del cap di 1400.
- **Hit & Exp**: Verifica visiva istantanea del cap 8% Special Hit (con aura Draenei Heroic Presence +1%) e soft cap 26 Expertise.

### 9. Sunder Armor Tracker (19 - Sunder Armor Tracker)
A destra della Rotational Bar (x = 160, y = -7):
- **Cariche in alto al centro**: da 1 a 5 cariche (x1..x5, font 12) ancorate in alto (`INNER_TOP`), lasciando libero lo spazio inferiore per il timer ed evitando qualsiasi sovrapposizione visiva, con evidenziazione in verde brillante al raggiungimento del cap di 5 cariche (x5).
- **Timer di scadenza numerico** (es. 27s, font 10) ancorato alla base dell'icona (`INNER_BOTTOM`).
- **Riconoscimento Expose Armor** del Ladro (EA in alto in ciano) per evitare di sovrascrivere il debuff.
- **Allerta 'OFF'**: se il debuff manca sul bersaglio, mostra esclusivamente la scritta rossa OFF alla base dell'icona.

---

## 📥 Come Importare in Gioco

1. In World of Warcraft, apri WeakAuras digitando `/wa` in chat.
2. *(Consigliato)* Se presente una versione precedente di `Class Warrior (Fury)`, cancellala per evitare duplicati come `Castbar 2`.
3. Apri il file [`IMPORT_STRING.txt`](IMPORT_STRING.txt) o premi **"Copia Stringa !WA:1!"** nel [simulatore web](https://glacyal.github.io/fury-warrior-335a-am/).
4. Clicca su **Importa** (Import) in alto a sinistra in WeakAuras.
5. Premi `Ctrl + V` per incollare la stringa e premi **Importa Gruppo** (Import Group).

---

## 🛠️ Architettura e Sviluppo

Il repository include l'intero compilatore Python e la suite di test:

```powershell
# 1. Compila l'albero WeakAuras e genera IMPORT_STRING.txt
python generate.py

# 2. Sincronizza la stringa importata nella web app
python scripts/sync_docs.py

# 3. Esegui la suite di test parallela (9/9 PASS)
python tests/run_parallel_tests.py
```
