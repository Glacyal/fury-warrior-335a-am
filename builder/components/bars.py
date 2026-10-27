"""
Modulo Componente: 14 - Rage Bar & 16 - Castbar
================================================
Gestisce le barre centrali sincronizzate a 278px di larghezza:
1. 14 - Rage Bar (278x14px a y = -20):
   - Barra della rabbia (powertype = 1) con texture statusbar.
   - Colore base: rosso sangue [0.78, 0.12, 0.12, 1.0].
   - Transizione cromatica dinamica ad ambra dorato [1.0, 0.65, 0.10, 1.0] a >= 45 Rage (soglia scarico sicuro Heroic Strike).
   - Allerta starvation a < 25 Rage: colore rosso scuro [0.45, 0.05, 0.05, 1.0].
   - Testo centrale: valore numerico rabbia (%p).
2. 16 - Castbar (278x20px a y = +8):
   - Barra di lancio per Slam non-proc (1.5s), Lancio armi a distanza o GCD.
   - Mostra icona a sinistra, nome incantesimo a sinistra (%n) e tempo residuo a destra (%p).
"""
from builder.core.helpers import make_subtext
from builder.core.constants import TEXTURE_STATUSBAR, COLOR_RAGE, COLOR_RAGE_DUMP, COLOR_RAGE_STARVED, COLOR_RAGE_BG, COLOR_CASTBAR, COLOR_CASTBAR_BG


def build_bars_auras() -> list[dict]:
    """
    Costruisce e restituisce le 2 barre principali dell'HUD:
    - 14 - Rage Bar (Aurabar)
    - 16 - Castbar (Aurabar)
    """
    return [
        # =====================================================================
        # 14 - RAGE BAR
        # =====================================================================
        {
            "id": "14 - Rage Bar",
            "uid": "FWHUD_RAGEBAR",
            "parent": "Class Warrior (Fury)",
            "regionType": "aurabar",
            "internalVersion": 52,
            "width": 278,
            "height": 14,
            "xOffset": 0,
            "yOffset": -20,
            "barColor": COLOR_RAGE,
            "backgroundColor": COLOR_RAGE_BG,
            "texture": TEXTURE_STATUSBAR,
            "displayText_format_1.percentpower_format": "Number",
            "displayText_format_1.percentpower_decimal_precision": 0,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "unit",
                        "event": "Power",
                        "unit": "player",
                        "powertype": 1,
                        "use_unit": True,
                        "use_powertype": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "conditions": [
                # Condizione 1: Rage >= 45 -> Colore ambra dorato (Rage Dump / Heroic Strike sicuro)
                {
                    "check": {
                        "trigger": 1,
                        "variable": "power",
                        "op": ">=",
                        "value": "45",
                    },
                    "changes": [
                        {
                            "property": "barColor",
                            "value": COLOR_RAGE_DUMP,
                        }
                    ],
                },
                # Condizione 2: Rage < 25 -> Colore scuro desaturato (Starvation)
                {
                    "check": {
                        "trigger": 1,
                        "variable": "power",
                        "op": "<",
                        "value": "25",
                    },
                    "changes": [
                        {
                            "property": "barColor",
                            "value": COLOR_RAGE_STARVED,
                        }
                    ],
                },
            ],
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="CENTER", font_size=12, y_offset=0),
            ],
        },

        # =====================================================================
        # 16 - CASTBAR
        # =====================================================================
        {
            "id": "16 - Castbar",
            "uid": "FWHUD_CASTBAR",
            "parent": "Class Warrior (Fury)",
            "regionType": "aurabar",
            "internalVersion": 52,
            "width": 278,
            "height": 20,
            "xOffset": 0,
            "yOffset": 8,
            "barColor": COLOR_CASTBAR,
            "backgroundColor": COLOR_CASTBAR_BG,
            "texture": TEXTURE_STATUSBAR,
            "icon": True,
            "icon_side": "LEFT",
            "iconSource": -1,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "unit",
                        "event": "Cast",
                        "unit": "player",
                        "use_unit": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                make_subtext("%n", justify="LEFT", anchor_point="INNER_LEFT", font_size=11, y_offset=0),
                make_subtext("%p", justify="RIGHT", anchor_point="INNER_RIGHT", font_size=11, y_offset=0),
            ],
        },
    ]
