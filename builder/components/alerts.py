"""
Modulo Componente: 17 - Alerts
==============================
Gestisce gli avvisi testuali contestuali centrali (a y = 105):
1. Alert - Bloodsurge: Scritta singola centrata quando il buff Bloodsurge è attivo
   (|cFFFFFF00SLAM READY!|r).
"""


def build_alerts_auras() -> list[dict]:
    """
    Costruisce e restituisce l'aura del gruppo Alerts:
    - 17 - Alerts warDPS (Group)
    - Alert - Bloodsurge (Text: SLAM READY!)
    """
    return [
        {
            "id": "17 - Alerts warDPS",
            "uid": "FWHUD_ALERTS_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": 105,
            "controlledChildren": [
                "Alert - Bloodsurge",
            ],
        },
        # 1. Alert - Bloodsurge (Solo SLAM READY!)
        {
            "id": "Alert - Bloodsurge",
            "uid": "FWHUD_ALERT_BLOODSURGE",
            "parent": "17 - Alerts warDPS",
            "regionType": "text",
            "internalVersion": 52,
            "displayText": "|cFFFFFF00SLAM READY!|r",
            "fontSize": 20,
            "outline": "OUTLINE",
            "justify": "CENTER",
            "color": [1, 1, 0, 1],
            "selfPoint": "CENTER",
            "anchorPoint": "CENTER",
            "xOffset": 0,
            "yOffset": 0,
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
    ]
