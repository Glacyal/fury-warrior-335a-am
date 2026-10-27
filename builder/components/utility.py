"""
Modulo Componente: 05 - Trinkets & 06-13 - Utility Row (Warrior Fury)
======================================================================
Gestisce la riga orizzontale di utilità a y = -45 con riposizionamento dinamico
centrato naturale (da 3 a 9 icone) in base all'equipaggiamento e alle abilità:
1. 05 - Trinket 1 (Slot 13: Deathbringer's Will o altro monile, ICD o On-Use, Glow su proc)
2. 06 - Trinket 2 (Slot 14: Sharpened Twilight Scale o altro monile, ICD o On-Use, Glow su proc)
3. 07 - Cloak (Slot 15: Swordguard Embroidery +400 AP / Paracadute / Flexweave)
4. 08 - Death Wish (Spell ID 12292, durata attiva 30s + cooldown)
5. 09 - Gloves (Slot 10: Acceleratori Ipersonici Ingegneria +340 Haste per 12s, 60s CD)
6. 10 - Recklessness (Spell ID 1719, 3 cariche critico garantite + cooldown)
7. 11 - Shattering Throw (Spell ID 64382, debuff -20% armatura sul boss 10s + cooldown 5m)
8. 12 - Enraged Regeneration (Spell ID 55694, cura 30% HP in 10s + cooldown 3m)
9. 13 - Boots (Slot 8: Acceleratori a Nitro / Nitro Boosts Ingegneria, 180s CD)

Architettura derivata da fire-mage-335a-am: trigger custom status con check update,
customDuration, customIcon e customText con swipe e PixelGlow reattivo.
"""
from builder.core.helpers import make_subtext


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
        [50362] = { keywords = { "taunka", "vrykul", "irondwarf", "deathbringer" }, spellIds = { [71485] = true, [71491] = true, [71487] = true, [71556] = true, [71560] = true, [71558] = true }, icd = 105, dur = 30 },
        [50363] = { keywords = { "taunka", "vrykul", "irondwarf", "deathbringer" }, spellIds = { [71485] = true, [71491] = true, [71487] = true, [71556] = true, [71560] = true, [71558] = true }, icd = 105, dur = 30 },
        -- Sharpened Twilight Scale (Normal & Heroic)
        [54569] = { keywords = { "twilightprecision", "sharpenedtwilight", "twilight" }, spellIds = { [75473] = true, [75474] = true, [75456] = true }, icd = 45, dur = 15 },
        [54590] = { keywords = { "twilightprecision", "sharpenedtwilight", "twilight" }, spellIds = { [75473] = true, [75474] = true, [75456] = true }, icd = 45, dur = 15 },
        -- Death's Choice / Verdict (Normal & Heroic Horde / Alliance)
        [47115] = { keywords = { "paragon" }, spellIds = { [67708] = true, [67703] = true }, icd = 45, dur = 15 },
        [47131] = { keywords = { "paragon" }, spellIds = { [67773] = true, [67772] = true }, icd = 45, dur = 15 },
        [47303] = { keywords = { "paragon" }, spellIds = { [67708] = true, [67703] = true }, icd = 45, dur = 15 },
        [47464] = { keywords = { "paragon" }, spellIds = { [67773] = true, [67772] = true }, icd = 45, dur = 15 },
        -- Whispering Fanged Skull
        [50342] = { keywords = { "whisperingfangedskull" }, spellIds = { [71541] = true, [71540] = true }, icd = 45, dur = 15 },
        [50343] = { keywords = { "whisperingfangedskull" }, spellIds = { [71541] = true, [71540] = true }, icd = 45, dur = 15 },
        -- Darkmoon Card: Greatness (Strength)
        [44253] = { keywords = { "greatness" }, spellIds = { [60229] = true }, icd = 45, dur = 15 },
        [44254] = { keywords = { "greatness" }, spellIds = { [60229] = true }, icd = 45, dur = 15 },
        [44255] = { keywords = { "greatness" }, spellIds = { [60229] = true }, icd = 45, dur = 15 },
        [42987] = { keywords = { "greatness" }, spellIds = { [60229] = true }, icd = 45, dur = 15 },
        -- Mjolnir Runestone
        [45931] = { keywords = { "mjolnirrunestone", "runestone" }, spellIds = { [65019] = true }, icd = 45, dur = 10 },
        -- Grim Toll
        [40256] = { keywords = { "grimtoll" }, spellIds = { [60486] = true }, icd = 45, dur = 10 },
        -- Needle-Encrusted Scorpion
        [50198] = { keywords = { "needleencrusted", "scorpion" }, spellIds = { [71403] = true, [71401] = true }, icd = 45, dur = 10 },
        -- Comet's Trail
        [45609] = { keywords = { "cometstrail" }, spellIds = { [64772] = true }, icd = 45, dur = 10 },
        -- Banner of Victory
        [44914] = { keywords = { "bannerofvictory" }, spellIds = { [67671] = true }, icd = 45, dur = 10 },
        -- Mirror of Truth
        [40684] = { keywords = { "mirroroftruth" }, spellIds = { [60488] = true }, icd = 45, dur = 10 },
        -- Wrathstone (On-Use)
        [45263] = { keywords = { "wrathstone" }, spellIds = { [64765] = true }, icd = 120, dur = 20, onUse = true },
        -- Herkuml War Token
        [50355] = { keywords = { "herkuml" }, spellIds = { [71396] = true }, icd = 0, dur = 10 },
    }

    _G.FWHUD_CloakKeywords = { "swordguard", "spadatesta", "parachute", "flexweave", "flessibile" }
    _G.FWHUD_CloakSpellIds = { [55775] = true, [55767] = true, [54865] = true, [54753] = true }
    _G.FWHUD_CloakEnchantIDs = { [3730] = true, [3605] = true }

    _G.FWHUD_GlovesSpellIds = { [54758] = true }
    _G.FWHUD_GlovesKeywords = { "hyperspeed", "accelerat", "ipersonic", "340 haste" }

    _G.FWHUD_BootsEnchantIDs = { [3601] = true, [3784] = true }
    _G.FWHUD_BootsSpellIds = { [54861] = true, [54858] = true, [55016] = true }
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

        -- Slot 13 & 14 (Trinkets): sempre visibili per default se item presente o in configurazione standard
        if s == 13 or s == 14 then
            local eq = (itemID ~= nil and itemID > 0)
            if not itemID then eq = true end -- fallback di visualizzazione sicura in anteprima
            cache.isEquipped = eq
            return eq
        end

        if not itemID or itemID == 0 then
            cache.isEquipped = true -- fallback sicuro per non nascondere icone chiave
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
        if slot == 8 then
            if itemStart and itemDur and itemDur < 60 then itemStart, itemDur = 0, 0 end
            if not itemStart or itemDur == 0 or itemDur <= 1.5 then
                local sStart, sDur = GetSpellCooldown(54861)
                if sStart and sDur and sDur >= 60 then itemStart, itemDur = sStart, sDur end
            end
        elseif slot == 10 then
            if itemStart and itemDur and itemDur < 45 then itemStart, itemDur = 0, 0 end
            if not itemStart or itemDur == 0 or itemDur <= 1.5 then
                local sStart, sDur = GetSpellCooldown(54758)
                if sStart and sDur and sDur >= 45 then itemStart, itemDur = sStart, sDur end
            end
        end

        local isOnUseCooldown = false
        local remItemCD = 0
        if itemStart and itemDur and itemStart > 0 and itemDur > 1.5 then
            remItemCD = (itemStart + itemDur) - now
            if remItemCD > 0.1 then isOnUseCooldown = true end
        end

        local baseIcon = GetInventoryItemTexture("player", slot)
        if not baseIcon then
            baseIcon = (slot == 13 and "Interface\\Icons\\INV_Misc_Ornament_02") or
                       (slot == 14 and "Interface\\Icons\\INV_Misc_RubySanctum1") or
                       (slot == 15 and "Interface\\Icons\\INV_Misc_Cape_19") or
                       (slot == 10 and "Interface\\Icons\\INV_Gauntlets_26") or
                       (slot == 8  and "Interface\\Icons\\Ability_Kick") or nil
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
                if spellId and (spellId == 54861 or spellId == 54858 or spellId == 55016) then isMatch = true end
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
            return finish("ACTIVE", remBuff, durBuff, buffIcon or baseIcon)
        end

        if icdState.isProc then
            icdState.isProc = false
            if icdState.lastEnd == 0 or icdState.lastEnd > now then
                icdState.lastEnd = now
            end
        end

        if isOnUseCooldown then
            return finish("COOLDOWN", remItemCD, itemDur, baseIcon)
        end

        if icdState.lastStart > 0 and targetICD > 0 then
            local elapsed = now - icdState.lastStart
            if elapsed < targetICD then
                local remICD = targetICD - elapsed
                return finish("ICD", remICD, targetICD, baseIcon)
            end
        end

        return finish("READY", 0, 0, baseIcon)
    end

    -- Monitoraggio unificato per i Cooldown del Guerriero
    _G.FWHUD_CheckWarriorSpell = function(spellId, buffId)
        local now = GetTime()
        local defIcon = select(3, GetSpellInfo(spellId))
        if not defIcon then
            if spellId == 12292 then defIcon = "Interface\\Icons\\Spell_Shadow_DeathPact"
            elseif spellId == 1719 then defIcon = "Interface\\Icons\\Ability_CriticalStrike"
            elseif spellId == 64382 then defIcon = "Interface\\Icons\\Ability_Warrior_ShatteringThrow"
            elseif spellId == 55694 then defIcon = "Interface\\Icons\\Ability_Warrior_EnragedRegeneration"
            end
        end

        -- 1. Verifica buff attivo su player
        if buffId then
            for i = 1, 40 do
                local name, _, icon, count, _, duration, expirationTime, _, _, _, sId = UnitBuff("player", i)
                if not name then break end
                if sId == buffId or (sId == spellId) then
                    local rem = (expirationTime and expirationTime > 0) and (expirationTime - now) or 0
                    local dur = (duration and duration > 0) and duration or 0
                    return "ACTIVE", rem, dur, count or 1, icon or defIcon
                end
            end
        end

        -- Per Shattering Throw: verifica debuff sul bersaglio
        if spellId == 64382 and UnitExists("target") then
            for i = 1, 40 do
                local name, _, icon, count, _, duration, expirationTime, caster, _, _, sId = UnitDebuff("target", i)
                if not name then break end
                if sId == 64382 or name == "Shattering Throw" or name == "Lancio Frantumante" then
                    local rem = (expirationTime and expirationTime > 0) and (expirationTime - now) or 0
                    local dur = (duration and duration > 0) and duration or 10
                    return "ACTIVE", rem, dur, count or 1, icon or defIcon
                end
            end
        end

        -- 2. Verifica tempo di ricarica
        local start, duration = GetSpellCooldown(spellId)
        if start and duration and start > 0 and duration > 1.5 then
            local remCD = (start + duration) - now
            if remCD > 0.1 then
                return "COOLDOWN", remCD, duration, 0, defIcon
            end
        end

        -- 3. Abilità pronta all'uso
        return "READY", 0, 0, 0, defIcon
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
        if N >= 9 then step = 32
        elseif N == 8 then step = 34
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
        f:RegisterEvent("UNIT_INVENTORY_CHANGED")
        f:RegisterEvent("SPELL_UPDATE_COOLDOWN")
        f:RegisterEvent("ACTIONBAR_UPDATE_COOLDOWN")
        f:RegisterEvent("BAG_UPDATE_COOLDOWN")
        f:RegisterEvent("UNIT_AURA")
        f:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
        f:SetScript("OnEvent", function(self, event, ...)
            _G.FWHUD_SlotEquipCache = nil
            _G.FWHUD_SlotCache = nil
            _G.FWHUD_BuffCache = nil
            _G.FWHUD_UpdateUtilityRowPositions(true)
        end)
    end

    _G.FWHUD_CoreInitDone = true
