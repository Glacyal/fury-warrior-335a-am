"""
Modulo Componente: 18 - Stats Panel (Warrior Fury)
===================================================
Gestisce il pannello delle statistiche in tempo reale (88x60px a x = -190, y = -45):
- Mostra 5 righe di statistiche dinamiche calcolate con throttling a 10 Hz (0.1s):
  1. Attack Power (AP base + posBuff + negBuff)
  2. Melee Crit (con GetCritChance() + debuff sul bersaglio Heart of the Crusader / Master Poisoner / Totem of Wrath +3%)
  3. Melee Haste (GetCombatRatingBonus(18) + moltiplicatori raid: Windfury Totem / Improved Icy Talons +20%,
     Swift Retribution / Improved Moonkin Form +3%, Bloodlust/Heroism +30%, Flurry +25%, Berserking Troll +20%)
  4. Armor Penetration (ArP rating e %, con evidenziazione verde al raggiungimento dell'Hard Cap di 1400)
  5. Melee Hit (soglia cap 8%, aura Draenei Heroic Presence +1%) ed Expertise (soft cap 26)

Compatibilità: WeakAuras 4.0.0 (internalVersion: 52).
"""
from builder.core.constants import TEXTURE_WHITE8X8, FONT_EXPRESSWAY


def make_stats_custom_text() -> str:
    """
    Funzione Lua personalizzata che calcola e formatta in tempo reale:
    Attack Power, Melee Crit, Melee Haste, Armor Penetration (con hard cap 1400) e Hit/Expertise.
    """
    return """function()
    local now = GetTime()
    if _G.FWHUD_LastStatsText and (now - (_G.FWHUD_LastStatsTime or 0)) < 0.1 then
        return _G.FWHUD_LastStatsText
    end

    -- 1. ATTACK POWER (Base + Positive Buffs + Negative Buffs)
    local base, posBuff, negBuff = UnitAttackPower("player")
    local ap = (base or 0) + (posBuff or 0) + (negBuff or 0)

    -- 2. MELEE CRIT (GetCritChance() + Debuff +3% sul target: Heart of the Crusader / Master Poisoner / Totem of Wrath)
    local crit = GetCritChance() or 0
    local targetCritBonus = 0
    if UnitExists("target") and not UnitIsDead("target") and UnitCanAttack("player", "target") then
        for i = 1, 40 do
            local name, _, _, _, _, _, _, _, _, _, spellId = UnitDebuff("target", i)
            if not name then break end
            if spellId == 21183 or spellId == 20337 or spellId == 20336 or spellId == 20335 or
               spellId == 58410 or spellId == 57724 or spellId == 57723 or
               spellId == 30706 or spellId == 30708 or
               name == "Heart of the Crusader" or name == "Cuore del Crociato" or
               name == "Master Poisoner" or name == "Maestro dei Veleni" or name == "Mastro Velenifero" or
               name == "Totem of Wrath" or name == "Totem dell'Ira" then
                targetCritBonus = 3.0
                break
            end
        end
    end
    crit = crit + targetCritBonus

    -- 3. MELEE HASTE (Rating + Buff, Totem, Lust, Flurry, Berserking Troll, Swift Retrib)
    -- In 3.3.5a: CR_HASTE_MELEE = 18 (25.2157 rating = 1%)
    local hasteRatingBonus = GetCombatRatingBonus(18) or 0
    local hasteMult = 1 + (hasteRatingBonus / 100)

    local hasLust = false
    local has20Haste = false
    local has3Haste = false
    local hasFlurry = false
    local hasTrollBerserk = false
    local hasHeroicPresence = false

    for i = 1, 40 do
        local name, _, _, count, _, _, _, _, _, _, spellId = UnitBuff("player", i)
        if not name then break end

        -- Bloodlust / Heroism (+30% Haste)
        if not hasLust and (spellId == 2825 or spellId == 32182 or name == "Bloodlust" or name == "Heroism" or name == "Bramosia Sanguinaria" or name == "Eroismo") then
            hasLust = true
            hasteMult = hasteMult * 1.30
        -- +20% Melee Haste: Windfury Totem (Shaman) o Improved Icy Talons (Frost DK) - Non stackano
        elseif not has20Haste and (spellId == 55610 or spellId == 8512 or spellId == 10613 or spellId == 10614 or spellId == 25587 or spellId == 58656
            or name == "Improved Icy Talons" or name == "Artigli Gelidi Migliorati"
            or name == "Windfury Totem" or name == "Totem del Furore del Vento"
            or string.find(name, "Windfury") or string.find(name, "Furore del Vento")) then
            has20Haste = true
            hasteMult = hasteMult * 1.20
        -- +3% Raid Haste: Swift Retribution (Paladino) vs Improved Moonkin Form (Druido) - Non stackano
        elseif not has3Haste and (spellId == 48396 or spellId == 53648 or spellId == 53379 or spellId == 24907 or spellId == 31583
            or name == "Swift Retribution" or name == "Ritorsione Rapida"
            or name == "Improved Moonkin Form" or name == "Forma di Lunagufo Migliorata") then
            has3Haste = true
            hasteMult = hasteMult * 1.03
        -- Flurry (+25% Attack Speed talento Fury Warrior)
        elseif not hasFlurry and (spellId == 16280 or spellId == 16279 or spellId == 16278 or spellId == 16277 or spellId == 16256
            or name == "Flurry" or name == "Raffica") then
            hasFlurry = true
            hasteMult = hasteMult * 1.25
        -- Berserking Razziale Troll (+20% Haste - Spell ID 26297 per distinguere dall'incanto arma 59620)
        elseif not hasTrollBerserk and (spellId == 26297 or (name == "Berserking" and count == 0 and spellId ~= 59620)) then
            hasTrollBerserk = true
            hasteMult = hasteMult * 1.20
        end

        -- Heroic Presence (Draenei aura nel gruppo: +1% Hit a tutti gli attacchi fisici e magici)
        if not hasHeroicPresence and (spellId == 28878 or spellId == 6562 or name == "Heroic Presence" or name == "Presenza Eroica") then
            hasHeroicPresence = true
        end
    end

    local hastePct = (hasteMult - 1) * 100

    -- 4. ARMOR PENETRATION (Combat Rating 25 in 3.3.5a: 13.996 rating = 1%, Hard Cap = 1400)
    local arpRating = GetCombatRating(25) or 0
    local arpBonus = GetCombatRatingBonus(25) or 0
    local arpPct = arpBonus > 0 and arpBonus or (arpRating / 13.996)
    if GetShapeshiftForm and GetShapeshiftForm() == 1 then
        arpPct = arpPct + 10.0 -- Battle Stance passive +10% ArP se non in Berserker Stance
    end
    local arpStr
    if arpRating >= 1400 or arpPct >= 100 then
        arpStr = "|cFF22C55E100% (CAP)|r"
    else
        arpStr = string.format("%.1f%% (%d)", arpPct, arpRating)
    end

    -- 5. HIT & EXPERTISE (Melee Hit: CR 6, 32.79 rating = 1%, Special Cap = 8%; Draenei aura +1%; Expertise: soft cap 26)
    local hitRating = GetCombatRating(6) or 0
    local hitBonus = GetCombatRatingBonus(6) or 0
    local hitPct = hitBonus > 0 and hitBonus or (hitRating / 32.79)
    local draeneiBonus = hasHeroicPresence and 1.0 or 0.0
    local totalHit = hitPct + draeneiBonus

    local expertise = GetExpertise and GetExpertise() or 0
    local hitColor = totalHit >= 8.0 and "|cFF22C55E" or "|cFFFFFFFF"
    local expColor = expertise >= 26 and "|cFF22C55E" or "|cFFFFFFFF"

    local hitExpStr = string.format("%s%.1f%%|r | %s%d Exp|r", hitColor, totalHit, expColor, expertise)

    local res = string.format(
        "|cFFFFFFFFAP:|r |cFFFFFF55%d|r\\n|cFFFFFFFFCrit:|r |cFFFF9933%.1f%%|r\\n|cFFFFFFFFHaste:|r |cFFCC44FF%.1f%%|r\\n|cFFFFFFFFArP:|r %s\\n|cFFFFFFFFHit:|r %s",
        ap, crit, hastePct, arpStr, hitExpStr
    )

    _G.FWHUD_LastStatsText = res
    _G.FWHUD_LastStatsTime = now
    return res
end"""


