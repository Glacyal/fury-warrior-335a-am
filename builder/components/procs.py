"""
Modulo Componente: 01 - Procs (Dynamic Group)
=============================================
Gestisce la barra orizzontale dinamica superiore dei proc di combattimento (y = 52):
- Crescita orizzontale centrata (space = 6px, icone 34x34px).
- Include rigorosamente i SOLI proc rotazionali di combattimento (Zero Clutter):
  1. Bloodsurge (Slam istantaneo con Pixel Glow e timer 5s)
  2. Victory Rush (Proc Victorious con countdown durata 20s e glow)
  3. Flurry (+25% Attack Speed per 3 colpi dopo un critico)
  4. Wrecking Crew / Enrage (+10% danno fisico per 12s)
  5. Rend (Debuff 15s Bleed su target)
  6. Execute Usable (Target <= 20% HP con bordo luminoso)
  7. Weapon Desync Alert (Allarme rosso lampeggiante SYNC se armi sincronizzate < 0.30s)
Tutti gli effetti di equipaggiamento (Tier Sets T7-T10, Incanti arma/anello, Monili)
sono gestiti nella riga inferiore Utility a y = -45, identicamente a fire-mage-335a-am.
"""
from builder.core.helpers import make_subtext, make_glow_action
from builder.components.rotational import SHARED_SWING_TIMER_LUA


