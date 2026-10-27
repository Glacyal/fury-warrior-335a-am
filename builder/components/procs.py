"""
Modulo Componente: 01 - Procs (Dynamic Group)
=============================================
Gestisce la barra orizzontale dinamica superiore dei proc di combattimento (y = 52):
- Crescita orizzontale centrata (space = 6px, icone 34x34px).
- Include i seguenti proc e debuff attivi:
  1. Bloodsurge (Slam istantaneo con Pixel Glow e timer 5s)
  2. Victory Rush (Proc Victorious con countdown durata 20s e glow)
  3. Tier 10 4P (Siegebreaker: 2 cariche e -1s CD su Bloodthirst)
  4. Tier 10 2P (+16% Attack Power per 10s da Deep Wounds)
  5. Flurry (+25% Attack Speed per 3 colpi dopo un critico)
  6. Wrecking Crew / Enrage (+10% danno fisico per 12s)
  7. Deathbringer's Will (DBW: Taunka / Vrykul / Iron Dwarf)
  8. Berserking (+400 Attack Power da incanto arma)
  9. Execute Usable (Target <= 20% HP con bordo luminoso)
"""
from builder.core.helpers import make_subtext, make_glow_action


def build_procs_auras() -> list[dict]:
    """
    Costruisce e restituisce le 10 aure del gruppo dinamico Procs:
    - 01 - Procs (Dynamic Group)
    - Bloodsurge, Victory Rush, Tier 10 4P, Tier 10 2P, Flurry, Wrecking Crew, DBW, Berserking, Execute Usable.
    """
    return [
        {
            "id": "01 - Procs",
            "uid": "FWHUD_PROCS_DG",
            "parent": "Class Warrior (Fury)",
            "regionType": "dynamicgroup",
            "internalVersion": 52,
            "grow": "HORIZONTAL",
            "align": "CENTER",
            "space": 6,
            "xOffset": 0,
            "yOffset": 52,
            "controlledChildren": [
                "Bloodsurge",
                "Victory Rush",
                "Tier 10 4P",
                "Tier 10 2P",
                "Flurry",
                "Wrecking Crew",
                "Deathbringer's Will",
                "Berserking",
                "Execute Usable",
            ],
        },
        # 1. Bloodsurge (Buff 46916 - Slam istantaneo)
        {
            "id": "Bloodsurge",
            "uid": "FWHUD_PROC_BLOODSURGE",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_Bloodsurge",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "actions": {
                "start": make_glow_action(),
                "finish": {"do_glow": True, "glow_action": "hide"},
            },
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
                make_subtext("%s", justify="RIGHT", anchor_point="INNER_TOPRIGHT", font_size=10, y_offset=-2),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Bloodsurge", "46916"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 2. Victory Rush (Proc Victorious - 32216 / durata 20s)
        {
            "id": "Victory Rush",
            "uid": "FWHUD_PROC_VICTORY_RUSH",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_VictoryRush",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "actions": {
                "start": make_glow_action(),
                "finish": {"do_glow": True, "glow_action": "hide"},
            },
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Victorious", "Victory Rush", "32216", "34428"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 3. Tier 10 4P (Siegebreaker - 70846)
        {
            "id": "Tier 10 4P",
            "uid": "FWHUD_PROC_T10_4P",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_Siegebreaker",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Siegebreaker", "70846"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 4. Tier 10 2P (+16% Attack Power - 70845)
        {
            "id": "Tier 10 2P",
            "uid": "FWHUD_PROC_T10_2P",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_Riposte",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["70845", "Item - Warrior T10 Melee 2P Bonus"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 5. Flurry (+25% Attack Speed - 16280)
        {
            "id": "Flurry",
            "uid": "FWHUD_PROC_FLURRY",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_GhoulFrenzy",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
                make_subtext("%s", justify="RIGHT", anchor_point="INNER_TOPRIGHT", font_size=10, y_offset=-2),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Flurry", "16280", "16284"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 6. Wrecking Crew / Enrage (+10% danno - 57519 / 57516)
        {
            "id": "Wrecking Crew",
            "uid": "FWHUD_PROC_WRECKING_CREW",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_Trauma",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Enrage", "Wrecking Crew", "57519", "57516"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 7. Deathbringer's Will (DBW Proc: Taunka / Vrykul / Iron Dwarf)
        {
            "id": "Deathbringer's Will",
            "uid": "FWHUD_PROC_DBW",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\INV_Misc_Ornament_02",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": [
                            "Strength of the Taunka",
                            "Agility of the Vrykul",
                            "Speed of the Iron Dwarf",
                            "Aim of the Iron Dwarf",
                            "Power of the Taunka",
                            "71485", "71491", "71487", "71486", "71484"
                        ],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 8. Berserking (+400 Attack Power - 59620)
        {
            "id": "Berserking",
            "uid": "FWHUD_PROC_BERSERKING",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Spell_Nature_BloodLust",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
                make_subtext("%s", justify="RIGHT", anchor_point="INNER_TOPRIGHT", font_size=10, y_offset=-2),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Berserking", "59620"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 9. Execute Usable (Target <= 20% HP)
        {
            "id": "Execute Usable",
            "uid": "FWHUD_PROC_EXECUTE",
            "parent": "01 - Procs",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\INV_Sword_48",
            "auto": False,
            "color": [1, 0.2, 0.2, 1],
            "desaturate": False,
            "actions": {
                "start": make_glow_action(),
                "finish": {"do_glow": True, "glow_action": "hide"},
            },
            "subRegions": [
                make_subtext("EXEC", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11, y_offset=1),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "unit",
                        "event": "Health",
                        "unit": "target",
                        "percenthealth": "20",
                        "percenthealth_operator": "<=",
                        "use_percenthealth": True,
                        "use_unit": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
    ]
