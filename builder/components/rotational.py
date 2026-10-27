"""
Modulo Componente: 15 - Rotational Bar (Dual Swing Timer & Heroic Strike Queued)
===============================================================================
Gestisce la barra orizzontale centrale composita a y = -7 (278x7px):
1. Background Frame (278x7px, scuro semitrasparente).
2. Mezza Barra Sinistra (137x5px a x = -70.5): Swing Timer Mano Primaria (MH) con timing %c (es. 1.8s).
3. Mezza Barra Destra (137x5px a x = +70.5): Swing Timer Mano Secondaria (OH) con timing %c (es. 1.2s).
4. Indicatore Heroic Strike / Cleave Queued:
   - Rileva in tempo reale se Heroic Strike (47450) o Cleave (47520) è accodato tramite IsCurrentSpell().
   - Applica Pixel Glow dorato istantaneo su tutta la barra e testo centrale |cFFFFD700[HS QUEUED]|r.
"""
from builder.core.helpers import make_subtext, make_glow_action
from builder.core.constants import TEXTURE_STATUSBAR, TEXTURE_WHITE8X8


# =============================================================================
# LOGICA LUA CONDIVISA: SWING TIMER & HEROIC STRIKE QUEUING
# =============================================================================
SHARED_SWING_TIMER_LUA = r"""_G.FWHUD_GetSwing = function()
    _G.FWHUD_Swing = _G.FWHUD_Swing or {
        mhStart = 0,
        mhDur = 3.0,
        ohStart = 0,
        ohDur = 3.0,
        hsQueued = false,
    }
    local sw = _G.FWHUD_Swing

    local f = _G.FWHUD_SwingFrame
    if not f then
        f = CreateFrame("Frame", "FWHUD_SwingFrame")
        _G.FWHUD_SwingFrame = f

        local function handleCLEU(...)
            local ts, ev, srcGUID = select(1, ...), select(2, ...), select(3, ...)
            if srcGUID ~= UnitGUID("player") then return end

            local now = GetTime()
            local mhSpeed, ohSpeed = UnitAttackSpeed("player")
            mhSpeed = mhSpeed or 3.0
            ohSpeed = ohSpeed or 0
            local hasOH = (OffhandHasWeapon and OffhandHasWeapon()) or (ohSpeed > 0)

            if ev == "SWING_DAMAGE" or ev == "SWING_MISSED" then
                if not hasOH then
                    sw.mhStart = now
                    sw.mhDur = mhSpeed
                elseif not sw.mhStart or sw.mhStart == 0 then
                    sw.mhStart = now
                    sw.mhDur = mhSpeed
                elseif not sw.ohStart or sw.ohStart == 0 then
                    sw.ohStart = now
                    sw.ohDur = ohSpeed
                else
                    local mhRem = (sw.mhStart + sw.mhDur) - now
                    local ohRem = (sw.ohStart + sw.ohDur) - now
                    if mhRem <= ohRem then
                        sw.mhStart = now
                        sw.mhDur = mhSpeed
                    else
                        sw.ohStart = now
                        sw.ohDur = ohSpeed
                    end
                end
            elseif ev == "SPELL_DAMAGE" or ev == "SPELL_MISSED" then
                local sId = select(9, ...)
                local sName = select(10, ...)
                if sId == 47450 or sId == 47520 or sName == "Heroic Strike" or sName == "Cleave" then
                    sw.mhStart = now
                    sw.mhDur = mhSpeed
                    sw.hsQueued = false
                end
            elseif ev == "SPELL_EXTRA_ATTACKS" then
                sw.mhStart = now
                sw.mhDur = mhSpeed
            end
        end

        f:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
        f:RegisterEvent("UNIT_ATTACK_SPEED")
        f:RegisterEvent("PLAYER_ENTERING_WORLD")
        f:RegisterEvent("START_AUTOREPEAT_SPELL")
        f:RegisterEvent("STOP_AUTOREPEAT_SPELL")
        f:SetScript("OnEvent", function(self, event, ...)
            if event == "COMBAT_LOG_EVENT_UNFILTERED" then
                handleCLEU(...)
            elseif event == "UNIT_ATTACK_SPEED" then
                local u = select(1, ...)
                if u == "player" then
                    local mh, oh = UnitAttackSpeed("player")
                    if mh and mh > 0 then sw.mhDur = mh end
                    if oh and oh > 0 then sw.ohDur = oh end
                end
            elseif event == "PLAYER_ENTERING_WORLD" then
                local mh, oh = UnitAttackSpeed("player")
                if mh and mh > 0 then sw.mhDur = mh end
                if oh and oh > 0 then sw.ohDur = oh end
            end
        end)
    end

    local isHS = IsCurrentSpell and (IsCurrentSpell(47450) or IsCurrentSpell(47520) or IsCurrentSpell("Heroic Strike") or IsCurrentSpell("Cleave"))
    sw.hsQueued = (isHS == true or isHS == 1)

    return sw
end"""


