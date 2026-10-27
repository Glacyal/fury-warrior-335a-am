"""
Modulo Componente: 05 - Trinkets & 06-13 - Utility Row (Warrior Fury)
======================================================================
Gestisce la riga orizzontale di utilità a y = -45 con riposizionamento dinamico
centrato naturale (da 3 a 9 icone) in base all'equipaggiamento e alle abilità:
1. 05 - Trinket 1 (Slot 13: ICD 45s/90s/105s o On-Use, Pixel Glow su proc)
2. 06 - Trinket 2 (Slot 14: ICD 45s/90s/105s o On-Use, Pixel Glow su proc)
3. 07 - Cloak (Slot 15: Swordguard Embroidery +400 AP / Paracadute / Flexweave)
4. 08 - Death Wish (Spell ID 12292, durata attiva 30s + cooldown 2m/3m)
5. 09 - Gloves (Slot 10: Acceleratori Ipersonici Ingegneria +340 Haste per 12s, 60s CD)
6. 10 - Recklessness (Spell ID 1719, 3 cariche critico garantite + cooldown 3m/5m)
7. 11 - Shattering Throw (Spell ID 64382, debuff -20% armatura sul boss 10s + cooldown 5m)
8. 12 - Enraged Regeneration (Spell ID 55694, cura 30% HP in 10s + cooldown 3m)
9. 13 - Boots (Slot 8: Acceleratori a Nitro / Nitro Boosts Ingegneria, 180s CD)
"""
from builder.core.helpers import make_subtext, make_glow_action