end"""


def make_slot_custom_text(slot: int) -> str:
    """Testo descrittivo del monile/mantello/guanti/scarpe (%c), con pixel glow su proc attivo e timer cooldown."""
    return f"""function()
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if _G.FWHUD_UpdateUtilityRowPositions then
        _G.FWHUD_UpdateUtilityRowPositions()
    end
    if not _G.FWHUD_CheckSlot then return "" end
    local state, rem, dur, icon = _G.FWHUD_CheckSlot({slot})
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)
    local glowKey = "FWHUD_SLOT_{slot}_GLOW"
    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {{1, 0.85, 0.1, 1}}, 8, 0.25, 10, 2, 0, 0, false, glowKey)
        end
        return string.format("|cFFFFFF00%.1fs|r", rem)
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, glowKey)
        end
        if (state == "ICD" or state == "COOLDOWN") and rem > 0.1 then
            if rem >= 60 then
                local m = math.floor(rem / 60)
                local s = math.floor(rem % 60)
                return string.format("%d:%02d", m, s)
            else
                return string.format("%.0f", rem)
            end
        end
        return ""
    end
end"""


def make_slot_custom_duration(slot: int) -> str:
    """Durata e scadenza dello swipe di ricarica per lo slot indicato."""
    return f"""function()
    if not _G.FWHUD_CheckSlot then return 0, 0 end
    local state, rem, dur = _G.FWHUD_CheckSlot({slot})
    if (state == "ACTIVE" or state == "ICD" or state == "COOLDOWN") and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_slot_custom_icon(slot: int, default_icon: str) -> str:
    """Restituisce dinamicamente l'icona dell'oggetto equipaggiato o del proc attivo."""
    return f"""function()
    if _G.FWHUD_CheckSlot then
        local state, rem, dur, icon = _G.FWHUD_CheckSlot({slot})
        if state == "ACTIVE" and icon then
            return icon
        end
        if icon then return icon end
    end
    return GetInventoryItemTexture("player", {slot}) or "{default_icon}"
end"""


