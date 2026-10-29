"""
Modulo Componente: 02 - Battle Shout, 03 - Commanding Shout, 04 - Berserker Stance
===================================================================================
Gestisce i buff di classe e la stance con architettura identica a Fire Mage (x = -222, -190, -158 a y = 0):
1. 02 - Battle Shout:
   - Gruppo a x = -222, y = 0
   - Active: visibile SOLO quando il buff (Battle Shout o BoM/GBoM del Paladino) sta per scadere (<= 30s).
   - OFF: visibile (in combat e out of combat) quando manca SIA Battle Shout CHE BoM/GBoM (desaturato + 'OFF').
   - Nascosto: se attivo e sano (> 30s).
2. 03 - Commanding Shout:
   - Gruppo a x = -190, y = 0
   - Active: visibile SOLO quando il buff (Commanding Shout o Blood Pact dell'Imp) sta per scadere (<= 30s).
   - OFF: visibile (in combat e out of combat) quando manca SIA Commanding Shout CHE Blood Pact (desaturato + 'OFF').
   - Nascosto: se attivo e sano (> 30s).
3. 04 - Berserker Stance:
   - Gruppo a x = -158, y = 0
   - Allerta immediata se in combattimento il guerriero si trova fuori dalla Berserker Stance (Stance 3).
"""
from builder.core.helpers import make_subtext


# =============================================================================
# LOGICA LUA CONDIVISA: CACHE BUFF GUERRIERO & VERIFICA SOVRAPPOSIZIONI RAID
# =============================================================================
SHARED_WARRIOR_BUFFS_LUA = r"""function()
    local now_b = GetTime()
    local c = _G.FWHUD_BuffCache
    if c and c.time == now_b then
        return c
    end
    c = {
        time = now_b,
        bySpellId = {},
        byName = {},
        list = {},
        hasBoM = false,
        bomDuration = 0,
        bomExpiration = 0,
        bomIcon = nil,
        hasBloodPact = false,
        bpDuration = 0,
        bpExpiration = 0,
        bpIcon = nil,
        hasBattleShout = false,
        bsDuration = 0,
        bsExpiration = 0,
        bsIcon = nil,
        hasCommandingShout = false,
        csDuration = 0,
        csExpiration = 0,
        csIcon = nil,
    }

    local bsNameLocal = select(1, GetSpellInfo(47436))
    local csNameLocal = select(1, GetSpellInfo(47440))
    local bomNameLocal1 = select(1, GetSpellInfo(48934))
    local bomNameLocal2 = select(1, GetSpellInfo(19740))
    local bpNameLocal = select(1, GetSpellInfo(47982))

    for i = 1, 40 do
        local name, rank, icon, count, debuffType, duration, expirationTime, unitCaster, isStealable, shouldConsolidate, spellId = UnitBuff("player", i)
        if not name then break end
        local b = {
            name = name,
            rank = rank,
            icon = icon,
            count = count,
            debuffType = debuffType,
            duration = duration,
            expirationTime = expirationTime,
            unitCaster = unitCaster,
            isStealable = isStealable,
            shouldConsolidate = shouldConsolidate,
            spellId = spellId,
        }
        c.list[#c.list + 1] = b
        if spellId then c.bySpellId[spellId] = b end
        if name then c.byName[name] = b end

        -- Controllo Blessing of Might / Greater Blessing of Might (Paladino: non stacka con Battle Shout)
        if spellId == 48934 or spellId == 48932 or spellId == 25782 or spellId == 25916 or
           spellId == 27140 or spellId == 19740 or spellId == 19834 or spellId == 19835 or
           (bomNameLocal1 and name == bomNameLocal1) or (bomNameLocal2 and name == bomNameLocal2) or
           name == "Greater Blessing of Might" or name == "Blessing of Might" or
           name == "Benedizione della Potenza Superiore" or name == "Benedizione della Potenza" then
            c.hasBoM = true
            c.bomDuration = duration or 1800
            c.bomExpiration = (expirationTime and expirationTime > 0) and expirationTime or (now_b + 1800)
            c.bomIcon = icon or select(3, GetSpellInfo(48934)) or select(3, GetSpellInfo(19740))
        end

        -- Controllo Blood Pact (Warlock Imp: non stacka con Commanding Shout)
        if spellId == 47982 or spellId == 47981 or spellId == 27268 or spellId == 11767 or
           spellId == 11766 or spellId == 6307 or (bpNameLocal and name == bpNameLocal) or
           name == "Blood Pact" or name == "Patto di Sangue" then
            c.hasBloodPact = true
            c.bpDuration = duration or 1800
            c.bpExpiration = (expirationTime and expirationTime > 0) and expirationTime or (now_b + 1800)
            c.bpIcon = icon or select(3, GetSpellInfo(47982))
        end

        -- Controllo Battle Shout
        if spellId == 47436 or spellId == 25289 or spellId == 11551 or spellId == 11550 or
           spellId == 11549 or spellId == 6192 or spellId == 5242 or spellId == 2048 or spellId == 6673 or
           (bsNameLocal and name == bsNameLocal) or name == "Battle Shout" or name == "Urlo di Battaglia" then
            c.hasBattleShout = true
            c.bsDuration = duration or 120
            c.bsExpiration = (expirationTime and expirationTime > 0) and expirationTime or (now_b + 120)
            c.bsIcon = icon or select(3, GetSpellInfo(47436))
        end

        -- Controllo Commanding Shout (Rank 1: 469/45517, Rank 2: 47439, Rank 3: 47440)
        if spellId == 47440 or spellId == 47439 or spellId == 469 or spellId == 45517 or
           (csNameLocal and name == csNameLocal) or name == "Commanding Shout" or name == "Urlo di Comando" then
            c.hasCommandingShout = true
            c.csDuration = duration or 120
            c.csExpiration = (expirationTime and expirationTime > 0) and expirationTime or (now_b + 120)
            c.csIcon = icon or select(3, GetSpellInfo(47440))
        end
    end

    _G.FWHUD_BuffCache = c
    return c
end"""


