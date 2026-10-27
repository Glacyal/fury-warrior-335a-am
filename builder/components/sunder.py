"""
Modulo Componente: 19 - Sunder Armor Tracker
============================================
Gestisce il monitoraggio del debuff Sunder Armor / Expose Armor sul bersaglio corrente:
- Posizione: xOffset = 169, yOffset = 45 (sul lato destro rispetto alla barra centrale).
- Traccia:
  * Conteggio cariche (da 1 a 5 cariche, stack count %s).
  * Conto alla rovescia di scadenza (%p).
  * Segnalazione intelligente:
    - Se presenti 5 cariche: stack count evidenziato in verde.
    - Se presente Expose Armor del Ladro: mostra icona con etichetta 'EXPOSE' per non sovrascrivere.
    - Se mancante su target nemico in combattimento: allerta rossa 'SUNDER MISSING'.
"""
from builder.core.helpers import make_subtext


def build_sunder_auras() -> list[dict]:
    """
    Costruisce e restituisce l'aura del componente Sunder Armor Tracker:
    - 21 - Sunder Armor Tracker
    """
    return [
        {
            "id": "21 - Sunder Armor Tracker",
            "uid": "FWHUD_SUNDER_TRACKER",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 32,
            "height": 32,
            "xOffset": 169,
            "yOffset": 45,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_Sunder",
            "auto": False,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "subRegions": [
                make_subtext("%s", justify="RIGHT", anchor_point="INNER_TOPRIGHT", font_size=13, y_offset=-1),
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=0),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "stateupdate",
                        "check": "event",
                        "events": "UNIT_AURA:target PLAYER_TARGET_CHANGED PLAYER_REGEN_DISABLED PLAYER_REGEN_ENABLED",
                        "custom": """function(allstates, event, ...)
                            if not UnitExists("target") or UnitIsFriend("player", "target") or UnitIsDead("target") then
                                allstates[""] = { show = false, changed = true }
                                return true
                            end

                            local now = GetTime()
                            local sunderCount = 0
                            local sunderExp = 0
                            local sunderDur = 30
                            local isExpose = false

                            for i = 1, 40 do
                                local name, _, icon, count, _, dur, exp, _, _, _, spellId = UnitDebuff("target", i)
                                if not name then break end

                                if spellId == 47467 or spellId == 7386 or spellId == 11597 or name == "Sunder Armor" or name == "Fendente d'Armatura" then
                                    sunderCount = (count and count > 0) and count or 1
                                    sunderDur = (dur and dur > 0) and dur or 30
                                    sunderExp = (exp and exp > 0) and exp or (now + sunderDur)
                                    break
                                elseif spellId == 8647 or spellId == 48669 or name == "Expose Armor" or name == "Armatura Esclusa" then
                                    isExpose = true
                                    sunderDur = (dur and dur > 0) and dur or 30
                                    sunderExp = (exp and exp > 0) and exp or (now + sunderDur)
                                    break
                                end
                            end

                            if isExpose then
                                allstates[""] = {
                                    show = true,
                                    changed = true,
                                    progressType = "timed",
                                    duration = sunderDur,
                                    expirationTime = sunderExp,
                                    icon = "Interface\\\\Icons\\\\Ability_Warrior_Riposte",
                                    stacks = "EA",
                                }
                            elseif sunderCount > 0 then
                                allstates[""] = {
                                    show = true,
                                    changed = true,
                                    progressType = "timed",
                                    duration = sunderDur,
                                    expirationTime = sunderExp,
                                    icon = "Interface\\\\Icons\\\\Ability_Warrior_Sunder",
                                    stacks = sunderCount,
                                }
                            else
                                local inCombat = UnitAffectingCombat("player")
                                if inCombat then
                                    allstates[""] = {
                                        show = true,
                                        changed = true,
                                        progressType = "static",
                                        icon = "Interface\\\\Icons\\\\Ability_Warrior_Sunder",
                                        stacks = "0",
                                        color = { 1, 0.2, 0.2, 0.9 },
                                    }
                                else
                                    allstates[""] = { show = false, changed = true }
                                end
                            end
                            return true
                        end""",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
    ]

