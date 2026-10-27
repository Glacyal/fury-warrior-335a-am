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
- **02 - Battle Shout**: Nascosto in combattimento se attivo con più di 30 secondi; mostra il timer in scadenza e allerta se assente. **Filtro Overlap**: Viene soppresso automaticamente se è attivo *Blessing of Might* o *Greater Blessing of Might* del Paladino (buff equivalente/superiore).
- **03 - Commanding Shout**: Diventa la shout di riferimento se Battle Shout è coperto dal Paladino. Viene soppresso automaticamente se è attivo il buff *Blood Pact* dell'Imp del Warlock.
- **04 - Berserker Stance**: Allerta immediata ad alta visibilità se durante il combattimento il guerriero si trova fuori dalla Berserker Stance.
- **Caricamento Specifico su [Rampage]**: Il talento passivo *Rampage* (Tab 2, Posizione 24 -> ID WeakAuras 64) è utilizzato come condizione di caricamento esclusiva dell'intero pacchetto: la suite si carica solo se il guerriero è specializzato Fury con Rampage attivo, e non occupa spazio visivo superfluo a schermo.

### 3. Riga Utility Adattiva (`05` - `13`, da 3 a 9 Icone a y = -45)
Fila orizzontale inferiore a y = -45 con riposizionamento e ricentratura automatica (espansione e contrazione dinamica identica a fire-mage-335a-am):
- **05 - Trinket 1 warDPS & 06 - Trinket 2 warDPS**: Riconoscimento automatico slot 13 & 14 (con suffisso dedicato `warDPS` per prevenire sovrascritture o duplicati `2` in caso di convivenza con la suite Fire Mage). Catalogo integrato di **tutti i monili da mischia 3.3.5a** (Deathbringer's Will, Sharpened Twilight Scale, Death's Choice/Verdict, Whispering Fanged Skull, Herkuml War Token, Needle-Encrusted Scorpion, Mjolnir Runestone, Comet's Trail, Darkmoon Card: Greatness, Grim Toll, Mirror of Truth, Wrathstone, Mark of Supremacy, ecc.) con tracciamento durata attiva, Pixel Glow e conto alla rovescia ICD.
- **07 - Cloak warDPS**: Attivo con incanti da mischia (Swordguard Embroidery +400 AP o paracadute/flexweave).
- **08 - Tier Set warDPS (T7 - T10)**: Rilevamento automatico dell'armatura Tier equipaggiata (>= 2 o >= 4 pezzi) e tracciamento proc:
  - **Tier 10 (Ymirjar Lord)**: 4P Siegebreaker (2 cariche e -0.5s GCD su Slam) e 2P Advantage (+16% AP per 10s da Deep Wounds).
  - **Tier 8 (Siegebreaker)**: 4P (+20% Attack Speed per 5s) e 2P (+150 Crit per 5s).
  - **Tier 7 (Dreadnaught)**: 4P (+610 AP per 10s da critico).
  - **Tier 9 (Hellscream/Wrynn)**: Bonus passivi di stance e critico.
- **09 - Enchants warDPS (Armi & Anello)**: Monitoraggio in tempo reale degli incanti arma ed anello:
  - **Berserking MH & OH**: Rilevamento singolo o doppio stack (**x2 con +800 AP complessivi**) con timer e Pixel Glow.
  - **Executioner**: +120 Armor Penetration per 15s.
  - **Mongoose**: +120 Agilità e 2% Haste per 15s.
  - **Ashen Band of Endless Might**: Proc anello +480 AP per 10s (60s ICD).
- **10 - Gloves warDPS**: Acceleratori Ipersonici Ingegneria (+340 Haste per 12s, 60s CD).
- **11 - Death Wish**: Durata attiva 30s (+20% danno) e cooldown.
- **12 - Recklessness**: Tracciamento delle 3 cariche di critico garantito e cooldown.
- **13 - Boots warDPS**: Stivali a nitro (Nitro Boosts) o incanti velocità con stato pronto e ricarica.

### 4. Barra della Rabbia Dinamica (`14 - Rage Bar`)
Barra orizzontale di precisione (278x14px a y = -20) con lettura numerica (%p) e cambio cromatico a 3 stadi:
- **< 25 Rage**: Rosso scuro attenuato (allerta starvation).
- **25 - 44 Rage**: Rosso sangue pieno (capacità di lanciare Bloodthirst/Whirlwind).
- **>= 45 Rage**: Transizione istantanea ad **Ambra/Oro** per indicare il via libera allo scarico sicuro con Heroic Strike/Cleave!

### 5. Barra Rotazionale & Dual Swing Timer (`15 - Rotational Bar`)
Posizionata visivamente a centro schermo subito sopra la barra della rabbia (278x7px):
- **Doppio Swing Timer Speculare con Timing Numerico Live**:
  - **Mezza Barra Sinistra (MH)**: Avanzamento dello swing per la Mano Primaria con etichetta `MH` e countdown numerico al decimo di secondo (es. `1.8s` in combattimento, velocità arma da fermo).
  - **Mezza Barra Destra (OH)**: Avanzamento dello swing per la Mano Secondaria con countdown numerico al decimo di secondo (es. `1.2s` in combattimento, velocità arma da fermo) ed etichetta `OH`.
- **Rilevamento Heroic Strike / Cleave Queued**:
  - Non appena Heroic Strike o Cleave viene accodato, l'intera barra si illumina istantaneamente con un **Pixel Glow dorato** e compare la dicitura centrale `[HS QUEUED]`.
  - Fornisce la certezza visiva che il colpo successivo eliminerà i glancing blow sulla mano primaria e applicherà all'arma secondaria il cap di hit speciale (8%) invece della penalità 27% del dual wield!

### 6. Castbar Centrale (`16 - Castbar warDPS`)
Barra sincronizzata (278x20px a y = 8) per lanci di Slam non-proc e cannellature, con icona incantesimo a sinistra, nome al centro e tempo a destra.

### 7. Avvisi Testuali ad Alta Visibilità (`17 - Alerts warDPS`)
Avvisi a caratteri cubitali a centro schermo (y = 105):
- `BLOODSURGE! / SLAM READY!` in giallo/arancione quando Bloodsurge si attiva.
- `EXECUTE PHASE (< 20%)!` in rosso fuoco quando il target scende sotto il 20% di salute.

### 8. Pannello Statistiche in Tempo Reale (`18 - Stats Panel warDPS`)
Pannello compatto (88x48px a x = -190, y = -45) con aggiornamento throttled a 10 Hz:
- **AP**: Attack power totale con buff e moltiplicatori.
- **Crit**: Critico in mischia con debuff Heart of the Crusader / Master Poisoner (+3%) sul bersaglio.
- **ArP**: Percentuale e rating, con dicitura **CAP in verde** al raggiungimento del cap di 1400.
- **Hit & Exp**: Verifica visiva istantanea del cap 8% Special Hit e soft cap 26 Expertise.

### 9. Sunder Armor Tracker (`19 - Sunder Armor Tracker`)
Colonna destra (x = 169, y = 45):
- Traccia da 1 a 5 cariche sul bersaglio corrente con countdown di durata.
- Colore verde al raggiungimento delle 5 cariche massime.
- Riconoscimento intelligente di Expose Armor del ladro per non sovrascrivere il debuff.
- Allerta rossa '0' in combattimento se nessun debuff di armatura è presente sul boss.

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

# 3. Esegui la suite di test parallela (8/8 PASS)
python tests/run_parallel_tests.py
```