# =============================================================================
# LOGICA LUA CONDIVISA CENTRALIZZATA (BOOTSTRAP UTILITY WARRIOR)
# =============================================================================
SHARED_WARRIOR_CORE_BOOTSTRAP_LUA = r"""function()
    _G.FWHUD_GetPlayerBuffs = _G.FWHUD_GetPlayerBuffs or function()
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
    end

    if _G.FWHUD_CoreInitDone then return end

    _G.FWHUD_ICD = _G.FWHUD_ICD or {
        [8]  = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 },
        [10] = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 },
        [13] = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 },
        [14] = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 },
        [15] = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 },
    }

    _G.FWHUD_TrinketDB = {
        -- Deathbringer's Will (Normal & Heroic)
        [50362] = { keywords = { "taunka", "vrykul", "irondwarf", "deathbringer" }, spellIds = { [71485] = true, [71491] = true, [71487] = true }, icd = 105, dur = 30 },
        [50363] = { keywords = { "taunka", "vrykul", "irondwarf", "deathbringer" }, spellIds = { [71485] = true, [71491] = true, [71487] = true }, icd = 105, dur = 30 },
        -- Sharpened Twilight Scale (Normal & Heroic)
        [54569] = { keywords = { "twilightprecision", "sharpenedtwilight" }, spellIds = { [75473] = true, [75474] = true }, icd = 45, dur = 15 },
        [54590] = { keywords = { "twilightprecision", "sharpenedtwilight" }, spellIds = { [75473] = true, [75474] = true }, icd = 45, dur = 15 },
        -- Death's Choice / Verdict (Normal & Heroic Horde / Alliance)
        [47115] = { keywords = { "paragon" }, spellIds = { [67708] = true, [67703] = true }, icd = 45, dur = 15 },
        [47131] = { keywords = { "paragon" }, spellIds = { [67773] = true, [67772] = true }, icd = 45, dur = 15 },
        [47303] = { keywords = { "paragon" }, spellIds = { [67708] = true, [67703] = true }, icd = 45, dur = 15 },
        [47464] = { keywords = { "paragon" }, spellIds = { [67773] = true, [67772] = true }, icd = 45, dur = 15 },
        -- Whispering Fanged Skull
        [50342] = { keywords = { "whisperingfangedskull" }, spellIds = { [71541] = true }, icd = 45, dur = 15 },
        [50343] = { keywords = { "whisperingfangedskull" }, spellIds = { [71541] = true }, icd = 45, dur = 15 },
        -- Darkmoon Card: Greatness (Strength)
        [44253] = { keywords = { "greatness" }, spellIds = { [60229] = true }, icd = 45, dur = 15 },
        -- Mjolnir Runestone
        [45931] = { keywords = { "mjolnirrunestone", "runestone" }, spellIds = { [65019] = true }, icd = 45, dur = 10 },
        -- Grim Toll
        [40256] = { keywords = { "grimtoll" }, spellIds = { [60486] = true }, icd = 45, dur = 10 },
        -- Needle-Encrusted Scorpion
        [50198] = { keywords = { "needleencrusted", "scorpion" }, spellIds = { [71403] = true }, icd = 45, dur = 10 },
        -- Comet's Trail
        [45609] = { keywords = { "cometstrail" }, spellIds = { [64772] = true }, icd = 45, dur = 10 },
        -- Banner of Victory
        [44914] = { keywords = { "bannerofvictory" }, spellIds = { [67671] = true }, icd = 45, dur = 10 },
        -- Mirror of Truth
        [40684] = { keywords = { "mirroroftruth" }, spellIds = { [60488] = true }, icd = 45, dur = 10 },
        -- Wrathstone (On-Use)
        [45263] = { keywords = { "wrathstone" }, spellIds = { [64765] = true }, icd = 120, dur = 20, onUse = true },
    }

    _G.FWHUD_CloakKeywords = { "swordguard", "spadatesta", "parachute", "flexweave", "flessibile" }
    _G.FWHUD_CloakSpellIds = { [55775] = true, [55767] = true, [54865] = true, [54753] = true }
    _G.FWHUD_CloakEnchantIDs = { [3730] = true, [3605] = true }

    _G.FWHUD_GlovesSpellIds = { [54758] = true }
    _G.FWHUD_GlovesKeywords = { "hyperspeed", "accelerat", "ipersonic", "340 haste" }

    _G.FWHUD_BootsEnchantIDs = { [3601] = true, [3784] = true }
    _G.FWHUD_BootsSpellIds = { [54861] = true }
    _G.FWHUD_BootsKeywords = { "nitro", "boosts", "acceleratori a nitro" }

    _G.FWHUD_CheckSlotEquipped = function(s)
        local now_t = GetTime()
        _G.FWHUD_SlotEquipCache = _G.FWHUD_SlotEquipCache or {}
        local cache = _G.FWHUD_SlotEquipCache[s]
        if cache and (now_t - cache.time < 0.25) then
            return cache.isEquipped
        end
        if not cache then
            cache = { time = 0, isEquipped = false }
            _G.FWHUD_SlotEquipCache[s] = cache
        end
        cache.time = now_t

        local itemID = GetInventoryItemID and GetInventoryItemID("player", s)
        if not itemID then
            local link = GetInventoryItemLink("player", s)
            if link then itemID = tonumber(link:match("item:(%d+)")) end
        end

        if s == 13 or s == 14 then
            local eq = (itemID ~= nil and itemID > 0)
            cache.isEquipped = eq
            return eq
        end

        if not itemID or itemID == 0 then
            cache.isEquipped = false
            return false
        end

        local itemLink = GetInventoryItemLink("player", s)
        local enchantID = nil
        if itemLink then
            enchantID = tonumber(itemLink:match("item:%d+:(%d+)"))
        end

        if s == 10 then
            if enchantID == 3604 or enchantID == 3834 then cache.isEquipped = true return true end
            cache.isEquipped = true
            return true
        end

        if s == 8 then
            if enchantID and _G.FWHUD_BootsEnchantIDs and _G.FWHUD_BootsEnchantIDs[enchantID] then
                cache.isEquipped = true
                return true
            end
            cache.isEquipped = true
            return true
        end

        if s == 15 then
            if enchantID and _G.FWHUD_CloakEnchantIDs and _G.FWHUD_CloakEnchantIDs[enchantID] then
                cache.isEquipped = true
                return true
            end
            cache.isEquipped = true
            return true
        end

        cache.isEquipped = true
        return true
    end

    _G.FWHUD_CheckSlot = function(slot)
        local now = GetTime()
        _G.FWHUD_SlotCache = _G.FWHUD_SlotCache or {}
        if _G.FWHUD_SlotCache[slot] and _G.FWHUD_SlotCache[slot].time == now then
            local c = _G.FWHUD_SlotCache[slot]
            return c.state, c.rem, c.dur, c.icon
        end

        local function finish(st, r, d, ic)
            local c = _G.FWHUD_SlotCache[slot]
            if not c then
                c = {}
                _G.FWHUD_SlotCache[slot] = c
            end
            c.time = now
            c.state = st
            c.rem = r
            c.dur = d
            c.icon = ic
            return st, r, d, ic
        end

        local itemID = nil
        if GetInventoryItemID then itemID = GetInventoryItemID("player", slot) end
        if not itemID then
            local link = GetInventoryItemLink("player", slot)
            if link then itemID = tonumber(link:match("item:(%d+)")) end
        end
        local icdState = _G.FWHUD_ICD[slot]
        if icdState.lastItemID and itemID and icdState.lastItemID ~= itemID then
            icdState.lastStart = 0
            icdState.lastEnd = 0
            icdState.isProc = false
        end
        if itemID then icdState.lastItemID = itemID end

        local entry = itemID and _G.FWHUD_TrinketDB[itemID]
        local targetICD = (entry and entry.icd) or (slot == 10 and 60) or (slot == 8 and 180) or (slot == 15 and 45) or 45
        local defaultDur = (entry and entry.dur) or (slot == 10 and 12) or (slot == 8 and 5) or (slot == 15 and 15) or 10

        local itemStart, itemDur = GetInventoryItemCooldown("player", slot)
        local isOnUseCooldown = false
        local remItemCD = 0
        if itemStart and itemDur and itemStart > 0 and itemDur > 1.5 then
            remItemCD = (itemStart + itemDur) - now
            if remItemCD > 0.1 then isOnUseCooldown = true end
        end

        local foundBuff = false
        local remBuff = 0
        local durBuff = 0
        local buffIcon = nil

        local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
        local buffList = buffs and buffs.list
        local numBuffs = buffList and #buffList or 40

        for i = 1, numBuffs do
            local name, icon, count, duration, expirationTime, spellId
            if buffList then
                local b = buffList[i]
                if not b then break end
                name = b.name
                icon = b.icon
                count = b.count
                duration = b.duration
                expirationTime = b.expirationTime
                spellId = b.spellId
            else
                local n, _, ic, ct, _, dur, exp, _, _, _, spId = UnitBuff("player", i)
                if not n then break end
                name = n
                icon = ic
                count = ct
                duration = dur
                expirationTime = exp
                spellId = spId
            end
            local isMatch = false

            if slot == 15 then
                if spellId and _G.FWHUD_CloakSpellIds and _G.FWHUD_CloakSpellIds[spellId] then
                    isMatch = true
                end
            elseif slot == 10 then
                if spellId and _G.FWHUD_GlovesSpellIds and _G.FWHUD_GlovesSpellIds[spellId] then
                    isMatch = true
                end
            elseif slot == 8 then
                if spellId and spellId == 54861 then isMatch = true end
            else
                if entry and spellId and entry.spellIds and entry.spellIds[spellId] then
                    isMatch = true
                end
            end

            if isMatch then
                durBuff = (duration and duration > 0) and duration or defaultDur
                remBuff = (expirationTime and expirationTime > 0) and (expirationTime - now) or durBuff
                if remBuff > 0.05 then
                    foundBuff = true
                    buffIcon = icon
                    break
                end
            end
        end

        if foundBuff then
            if not icdState.isProc or (now - icdState.lastStart > durBuff + 2) then
                icdState.lastStart = now - (durBuff - remBuff)
                icdState.lastEnd = icdState.lastStart + targetICD
                icdState.isProc = true
            end
            return finish("ACTIVE", remBuff, durBuff, buffIcon)
        end

        if icdState.isProc then
            icdState.isProc = false
            if icdState.lastEnd == 0 or icdState.lastEnd > now then
                icdState.lastEnd = now
            end
        end

        if isOnUseCooldown then
            return finish("COOLDOWN", remItemCD, itemDur, nil)
        end

        if icdState.lastStart > 0 and targetICD > 0 then
            local elapsed = now - icdState.lastStart
            if elapsed < targetICD then
                local remICD = targetICD - elapsed
                return finish("COOLDOWN", remICD, targetICD, nil)
            end
        end

        return finish("READY", 0, 0, nil)
    end

    local lastRowUpdate = 0
    _G.FWHUD_UpdateUtilityRowPositions = function(force)
        local now = GetTime()
        if not force and (now - lastRowUpdate < 0.15) then return end
        lastRowUpdate = now

        if not WeakAuras or not WeakAuras.regions then return end
        local groupObj = WeakAuras.regions["Class Warrior (Fury)"]
        local group = groupObj and (groupObj.region or (groupObj.GetPoint and groupObj))
        if not group then return end

        local hasT1 = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped(13)
        local hasT2 = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped(14)
        local hasCloak = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped(15)
        local hasGloves = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped(10)
        local hasBoots = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped(8)

        local activeOrder = {}
        if hasT1 then table.insert(activeOrder, "05 - Trinket 1") end
        if hasT2 then table.insert(activeOrder, "06 - Trinket 2") end
        if hasCloak then table.insert(activeOrder, "07 - Cloak") end
        table.insert(activeOrder, "08 - Death Wish")
        if hasGloves then table.insert(activeOrder, "09 - Gloves") end
        table.insert(activeOrder, "10 - Recklessness")
        table.insert(activeOrder, "11 - Shattering Throw")
        table.insert(activeOrder, "12 - Enraged Regeneration")
        if hasBoots then table.insert(activeOrder, "13 - Boots") end

        local N = #activeOrder
        local step = 38
        if N >= 9 then step = 29
        elseif N == 8 then step = 32
        elseif N == 7 then step = 38
        elseif N == 6 then step = 44
        elseif N == 5 then step = 48
        else step = 52 end

        for i, id in ipairs(activeOrder) do
            local targetX = math.floor(((i - (N + 1) / 2) * step) + 0.5)
            local regObj = WeakAuras.regions[id]
            local r = regObj and (regObj.region or (regObj.GetPoint and regObj))
            if r and r.ClearAllPoints and r.SetPoint then
                r:ClearAllPoints()
                r:SetPoint("CENTER", group, "CENTER", targetX, -45)
            end
        end
    end

    local f = _G.FWHUD_CoreFrame
    if not f then
        f = CreateFrame("Frame", "FWHUD_CoreFrame")
        _G.FWHUD_CoreFrame = f
        f:RegisterEvent("PLAYER_ENTERING_WORLD")
        f:RegisterEvent("PLAYER_EQUIPMENT_CHANGED")
        f:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
        f:SetScript("OnEvent", function(self, event, ...)
            if event == "PLAYER_ENTERING_WORLD" or event == "PLAYER_EQUIPMENT_CHANGED" then
                _G.FWHUD_SlotEquipCache = nil
                _G.FWHUD_SlotCache = nil
                _G.FWHUD_UpdateUtilityRowPositions(true)
            end
        end)
    end

    _G.FWHUD_CoreInitDone = true
end"""


