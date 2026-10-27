"""
Modulo Componente: 02 - Battle Shout, 03 - Commanding Shout, 04 - Berserker Stance
===================================================================================
Gestisce i buff di classe e la stance con intelligenza raid (x = -190, -220, -160 a y = 0):
1. 02 - Battle Shout:
   - Zero Clutter: nascosto se attivo con > 30s.
   - Mostra timer se <= 30s.
   - Allerta mancante in combat SOLO se NON è presente Greater Blessing of Might (GBoM)
     o Blessing of Might del Paladino (che non si sommano e sono superiori/equivalenti).
2. 03 - Commanding Shout:
   - Zero Clutter: nascosto se attivo con > 30s.
   - Mostra timer se <= 30s.
   - Allerta mancante in combat SOLO se NON è presente Blood Pact (Patto di Sangue del Warlock Imp)
     e il guerriero ha già GBoM (segno che il guerriero deve fornire Commanding Shout).
3. 04 - Berserker Stance:
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
        hasBloodPact = false,
        hasBattleShout = false,
        hasCommandingShout = false,
        bsDuration = 0,
        bsExpiration = 0,
        csDuration = 0,
        csExpiration = 0,
    }

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
           name == "Greater Blessing of Might" or name == "Blessing of Might" or
           name == "Benedizione della Potenza Superiore" or name == "Benedizione della Potenza" then
            c.hasBoM = true
        end

        -- Controllo Blood Pact (Warlock Imp: non stacka con Commanding Shout)
        if spellId == 47982 or spellId == 47981 or spellId == 27268 or spellId == 11767 or
           spellId == 11766 or spellId == 6307 or name == "Blood Pact" or name == "Patto di Sangue" then
            c.hasBloodPact = true
        end

        -- Controllo Battle Shout
        if spellId == 47436 or spellId == 25289 or spellId == 11551 or spellId == 11550 or
           spellId == 11549 or spellId == 6192 or spellId == 5242 or spellId == 2048 or spellId == 6673 or
           name == "Battle Shout" or name == "Urlo di Battaglia" then
            c.hasBattleShout = true
            c.bsDuration = duration or 120
            c.bsExpiration = expirationTime or (now_b + 120)
        end

        -- Controllo Commanding Shout
        if spellId == 47440 or spellId == 469 or name == "Commanding Shout" or name == "Urlo di Comando" then
            c.hasCommandingShout = true
            c.csDuration = duration or 120
            c.csExpiration = expirationTime or (now_b + 120)
        end
    end

    _G.FWHUD_BuffCache = c
    return c
end"""


def build_buffs_auras() -> list[dict]:
    """
    Costruisce e restituisce le aure relative ai buff passivi e alla stance del guerriero:
    - 02 - Battle Shout
    - 03 - Commanding Shout
    - 04 - Berserker Stance
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
        # 02 - Active (mostra timer solo se attivo con <= 30 secondi)
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
                        "auranames": ["Battle Shout", "47436"],
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
        # 02 - Missing (Allerta rossa in combattimento SOLO se manca sia Battle Shout che Blessing of Might del Paladino)
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
            "init_completed": SHARED_WARRIOR_BUFFS_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "stateupdate",
                        "check": "event",
                        "events": "UNIT_AURA:player PLAYER_REGEN_DISABLED PLAYER_REGEN_ENABLED",
                        "custom": """function(allstates, event, ...)
                            local inCombat = UnitAffectingCombat("player")
                            if not inCombat then
                                allstates[""] = { show = false, changed = true }
                                return true
                            end

                            local c = _G.FWHUD_BuffCache or (_G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs())
                            -- Se ha Blessing of Might o ha Battle Shout, NON mostrare missing
                            if (c and c.hasBoM) or (c and c.hasBattleShout) then
                                allstates[""] = { show = false, changed = true }
                            else
                                allstates[""] = {
                                    show = true,
                                    changed = true,
                                    progressType = "static",
                                    icon = "Interface\\\\Icons\\\\Ability_Warrior_BattleShout",
                                }
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
        # 03 - COMMANDING SHOUT (Gruppo Madre a x = -220, y = 0)
        # =====================================================================
        {
            "id": "03 - Commanding Shout",
            "uid": "FWHUD_CS_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": -220,
            "yOffset": 0,
            "controlledChildren": [
                "03 - Commanding Shout - Active",
                "03 - Commanding Shout - Missing",
            ],
        },
        # 03 - Active (mostra timer solo se attivo con <= 30 secondi)
        {
            "id": "03 - Commanding Shout - Active",
            "uid": "FWHUD_CS_ACTIVE",
            "parent": "03 - Commanding Shout",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 32,
            "height": 32,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_RallyingCry",
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
                        "auranames": ["Commanding Shout", "47440"],
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
        # 03 - Missing (Mostra missing se in combat con BoM attivo dal Paladino, ma manca sia Commanding Shout che Blood Pact dell'Imp)
        {
            "id": "03 - Commanding Shout - Missing",
            "uid": "FWHUD_CS_MISSING",
            "parent": "03 - Commanding Shout",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 32,
            "height": 32,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_RallyingCry",
            "auto": False,
            "color": [1, 0.4, 0.1, 0.9],
            "desaturate": True,
            "subRegions": [
                make_subtext("CMD", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=1),
            ],
            "init_completed": SHARED_WARRIOR_BUFFS_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "stateupdate",
                        "check": "event",
                        "events": "UNIT_AURA:player PLAYER_REGEN_DISABLED PLAYER_REGEN_ENABLED",
                        "custom": """function(allstates, event, ...)
                            local inCombat = UnitAffectingCombat("player")
                            if not inCombat then
                                allstates[""] = { show = false, changed = true }
                                return true
                            end

                            local c = _G.FWHUD_BuffCache or (_G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs())
                            -- Se ha già Commanding Shout o ha Blood Pact, oppure NON ha BoM (nel qual caso serve Battle Shout), non mostrare missing
                            if (c and c.hasCommandingShout) or (c and c.hasBloodPact) or (c and not c.hasBoM) then
                                allstates[""] = { show = false, changed = true }
                            else
                                allstates[""] = {
                                    show = true,
                                    changed = true,
                                    progressType = "static",
                                    icon = "Interface\\\\Icons\\\\Ability_Warrior_RallyingCry",
                                }
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
        # 04 - BERSERKER STANCE (x = -160, y = 0)
        # =====================================================================
        {
            "id": "04 - Berserker Stance",
            "uid": "FWHUD_STANCE_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": -160,
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
            "width": 32,
            "height": 32,
            "displayIcon": "Interface\\Icons\\Ability_Racial_Avatar",
            "auto": False,
            "color": [1, 0.2, 0.1, 1],
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
    ]
