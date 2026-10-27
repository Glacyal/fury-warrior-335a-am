"""
Modulo Componente: 17 - Alerts
==============================
Gestisce gli avvisi testuali contestuali centrali (a y = 105):
1. Alert - Bloodsurge: Scritta a due righe quando il buff Bloodsurge è attivo
   (|cFFFF2200BLOODSURGE!|r\\n|cFFFFFF00SLAM READY!|r).
2. Alert - Execute Phase: Avviso immediato quando il target scende sotto il 20% di salute
   (|cFFFF0000EXECUTE PHASE (< 20%)!|r).
"""


def build_alerts_auras() -> list[dict]:
    """
    Costruisce e restituisce le aure del gruppo Alerts:
    - 17 - Alerts (Group)
    - Alert - Bloodsurge (Text)
    - Alert - Execute Phase (Text)
    """
    return [
        {
            "id": "17 - Alerts",
            "uid": "FWHUD_ALERTS_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": 105,
            "controlledChildren": [
                "Alert - Bloodsurge",
                "Alert - Execute Phase",
            ],
        },
        # 1. Alert - Bloodsurge
        {
            "id": "Alert - Bloodsurge",
            "uid": "FWHUD_ALERT_BLOODSURGE",
            "parent": "17 - Alerts",
            "regionType": "text",
            "internalVersion": 52,
            "displayText": "|cFFFF2200BLOODSURGE!|r\\n|cFFFFFF00SLAM READY!|r",
            "fontSize": 20,
            "outline": "OUTLINE",
            "justify": "CENTER",
            "color": [1, 1, 1, 1],
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
        # 2. Alert - Execute Phase (< 20% HP)
        {
            "id": "Alert - Execute Phase",
            "uid": "FWHUD_ALERT_EXECUTE",
            "parent": "17 - Alerts",
            "regionType": "text",
            "internalVersion": 52,
            "displayText": "|cFFFF0000EXECUTE PHASE (< 20%)!|r",
            "fontSize": 18,
            "outline": "OUTLINE",
            "justify": "CENTER",
            "color": [1, 0.2, 0.2, 1],
            "selfPoint": "CENTER",
            "anchorPoint": "CENTER",
            "xOffset": 0,
            "yOffset": -28,
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

