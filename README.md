# Class Warrior (Fury) — WeakAuras Suite

[![WoW Version](https://img.shields.io/badge/World%20of%20Warcraft-3.3.5a%20(12340)-orange.svg)](https://github.com/Glacyal/fury-warrior-335a-am)
[![WeakAuras](https://img.shields.io/badge/WeakAuras-4.0.0-blue.svg)](https://github.com/Glacyal/fury-warrior-335a-am)
[![Class](https://img.shields.io/badge/Class-Warrior%20(Fury%20TG)-red.svg)](https://github.com/Glacyal/fury-warrior-335a-am)
[![GitHub Pages](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen.svg)](https://glacyal.github.io/fury-warrior-335a-am/)
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-gray.svg?logo=paypal&logoColor=white&labelColor=0079c1)](https://www.paypal.me/AMantmar)

Suite WeakAuras completa, modulare e ad altissime prestazioni per **Warrior Fury (Titan's Grip) Livello 80** in World of Warcraft 3.3.5a (*Wrath of the Lich King - Build 12340*).  
Progettata per garantire la massima efficacia in combattimento, un consumo CPU trascurabile (&lt; 0.1% in raid 25), un monitoraggio millisecondo-preciso di **Heroic Strike Queueing**, **Swing Timer Dual-Wield**, proc di **Bloodsurge** e una visuale perfettamente pulita (*Zero Clutter*).

---

## 🌐 Anteprima Online (Live Simulator)

Visualizza e interagisci con l'HUD direttamente dal browser senza installare nulla:  
👉 **[Apri il Simulatore Web su GitHub Pages](https://glacyal.github.io/fury-warrior-335a-am/)**  

---

## 🌟 Caratteristiche Principali

Tutti i componenti del pacchetto sono organizzati con una numerazione sequenziale rigorosa da **01** a **19**:

### 1. Barra Rotazionale & Dual Swing Timer (`15 - Rotational Bar`)
Posizionata visivamente a centro schermo subito sopra la barra della rabbia (278x7px):
- **Doppio Swing Timer Speculare**:
  - **Mezza Barra Sinistra (MH)**: Avanzamento dello swing per la Mano Primaria.
  - **Mezza Barra Destra (OH)**: Avanzamento dello swing per la Mano Secondaria.
- **Rilevamento Heroic Strike / Cleave Queued**:
  - Non appena Heroic Strike o Cleave viene accodato, l'intera barra si illumina istantaneamente con un **Pixel Glow dorato** e compare la dicitura centrale `[HS QUEUED]`.
  - Fornisce la certezza visiva che il colpo successivo eliminerà i glancing blow sulla mano primaria e applicherà all'arma secondaria il cap di hit speciale (8%) invece della penalità 27% del dual wield!

### 2. Barra della Rabbia Dinamica (`14 - Rage Bar`)
Barra orizzontale di precisione (278x14px a y = -20) con lettura numerica (%p) e cambio cromatico a 3 stadi:
- **&lt; 25 Rage**: Rosso scuro attenuato (allerta starvation).
- **25 - 44 Rage**: Rosso sangue pieno (capacità di lanciare Bloodthirst/Whirlwind).
- **&gt;= 45 Rage**: Transizione istantanea ad **Ambra/Oro** per indicare il via libera allo scarico sicuro con Heroic Strike/Cleave!

### 3. Gruppo Dinamico Procs (`01 - Procs`)
Barra orizzontale superiore (y = 52) con riposizionamento automatico:
1. **Victory Rush**: Proc *Victorious* (Spell 34428 / Buff 32216) con conto alla rovescia di 20 secondi e pixel glow verde.
2. **Bloodsurge**: Slam istantaneo con pixel glow dorato e conto alla rovescia di 5 secondi.
3. **Tier 10 4P (Siegebreaker)**: Tracciamento delle 2 cariche di Slam e -1s su Bloodthirst.
4. **Tier 10 2P**: +16% Attack Power per 10s da tick di Deep Wounds.
5. **Flurry**: +25% attack speed (3 cariche) dopo un critico in mischia.
6. **Wrecking Crew / Enrage**: +10% danno fisico per 12s da critico.
7. **Deathbringer's Will (DBW)**: Monitoraggio dei proc Taunka (+1200 AP), Vrykul (+9.6% Crit), Iron Dwarf (+42.8% ArP).
8. **Berserking**: Proc +400 AP da incanto armi.
9. **Execute Usable**: Icona attiva con bordo luminoso quando il boss scende sotto il 20% di salute.

### 4. Zero Clutter & Intelligenza Overlap di Raid
- **02 - Battle Shout**: Nascosto in combattimento se attivo con più di 30 secondi; mostra il timer in scadenza e allerta se assente. **Filtro Overlap**: Viene soppresso automaticamente se è attivo *Blessing of Might* o *Greater Blessing of Might* del Paladino (buff equivalente/superiore).
- **03 - Commanding Shout**: Diventa la shout di riferimento se Battle Shout è coperto dal Paladino. Viene soppresso automaticamente se è attivo il buff *Blood Pact* dell'Imp del Warlock.
- **04 - Berserker Stance**: Allerta immediata ad alta visibilità se durante il combattimento il guerriero si trova fuori dalla Berserker Stance.
- *(Nota su Rampage)*: Rimosso dall'HUD per eliminare il disordine visivo, essendo in 3.3.5a un'aura passiva permanente al critico fisico.

### 5. Riga Utility Adattiva (`05` - `13`, da 3 a 9 Icone)
La fila inferiore a y = -45 si adatta e si ricentra automaticamente:
- **05 - Trinket 1 & 06 - Trinket 2**: Rilevamento automatico slot 13 & 14, timer ICD e glow su proc attivo.
- **07 - Cloak**: Attivo con incanti da mischia (Swordguard Embroidery +400 AP o paracadute).
- **08 - Death Wish**: Durata attiva 30s (+20% danno) e cooldown.
- **09 - Gloves**: Acceleratori Ipersonici Ingegneria (+340 Haste per 12s).
- **10 - Recklessness**: Tracciamento delle 3 cariche di critico garantito e cooldown.
- **11 - Shattering Throw**: Debuff -20% armatura sul boss per 10s e cooldown (5 min).
- **12 - Enraged Regeneration**: Cura 30% HP in 10s e cooldown.
- **13 - Boots**: Stivali a nitro (Nitro Boosts) con stato pronto e ricarica.

### 6. Pannello Statistiche in Tempo Reale (`18 - Stats Panel`)
Pannello compatto (88x48px a x = -190, y = -45) con aggiornamento throttled a 10 Hz:
- **AP**: Attack power totale con buff e moltiplicatori.
- **Crit**: Critico in mischia con debuff Heart of the Crusader / Master Poisoner (+3%) sul bersaglio.
- **ArP**: Percentuale e rating, con dicitura **CAP in verde** al raggiungimento del cap di 1400.
- **Hit & Exp**: Verifica visiva istantanea del cap 8% Special Hit e soft cap 26 Expertise.

### 7. Sunder Armor Tracker (`19 - Sunder Armor Tracker`)
Colonna destra (x = 169, y = 45):
- Traccia da 1 a 5 cariche sul bersaglio corrente con countdown di durata.
- Colore verde al raggiungimento delle 5 cariche massime.
- Riconoscimento intelligente di Expose Armor del ladro per non sovrascrivere il debuff.
- Allerta rossa '0' in combattimento se nessun debuff di armatura è presente sul boss.

---

## 📥 Come Importare in Gioco

1. Apri il file [`IMPORT_STRING.txt`](IMPORT_STRING.txt) o premi **"Copia Stringa !WA:1!"** nel simulatore web.
2. In World of Warcraft, apri WeakAuras digitando `/wa` in chat.
3. Clicca su **Importa** (Import) in alto a sinistra.
4. Premi `Ctrl + V` per incollare la stringa e premi **Importa Gruppo** (Import Group).

---

## 🛠️ Architettura e Sviluppo

Il repository include l'intero compilatore Python e la suite di test:

```powershell
# 1. Compila l'albero WeakAuras e genera IMPORT_STRING.txt
python generate.py

# 2. Sincronizza la stringa compilata nel simulatore web
python scripts/sync_docs.py

# 3. Esegui la suite di test paralleli ad alte prestazioni
python tests/run_parallel_tests.py
```

