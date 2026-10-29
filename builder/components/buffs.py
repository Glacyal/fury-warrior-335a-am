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
SHARED_WARRIOR_BUFFS_LUA = r"""function(force)
    local now_b = GetTime()
    local c = _G.FWHUD_BuffCache
    if not force and c and c.time == now_b then
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
        hasBloodPact = false,
        bpDuration = 0,
        bpExpiration = 0,
        hasBattleShout = false,
        bsDuration = 0,
        bsExpiration = 0,
        hasCommandingShout = false,
        csDuration = 0,
        csExpiration = 0,
    }

    local bsNameLocal = (GetSpellInfo and select(1, GetSpellInfo(47436))) or "Battle Shout"
    local csNameLocal = (GetSpellInfo and select(1, GetSpellInfo(47440))) or "Commanding Shout"
    local bomNameLocal1 = (GetSpellInfo and select(1, GetSpellInfo(48934))) or "Greater Blessing of Might"
    local bomNameLocal2 = (GetSpellInfo and select(1, GetSpellInfo(19740))) or "Blessing of Might"
    local bpNameLocal = (GetSpellInfo and select(1, GetSpellInfo(47982))) or "Blood Pact"

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

        local lowerName = string.lower(name)
        local lowerIcon = icon and string.lower(icon) or ""

        -- Controllo Blessing of Might / Greater Blessing of Might (Paladino: non stacka con Battle Shout)
        if spellId == 48934 or spellId == 48933 or spellId == 48932 or spellId == 48931 or
           spellId == 27141 or spellId == 27140 or spellId == 25916 or spellId == 25782 or
           spellId == 25291 or spellId == 19838 or spellId == 19837 or spellId == 19836 or
           spellId == 19835 or spellId == 19834 or spellId == 19740 or
           (bomNameLocal1 and name == bomNameLocal1) or (bomNameLocal2 and name == bomNameLocal2) or
           string.find(lowerName, "might") or string.find(lowerName, "potenza") or
           string.find(lowerIcon, "spell_holy_greaterblessingofkings") or string.find(lowerIcon, "spell_holy_fistofjustice") then
            c.hasBoM = true
            c.bomDuration = duration or 1800
            c.bomExpiration = (expirationTime and expirationTime > 0) and expirationTime or (now_b + 1800)
        end

        -- Controllo Blood Pact (Warlock Imp: non stacka con Commanding Shout)
        if spellId == 47982 or spellId == 47981 or spellId == 27268 or spellId == 11767 or
           spellId == 11766 or spellId == 6307 or (bpNameLocal and name == bpNameLocal) or
           string.find(lowerName, "blood pact") or string.find(lowerName, "patto di sangue") or
           string.find(lowerIcon, "spell_shadow_bloodboil") then
            c.hasBloodPact = true
            c.bpDuration = duration or 1800
            c.bpExpiration = (expirationTime and expirationTime > 0) and expirationTime or (now_b + 1800)
        end

        -- Controllo Battle Shout
        if spellId == 47436 or spellId == 25289 or spellId == 11551 or spellId == 11550 or
           spellId == 11549 or spellId == 6192 or spellId == 5242 or spellId == 2048 or spellId == 6673 or
           (bsNameLocal and name == bsNameLocal) or string.find(lowerName, "battle shout") or string.find(lowerName, "urlo di battaglia") or
           string.find(lowerIcon, "ability_warrior_battleshout") then
            c.hasBattleShout = true
            c.bsDuration = duration or 120
            c.bsExpiration = (expirationTime and expirationTime > 0) and expirationTime or (now_b + 120)
        end

        -- Controllo Commanding Shout (Rank 1: 469/45517, Rank 2: 47439, Rank 3: 47440)
        if spellId == 47440 or spellId == 47439 or spellId == 469 or spellId == 45517 or
           (csNameLocal and name == csNameLocal) or string.find(lowerName, "commanding shout") or string.find(lowerName, "urlo di comando") or
           string.find(lowerIcon, "ability_warrior_commandingshout") or string.find(lowerIcon, "ability_warrior_rallyingcry") then
            c.hasCommandingShout = true
            c.csDuration = duration or 120
            c.csExpiration = (expirationTime and expirationTime > 0) and expirationTime or (now_b + 120)
        end
    end

    _G.FWHUD_BuffCache = c
    return c
end"""


