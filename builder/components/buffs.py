"""
Modulo Componente: 02 - Battle Shout, 03 - Berserker Stance, 04 - Rampage
========================================================================
Gestisce la colonna sinistra dei buff di classe e stance (x = -190, -220, -160 a y = 0):
1. 02 - Battle Shout (Gruppo + Active [<= 30s] + OFF [mancante in combat, fallback Commanding Shout])
2. 03 - Berserker Stance (Gruppo + Warning [se in combat e non in Berserker Stance])
3. 04 - Rampage (Gruppo + Active + Missing [allerta se buff 5% crit manca in combat])
"""
from builder.core.helpers import make_subtext


# =============================================================================
# LOGICA LUA CONDIVISA: CACHE BUFF GUERRIERO UNIFICATA
# =============================================================================
SHARED_WARRIOR_BUFFS_LUA = r"""function()
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


def build_buffs_auras() -> list[dict]:
    """
    Costruisce e restituisce le aure relative ai buff passivi e alla stance del guerriero:
    - 02 - Battle Shout
    - 03 - Berserker Stance
    - 04 - Rampage
    """
    return [
        # =====================================================================
        # 02 - BATTLE SHOUT (Gruppo Madre a x = -190, y = 0)
        # =====================================================================
        {
            "id": "02 - Battle Shout",
            "uid": "FWHUD_BS_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": -190,
            "yOffset": 0,
            "controlledChildren": [
                "02 - Battle Shout - Active",
                "02 - Battle Shout - Missing",
            ],
        },
        # 02 - Active (mostra timer solo se <= 30 secondi)
        {
            "id": "02 - Battle Shout - Active",
            "uid": "FWHUD_BS_ACTIVE",
            "parent": "02 - Battle Shout",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 32,
            "height": 32,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_BattleShout",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Battle Shout", "Commanding Shout", "47436", "47440"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                        "rem_operator": "<=",
                        "rem": "30",
                        "use_rem": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 02 - Missing (Allerta rossa in combattimento se manca Battle Shout e Commanding Shout)
        {
            "id": "02 - Battle Shout - Missing",
            "uid": "FWHUD_BS_MISSING",
            "parent": "02 - Battle Shout",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 32,
            "height": 32,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_BattleShout",
            "auto": False,
            "color": [1, 0.2, 0.2, 0.9],
            "desaturate": True,
            "subRegions": [
                make_subtext("MISS", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=1),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Battle Shout", "Commanding Shout", "47436", "47440"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnMissing",
                    },
                    "untrigger": {}
                },
                2: {
                    "trigger": {
                        "type": "unit",
                        "event": "Conditions",
                        "unit": "player",
                        "use_inCombat": True,
                        "inCombat": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },

        # =====================================================================
        # 03 - BERSERKER STANCE (x = -220, y = 0)
        # =====================================================================
        {
            "id": "03 - Berserker Stance",
            "uid": "FWHUD_STANCE_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": -220,
            "yOffset": 0,
            "controlledChildren": [
                "03 - Berserker Stance - OutOfStance",
            ],
        },
        {
            "id": "03 - Berserker Stance - OutOfStance",
            "uid": "FWHUD_STANCE_WARNING",
            "parent": "03 - Berserker Stance",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 32,
            "height": 32,
            "displayIcon": "Interface\\Icons\\Ability_Racial_Avatar",
            "auto": False,
            "color": [1, 0.3, 0.1, 1],
            "desaturate": False,
            "subRegions": [
                make_subtext("STANCE", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=9, y_offset=1),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "stateupdate",
                        "check": "event",
                        "events": "UPDATE_SHAPESHIFT_FORM PLAYER_REGEN_DISABLED PLAYER_REGEN_ENABLED",
                        "custom": """function(allstates, event, ...)
                            local inCombat = UnitAffectingCombat("player")
                            local form = GetShapeshiftForm()
                            -- Form 3 = Berserker Stance
                            if inCombat and form ~= 3 then
                                allstates[""] = {
                                    show = true,
                                    changed = true,
                                    progressType = "static",
                                    icon = "Interface\\\\Icons\\\\Ability_Racial_Avatar",
                                }
                            else
                                allstates[""] = { show = false, changed = true }
                            end
                            return true
                        end""",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },

        # =====================================================================
        # 04 - RAMPAGE (x = -160, y = 0)
        # =====================================================================
        {
            "id": "04 - Rampage",
            "uid": "FWHUD_RAMPAGE_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": -160,
            "yOffset": 0,
            "controlledChildren": [
                "04 - Rampage - Missing",
            ],
        },
        {
            "id": "04 - Rampage - Missing",
            "uid": "FWHUD_RAMPAGE_MISSING",
            "parent": "04 - Rampage",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 32,
            "height": 32,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_Rampage",
            "auto": False,
            "color": [1, 0.4, 0.2, 0.8],
            "desaturate": True,
            "subRegions": [
                make_subtext("RAMP", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=9, y_offset=1),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Rampage", "Leader of the Pack", "29801", "17007"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnMissing",
                    },
                    "untrigger": {}
                },
                2: {
                    "trigger": {
                        "type": "unit",
                        "event": "Conditions",
                        "unit": "player",
                        "use_inCombat": True,
                        "inCombat": True,
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
    ]