def make_slot_trigger_custom(slot: int) -> str:
    """Trigger custom per verificare se lo slot è equipaggiato."""
    return f"""function(event, ...)
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if not _G.FWHUD_CheckSlotEquipped then return false end
    return _G.FWHUD_CheckSlotEquipped({slot})
end"""


def make_slot_untrigger_custom(slot: int) -> str:
    """Untrigger custom quando lo slot non è equipaggiato."""
    return f"""function(event, ...)
    if not _G.FWHUD_CheckSlotEquipped then return true end
    return not _G.FWHUD_CheckSlotEquipped({slot})
end"""


def make_warrior_spell_custom_text(spell_id: int, buff_id: int, glow_key: str) -> str:
    """Testo descrittivo del cooldown guerriero (%c), con pixel glow su proc attivo e timer cooldown."""
    return f"""function()
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if _G.FWHUD_UpdateUtilityRowPositions then
        _G.FWHUD_UpdateUtilityRowPositions()
    end
    if not _G.FWHUD_CheckWarriorSpell then return "" end
    local state, rem, dur, count, icon = _G.FWHUD_CheckWarriorSpell({spell_id}, {buff_id or "nil"})
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)
    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {{1, 0.85, 0.1, 1}}, 8, 0.25, 10, 2, 0, 0, false, "{glow_key}")
        end
        if count and count > 1 then
            return string.format("|cFFFFFF00x%d|r", count)
        elseif rem > 0 then
            return string.format("|cFFFFFF00%.1fs|r", rem)
        end
        return "|cFFFFFF00ON|r"
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, "{glow_key}")
        end
        if state == "COOLDOWN" and rem > 0.1 then
            if rem >= 60 then
                local m = math.floor(rem / 60)
                local s = math.floor(rem % 60)
                return string.format("%d:%02d", m, s)
            else
                return string.format("%.0f", rem)
            end
        end
        return ""
    end
end"""