def build_stats_auras() -> list[dict]:
    """
    Costruisce e restituisce le 2 aure che compongono il pannello statistiche:
    - 18 - Stats Panel warDPS (Group)
    - Stats Panel - Background warDPS (Texture 88x60px)
    - Stats Panel - Text warDPS (Text a 5 righe dinamiche con aggiornamento continuo)
    """
    stats_events = "UNIT_AURA,UNIT_STATS,UNIT_ATTACK_POWER,COMBAT_RATING_UPDATE,PLAYER_DAMAGE_DONE_MODS,PLAYER_ENTERING_WORLD,UNIT_INVENTORY_CHANGED,PLAYER_EQUIPMENT_CHANGED,PLAYER_TARGET_CHANGED,RAID_ROSTER_UPDATE,PARTY_MEMBERS_CHANGED,CHARACTER_POINTS_CHANGED"

    return [
        {
            "id": "18 - Stats Panel warDPS",
            "uid": "FWHUD_STATS_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": -190,
            "yOffset": -45,
            "controlledChildren": [
                "Stats Panel - Background warDPS",
                "Stats Panel - Text warDPS",
            ],
        },
        # Background Frame (88x60px)
        {
            "id": "Stats Panel - Background warDPS",
            "uid": "FWHUD_STATS_BG",
            "parent": "18 - Stats Panel warDPS",
            "regionType": "texture",
            "internalVersion": 52,
            "width": 88,
            "height": 60,
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
        # Testo Dinamico a 5 Righe (Aggiornamento reattivo %c)
        {
            "id": "Stats Panel - Text warDPS",
            "uid": "FWHUD_STATS_TEXT",
            "parent": "18 - Stats Panel warDPS",
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