def build_rotational_auras() -> list[dict]:
    """
    Costruisce e restituisce le 4 aure che compongono il componente Rotational Bar:
    - 15 - Rotational Bar (Group)
    - Rotational Bar - Background (Texture 278x7px)
    - Rotational Bar - MH Swing (Aurabar 137x5px a x = -70.5) con timing live %c
    - Rotational Bar - OH Swing (Aurabar 137x5px a x = +70.5) con timing live %c
    - Rotational Bar - HS Queued (Texture / Overlay con Pixel Glow)
    """
    return [
        # Gruppo Contenitore
        {
            "id": "15 - Rotational Bar",
            "uid": "FWHUD_ROTCENTER_GRP",
            "parent": "Class Warrior (Fury)",
            "regionType": "group",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": -7,
            "anchorPoint": "CENTER",
            "selfPoint": "CENTER",
            "controlledChildren": [
                "Rotational Bar - Background",
                "Rotational Bar - MH Swing",
                "Rotational Bar - OH Swing",
                "Rotational Bar - HS Queued",
            ],
            "actions": {
                "init": {
                    "do_custom": True,
                    "custom": SHARED_SWING_TIMER_LUA,
                },
                "start": {},
                "finish": {},
            },
        },
        # Background Frame (278x7px)
        {
            "id": "Rotational Bar - Background",
            "uid": "FWHUD_ROTCENTER_BG",
            "parent": "15 - Rotational Bar",
            "regionType": "texture",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": 0,
            "width": 278,
            "height": 7,
            "texture": TEXTURE_WHITE8X8,
            "color": [0.08, 0.04, 0.04, 0.85],
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
        # MH Swing (Mezza barra sinistra: 137x5px a x = -70.5) con etichetta MH e timing %c
        {
            "id": "Rotational Bar - MH Swing",
            "uid": "FWHUD_ROTCENTER_MH",
            "parent": "15 - Rotational Bar",
            "regionType": "aurabar",
            "internalVersion": 52,
            "width": 137,
            "height": 5,
            "xOffset": -70.5,
            "yOffset": 0,
            "barColor": [0.85, 0.45, 0.15, 1.0],
            "backgroundColor": [0.12, 0.06, 0.04, 0.6],
            "texture": TEXTURE_STATUSBAR,
            "inverse": False,
            "actions": {
                "init": {
                    "do_custom": True,
                    "custom": SHARED_SWING_TIMER_LUA,
                },
                "start": {},
                "finish": {},
            },
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "custom": "function() return true end",
                        "customDuration": """function()
                            if _G.FWHUD_GetSwing then _G.FWHUD_GetSwing() end
                            if WeakAuras and WeakAuras.GetSwingTimerInfo then
                                local d, e = WeakAuras.GetSwingTimerInfo("main")
                                if e and e > GetTime() then return d, e end
                            end
                            local sw = _G.FWHUD_Swing
                            local now = GetTime()
                            local start = sw and sw.mhStart or 0
                            local dur = sw and sw.mhDur or select(1, UnitAttackSpeed("player")) or 3.0
                            local exp = start + dur
                            if exp > now and start > 0 then
                                return dur, exp
                            end
                            return dur, now + dur
                        end""",
                        "customText": """function()
                            if _G.FWHUD_GetSwing then _G.FWHUD_GetSwing() end
                            local now = GetTime()
                            if WeakAuras and WeakAuras.GetSwingTimerInfo then
                                local d, e = WeakAuras.GetSwingTimerInfo("main")
                                if e and e > now then
                                    return string.format("%.1fs", e - now)
                                end
                            end
                            local sw = _G.FWHUD_Swing
                            if sw and sw.mhStart and sw.mhStart > 0 then
                                local rem = (sw.mhStart + (sw.mhDur or 3.0)) - now
                                if rem > 0 then
                                    return string.format("%.1fs", rem)
                                end
                            end
                            local spd = select(1, UnitAttackSpeed("player")) or 3.0
                            return string.format("%.1fs", spd)
                        end""",
                        "customTextUpdate": "update",
                    },
                    "untrigger": {
                        "custom": "function() return false end",
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                make_subtext("MH", justify="LEFT", anchor_point="INNER_LEFT", font_size=9, y_offset=0, extra_props={"text_xOffset": 3, "text_color": [1.0, 0.75, 0.2, 1.0]}),
                make_subtext("%c", justify="LEFT", anchor_point="INNER_LEFT", font_size=9, y_offset=0, extra_props={"text_xOffset": 24, "text_color": [1.0, 1.0, 1.0, 1.0]}),
            ],
        },
        # OH Swing (Mezza barra destra: 137x5px a x = +70.5) con etichetta OH e timing %c
        {
            "id": "Rotational Bar - OH Swing",
            "uid": "FWHUD_ROTCENTER_OH",
            "parent": "15 - Rotational Bar",
            "regionType": "aurabar",
            "internalVersion": 52,
            "width": 137,
            "height": 5,
            "xOffset": 70.5,
            "yOffset": 0,
            "barColor": [0.75, 0.35, 0.10, 1.0],
            "backgroundColor": [0.12, 0.06, 0.04, 0.6],
            "texture": TEXTURE_STATUSBAR,
            "inverse": False,
            "actions": {
                "init": {
                    "do_custom": True,
                    "custom": SHARED_SWING_TIMER_LUA,
                },
                "start": {},
                "finish": {},
            },
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "custom": "function() return true end",
                        "customDuration": """function()
                            if _G.FWHUD_GetSwing then _G.FWHUD_GetSwing() end
                            if WeakAuras and WeakAuras.GetSwingTimerInfo then
                                local d, e = WeakAuras.GetSwingTimerInfo("off")
                                if e and e > GetTime() then return d, e end
                            end
                            local sw = _G.FWHUD_Swing
                            local now = GetTime()
                            local start = sw and sw.ohStart or 0
                            local dur = sw and sw.ohDur or select(2, UnitAttackSpeed("player")) or 3.0
                            local exp = start + dur
                            if exp > now and start > 0 then
                                return dur, exp
                            end
                            return dur, now + dur
                        end""",
                        "customText": """function()
                            if _G.FWHUD_GetSwing then _G.FWHUD_GetSwing() end
                            local now = GetTime()
                            if WeakAuras and WeakAuras.GetSwingTimerInfo then
                                local d, e = WeakAuras.GetSwingTimerInfo("off")
                                if e and e > now then
                                    return string.format("%.1fs", e - now)
                                end
                            end
                            local sw = _G.FWHUD_Swing
                            if sw and sw.ohStart and sw.ohStart > 0 then
                                local rem = (sw.ohStart + (sw.ohDur or 3.0)) - now
                                if rem > 0 then
                                    return string.format("%.1fs", rem)
                                end
                            end
                            local _, spd = UnitAttackSpeed("player")
                            spd = spd or 0
                            if spd > 0 then
                                return string.format("%.1fs", spd)
                            end
                            return "-"
                        end""",
                        "customTextUpdate": "update",
                    },
                    "untrigger": {
                        "custom": "function() return false end",
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                make_subtext("%c", justify="RIGHT", anchor_point="INNER_RIGHT", font_size=9, y_offset=0, extra_props={"text_xOffset": -24, "text_color": [1.0, 1.0, 1.0, 1.0]}),
                make_subtext("OH", justify="RIGHT", anchor_point="INNER_RIGHT", font_size=9, y_offset=0, extra_props={"text_xOffset": -3, "text_color": [1.0, 0.65, 0.2, 1.0]}),
            ],
        },
        # HS Queued Indicator (Border / Glow / Text overlay quando Heroic Strike o Cleave è accodato)
        {
            "id": "Rotational Bar - HS Queued",
            "uid": "FWHUD_ROTCENTER_HSQ",
            "parent": "15 - Rotational Bar",
            "regionType": "texture",
            "internalVersion": 52,
            "width": 278,
            "height": 7,
            "xOffset": 0,
            "yOffset": 0,
            "texture": TEXTURE_STATUSBAR,
            "color": [1.0, 0.84, 0.0, 0.35],
            "actions": {
                "start": make_glow_action(),
                "finish": {"do_glow": True, "glow_action": "hide"},
            },
            "subRegions": [
                make_subtext("|cFFFFD700[HS QUEUED]|r", justify="CENTER", anchor_point="CENTER", font_size=10, y_offset=0),
            ],
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "event",
                        "events": "CURRENT_SPELL_CAST_CHANGED,ACTIONBAR_UPDATE_STATE,START_AUTOREPEAT_SPELL,STOP_AUTOREPEAT_SPELL,UNIT_SPELLCAST_SUCCEEDED,PLAYER_ENTERING_WORLD",
                        "custom": """function()
                            return IsCurrentSpell and (IsCurrentSpell(47450) or IsCurrentSpell(47520) or IsCurrentSpell("Heroic Strike") or IsCurrentSpell("Cleave"))
                        end""",
                    },
                    "untrigger": {
                        "custom": """function()
                            local isHS = IsCurrentSpell and (IsCurrentSpell(47450) or IsCurrentSpell(47520) or IsCurrentSpell("Heroic Strike") or IsCurrentSpell("Cleave"))
                            return not isHS
                        end""",
                    }
                },
                "activeTriggerMode": -10,
            },
        },
    ]