def build_buffs_auras() -> list[dict]:
    """
    Costruisce e restituisce le 6 aure (3 gruppi con figli Active e OFF) relative ai buff passivi e alla stance:
    - 02 - Battle Shout (Active + OFF)
    - 03 - Commanding Shout (Active + OFF)
    - 04 - Berserker Stance (OutOfStance)
    """
    buff_events = "UNIT_AURA,PLAYER_REGEN_DISABLED,PLAYER_REGEN_ENABLED,PLAYER_ENTERING_WORLD"

    return [
        # =====================================================================
        # 02 - BATTLE SHOUT (Gruppo Madre a x = -222, y = 0)
        # =====================================================================
        {
            "id": "02 - Battle Shout",
            "uid": "FWHUD_BS_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": -222,
            "yOffset": 0,
            "controlledChildren": [
                "02 - Battle Shout - Active",
                "02 - Battle Shout - OFF",
            ],
        },
        # 02 - Active (mostra timer solo se il buff o BoM è attivo ma con <= 30 secondi)
        {
            "id": "02 - Battle Shout - Active",
            "uid": "FWHUD_BS_ACTIVE",
            "parent": "02 - Battle Shout",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": 0,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_BattleShout",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "customTextUpdate": "update",
            "customText": """function()
    _G.FWHUD_BuffCache_Func = _G.FWHUD_BuffCache_Func or """ + SHARED_WARRIOR_BUFFS_LUA + """
    local c = _G.FWHUD_BuffCache_Func()
    local exp = (c and c.hasBattleShout and c.bsExpiration) or (c and c.hasBoM and c.bomExpiration) or 0
    if exp > 0 then
        local rem = exp - GetTime()
        if rem > 60 then
            return string.format("|cFFFFFF00%d:%02d|r", math.floor(rem / 60), math.floor(rem % 60))
        elseif rem > 0 then
            return string.format("|cFFFF4444%.0fs|r", rem)
        end
    end
    return ""
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
                        "check": "update",
                        "events": buff_events,
                        "custom": """function()
    _G.FWHUD_BuffCache_Func = _G.FWHUD_BuffCache_Func or """ + SHARED_WARRIOR_BUFFS_LUA + """
    local c = _G.FWHUD_BuffCache_Func()
    local now = GetTime()
    local exp = (c and c.hasBattleShout and c.bsExpiration) or (c and c.hasBoM and c.bomExpiration) or 0
    if exp > 0 then
        local rem = exp - now
        return rem > 0 and rem <= 30
    end
    return false
end""",
                        "customDuration": """function()
    _G.FWHUD_BuffCache_Func = _G.FWHUD_BuffCache_Func or """ + SHARED_WARRIOR_BUFFS_LUA + """
    local c = _G.FWHUD_BuffCache_Func()
    if c and c.hasBattleShout and c.bsExpiration and c.bsExpiration > 0 then
        return c.bsDuration or 120, c.bsExpiration
    elseif c and c.hasBoM and c.bomExpiration and c.bomExpiration > 0 then
        return c.bomDuration or 1800, c.bomExpiration
    end
    return 0, 0
end""",
                        "customIcon": """function()
    _G.FWHUD_BuffCache_Func = _G.FWHUD_BuffCache_Func or """ + SHARED_WARRIOR_BUFFS_LUA + """
    local c = _G.FWHUD_BuffCache_Func()
    if c and c.hasBoM and not c.hasBattleShout then
        return c.bomIcon or select(3, GetSpellInfo(48934)) or select(3, GetSpellInfo(19740)) or "Interface\\Icons\\Spell_Holy_GreaterBlessingofKings"
    end
    return c.bsIcon or select(3, GetSpellInfo(47436)) or "Interface\\Icons\\Ability_Warrior_BattleShout"
end""",
                    },
                    "untrigger": {},
                },
                "activeTriggerMode": -10,
            },
        },
        # 02 - OFF (Visibile SIA in combat CHE out of combat quando manca sia Battle Shout che BoM/GBoM)
        {
            "id": "02 - Battle Shout - OFF",
            "uid": "FWHUD_BS_OFF",
            "parent": "02 - Battle Shout",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": 0,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_BattleShout",
            "auto": False,
            "desaturate": True,
            "color": [0.6, 0.6, 0.6, 0.8],
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("|cFFFF4444OFF|r", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=1),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": buff_events,
                        "custom": """function()
    _G.FWHUD_BuffCache_Func = _G.FWHUD_BuffCache_Func or """ + SHARED_WARRIOR_BUFFS_LUA + """
    local c = _G.FWHUD_BuffCache_Func()
    if (c and c.hasBoM) or (c and c.hasBattleShout) then return false end
    return true
end""",
                    },
                    "untrigger": {},
                },
                "activeTriggerMode": -10,
            },
        },

        # =====================================================================
        # 03 - COMMANDING SHOUT (Gruppo Madre a x = -190, y = 0)
        # =====================================================================
        {
            "id": "03 - Commanding Shout",
            "uid": "FWHUD_CS_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": -190,
            "yOffset": 0,
            "controlledChildren": [
                "03 - Commanding Shout - Active",
                "03 - Commanding Shout - OFF",
            ],
        },
        # 03 - Active (mostra timer solo se il buff o Blood Pact è attivo ma con <= 30 secondi)
        {
            "id": "03 - Commanding Shout - Active",
            "uid": "FWHUD_CS_ACTIVE",
            "parent": "03 - Commanding Shout",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": 0,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_CommandingShout",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "customTextUpdate": "update",
            "customText": """function()
    _G.FWHUD_BuffCache_Func = _G.FWHUD_BuffCache_Func or """ + SHARED_WARRIOR_BUFFS_LUA + """
    local c = _G.FWHUD_BuffCache_Func()
    local exp = (c and c.hasCommandingShout and c.csExpiration) or 0
    if exp > 0 then
        local rem = exp - GetTime()
        if rem > 60 then
            return string.format("|cFFFFFF00%d:%02d|r", math.floor(rem / 60), math.floor(rem % 60))
        elseif rem > 0 then
            return string.format("|cFFFF4444%.0fs|r", rem)
        end
    end
    return ""
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
                        "check": "update",
                        "events": buff_events,
                        "custom": """function()
    _G.FWHUD_BuffCache_Func = _G.FWHUD_BuffCache_Func or """ + SHARED_WARRIOR_BUFFS_LUA + """
    local c = _G.FWHUD_BuffCache_Func()
    local now = GetTime()
    local exp = (c and c.hasCommandingShout and c.csExpiration) or 0
    if exp > 0 then
        local rem = exp - now
        return rem > 0 and rem <= 30
    end
    return false
end""",
                        "customDuration": """function()
    _G.FWHUD_BuffCache_Func = _G.FWHUD_BuffCache_Func or """ + SHARED_WARRIOR_BUFFS_LUA + """
    local c = _G.FWHUD_BuffCache_Func()
    if c and c.hasCommandingShout and c.csExpiration and c.csExpiration > 0 then
        return c.csDuration or 120, c.csExpiration
    end
    return 0, 0
end""",
                        "customIcon": """function()
    _G.FWHUD_BuffCache_Func = _G.FWHUD_BuffCache_Func or """ + SHARED_WARRIOR_BUFFS_LUA + """
    local c = _G.FWHUD_BuffCache_Func()
    if c and c.hasBloodPact and not c.hasCommandingShout then
        return c.bpIcon or select(3, GetSpellInfo(47982)) or "Interface\\Icons\\Spell_Shadow_BloodBoil"
    end
    return c.csIcon or select(3, GetSpellInfo(47440)) or "Interface\\Icons\\Ability_Warrior_CommandingShout"
end""",
                    },
                    "untrigger": {},
                },
                "activeTriggerMode": -10,
            },
        },
        # 03 - OFF (Visibile SIA in combat CHE out of combat quando manca sia Commanding Shout che Blood Pact)
        {
            "id": "03 - Commanding Shout - OFF",
            "uid": "FWHUD_CS_OFF",
            "parent": "03 - Commanding Shout",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": 0,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_CommandingShout",
            "auto": False,
            "desaturate": True,
            "color": [0.6, 0.6, 0.6, 0.8],
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("|cFFFF4444OFF|r", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=1),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": buff_events,
                        "custom": """function()
    _G.FWHUD_BuffCache_Func = _G.FWHUD_BuffCache_Func or """ + SHARED_WARRIOR_BUFFS_LUA + """
    local c = _G.FWHUD_BuffCache_Func()
    if (c and c.hasCommandingShout) or (c and c.hasBloodPact) then return false end
    return true
end""",
                    },
                    "untrigger": {},
                },
                "activeTriggerMode": -10,
            },
        },

        # =====================================================================
        # 04 - BERSERKER STANCE (Gruppo Madre a x = -158, y = 0)
        # =====================================================================
        {
            "id": "04 - Berserker Stance",
            "uid": "FWHUD_STANCE_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": -158,
            "yOffset": 0,
            "controlledChildren": [
                "04 - Berserker Stance - OutOfStance",
            ],
        },
        {
            "id": "04 - Berserker Stance - OutOfStance",
            "uid": "FWHUD_STANCE_WARNING",
            "parent": "04 - Berserker Stance",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Ability_Racial_Avatar",
            "auto": False,
            "color": [1, 0.2, 0.1, 1],
            "desaturate": False,
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("STANCE", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=8, y_offset=1),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": "UPDATE_SHAPESHIFT_FORM,PLAYER_REGEN_DISABLED,PLAYER_REGEN_ENABLED,PLAYER_ENTERING_WORLD",
                        "custom": """function(event, ...)
                            local inCombat = UnitAffectingCombat("player")
                            local form = GetShapeshiftForm()
                            return inCombat and (form ~= 3)
                        end""",
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
                            local inCombat = UnitAffectingCombat("player")
                            local form = GetShapeshiftForm()
                            return (not inCombat) or (form == 3)
                        end"""
                    }
                },
                "activeTriggerMode": -10,
            },
        },
    ]
