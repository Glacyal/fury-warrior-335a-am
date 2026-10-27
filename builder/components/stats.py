"""
Modulo Componente: 18 - Stats Panel (Warrior Fury)
===================================================
Gestisce il pannello delle statistiche in tempo reale (88x48px a x = -190, y = -45):
- Mostra 4 righe di statistiche dinamiche calcolate con throttling a 10 Hz (0.1s):
  1. Attack Power (AP base + posBuff + negBuff)
  2. Melee Crit (con GetCritChance() + debuff sul bersaglio Heart of the Crusader / Master Poisoner / Totem of Wrath +3%)
  3. Armor Penetration (ArP rating e %, con evidenziazione verde al raggiungimento dell'Hard Cap di 1400)
  4. Melee Hit (soglia cap 8%) ed Expertise (soft cap 26)

Compatibilità: WeakAuras 4.0.0 (internalVersion: 52).
"""
from builder.core.constants import TEXTURE_WHITE8X8, FONT_EXPRESSWAY


def make_stats_custom_text() -> str:
    """
    Funzione Lua personalizzata che calcola e formatta in tempo reale:
    Attack Power, Melee Crit, Armor Penetration (con hard cap 1400) e Hit/Expertise.
    """
    return """function()
    local now = GetTime()
    if _G.FWHUD_LastStatsText and (now - (_G.FWHUD_LastStatsTime or 0)) < 0.1 then
        return _G.FWHUD_LastStatsText
    end

    -- 1. ATTACK POWER
    local base, posBuff, negBuff = UnitAttackPower("player")
    local ap = (base or 0) + (posBuff or 0) + (negBuff or 0)

    -- 2. MELEE CRIT (con controllo debuff +3% sul target: Heart of the Crusader / Master Poisoner / Totem of Wrath)
    local crit = GetCritChance() or 0
    local hasCritDebuff = false
    if UnitExists("target") and not UnitIsFriend("player", "target") then
        for i = 1, 40 do
            local name, _, _, _, _, _, _, _, _, _, spellId = UnitDebuff("target", i)
            if not name then break end
            if spellId == 21183 or spellId == 58410 or spellId == 57723 or spellId == 30706 or
               name == "Heart of the Crusader" or name == "Master Poisoner" or name == "Totem of Wrath" or
               name == "Cuore del Crociato" or name == "Maestro dei Veleni" then
                hasCritDebuff = true
                break
            end
        end
    end
    if hasCritDebuff then crit = crit + 3.0 end

    -- 3. ARMOR PENETRATION (Combat Rating 25 in 3.3.5a: 13.996 rating = 1%, Hard Cap = 1400)
    local arpRating = GetCombatRating(25) or 0
    local arpBonus = GetCombatRatingBonus(25) or 0
    local arpPct = arpBonus > 0 and arpBonus or (arpRating / 13.996)
    local arpStr
    if arpRating >= 1400 or arpPct >= 100 then
        arpStr = "|cFF22C55E100% (CAP)|r"
    else
        arpStr = string.format("%.1f%% (%d)", arpPct, arpRating)
    end

    -- 4. HIT & EXPERTISE (Melee Hit: CR 6, 32.79 rating = 1%, Special Cap = 8%; Expertise: soft cap 26)
    local hitRating = GetCombatRating(6) or 0
    local hitBonus = GetCombatRatingBonus(6) or 0
    local hitPct = hitBonus > 0 and hitBonus or (hitRating / 32.79)
    local expertise = GetExpertise and GetExpertise() or 0
    local hitColor = hitPct >= 8.0 and "|cFF22C55E" or "|cFFFFFFFF"
    local expColor = expertise >= 26 and "|cFF22C55E" or "|cFFFFFFFF"

    local hitExpStr = string.format("%s%.1f%%|r | %s%d Exp|r", hitColor, hitPct, expColor, expertise)

    local res = string.format(
        "|cFFFFFFFFAP:|r |cFFFFFF55%d|r\\n|cFFFFFFFFCrit:|r |cFFFF9933%.1f%%|r\\n|cFFFFFFFFArP:|r %s\\n|cFFFFFFFFHit:|r %s",
        ap, crit, arpStr, hitExpStr
    )

    _G.FWHUD_LastStatsText = res
    _G.FWHUD_LastStatsTime = now
    return res
end"""


def build_stats_auras() -> list[dict]:
    """
    Costruisce e restituisce le 2 aure che compongono il pannello statistiche:
    - 18 - Stats Panel (Group)
    - Stats Panel - Background (Texture 88x48px)
    - Stats Panel - Text (Text a 4 righe dinamiche con aggiornamento continuo)
    """
    stats_events = "UNIT_AURA,UNIT_STATS,UNIT_ATTACK_POWER,COMBAT_RATING_UPDATE,PLAYER_DAMAGE_DONE_MODS,PLAYER_ENTERING_WORLD,UNIT_INVENTORY_CHANGED,PLAYER_EQUIPMENT_CHANGED,PLAYER_TARGET_CHANGED,RAID_ROSTER_UPDATE,PARTY_MEMBERS_CHANGED,CHARACTER_POINTS_CHANGED"

    return [
        {
            "id": "20 - Stats Panel",
            "uid": "FWHUD_STATS_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": -190,
            "yOffset": -45,
            "controlledChildren": [
                "Stats Panel - Background",
                "Stats Panel - Text",
            ],
        },
        # Background Frame (88x48px)
        {
            "id": "Stats Panel - Background",
            "uid": "FWHUD_STATS_BG",
            "parent": "20 - Stats Panel",
            "regionType": "texture",
            "internalVersion": 52,
            "width": 88,
            "height": 48,
            "xOffset": 0,
            "yOffset": 0,
            "texture": TEXTURE_WHITE8X8,
            "color": [0.06, 0.04, 0.04, 0.85],
            "selfPoint": "CENTER",
            "anchorPoint": "CENTER",
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": "PLAYER_ENTERING_WORLD,PLAYER_ALIVE",
                        "custom": "function() return true end",
                    },
                    "untrigger": {
                        "custom": "function() return false end",
                    }
                },
                "activeTriggerMode": -10,
            },
        },
        # Testo Dinamico a 4 Righe (Aggiornamento reattivo %c)
        {
            "id": "Stats Panel - Text",
            "uid": "FWHUD_STATS_TEXT",
            "parent": "20 - Stats Panel",
            "regionType": "text",
            "internalVersion": 52,
            "fontSize": 9,
            "font": FONT_EXPRESSWAY,
            "outline": "OUTLINE",
            "justify": "LEFT",
            "color": [1, 1, 1, 1],
            "selfPoint": "CENTER",
            "anchorPoint": "CENTER",
            "xOffset": 2,
            "yOffset": 0,
            "displayText": "%c",
            "customTextUpdate": "update",
            "customText": make_stats_custom_text(),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": stats_events,
                        "custom": "function(event, ...) return true end",
                    },
                    "untrigger": {
                        "custom": "function(event, ...) return false end",
                    }
                },
                "activeTriggerMode": -10,
            },
        },
    ]