SHARED_GET_PLAYER_BUFFS_LUA = r"""function()
    local now_b = GetTime()
    local c = _G.FWHUD_BuffCache
    if c and c.time == now_b then
        return c
    end
    c = { time = now_b, bySpellId = {}, byName = {}, list = {} }
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
    end
    _G.FWHUD_BuffCache = c
    return c
end"""


# =============================================================================
# HELPER LUA: BATTLE SHOUT ACTIVE (ARCHITETTURA IDENTICA A MOLTEN ARMOR)
# =============================================================================
BS_BUFF_LOOKUP_LUA = """local b = c.bySpellId[47436] or c.bySpellId[25289] or c.bySpellId[11551] or c.bySpellId[11550] or c.bySpellId[11549] or c.bySpellId[6192] or c.bySpellId[5242] or c.bySpellId[2048] or c.bySpellId[6673]
        or c.bySpellId[48934] or c.bySpellId[48933] or c.bySpellId[48932] or c.bySpellId[48931] or c.bySpellId[27141] or c.bySpellId[27140] or c.bySpellId[25916] or c.bySpellId[25782] or c.bySpellId[25291] or c.bySpellId[19838] or c.bySpellId[19837] or c.bySpellId[19836] or c.bySpellId[19835] or c.bySpellId[19834] or c.bySpellId[19740]
        or c.byName["Battle Shout"] or c.byName["Urlo di Battaglia"]
        or c.byName["Greater Blessing of Might"] or c.byName["Blessing of Might"]
        or c.byName["Benedizione della Potenza Superiore"] or c.byName["Benedizione della Potenza"]"""


def make_bs_custom_text() -> str:
    """Conto alla rovescia formattato per Battle Shout (visibile quando rem <= 30)."""
    return f"""function()
    _G.FWHUD_GetPlayerBuffs = _G.FWHUD_GetPlayerBuffs or {SHARED_GET_PLAYER_BUFFS_LUA}
    local c = _G.FWHUD_GetPlayerBuffs()
    {BS_BUFF_LOOKUP_LUA}
    if b and b.expirationTime and b.expirationTime > 0 then
        local rem = b.expirationTime - GetTime()
        if rem > 60 then
            local m = math.floor(rem / 60)
            local s = math.floor(rem % 60)
            return string.format("|cFFFFFF00%d:%02d|r", m, s)
        elseif rem > 0 then
            return string.format("|cFFFF4444%.0fs|r", rem)
        end
    end
    return ""
end"""


def make_bs_trigger() -> str:
    """Trigger Lua per Battle Shout Active con schedulazione timer su soglia 30s (zero sfarfallio)."""
    return f"""function(event, ...)
    _G.FWHUD_GetPlayerBuffs = _G.FWHUD_GetPlayerBuffs or {SHARED_GET_PLAYER_BUFFS_LUA}
    local now = GetTime()
    local c = _G.FWHUD_GetPlayerBuffs()
    {BS_BUFF_LOOKUP_LUA}
    if b and b.expirationTime and b.expirationTime > 0 then
        local rem = b.expirationTime - now
        if rem > 30 then
            local delay = rem - 30
            if _G.FWHUD_BS_ScheduledExp ~= b.expirationTime then
                _G.FWHUD_BS_ScheduledExp = b.expirationTime
                _G.FWHUD_BS_TimerSeq = (_G.FWHUD_BS_TimerSeq or 0) + 1
                local mySeq = _G.FWHUD_BS_TimerSeq
                local timerAfter = (C_Timer and C_Timer.After) or (_G.C_Timer and _G.C_Timer.After)
                if timerAfter then
                    timerAfter(delay, function()
                        if _G.FWHUD_BS_TimerSeq == mySeq and WeakAuras and WeakAuras.ScanEvents then
                            WeakAuras.ScanEvents("FWHUD_BS_THRESHOLD")
                        end
                    end)
                elseif WeakAuras and WeakAuras.timer and WeakAuras.timer.ScheduleTimer then
                    WeakAuras.timer:ScheduleTimer(function()
                        if _G.FWHUD_BS_TimerSeq == mySeq and WeakAuras and WeakAuras.ScanEvents then
                            WeakAuras.ScanEvents("FWHUD_BS_THRESHOLD")
                        end
                    end, delay)
                end
            end
            return false
        elseif rem > 0 then
            _G.FWHUD_BS_ScheduledExp = nil
            return true
        end
    end
    _G.FWHUD_BS_ScheduledExp = nil
    _G.FWHUD_BS_TimerSeq = (_G.FWHUD_BS_TimerSeq or 0) + 1
    return false
end"""