def make_warrior_spell_custom_duration(spell_id: int, buff_id: int) -> str:
    """Durata e scadenza dello swipe per il cooldown/buff del guerriero."""
    return f"""function()
    if not _G.FWHUD_CheckWarriorSpell then return 0, 0 end
    local state, rem, dur = _G.FWHUD_CheckWarriorSpell({spell_id}, {buff_id or "nil"})
    if (state == "ACTIVE" or state == "COOLDOWN") and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_warrior_spell_custom_icon(spell_id: int, default_icon: str) -> str:
    """Restituisce l'icona dell'abilità guerriero."""
    return f"""function()
    if _G.FWHUD_CheckWarriorSpell then
        local state, rem, dur, count, icon = _G.FWHUD_CheckWarriorSpell({spell_id}, nil)
        if icon then return icon end
    end
    local icon = select(3, GetSpellInfo({spell_id}))
    return icon or "{default_icon}"
end"""


def build_utility_auras() -> list[dict]:
    """
    Costruisce e restituisce le 9 aure della riga utility adattiva centrata a y = -45:
    - 05 - Trinket 1 (Icon, Slot 13)
    - 06 - Trinket 2 (Icon, Slot 14)
    - 07 - Cloak (Icon, Slot 15)
    - 08 - Death Wish (Icon, Spell 12292)
    - 09 - Gloves (Icon, Slot 10)
    - 10 - Recklessness (Icon, Spell 1719)
    - 11 - Shattering Throw (Icon, Spell 64382)
    - 12 - Enraged Regeneration (Icon, Spell 55694)
    - 13 - Boots (Icon, Slot 8)
    """
    events_list = "PLAYER_EQUIPMENT_CHANGED,UNIT_INVENTORY_CHANGED,PLAYER_ENTERING_WORLD,ZONE_CHANGED_NEW_AREA,UNIT_AURA,SPELL_UPDATE_COOLDOWN,ACTIONBAR_UPDATE_COOLDOWN,BAG_UPDATE_COOLDOWN,COMBAT_LOG_EVENT_UNFILTERED"

    return [
        # 05 - Trinket 1 (Slot 13)
        {
            "id": "05 - Trinket 1",
            "uid": "FWHUD_UTIL_TRINKET1",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -140,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\INV_Misc_Ornament_02",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_slot_custom_text(13),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_slot_trigger_custom(13),
                        "customDuration": make_slot_custom_duration(13),
                        "customIcon": make_slot_custom_icon(13, "Interface\\Icons\\INV_Misc_Ornament_02"),
                    },
                    "untrigger": {
                        "custom": make_slot_untrigger_custom(13)
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 06 - Trinket 2 (Slot 14)
        {
            "id": "06 - Trinket 2",
            "uid": "FWHUD_UTIL_TRINKET2",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -105,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\INV_Misc_RubySanctum1",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_slot_custom_text(14),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_slot_trigger_custom(14),
                        "customDuration": make_slot_custom_duration(14),
                        "customIcon": make_slot_custom_icon(14, "Interface\\Icons\\INV_Misc_RubySanctum1"),
                    },
                    "untrigger": {
                        "custom": make_slot_untrigger_custom(14)
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 07 - Cloak (Slot 15)
        {
            "id": "07 - Cloak",
            "uid": "FWHUD_UTIL_CLOAK",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -70,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\INV_Misc_Cape_19",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_slot_custom_text(15),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_slot_trigger_custom(15),
                        "customDuration": make_slot_custom_duration(15),
                        "customIcon": make_slot_custom_icon(15, "Interface\\Icons\\INV_Misc_Cape_19"),
                    },
                    "untrigger": {
                        "custom": make_slot_untrigger_custom(15)
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 08 - Death Wish (Spell 12292)
        {
            "id": "08 - Death Wish",
            "uid": "FWHUD_UTIL_DEATHWISH",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -35,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Spell_Shadow_DeathPact",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_warrior_spell_custom_text(12292, 12292, "FWHUD_DW_GLOW"),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": """function(event, ...)
    return true
