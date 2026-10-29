"""
Modulo Componente: 19 - Sunder Armor Tracker
============================================
Gestisce il monitoraggio del debuff Sunder Armor / Expose Armor sul bersaglio corrente:
- Posizione: xOffset = 160, yOffset = -7 (sul lato destro rispetto alla barra centrale).
- Traccia:
  * Conteggio cariche (da 1 a 5 cariche, stack count %s).
  * Conto alla rovescia di scadenza (%p o timer formattato).
  * Segnalazione intelligente:
    - Se presenti 5 cariche: stack count centrato 'x5' in verde.
    - Se presente Expose Armor del Ladro: etichetta centrata 'EA' in ciano per non sovrascrivere.
    - Se mancante su target nemico: solo allerta rossa 'OFF' posizionata alla base del riquadro.
    - Timer di scadenza numerico (es. 27s) centrato alla base (%c1), cariche (x1-x5 / EA) centrate (%c2).
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
            "xOffset": 160,
            "yOffset": -7,
            "displayIcon": "Interface\\Icons\\ability_warrior_sunder",
            "auto": False,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "customTextUpdate": "update",
            "customText": """function()
    if not UnitExists("target") or UnitIsFriend("player", "target") or UnitIsDead("target") then
        return "", ""
    end
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

    local timerText = ""
    local centerText = ""

    if isExpose then
        centerText = "|cFF00FFFFEA|r"
        if sunderRem > 0.1 then
            timerText = string.format("%.0fs", sunderRem)
        end
    elseif sunderCount > 0 then
        local stackColor = (sunderCount >= 5) and "|cFF00FF00" or "|cFFFFFFFF"
        centerText = string.format("%sx%d|r", stackColor, sunderCount)
        if sunderRem > 0.1 then
            timerText = string.format("%.0fs", sunderRem)
        end
    else
        -- Solo 'OFF' in rosso alla base quando manca Sunder Armor (nessuna scritta al centro)
        timerText = "|cFFFF0000OFF|r"
        centerText = ""
    end

    return timerText, centerText
end""",
            "subRegions": [
                {"type": "subbackground"},
                # 1. Timer / Status alla base (%c1): timer esatto (es. 27s) o 'OFF' in rosso quando mancante
                make_subtext("%c1", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=0),
                # 2. Cariche al centro (%c2): cariche centrate (x1, x2, x3, x4, x5 o EA)
                make_subtext("%c2", justify="CENTER", anchor_point="INNER_TOP", font_size=12, y_offset=-1),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
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
                        "customStacks": """function()
    if not UnitExists("target") or UnitIsFriend("player", "target") or UnitIsDead("target") then return 0 end
    for i = 1, 40 do
        local name, _, _, count, _, _, _, _, _, _, spellId = UnitDebuff("target", i)
        if not name then break end
        if spellId == 47467 or spellId == 7386 or spellId == 11597 or name == "Sunder Armor" or name == "Fendente d'Armatura" then
            return (count and count > 0) and count or 1
        end
    end
    return 0
end""",
                        "customIcon": """function()
    if UnitExists("target") and not UnitIsFriend("player", "target") then
        for i = 1, 40 do
            local name, _, icon, _, _, _, _, _, _, _, spellId = UnitDebuff("target", i)
            if not name then break end
            if spellId == 8647 or spellId == 48669 or name == "Expose Armor" or name == "Armatura Esclusa" then
                return icon or (GetSpellInfo and select(3, GetSpellInfo(8647))) or "Interface\\Icons\\Ability_Warrior_Riposte"
            elseif spellId == 47467 or spellId == 7386 or spellId == 11597 or name == "Sunder Armor" or name == "Fendente d'Armatura" then
                return icon or (GetSpellInfo and select(3, GetSpellInfo(7386))) or "Interface\\Icons\\ability_warrior_sunder"
            end
        end
    end
    return (GetSpellInfo and select(3, GetSpellInfo(7386))) or (GetSpellInfo and select(3, GetSpellInfo(47467))) or "Interface\\Icons\\ability_warrior_sunder"
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