def make_bs_custom_duration() -> str:
    """Durata e scadenza per lo swipe cooldown di Battle Shout."""
    return f"""function()
    _G.FWHUD_GetPlayerBuffs = _G.FWHUD_GetPlayerBuffs or {SHARED_GET_PLAYER_BUFFS_LUA}
    local c = _G.FWHUD_GetPlayerBuffs()
    {BS_BUFF_LOOKUP_LUA}
    if b then
        return b.duration or 120, b.expirationTime
    end
    return 0, 0
end"""


def make_bs_untrigger() -> str:
    """Untrigger Lua per Battle Shout Active."""
    return f"""function(event, ...)
    _G.FWHUD_GetPlayerBuffs = _G.FWHUD_GetPlayerBuffs or {SHARED_GET_PLAYER_BUFFS_LUA}
    local now = GetTime()
    local c = _G.FWHUD_GetPlayerBuffs()
    {BS_BUFF_LOOKUP_LUA}
    if b and b.expirationTime and b.expirationTime > 0 then
        local rem = b.expirationTime - now
        return not (rem > 0 and rem <= 30)
    end
    return true
end"""


# =============================================================================
# HELPER LUA: COMMANDING SHOUT ACTIVE (ARCHITETTURA IDENTICA A MOLTEN ARMOR)
# =============================================================================
CS_BUFF_LOOKUP_LUA = """local b = c.bySpellId[47440] or c.bySpellId[47439] or c.bySpellId[469] or c.bySpellId[45517]
        or c.bySpellId[47982] or c.bySpellId[47981] or c.bySpellId[27268] or c.bySpellId[11767] or c.bySpellId[11766] or c.bySpellId[6307]
        or c.byName["Commanding Shout"] or c.byName["Urlo di Comando"]
        or c.byName["Blood Pact"] or c.byName["Patto di Sangue"]"""


def make_cs_custom_text() -> str:
    """Conto alla rovescia formattato per Commanding Shout (visibile quando rem <= 30)."""
    return f"""function()
    _G.FWHUD_GetPlayerBuffs = _G.FWHUD_GetPlayerBuffs or {SHARED_GET_PLAYER_BUFFS_LUA}
    local c = _G.FWHUD_GetPlayerBuffs()
    {CS_BUFF_LOOKUP_LUA}
    if b and b.expirationTime and b.expirationTime > 0 then
        local rem = b.expirationTime - GetTime()
        if rem > 60 then
            local m = math.floor(rem / 60)
            local s = math.floor(rem % 60)
            return string.format("|cFFFFFF00%d:%02d|r", m, s)
        elseif rem > 0 then
            return string.format("|cFFFF4444%.0fs|r", rem)
        end
    end
    return ""
end"""


def make_cs_trigger() -> str:
    """Trigger Lua per Commanding Shout Active con schedulazione timer su soglia 30s (zero sfarfallio)."""
    return f"""function(event, ...)
    _G.FWHUD_GetPlayerBuffs = _G.FWHUD_GetPlayerBuffs or {SHARED_GET_PLAYER_BUFFS_LUA}
    local now = GetTime()
    local c = _G.FWHUD_GetPlayerBuffs()
    {CS_BUFF_LOOKUP_LUA}
    if b and b.expirationTime and b.expirationTime > 0 then
        local rem = b.expirationTime - now
        if rem > 30 then
            local delay = rem - 30
            if _G.FWHUD_CS_ScheduledExp ~= b.expirationTime then
                _G.FWHUD_CS_ScheduledExp = b.expirationTime
                _G.FWHUD_CS_TimerSeq = (_G.FWHUD_CS_TimerSeq or 0) + 1
                local mySeq = _G.FWHUD_CS_TimerSeq
                local timerAfter = (C_Timer and C_Timer.After) or (_G.C_Timer and _G.C_Timer.After)
                if timerAfter then
                    timerAfter(delay, function()
                        if _G.FWHUD_CS_TimerSeq == mySeq and WeakAuras and WeakAuras.ScanEvents then
                            WeakAuras.ScanEvents("FWHUD_CS_THRESHOLD")
                        end
                    end)
                elseif WeakAuras and WeakAuras.timer and WeakAuras.timer.ScheduleTimer then
                    WeakAuras.timer:ScheduleTimer(function()
                        if _G.FWHUD_CS_TimerSeq == mySeq and WeakAuras and WeakAuras.ScanEvents then
                            WeakAuras.ScanEvents("FWHUD_CS_THRESHOLD")
                        end
                    end, delay)
                end
            end
            return false
        elseif rem > 0 then
            _G.FWHUD_CS_ScheduledExp = nil
            return true
        end
    end
    _G.FWHUD_CS_ScheduledExp = nil
    _G.FWHUD_CS_TimerSeq = (_G.FWHUD_CS_TimerSeq or 0) + 1
    return false
end"""


