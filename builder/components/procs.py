"""
Modulo Componente: 01 - Procs (Dynamic Group)
=============================================
Gestisce la barra orizzontale dinamica superiore dei proc di combattimento (y = 52):
- Crescita orizzontale centrata (space = 6px, icone 34x34px).
- Include rigorosamente i SOLI proc rotazionali di combattimento (Zero Clutter):
  1. Bloodsurge (Slam istantaneo con Pixel Glow e timer 5s)
  2. Victory Rush (Proc Victorious con countdown durata 20s e glow)
  3. Flurry (+25% Attack Speed per 3 colpi dopo un critico)
  4. Wrecking Crew / Enrage (+10% danno fisico per 12s)
  5. Execute Usable (Target <= 20% HP con bordo luminoso)
Tutti gli effetti di equipaggiamento (Tier Sets T7-T10, Incanti arma/anello, Monili)
sono gestiti nella riga inferiore Utility a y = -45, identicamente a fire-mage-335a-am.
"""
from builder.core.helpers import make_subtext, make_glow_action


def build_procs_auras() -> list[dict]:
    """
    Costruisce e restituisce le 6 aure del gruppo dinamico Procs:
    - 01 - Procs (Dynamic Group)
    - Bloodsurge, Victory Rush, Flurry, Wrecking Crew, Execute Usable.
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
                "Flurry",
                "Wrecking Crew",
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
        # 3. Flurry (+25% Attack Speed - 16280)
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
        # 4. Wrecking Crew / Enrage (+10% danno - 57519 / 57516)
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
        # 5. Execute Usable (Target <= 20% HP)
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
