"""
Modulo Componente: 19 - Sunder Armor Tracker
============================================
Gestisce il monitoraggio del debuff Sunder Armor / Expose Armor sul bersaglio corrente:
- Posizione: xOffset = 169, yOffset = 45 (sul lato destro rispetto alla barra centrale).
- Traccia:
  * Conteggio cariche (da 1 a 5 cariche, stack count %s).
  * Conto alla rovescia di scadenza (%p o timer formattato).
  * Segnalazione intelligente:
    - Se presenti 5 cariche: stack count evidenziato in verde.
    - Se presente Expose Armor del Ladro: mostra icona con etichetta 'EA' per non sovrascrivere.
    - Se mancante su target nemico in combattimento: allerta rossa 'MISSING'.
"""
from builder.core.helpers import make_subtext


def build_sunder_auras() -> list[dict]:
    """
    Costruisce e restituisce l'aura del componente Sunder Armor Tracker:
    - 19 - Sunder Armor Tracker
    """
    sunder_events = "UNIT_AURA,PLAYER_TARGET_CHANGED,PLAYER_REGEN_DISABLED,PLAYER_REGEN_ENABLED,PLAYER_ENTERING_WORLD"

    return [
        {
            "id": "19 - Sunder Armor Tracker",
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
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "customTextUpdate": "update",
            "customText": """function()
    if not UnitExists("target") or UnitIsFriend("player", "target") or UnitIsDead("target") then return "" end
    local sunderCount = 0
    local isExpose = false
    local sunderRem = 0
    local now = GetTime()
    for i = 1, 40 do
        local name, _, _, count, _, dur, exp, _, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if spellId == 47467 or spellId == 7386 or spellId == 11597 or name == "Sunder Armor" or name == "Fendente d'Armatura" then
            sunderCount = (count and count > 0) and count or 1
            if exp and exp > 0 then sunderRem = exp - now end
            break
        elseif spellId == 8647 or spellId == 48669 or name == "Expose Armor" or name == "Armatura Esclusa" then
            isExpose = true
            if exp and exp > 0 then sunderRem = exp - now end
            break
        end
    end
    if isExpose then
        if sunderRem > 0 then
            return string.format("|cFF00FFFFEA %.0fs|r", sunderRem)
        else
            return "|cFF00FFFFEA|r"
        end
    elseif sunderCount > 0 then
        local color = (sunderCount >= 5) and "|cFF00FF00" or "|cFFFFFFFF"
        if sunderRem > 0 then
            return string.format("%sx%d %.0fs|r", color, sunderCount, sunderRem)
        else
            return string.format("%sx%d|r", color, sunderCount)
        end
    else
        local inCombat = UnitAffectingCombat("player")
        if inCombat then
            return "|cFFFF0000MISSING|r"
        end
        return ""
    end
end""",
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=0),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": sunder_events,
                        "custom": """function(event, ...)
    if not UnitExists("target") or UnitIsFriend("player", "target") or UnitIsDead("target") then
        return false
    end
    local inCombat = UnitAffectingCombat("player")
    local found = false
    for i = 1, 40 do
        local name, _, _, _, _, _, _, _, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if spellId == 47467 or spellId == 7386 or spellId == 11597 or name == "Sunder Armor" or name == "Fendente d'Armatura"
           or spellId == 8647 or spellId == 48669 or name == "Expose Armor" or name == "Armatura Esclusa" then
            found = true
            break
        end
    end
    if found or inCombat then
        return true
    end
    return false
end""",
                        "customDuration": """function()
    if not UnitExists("target") or UnitIsFriend("player", "target") or UnitIsDead("target") then return 0, 0 end
    for i = 1, 40 do
        local name, _, _, _, _, dur, exp, _, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if spellId == 47467 or spellId == 7386 or spellId == 11597 or name == "Sunder Armor" or name == "Fendente d'Armatura"
           or spellId == 8647 or spellId == 48669 or name == "Expose Armor" or name == "Armatura Esclusa" then
            if dur and dur > 0 and exp and exp > 0 then
                return dur, exp
            end
        end
    end
    return 0, 0
end""",
                        "customIcon": """function()
    if UnitExists("target") and not UnitIsFriend("player", "target") then
        for i = 1, 40 do
            local name, _, icon, _, _, _, _, _, _, _, spellId = UnitDebuff("target", i)
            if not name then break end
            if spellId == 8647 or spellId == 48669 or name == "Expose Armor" or name == "Armatura Esclusa" then
                return "Interface\\Icons\\Ability_Warrior_Riposte"
            elseif spellId == 47467 or spellId == 7386 or spellId == 11597 or name == "Sunder Armor" or name == "Fendente d'Armatura" then
                return icon or "Interface\\Icons\\Ability_Warrior_Sunder"
            end
        end
    end
    return "Interface\\Icons\\Ability_Warrior_Sunder"
end""",
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    if not UnitExists("target") or UnitIsFriend("player", "target") or UnitIsDead("target") then
        return true
    end
    local inCombat = UnitAffectingCombat("player")
    local found = false
    for i = 1, 40 do
        local name, _, _, _, _, _, _, _, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if spellId == 47467 or spellId == 7386 or spellId == 11597 or name == "Sunder Armor" or name == "Fendente d'Armatura"
           or spellId == 8647 or spellId == 48669 or name == "Expose Armor" or name == "Armatura Esclusa" then
            found = true
            break
        end
    end
    return not (found or inCombat)
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
        },
    ]
