"""
Modulo Componente: 17 - Alerts
==============================
Gestisce gli avvisi testuali contestuali centrali (a y = 78, appena sopra Procs):
1. Alert - Bloodsurge: Scritta singola centrata quando il buff Bloodsurge è attivo
   (|cFFFFFF00SLAM READY!|r) accompagnata da notifica sonora (Doppio Fendente d'Aria).
"""


def build_alerts_auras() -> list[dict]:
    """
    Costruisce e restituisce l'aura del gruppo Alerts:
    - 17 - Alerts warDPS (Group)
    - Alert - Bloodsurge (Text: SLAM READY! con suono DoubleWhoosh)
    """
    return [
        {
            "id": "17 - Alerts warDPS",
            "uid": "FWHUD_ALERTS_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": 78,
            "controlledChildren": [
                "Alert - Bloodsurge",
            ],
        },
        # 1. Alert - Bloodsurge (Solo SLAM READY! con suono Doppio Fendente d'Aria)
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
            "actions": {
                "init": {"do_custom": False},
                "start": {
                    "do_sound": True,
                    "sound": "Interface\\AddOns\\WeakAuras\\Media\\Sounds\\DoubleWhoosh.ogg",
                    "sound_path": "Interface\\AddOns\\WeakAuras\\Media\\Sounds\\DoubleWhoosh.ogg",
                    "sound_channel": "Master",
                },
                "finish": {"do_sound": False},
            },
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Bloodsurge", "Ondata di Sangue", "46916"],
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
