"""
Modulo Componente: 15 - Rotational Bar (Dual Swing Timer & Heroic Strike Queued)
===============================================================================
Gestisce la barra orizzontale centrale composita a y = -7 (278x7px):
1. Background Frame (278x7px, scuro semitrasparente).
2. Mezza Barra Sinistra (137x5px a x = -70.5): Swing Timer Mano Primaria (MH).
3. Mezza Barra Destra (137x5px a x = +70.5): Swing Timer Mano Secondaria (OH).
4. Indicatore Heroic Strike / Cleave Queued:
   - Rileva in tempo reale se Heroic Strike (47450) o Cleave (47520) è accodato tramite IsCurrentSpell().
   - Applica Pixel Glow dorato istantaneo su tutta la barra e testo centrale |cFFFFD700[HS QUEUED]|r.
"""
from builder.core.helpers import make_subtext, make_glow_action
from builder.core.constants import TEXTURE_STATUSBAR, TEXTURE_WHITE8X8


# =============================================================================
# LOGICA LUA CONDIVISA: SWING TIMER & HEROIC STRIKE QUEUING
# =============================================================================
SHARED_SWING_TIMER_LUA = r"""function()
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
        local playerGUID = UnitGUID("player")

        local function notifySwing()
            if WeakAuras and WeakAuras.ScanEvents then
                WeakAuras.ScanEvents("FWHUD_SWING_UPDATE")
            end
        end

        local function handleCombatLog(...)
            local timestamp, evType, srcGUID = select(1, ...), select(2, ...), select(3, ...)
            if srcGUID ~= playerGUID then return end

            local now = GetTime()
            local mhSpeed, ohSpeed = UnitAttackSpeed("player")
            mhSpeed = mhSpeed or 3.0
            ohSpeed = ohSpeed or 3.0

            if evType == "SWING_DAMAGE" or evType == "SWING_MISSED" then
                -- In WotLK 3.3.5a: arg9 o arg12 specifica se l'attacco è offhand
                local isOffhand = select(9, ...)
                if type(isOffhand) ~= "boolean" then
                    isOffhand = select(12, ...)
                end

                if isOffhand == true or isOffhand == 1 then
                    sw.ohStart = now
                    sw.ohDur = ohSpeed
                else
                    sw.mhStart = now
                    sw.mhDur = mhSpeed
                end
                notifySwing()
            elseif evType == "SPELL_EXTRA_ATTACKS" then
                sw.mhStart = now
                sw.mhDur = mhSpeed
                notifySwing()
            end
        end

        f:RegisterEvent("PLAYER_ENTERING_WORLD")
        f:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
        f:RegisterEvent("START_AUTOREPEAT_SPELL")
        f:RegisterEvent("STOP_AUTOREPEAT_SPELL")
        f:RegisterEvent("UNIT_SPELLCAST_SUCCEEDED")
        f:SetScript("OnEvent", function(self, ev, ...)
            if ev == "COMBAT_LOG_EVENT_UNFILTERED" then
                handleCombatLog(...)
            elseif ev == "PLAYER_ENTERING_WORLD" then
                playerGUID = UnitGUID("player")
            end
        end)
    end

    -- Controllo continuo dello stato di accodamento Heroic Strike o Cleave
    local isHS = IsCurrentSpell and (IsCurrentSpell(47450) or IsCurrentSpell(47520) or IsCurrentSpell("Heroic Strike") or IsCurrentSpell("Cleave"))
    if sw.hsQueued ~= (isHS == true or isHS == 1) then
        sw.hsQueued = (isHS == true or isHS == 1)
        if WeakAuras and WeakAuras.ScanEvents then
            WeakAuras.ScanEvents("FWHUD_HS_QUEUE_UPDATE")
        end
    end

    return sw
end"""


def build_rotational_auras() -> list[dict]:
    """
    Costruisce e restituisce le 4 aure che compongono il componente Rotational Bar:
    - 15 - Rotational Bar (Group)
    - Rotational Bar - Background (Texture 278x7px)
    - Rotational Bar - MH Swing (Aurabar 137x5px a x = -70.5)
    - Rotational Bar - OH Swing (Aurabar 137x5px a x = +70.5)
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
        # MH Swing (Mezza barra sinistra: 137x5px a x = -70.5)
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
            "init_completed": SHARED_SWING_TIMER_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "stateupdate",
                        "check": "event",
                        "events": "FWHUD_SWING_UPDATE FRAME_UPDATE",
                        "custom": """function(allstates, event, ...)
                            local sw = _G.FWHUD_Swing or (_G.FWHUD_InitSwing and _G.FWHUD_InitSwing())
                            local now = GetTime()
                            local start = sw and sw.mhStart or 0
                            local dur = sw and sw.mhDur or 3.0
                            local exp = start + dur
                            if exp > now and start > 0 then
                                allstates[""] = {
                                    show = true,
                                    changed = true,
                                    progressType = "timed",
                                    duration = dur,
                                    expirationTime = exp,
                                }
                            else
                                allstates[""] = {
                                    show = true,
                                    changed = true,
                                    progressType = "static",
                                    value = 0,
                                    total = 1,
                                }
                            end
                            return true
                        end""",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                make_subtext("MH", justify="LEFT", anchor_point="INNER_LEFT", font_size=9, y_offset=0),
            ],
        },
        # OH Swing (Mezza barra destra: 137x5px a x = +70.5)
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
            "init_completed": SHARED_SWING_TIMER_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "stateupdate",
                        "check": "event",
                        "events": "FWHUD_SWING_UPDATE FRAME_UPDATE",
                        "custom": """function(allstates, event, ...)
                            local sw = _G.FWHUD_Swing or (_G.FWHUD_InitSwing and _G.FWHUD_InitSwing())
                            local now = GetTime()
                            local start = sw and sw.ohStart or 0
                            local dur = sw and sw.ohDur or 3.0
                            local exp = start + dur
                            if exp > now and start > 0 then
                                allstates[""] = {
                                    show = true,
                                    changed = true,
                                    progressType = "timed",
                                    duration = dur,
                                    expirationTime = exp,
                                }
                            else
                                allstates[""] = {
                                    show = true,
                                    changed = true,
                                    progressType = "static",
                                    value = 0,
                                    total = 1,
                                }
                            end
                            return true
                        end""",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                make_subtext("OH", justify="RIGHT", anchor_point="INNER_RIGHT", font_size=9, y_offset=0),
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
            "init_completed": SHARED_SWING_TIMER_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "stateupdate",
                        "check": "event",
                        "events": "FWHUD_HS_QUEUE_UPDATE FRAME_UPDATE",
                        "custom": """function(allstates, event, ...)
                            local isHS = IsCurrentSpell and (IsCurrentSpell(47450) or IsCurrentSpell(47520) or IsCurrentSpell("Heroic Strike") or IsCurrentSpell("Cleave"))
                            if isHS == true or isHS == 1 then
                                allstates[""] = {
                                    show = true,
                                    changed = true,
                                    progressType = "static",
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