def build_utility_auras() -> list[dict]:
    """
    Costruisce e restituisce le 9 aure della riga utility adattiva centrata a y = -45:
    - 05 - Trinket 1
    - 06 - Trinket 2
    - 07 - Cloak
    - 08 - Death Wish
    - 09 - Gloves
    - 10 - Recklessness
    - 11 - Shattering Throw
    - 12 - Enraged Regeneration
    - 13 - Boots
    """
    auras = []

    # Helper per generare i componenti utility a slot
    def make_slot_aura(id_name, uid, slot_num, def_icon):
        return {
            "id": id_name,
            "uid": uid,
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "width": 28,
            "height": 28,
            "xOffset": 0,
            "yOffset": -45,
            "displayIcon": def_icon,
            "auto": False,
            "color": [1, 1, 1, 1],
            "cooldown": True,
            "cooldownSwipe": True,
            "subRegions": [
                make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11, y_offset=0),
            ],
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "stateupdate",
                        "check": "event",
                        "events": "UNIT_AURA:player ACTIONBAR_UPDATE_COOLDOWN BAG_UPDATE_COOLDOWN PLAYER_EQUIPMENT_CHANGED",
                        "custom": f"""function(allstates, event, ...)
                            if _G.FWHUD_UpdateUtilityRowPositions then _G.FWHUD_UpdateUtilityRowPositions() end
                            local isEq = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped({slot_num})
                            if not isEq then
                                allstates[""] = {{ show = false, changed = true }}
                                return true
                            end
                            local state, rem, dur, icon = _G.FWHUD_CheckSlot and _G.FWHUD_CheckSlot({slot_num})
                            if state == "ACTIVE" then
                                allstates[""] = {{
                                    show = true,
                                    changed = true,
                                    progressType = "timed",
                                    duration = dur,
                                    expirationTime = GetTime() + rem,
                                    icon = icon or "{def_icon}",
                                }}
                            elseif state == "COOLDOWN" then
                                allstates[""] = {{
                                    show = true,
                                    changed = true,
                                    progressType = "timed",
                                    duration = dur,
                                    expirationTime = GetTime() + rem,
                                    icon = icon or "{def_icon}",
                                }}
                            else
                                allstates[""] = {{
                                    show = true,
                                    changed = true,
                                    progressType = "static",
                                    icon = icon or "{def_icon}",
                                }}
                            end
                            return true
                        end""",
                    },
                    "untrigger": {}
                },
                "activeTriggerMode": -10,
            },
        }

    # 05 - Trinket 1 (Slot 13)
    auras.append(make_slot_aura("05 - Trinket 1", "FWHUD_UTIL_TRINKET1", 13, "Interface\\Icons\\INV_Jewelry_TrinketPVP_02"))
    # 06 - Trinket 2 (Slot 14)
    auras.append(make_slot_aura("06 - Trinket 2", "FWHUD_UTIL_TRINKET2", 14, "Interface\\Icons\\INV_Jewelry_Necklace_36"))
    # 07 - Cloak (Slot 15)
    auras.append(make_slot_aura("07 - Cloak", "FWHUD_UTIL_CLOAK", 15, "Interface\\Icons\\INV_Misc_Cape_19"))

    # 08 - Death Wish (Spell 12292)
    auras.append({
        "id": "08 - Death Wish",
        "uid": "FWHUD_UTIL_DEATHWISH",
        "parent": "Class Warrior (Fury)",
        "regionType": "icon",
        "internalVersion": 52,
        "width": 28,
        "height": 28,
        "xOffset": 0,
        "yOffset": -45,
        "displayIcon": "Interface\\Icons\\Spell_Shadow_DeathPact",
        "auto": True,
        "color": [1, 1, 1, 1],
        "cooldown": True,
        "cooldownSwipe": True,
        "subRegions": [
            make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11, y_offset=0),
        ],
        "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
        "triggers": {
            1: {
                "trigger": {
                    "type": "spell",
                    "event": "Cooldown Progress (Spell)",
                    "spellName": "12292",
                    "use_spellName": True,
                },
                "untrigger": {}
            },
            "activeTriggerMode": -10,
        },
    })

    # 09 - Gloves (Slot 10)
    auras.append(make_slot_aura("09 - Gloves", "FWHUD_UTIL_GLOVES", 10, "Interface\\Icons\\INV_Gauntlets_26"))

    # 10 - Recklessness (Spell 1719)
    auras.append({
        "id": "10 - Recklessness",
        "uid": "FWHUD_UTIL_RECKLESSNESS",
        "parent": "Class Warrior (Fury)",
        "regionType": "icon",
        "internalVersion": 52,
        "width": 28,
        "height": 28,
        "xOffset": 0,
        "yOffset": -45,
        "displayIcon": "Interface\\Icons\\Ability_CriticalStrike",
        "auto": True,
        "color": [1, 1, 1, 1],
        "cooldown": True,
        "cooldownSwipe": True,
        "subRegions": [
            make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11, y_offset=0),
            make_subtext("%s", justify="RIGHT", anchor_point="INNER_TOPRIGHT", font_size=10, y_offset=-2),
        ],
        "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
        "triggers": {
            1: {
                "trigger": {
                    "type": "spell",
                    "event": "Cooldown Progress (Spell)",
                    "spellName": "1719",
                    "use_spellName": True,
                },
                "untrigger": {}
            },
            "activeTriggerMode": -10,
        },
    })

    # 11 - Shattering Throw (Spell 64382)
    auras.append({
        "id": "11 - Shattering Throw",
        "uid": "FWHUD_UTIL_SHATTERING_THROW",
        "parent": "Class Warrior (Fury)",
        "regionType": "icon",
        "internalVersion": 52,
        "width": 28,
        "height": 28,
        "xOffset": 0,
        "yOffset": -45,
        "displayIcon": "Interface\\Icons\\Ability_Warrior_ShatteringThrow",
        "auto": True,
        "color": [1, 1, 1, 1],
        "cooldown": True,
        "cooldownSwipe": True,
        "subRegions": [
            make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11, y_offset=0),
        ],
        "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
        "triggers": {
            1: {
                "trigger": {
                    "type": "spell",
                    "event": "Cooldown Progress (Spell)",
                    "spellName": "64382",
                    "use_spellName": True,
                },
                "untrigger": {}
            },
            "activeTriggerMode": -10,
        },
    })

    # 12 - Enraged Regeneration (Spell 55694)
    auras.append({
        "id": "12 - Enraged Regeneration",
        "uid": "FWHUD_UTIL_ENRAGED_REGEN",
        "parent": "Class Warrior (Fury)",
        "regionType": "icon",
        "internalVersion": 52,
        "width": 28,
        "height": 28,
        "xOffset": 0,
        "yOffset": -45,
        "displayIcon": "Interface\\Icons\\Ability_Warrior_EnragedRegeneration",
        "auto": True,
        "color": [1, 1, 1, 1],
        "cooldown": True,
        "cooldownSwipe": True,
        "subRegions": [
            make_subtext("%p", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=11, y_offset=0),
        ],
        "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
        "triggers": {
            1: {
                "trigger": {
                    "type": "spell",
                    "event": "Cooldown Progress (Spell)",
                    "spellName": "55694",
                    "use_spellName": True,
                },
                "untrigger": {}
            },
            "activeTriggerMode": -10,
        },
    })

    # 13 - Boots (Slot 8)
    auras.append(make_slot_aura("13 - Boots", "FWHUD_UTIL_BOOTS", 8, "Interface\\Icons\\Ability_Kick"))

    return auras