def build_procs_auras() -> list[dict]:
    """
    Costruisce e restituisce le 8 aure del gruppo dinamico Procs:
    - 01 - Procs warDPS (Dynamic Group)
    - Bloodsurge, Victory Rush, Flurry, Wrecking Crew, Rend, Execute Usable, Weapon Desync Alert.
    """
    return [
        {
            "id": "01 - Procs warDPS",
            "uid": "FWHUD_PROCS_DG",
            "parent": "Class Warrior (Fury)",
            "regionType": "dynamicgroup",
            "internalVersion": 52,
            "grow": "HORIZONTAL",
            "align": "CENTER",
            "space": 6,
            "xOffset": 0,
            "yOffset": 52,
            "controlledChildren": [
                "Bloodsurge",
                "Victory Rush",
                "Flurry",
                "Wrecking Crew",
                "Rend",
                "Execute Usable",
                "Weapon Desync Alert",
            ],
        },
        # 1. Bloodsurge (Buff 46916 - Slam istantaneo)
        {
            "id": "Bloodsurge",
            "uid": "FWHUD_PROC_BLOODSURGE",
            "parent": "01 - Procs warDPS",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_Bloodsurge",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "actions": {
                "start": make_glow_action(),
                "finish": {"do_glow": True, "glow_action": "hide"},
            },
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
                make_subtext("%s", justify="RIGHT", anchor_point="INNER_TOPRIGHT", font_size=10, y_offset=-2),
            ],
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
        # 2. Victory Rush (Proc utilizzabile 20s post-kill - 34428)
        {
            "id": "Victory Rush",
            "uid": "FWHUD_PROC_VICTORY_RUSH",
            "parent": "01 - Procs warDPS",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_VictoryRush",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "actions": {
                "start": make_glow_action(),
                "finish": {"do_glow": True, "glow_action": "hide"},
            },
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "custom": """function()
    _G.FWHUD_VRState = _G.FWHUD_VRState or { lastStart = 0, lastEnd = 0, isUsable = false }
    if not _G.FWHUD_CheckVictoryRush then
        _G.FWHUD_CheckVictoryRush = function()
            local now = GetTime()
            local vr = _G.FWHUD_VRState
            local usable = IsUsableSpell(34428)
            if not usable and GetSpellInfo then
                usable = IsUsableSpell(GetSpellInfo(34428) or "Victory Rush")
            end
            if usable then
                if not vr.isUsable or now > vr.lastEnd then
                    vr.lastStart = now
                    vr.lastEnd = now + 20.0
                    vr.isUsable = true
                end
            else
                vr.isUsable = false
                vr.lastEnd = 0
            end
            if vr.isUsable and vr.lastEnd > now then
                return true, vr.lastEnd - now, 20.0
            end
            return false, 0, 0
        end
    end
    local isUsable = _G.FWHUD_CheckVictoryRush()
    return isUsable
end""",
                        "customDuration": """function()
    if not _G.FWHUD_CheckVictoryRush then return 0, 0 end
    local isUsable, rem, dur = _G.FWHUD_CheckVictoryRush()
    if isUsable and rem > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end""",
                        "customIcon": """function()
    return select(3, GetSpellInfo(34428)) or "Interface\\Icons\\Ability_Warrior_VictoryRush"
end""",
                    },
                    "untrigger": {
                        "custom": """function()
    if not _G.FWHUD_CheckVictoryRush then return true end
    local isUsable = _G.FWHUD_CheckVictoryRush()
    return not isUsable
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
        },
        # 3. Flurry (+25% Attack Speed - 16280)
        {
            "id": "Flurry",
            "uid": "FWHUD_PROC_FLURRY",
            "parent": "01 - Procs warDPS",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_GhoulFrenzy",
            "auto": True,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=12, y_offset=0),
                make_subtext("%s", justify="RIGHT", anchor_point="INNER_TOPRIGHT", font_size=10, y_offset=-2),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "aura2",
                        "unit": "player",
                        "auranames": ["Flurry", "Raffica", "16280", "16284"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 4. Wrecking Crew / Enrage (+10% danno - 57519 / 57516)
        {
            "id": "Wrecking Crew",
            "uid": "FWHUD_PROC_WRECKING_CREW",
            "parent": "01 - Procs warDPS",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_Trauma",
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
                        "auranames": ["Enrage", "Rabbia", "Wrecking Crew", "Squadra della Morte", "57519", "57516"],
                        "useName": True,
                        "debuffType": "HELPFUL",
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        },
        # 5. Rend (Debuff su target - 47465 / 15s)
        {
            "id": "Rend",
            "uid": "FWHUD_PROC_REND",
            "parent": "01 - Procs warDPS",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_Gouge",
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
                        "unit": "target",
                        "auranames": [
                            "Rend",
                            "Squarcio",
                            "47465",
                            "25208",
                            "11574",
                            "11573",
                            "11572",
                            "6548",
                            "6547",
                            "6546",
                            "772",
                        ],
                        "useName": True,
                        "debuffType": "HARMFUL",
                        "ownOnly": True,
                        "matchesShowOn": "showOnActive",
                    },
                    "untrigger": {},
                },
                "activeTriggerMode": -10,
            },
        },
        # 6. Execute Usable (Target <= 20% HP e Bersaglio VIVO)
        {
            "id": "Execute Usable",
            "uid": "FWHUD_PROC_EXECUTE",
            "parent": "01 - Procs warDPS",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\INV_Sword_48",
            "auto": False,
            "color": [1, 0.2, 0.2, 1],
            "desaturate": False,
            "actions": {
                "start": make_glow_action(),
                "finish": {"do_glow": True, "glow_action": "hide"},
            },
            "subRegions": [
                make_subtext("EXEC", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11, y_offset=1),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "custom": """function()
    if not UnitExists("target") or UnitIsDeadOrGhost("target") or not UnitCanAttack("player", "target") then
        return false
    end
    local maxHp = UnitHealthMax("target") or 0
    if maxHp <= 0 then return false end
    local hp = UnitHealth("target") or 0
    if hp <= 0 then return false end
    return (hp / maxHp) <= 0.20
end""",
                    },
                    "untrigger": {
                        "custom": """function()
    if not UnitExists("target") or UnitIsDeadOrGhost("target") or not UnitCanAttack("player", "target") then
        return true
    end
    local maxHp = UnitHealthMax("target") or 0
    if maxHp <= 0 then return true end
    local hp = UnitHealth("target") or 0
    return (hp <= 0) or ((hp / maxHp) > 0.20)
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
        },
        # 7. Weapon Desync Alert (Armi Sincronizzate < 0.30s - Avviso Rosso SYNC)
        {
            "id": "Weapon Desync Alert",
            "uid": "FWHUD_PROC_DESYNC",
            "parent": "01 - Procs warDPS",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 34,
            "height": 34,
            "displayIcon": "Interface\\Icons\\Ability_DualWield",
            "auto": False,
            "color": [1, 1, 1, 1],
            "desaturate": False,
            "actions": {
                "init": {
                    "do_custom": True,
                    "custom": SHARED_SWING_TIMER_LUA,
                },
                "start": make_glow_action(color=[1.0, 0.2, 0.2, 1.0]),
                "finish": {"do_glow": True, "glow_action": "hide"},
            },
            "subRegions": [
                make_subtext("SYNC", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11, y_offset=1, extra_props={"text_color": [1.0, 0.2, 0.2, 1.0]}),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "custom": """function()
    if not UnitAffectingCombat("player") then return false end
    if not UnitExists("target") or UnitIsDeadOrGhost("target") or not UnitCanAttack("player", "target") then return false end
    local _, ohSpeed = UnitAttackSpeed("player")
    if not ohSpeed or ohSpeed <= 0 then return false end
    if not _G.FWHUD_GetSwing then return false end
    local sw = _G.FWHUD_GetSwing()
    if not sw or not sw.mhStart or sw.mhStart == 0 or not sw.ohStart or sw.ohStart == 0 then return false end
    local now = GetTime()
    local mhDur = sw.mhDur or 3.0
    local ohDur = sw.ohDur or ohSpeed
    local mhRem = (sw.mhStart + mhDur) - now
    local ohRem = (sw.ohStart + ohDur) - now
    if mhRem < 0 or ohRem < 0 then return false end
    local delta = math.abs(mhRem - ohRem)
    return delta < 0.30
end""",
                    },
                    "untrigger": {
                        "custom": """function()
    if not UnitAffectingCombat("player") then return true end
    if not UnitExists("target") or UnitIsDeadOrGhost("target") or not UnitCanAttack("player", "target") then return true end
    local _, ohSpeed = UnitAttackSpeed("player")
    if not ohSpeed or ohSpeed <= 0 then return true end
    if not _G.FWHUD_GetSwing then return true end
    local sw = _G.FWHUD_GetSwing()
    if not sw or not sw.mhStart or sw.mhStart == 0 or not sw.ohStart or sw.ohStart == 0 then return true end
    local now = GetTime()
    local mhDur = sw.mhDur or 3.0
    local ohDur = sw.ohDur or ohSpeed
    local mhRem = (sw.mhStart + mhDur) - now
    local ohRem = (sw.ohStart + ohDur) - now
    if mhRem < 0 or ohRem < 0 then return true end
    local delta = math.abs(mhRem - ohRem)
    return delta >= 0.30
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
        },
    ]
