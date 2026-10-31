"""
Costruttore dell'Albero Gerarchico Completo WeakAuras — Class Warrior (Fury)
=============================================================================
Assembla i moduli indipendenti sotto il gruppo master 'Class Warrior (Fury)',
applicando le condizioni di caricamento di classe e talento su tutti i nodi foglia.
"""
import copy
from builder.core.constants import FURY_WARRIOR_LOAD
from builder.components.utility import SHARED_WARRIOR_CORE_BOOTSTRAP_LUA
from builder.components import (
    build_procs_auras,
    build_buffs_auras,
    build_utility_auras,
    build_bars_auras,
    build_rotational_auras,
    build_alerts_auras,
    build_stats_auras,
    build_sunder_auras,
)


def build_wa_tree() -> dict:
    """
    Costruisce e restituisce l'albero gerarchico completo per WeakAuras 4.0.0 (internalVersion 52).
    Assembla modularmente gli 8 componenti:
    1. 01 - Procs (Dynamic Group con Bloodsurge, Victory Rush, Flurry, Wrecking Crew, Execute)
    2. 02 - Battle Shout, 03 - Commanding Shout, 04 - Berserker Stance
    3. 05-13 - Utility Row (Trinket 1, Trinket 2, Cloak, Tier Set, Enchants, Gloves, Death Wish, Recklessness, Boots)
    4. 14 - Rage Bar, 16 - Castbar
    5. 15 - Rotational Bar (Dual Swing Timer & Heroic Strike Queued)
    6. 17 - Alerts (Bloodsurge & Execute Phase)
    7. 18 - Stats Panel (AP, Crit, ArP con Cap, Hit/Exp)
    8. 19 - Sunder Armor Tracker (1-5 cariche su boss)
    """
    data = {
        "m": "d",
        "v": 2000,
        "w": "4.0.0",
        "d": {
            "id": "Class Warrior (Fury)",
            "uid": "FWHUD_ROOT",
            "regionType": "group",
            "internalVersion": 52,
            "scale": 1.2,
            "xOffset": 0,
            "yOffset": -190,
            "anchorPoint": "CENTER",
            "selfPoint": "CENTER",
            "groupIcon": "Interface\\Icons\\Ability_Warrior_InnerRage",
            "displayIcon": "Interface\\Icons\\Ability_Warrior_InnerRage",
            "icon": "Interface\\Icons\\Ability_Warrior_InnerRage",
            "controlledChildren": [
                "01 - Procs warDPS",
                "02 - Battle Shout",
                "03 - Commanding Shout",
                "04 - Berserker Stance",
                "05 - Trinket 1 warDPS",
                "06 - Trinket 2 warDPS",
                "06b - Ring warDPS",
                "07 - Cloak warDPS",
                "08 - Tier Set warDPS",
                "09 - Enchants warDPS",
                "10 - Gloves warDPS",
                "11 - Death Wish",
                "12 - Recklessness",
                "13 - Boots warDPS",
                "14 - Rage Bar",
                "15 - Rotational Bar",
                "16 - Castbar warDPS",
                "17 - Alerts warDPS",
                "18 - Stats Panel warDPS",
                "19 - Sunder Armor Tracker",
            ],
            "load": copy.deepcopy(FURY_WARRIOR_LOAD),
            "actions": {
                "init": {
                    "do_custom": True,
                    "custom": f"_G.FWHUD_InitCore = {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}\n_G.FWHUD_InitCore()",
                },
                "start": {},
                "finish": {},
            },
        },
        "c": [],
    }

    # Assemblaggio ordinato dei componenti
    data["c"].extend(build_procs_auras())
    data["c"].extend(build_buffs_auras())
    data["c"].extend(build_utility_auras())
    data["c"].extend(build_bars_auras())
    data["c"].extend(build_rotational_auras())
    data["c"].extend(build_alerts_auras())
    data["c"].extend(build_stats_auras())
    data["c"].extend(build_sunder_auras())

    # Applicazione uniforme delle condizioni di caricamento (Warrior + Rampage)
    for item in data["c"]:
        item["load"] = copy.deepcopy(FURY_WARRIOR_LOAD)

    return data