end""",
                        "customDuration": make_warrior_spell_custom_duration(12292, 12292),
                        "customIcon": make_warrior_spell_custom_icon(12292, "Interface\\Icons\\Spell_Shadow_DeathPact"),
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    return false
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 09 - Gloves (Slot 10)
        {
            "id": "09 - Gloves",
            "uid": "FWHUD_UTIL_GLOVES",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 0,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\INV_Gauntlets_26",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_slot_custom_text(10),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_slot_trigger_custom(10),
                        "customDuration": make_slot_custom_duration(10),
                        "customIcon": make_slot_custom_icon(10, "Interface\\Icons\\INV_Gauntlets_26"),
                    },
                    "untrigger": {
                        "custom": make_slot_untrigger_custom(10)
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 10 - Recklessness (Spell 1719)
        {
            "id": "10 - Recklessness",
            "uid": "FWHUD_UTIL_RECKLESSNESS",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 35,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Ability_CriticalStrike",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_warrior_spell_custom_text(1719, 1719, "FWHUD_RECK_GLOW"),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": """function(event, ...)
    return true
end""",
                        "customDuration": make_warrior_spell_custom_duration(1719, 1719),
                        "customIcon": make_warrior_spell_custom_icon(1719, "Interface\\Icons\\Ability_CriticalStrike"),
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    return false
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 11 - Shattering Throw (Spell 64382)
        {
            "id": "11 - Shattering Throw",
            "uid": "FWHUD_UTIL_SHATTERING_THROW",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 70,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_ShatteringThrow",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_warrior_spell_custom_text(64382, 64382, "FWHUD_ST_GLOW"),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": """function(event, ...)
    return true