def make_cs_custom_duration() -> str:
    """Durata e scadenza per lo swipe cooldown di Commanding Shout."""
    return f"""function()
    _G.FWHUD_GetPlayerBuffs = _G.FWHUD_GetPlayerBuffs or {SHARED_GET_PLAYER_BUFFS_LUA}
    local c = _G.FWHUD_GetPlayerBuffs()
    {CS_BUFF_LOOKUP_LUA}
    if b then
        return b.duration or 120, b.expirationTime
    end
    return 0, 0
end"""


def make_cs_untrigger() -> str:
    """Untrigger Lua per Commanding Shout Active."""
    return f"""function(event, ...)
    _G.FWHUD_GetPlayerBuffs = _G.FWHUD_GetPlayerBuffs or {SHARED_GET_PLAYER_BUFFS_LUA}
    local now = GetTime()
    local c = _G.FWHUD_GetPlayerBuffs()
    {CS_BUFF_LOOKUP_LUA}
    if b and b.expirationTime and b.expirationTime > 0 then
        local rem = b.expirationTime - now
        return not (rem > 0 and rem <= 30)
    end
    return true
end"""


def build_buffs_auras() -> list[dict]:
    """
    Costruisce e restituisce le 6 aure (3 gruppi con figli Active e OFF) relative ai buff passivi e alla stance:
    - 02 - Battle Shout (Active + OFF)
    - 03 - Commanding Shout (Active + OFF)
    - 04 - Berserker Stance (OutOfStance)
    """
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
            "auto": False,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_bs_custom_text(),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": "UNIT_AURA,PLAYER_ENTERING_WORLD,FWHUD_BS_THRESHOLD",
                        "custom": make_bs_trigger(),
                        "customDuration": make_bs_custom_duration(),
                    },
                    "untrigger": {
                        "custom": make_bs_untrigger(),
                    },
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=0),
            ],
        },
        # 02 - OFF (Architettura nativa aura2 con showOnMissing e controllo sovrapposizioni BoM/GBoM)
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
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": [
                            "Battle Shout",
                            "Urlo di Battaglia",
                            "Greater Blessing of Might",
                            "Blessing of Might",
                            "Benedizione della Potenza Superiore",
                            "Benedizione della Potenza",
                        ],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnMissing",
                    },
                    "untrigger": {},
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("|cFFFF4444OFF|r", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=1),
            ],
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
            "displayIcon": "Interface\\Icons\\Ability_Warrior_RallyingCry",
            "auto": False,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_cs_custom_text(),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": "UNIT_AURA,PLAYER_ENTERING_WORLD,FWHUD_CS_THRESHOLD",
                        "custom": make_cs_trigger(),
                        "customDuration": make_cs_custom_duration(),
                    },
                    "untrigger": {
                        "custom": make_cs_untrigger(),
                    },
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=0),
            ],
        },
        # 03 - OFF (Architettura nativa aura2 con showOnMissing e controllo sovrapposizioni Blood Pact)
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
            "displayIcon": "Interface\\Icons\\Ability_Warrior_RallyingCry",
            "auto": False,
            "desaturate": True,
            "color": [0.6, 0.6, 0.6, 0.8],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": [
                            "Commanding Shout",
                            "Urlo di Comando",
                            "Blood Pact",
                            "Patto di Sangue",
                        ],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnMissing",
                    },
                    "untrigger": {},
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("|cFFFF4444OFF|r", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=1),
            ],
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
                        "check": "update",
                        "custom": """function()
    local form = GetShapeshiftForm()
    return form ~= 3 and UnitAffectingCombat("player")
end""",
                    },
                    "untrigger": {},
                },
                "activeTriggerMode": -10,
            },
        },
    ]