end""",
                        "customDuration": make_warrior_spell_custom_duration(64382, 64382),
                        "customIcon": make_warrior_spell_custom_icon(64382, "Interface\\Icons\\Ability_Warrior_ShatteringThrow"),
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    return false
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 12 - Enraged Regeneration (Spell 55694)
        {
            "id": "12 - Enraged Regeneration",
            "uid": "FWHUD_UTIL_ENRAGED_REGEN",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 105,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_EnragedRegeneration",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_warrior_spell_custom_text(55694, 55694, "FWHUD_ER_GLOW"),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": """function(event, ...)
    return true
end""",
                        "customDuration": make_warrior_spell_custom_duration(55694, 55694),
                        "customIcon": make_warrior_spell_custom_icon(55694, "Interface\\Icons\\Ability_Warrior_EnragedRegeneration"),
                    },
                    "untrigger": {
                        "custom": """function(event, ...)
    return false
end"""
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 13 - Boots (Slot 8)
        {
            "id": "13 - Boots",
            "uid": "FWHUD_UTIL_BOOTS",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 140,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Ability_Kick",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_slot_custom_text(8),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_slot_trigger_custom(8),
                        "customDuration": make_slot_custom_duration(8),
                        "customIcon": make_slot_custom_icon(8, "Interface\\Icons\\Ability_Kick"),
                    },
                    "untrigger": {
                        "custom": make_slot_untrigger_custom(8)
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },
    ]
