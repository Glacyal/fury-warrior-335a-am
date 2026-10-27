"""
Modulo Componente: 05-13 - Utility Row (Warrior Fury)
=====================================================
Gestisce la riga orizzontale di utilità a y = -45 con riposizionamento dinamico
centrato naturale (da 3 a 9 icone) in base all'equipaggiamento e alle abilità:
1. 05 - Trinket 1 (Slot 13: DBW, STS, Death's Choice o altro monile, ICD o On-Use, Pixel Glow su proc)
2. 06 - Trinket 2 (Slot 14: STS, DBW, Whispering Fanged Skull o altro monile, ICD/On-Use, Pixel Glow)
3. 07 - Cloak (Slot 15: Swordguard Embroidery +400 AP / Paracadute / Flexweave)
4. 08 - Tier Set (Slot Set: T10 Siegebreaker/Advantage, T8 Crit/Haste, T7 AP, T9 Passive)
5. 09 - Enchants (Slot 16/17: Berserking MH/OH x1/x2 +800 AP, Executioner, Mongoose, Ashen Band)
6. 10 - Gloves (Slot 10: Acceleratori Ipersonici Ingegneria +340 Haste per 12s, 60s CD)
7. 11 - Death Wish (Spell ID 12292, durata attiva 30s + cooldown)
8. 12 - Recklessness (Spell ID 1719, 3 cariche critico garantite + cooldown)
9. 13 - Boots (Slot 8: Acceleratori a Nitro / Nitro Boosts Ingegneria, 180s CD)

Architettura solida: bootstrap centrale idempotente iniettato in tutti i trigger e customText,
check update con swipe, customDuration, customIcon e customText con PixelGlow reattivo.
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
        -- Deathbringer's Will (Normal 50362, Heroic 50363)
        [50362] = { keywords = { "taunka", "vrykul", "irondwarf", "deathbringer" }, spellIds = { [71485] = true, [71491] = true, [71487] = true, [71556] = true, [71560] = true, [71558] = true }, icd = 105, dur = 30 },
        [50363] = { keywords = { "taunka", "vrykul", "irondwarf", "deathbringer" }, spellIds = { [71485] = true, [71491] = true, [71487] = true, [71556] = true, [71560] = true, [71558] = true }, icd = 105, dur = 30 },
        -- Sharpened Twilight Scale (Normal 54569, Heroic 54590)
        [54569] = { keywords = { "twilightprecision", "sharpenedtwilight", "twilight" }, spellIds = { [75473] = true, [75474] = true, [75456] = true }, icd = 45, dur = 15 },
        [54590] = { keywords = { "twilightprecision", "sharpenedtwilight", "twilight" }, spellIds = { [75473] = true, [75474] = true, [75456] = true }, icd = 45, dur = 15 },
        -- Death's Choice / Verdict (Normal Alliance 47115, Normal Horde 47131, Heroic Alliance 47303, Heroic Horde 47464)
        [47115] = { keywords = { "paragon" }, spellIds = { [67708] = true, [67703] = true }, icd = 45, dur = 15 },
        [47131] = { keywords = { "paragon" }, spellIds = { [67773] = true, [67772] = true }, icd = 45, dur = 15 },
        [47303] = { keywords = { "paragon" }, spellIds = { [67708] = true, [67703] = true }, icd = 45, dur = 15 },
        [47464] = { keywords = { "paragon" }, spellIds = { [67773] = true, [67772] = true }, icd = 45, dur = 15 },
        -- Whispering Fanged Skull (Normal 50342, Heroic 50343)
        [50342] = { keywords = { "whisperingfangedskull" }, spellIds = { [71541] = true, [71540] = true }, icd = 45, dur = 15 },
        [50343] = { keywords = { "whisperingfangedskull" }, spellIds = { [71541] = true, [71540] = true }, icd = 45, dur = 15 },
        -- Herkuml War Token (50355) - Stacking AP
        [50355] = { keywords = { "herkuml" }, spellIds = { [71396] = true }, icd = 0, dur = 10 },
        -- Needle-Encrusted Scorpion (50198)
        [50198] = { keywords = { "needleencrusted", "scorpion" }, spellIds = { [71403] = true, [71401] = true }, icd = 45, dur = 10 },
        -- Mjolnir Runestone (45931, 45866)
        [45931] = { keywords = { "mjolnirrunestone", "runestone" }, spellIds = { [65019] = true, [65014] = true }, icd = 45, dur = 10 },
        [45866] = { keywords = { "mjolnirrunestone", "runestone" }, spellIds = { [65019] = true, [65014] = true }, icd = 45, dur = 10 },
        -- Comet's Trail (45609)
        [45609] = { keywords = { "cometstrail" }, spellIds = { [64772] = true }, icd = 45, dur = 10 },
        -- Darkmoon Card: Greatness (44253, 44254, 44255, 42987)
        [44253] = { keywords = { "greatness" }, spellIds = { [60229] = true, [60233] = true }, icd = 45, dur = 15 },
        [44254] = { keywords = { "greatness" }, spellIds = { [60229] = true, [60233] = true }, icd = 45, dur = 15 },
        [44255] = { keywords = { "greatness" }, spellIds = { [60229] = true, [60233] = true }, icd = 45, dur = 15 },
        [42987] = { keywords = { "greatness" }, spellIds = { [60229] = true, [60233] = true }, icd = 45, dur = 15 },
        -- Grim Toll (40256)
        [40256] = { keywords = { "grimtoll" }, spellIds = { [60486] = true, [60485] = true }, icd = 45, dur = 10 },
        -- Mirror of Truth (40684)
        [40684] = { keywords = { "mirroroftruth" }, spellIds = { [60488] = true }, icd = 45, dur = 10 },
        -- Banner of Victory (44914)
        [44914] = { keywords = { "bannerofvictory" }, spellIds = { [67671] = true }, icd = 45, dur = 10 },
        -- Meteorite Whetstone (37390)
        [37390] = { keywords = { "meteorite" }, spellIds = { [60305] = true }, icd = 45, dur = 10 },
        -- Vestige of Haldor (37220)
        [37220] = { keywords = { "haldor" }, spellIds = { [60302] = true }, icd = 45, dur = 10 },
        -- Wrathstone (45263) - On-Use
        [45263] = { keywords = { "wrathstone" }, spellIds = { [64765] = true }, icd = 120, dur = 20, onUse = true },
        -- Mark of Supremacy (47734) - On-Use
        [47734] = { keywords = { "markofsupremacy" }, spellIds = { [67708] = true, [67706] = true }, icd = 120, dur = 20, onUse = true },
        -- Incisor Fragment (37723) - On-Use
        [37723] = { keywords = { "incisor" }, spellIds = { [60298] = true }, icd = 120, dur = 20, onUse = true },
        -- Loatheb's Shadow (39257) - On-Use
        [39257] = { keywords = { "loatheb" }, spellIds = { [60314] = true }, icd = 120, dur = 20, onUse = true },
        -- Sphere of Red Dragon's Blood (37111) - On-Use
        [37111] = { keywords = { "reddragonsblood" }, spellIds = { [60290] = true }, icd = 120, dur = 20, onUse = true },
        -- Feast of the Greatfather (44431)
        [44431] = { keywords = { "greatfather" }, spellIds = { [60490] = true }, icd = 45, dur = 15 },
        -- Blood of the Old God (45522)
        [45522] = { keywords = { "bloodoftheoldgod" }, spellIds = { [64790] = true }, icd = 45, dur = 10 },
        -- Pyrite Infuser (45286)
        [45286] = { keywords = { "pyriteinfuser" }, spellIds = { [65012] = true }, icd = 45, dur = 10 },
        -- Tears of the Vanquished (47215)
        [47215] = { keywords = { "revitalized" }, spellIds = { [67700] = true }, icd = 45, dur = 0 },
        -- PvP Medallions & Battlemaster's
        [42122] = { keywords = { "medallion" }, icd = 120, dur = 0, onUse = true },
        [42123] = { keywords = { "medallion" }, icd = 120, dur = 0, onUse = true },
        [51377] = { keywords = { "medallion" }, icd = 120, dur = 0, onUse = true },
        [51378] = { keywords = { "medallion" }, icd = 120, dur = 0, onUse = true },
        [42133] = { keywords = { "battlemaster" }, spellIds = { [59754] = true }, icd = 120, dur = 15, onUse = true },
        [44063] = { keywords = { "battlemaster" }, spellIds = { [59754] = true }, icd = 120, dur = 15, onUse = true },
        [50356] = { keywords = { "battlemaster" }, spellIds = { [59754] = true }, icd = 120, dur = 15, onUse = true },
    }

    _G.FWHUD_CloakKeywords = { "swordguard", "spadatesta", "parachute", "flexweave", "flessibile" }
    _G.FWHUD_CloakSpellIds = { [55775] = true, [55767] = true, [54865] = true, [54753] = true }
    _G.FWHUD_CloakEnchantIDs = { [3730] = true, [3605] = true }

    _G.FWHUD_GlovesSpellIds = { [54758] = true }
    _G.FWHUD_GlovesKeywords = { "hyperspeed", "accelerat", "ipersonic", "340 haste" }

    _G.FWHUD_BootsEnchantIDs = { [3601] = true, [3784] = true, [3232] = true, [983] = true }
    _G.FWHUD_BootsSpellIds = { [54861] = true, [54858] = true, [55016] = true }
    _G.FWHUD_BootsKeywords = { "nitro", "boosts", "acceleratori a nitro", "swiftness", "tuskarr" }

    -- Tier 10: Ymirjar Lord's Battlegear (277, 264, 251)
    _G.FWHUD_T10_Pieces = {
        [51225]=true,[51226]=true,[51227]=true,[51228]=true,[51229]=true,
        [50115]=true,[50116]=true,[50117]=true,[50118]=true,[50119]=true,
        [50849]=true,[50850]=true,[50851]=true,[50852]=true,[50853]=true
    }
    -- Tier 8: Siegebreaker Battlegear (232, 225)
    _G.FWHUD_T8_Pieces = {
        [46146]=true,[46147]=true,[46148]=true,[46149]=true,[46150]=true,
        [45318]=true,[45319]=true,[45320]=true,[45321]=true,[45322]=true
    }
    -- Tier 7: Dreadnaught Battlegear (213, 200)
    _G.FWHUD_T7_Pieces = {
        [40525]=true,[40527]=true,[40528]=true,[40529]=true,[40530]=true,
        [39597]=true,[39599]=true,[39601]=true,[39602]=true,[39603]=true
    }
    -- Tier 9: Hellscream's / Wrynn's Battlegear (258, 245, 232)
    _G.FWHUD_T9_Pieces = {
        [48328]=true,[48329]=true,[48330]=true,[48331]=true,[48332]=true,
        [48338]=true,[48339]=true,[48340]=true,[48341]=true,[48342]=true,
        [48386]=true,[48387]=true,[48388]=true,[48389]=true,[48390]=true,
        [48381]=true,[48382]=true,[48383]=true,[48384]=true,[48385]=true,
        [48426]=true,[48427]=true,[48428]=true,[48429]=true,[48430]=true,
        [48431]=true,[48432]=true,[48433]=true,[48434]=true,[48435]=true
    }

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

        -- Slot 13 & 14 (Trinkets): visible only if an item is equipped
        if s == 13 or s == 14 then
            local eq = (itemID ~= nil and itemID > 0)
            if itemID == nil then eq = true end
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

        local function scanTT(keywords)
            local tt = _G.FWHUD_ScanTT
            if not tt then
                tt = CreateFrame("GameTooltip", "FWHUD_ScanTT", UIParent, "GameTooltipTemplate")
                tt:SetOwner(UIParent, "ANCHOR_NONE")
                _G.FWHUD_ScanTT = tt
            end
            tt:ClearLines()
            tt:SetInventoryItem("player", s)
            for j = 1, tt:NumLines() do
                local line = _G["FWHUD_ScanTTTextLeft"..j]
                local text = line and line:GetText()
                if text then
                    local lt = text:lower()
                    local ltClean = lt:gsub("[%s%p%c]", "")
                    for _, kw in ipairs(keywords) do
                        local kwClean = kw:lower():gsub("[%s%p%c]", "")
                        if lt:find(kw, 1, true) or ltClean:find(kwClean, 1, true) then
                            return true
                        end
                    end
                end
            end
            return false
        end

        -- Slot 10 (Gloves): Hyperspeed Accelerators
        if s == 10 then
            local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
            if buffs and buffs.bySpellId[54758] then
                cache.isEquipped = true
                return true
            end
            if enchantID == 3604 then
                cache.isEquipped = true
                return true
            end
            if scanTT(_G.FWHUD_GlovesKeywords) then
                cache.isEquipped = true
                return true
            end
            cache.isEquipped = false
            return false
        end

        -- Slot 8 (Boots): Nitro Boosts / Speed
        if s == 8 then
            local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
            if buffs and (buffs.bySpellId[54861] or buffs.bySpellId[54858] or buffs.bySpellId[55016]) then
                cache.isEquipped = true
                return true
            end
            if enchantID and _G.FWHUD_BootsEnchantIDs[enchantID] then
                cache.isEquipped = true
                return true
            end
            if scanTT(_G.FWHUD_BootsKeywords) then
                cache.isEquipped = true
                return true
            end
            cache.isEquipped = false
            return false
        end

        -- Slot 15 (Cloak): Swordguard / Parachute / Flexweave
        if s == 15 then
            local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
            if buffs then
                for id, _ in pairs(_G.FWHUD_CloakSpellIds) do
                    if buffs.bySpellId[id] then
                        cache.isEquipped = true
                        return true
                    end
                end
            end
            if enchantID and _G.FWHUD_CloakEnchantIDs[enchantID] then
                cache.isEquipped = true
                return true
            end
            if scanTT(_G.FWHUD_CloakKeywords) then
                cache.isEquipped = true
                return true
            end
            cache.isEquipped = false
            return false
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
                if not sStart or sDur == 0 or sDur < 60 then sStart, sDur = GetSpellCooldown(54858) end
                if not sStart or sDur == 0 or sDur < 60 then sStart, sDur = GetSpellCooldown(55016) end
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
        local buffList = buffs and buffs.list or {}

        for _, b in ipairs(buffList) do
            local isMatch = false
            if slot == 15 then
                if b.spellId and _G.FWHUD_CloakSpellIds and _G.FWHUD_CloakSpellIds[b.spellId] then
                    isMatch = true
                end
            elseif slot == 10 then
                if b.spellId and _G.FWHUD_GlovesSpellIds and _G.FWHUD_GlovesSpellIds[b.spellId] then
                    isMatch = true
                end
            elseif slot == 8 then
                if b.spellId and (b.spellId == 54861 or b.spellId == 54858 or b.spellId == 55016) then
                    isMatch = true
                end
            else
                if entry and b.spellId and entry.spellIds and entry.spellIds[b.spellId] then
                    isMatch = true
                end
            end

            if isMatch then
                durBuff = (b.duration and b.duration > 0) and b.duration or defaultDur
                remBuff = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or durBuff
                if remBuff > 0.05 then
                    foundBuff = true
                    buffIcon = b.icon
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

    -- =========================================================================
    -- GESTIONE TIER SETS WARRIOR DPS (T10, T8, T7, T9)
    -- =========================================================================
    _G.FWHUD_CheckTierSetEquipped = function()
        local now = GetTime()
        local cache = _G.FWHUD_TierEquipCache
        if cache and (now - cache.time < 0.25) then return cache.hasSet end
        if not cache then cache = { time = 0, hasSet = false, setType = nil, count = 0 }; _G.FWHUD_TierEquipCache = cache end
        cache.time = now

        local slots = { 1, 3, 5, 7, 10 }
        local t10, t8, t7, t9 = 0, 0, 0, 0
        for _, s in ipairs(slots) do
            local id = GetInventoryItemID("player", s)
            if id then
                if _G.FWHUD_T10_Pieces[id] then t10 = t10 + 1
                elseif _G.FWHUD_T8_Pieces[id] then t8 = t8 + 1
                elseif _G.FWHUD_T7_Pieces[id] then t7 = t7 + 1
                elseif _G.FWHUD_T9_Pieces[id] then t9 = t9 + 1
                end
            end
        end
        if t10 >= 2 then
            cache.hasSet = true; cache.setType = "T10"; cache.count = t10
        elseif t8 >= 2 then
            cache.hasSet = true; cache.setType = "T8"; cache.count = t8
        elseif t7 >= 4 then
            cache.hasSet = true; cache.setType = "T7"; cache.count = t7
        elseif t9 >= 2 then
            cache.hasSet = true; cache.setType = "T9"; cache.count = t9
        else
            local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
            if buffs then
                if buffs.bySpellId[70845] or buffs.bySpellId[70844] or buffs.bySpellId[70846] or buffs.bySpellId[70848] then
                    cache.hasSet = true; cache.setType = "T10"; cache.count = 4; return true
                elseif buffs.bySpellId[64937] or buffs.bySpellId[64942] then
                    cache.hasSet = true; cache.setType = "T8"; cache.count = 4; return true
                elseif buffs.bySpellId[60578] then
                    cache.hasSet = true; cache.setType = "T7"; cache.count = 4; return true
                end
            end
            cache.hasSet = false; cache.setType = nil; cache.count = 0
        end
        return cache.hasSet
    end

    _G.FWHUD_CheckTierSet = function()
        local hasSet = _G.FWHUD_CheckTierSetEquipped()
        if not hasSet then
            return "NONE", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_Siegebreaker"
        end
        local now = GetTime()
        local cache = _G.FWHUD_TierEquipCache
        local setType = cache and cache.setType or "T10"
        local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
        local bList = buffs and buffs.list or {}

        if setType == "T10" then
            local defIcon = "Interface\\Icons\\Ability_Warrior_Siegebreaker"
            for _, b in ipairs(bList) do
                if b.spellId == 70846 or b.spellId == 70848 or (b.name and (b.name:find("Siegebreaker") or b.name:find("Spezzassedio"))) then
                    local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 10
                    local dur = (b.duration and b.duration > 0) and b.duration or 10
                    return "ACTIVE", rem, dur, b.count or 2, b.icon or defIcon, "T10-4P"
                end
            end
            for _, b in ipairs(bList) do
                if b.spellId == 70845 or b.spellId == 70844 or (b.name and (b.name:find("Advantage") or b.name:find("Vantaggio") or b.name:find("T10 2P"))) then
                    local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 10
                    local dur = (b.duration and b.duration > 0) and b.duration or 10
                    return "ACTIVE", rem, dur, 1, b.icon or "Interface\\Icons\\Ability_Warrior_Riposte", "T10-2P"
                end
            end
            return "READY", 0, 0, 0, defIcon, "T10"
        elseif setType == "T8" then
            local defIcon = "Interface\\Icons\\Spell_Nature_BloodLust"
            for _, b in ipairs(bList) do
                if b.spellId == 64942 or (b.name and (b.name:find("T8 4P") or b.name:find("Siegebreaker"))) then
                    local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 5
                    local dur = (b.duration and b.duration > 0) and b.duration or 5
                    return "ACTIVE", rem, dur, 1, b.icon or defIcon, "T8-4P"
                end
            end
            for _, b in ipairs(bList) do
                if b.spellId == 64937 or (b.name and (b.name:find("T8 2P"))) then
                    local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 5
                    local dur = (b.duration and b.duration > 0) and b.duration or 5
                    return "ACTIVE", rem, dur, 1, b.icon or "Interface\\Icons\\Ability_CriticalStrike", "T8-2P"
                end
            end
            return "READY", 0, 0, 0, defIcon, "T8"
        elseif setType == "T7" then
            local defIcon = "Interface\\Icons\\INV_Helmet_23"
            for _, b in ipairs(bList) do
                if b.spellId == 60578 or (b.name and (b.name:find("Dreadnaught") or b.name:find("T7 4P"))) then
                    local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 10
                    local dur = (b.duration and b.duration > 0) and b.duration or 10
                    return "ACTIVE", rem, dur, 1, b.icon or defIcon, "T7-4P"
                end
            end
            return "READY", 0, 0, 0, defIcon, "T7"
        elseif setType == "T9" then
            return "READY", 0, 0, 0, "Interface\\Icons\\INV_Helmet_05", "T9"
        end
        return "READY", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_Siegebreaker", "T10"
    end

    -- =========================================================================
    -- GESTIONE INCANTI ARMA (BERSERKING MH/OH, EXECUTIONER, MONGOOSE) & ANELLO
    -- =========================================================================
    _G.FWHUD_CheckEnchantsEquipped = function()
        local now = GetTime()
        local cache = _G.FWHUD_EnchantEquipCache
        if cache and (now - cache.time < 0.25) then return cache.hasEnchant end
        if not cache then cache = { time = 0, hasEnchant = false }; _G.FWHUD_EnchantEquipCache = cache end
        cache.time = now

        local mh = GetInventoryItemID("player", 16)
        local oh = GetInventoryItemID("player", 17)
        if mh or oh then
            cache.hasEnchant = true
            return true
        end
        cache.hasEnchant = false
        return false
    end

    _G.FWHUD_CheckEnchants = function()
        local now = GetTime()
        local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
        local bList = buffs and buffs.list or {}
        local defIcon = "Interface\\Icons\\Spell_Nature_BloodLust"

        -- 1. Berserking (Spell 59620 - MH e/o OH)
        local berserkCount = 0
        local berserkRem = 0
        local berserkDur = 15
        local berserkIcon = nil
        for _, b in ipairs(bList) do
            if b.spellId == 59620 or (b.name and (b.name == "Berserking" or b.name == "Furia Berserker")) then
                berserkCount = berserkCount + (b.count and b.count > 0 and b.count or 1)
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 15
                if rem > berserkRem then
                    berserkRem = rem
                    berserkDur = (b.duration and b.duration > 0) and b.duration or 15
                end
                berserkIcon = b.icon or defIcon
            end
        end
        if berserkCount > 0 then
            return "ACTIVE", berserkRem, berserkDur, berserkCount, berserkIcon or defIcon, "Berserking"
        end

        -- 2. Executioner (Spell 42976)
        for _, b in ipairs(bList) do
            if b.spellId == 42976 or (b.name and (b.name == "Executioner" or b.name == "Carnefice")) then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 15
                local dur = (b.duration and b.duration > 0) and b.duration or 15
                return "ACTIVE", rem, dur, 1, b.icon or "Interface\\Icons\\INV_Sword_48", "Executioner"
            end
        end

        -- 3. Mongoose (Spell 28093)
        for _, b in ipairs(bList) do
            if b.spellId == 28093 or (b.name and (b.name == "Lightning Speed" or b.name == "Velocità Fulminea" or b.name:find("Mongoose"))) then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 15
                local dur = (b.duration and b.duration > 0) and b.duration or 15
                return "ACTIVE", rem, dur, 1, b.icon or "Interface\\Icons\\Spell_Nature_PosisonSpike", "Mongoose"
            end
        end

        -- 4. Ashen Band of Endless Might (Spell 72412, 72414, 72416)
        for _, b in ipairs(bList) do
            if b.spellId == 72412 or b.spellId == 72414 or b.spellId == 72416 or (b.name and (b.name:find("Peerless") or b.name:find("Endless Might"))) then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 10
                local dur = (b.duration and b.duration > 0) and b.duration or 10
                return "ACTIVE", rem, dur, 1, b.icon or "Interface\\Icons\\INV_Jewelry_Ring_81", "Ashen Band"
            end
        end

        return "READY", 0, 0, 0, defIcon, "Enchants"
    end

    -- =========================================================================
    -- MONITORAGGIO ABILITÀ E COOLDOWN GUERRIERO
    -- =========================================================================
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

        local start, duration = GetSpellCooldown(spellId)
        if start and duration and start > 0 and duration > 1.5 then
            local remCD = (start + duration) - now
            if remCD > 0.1 then
                return "COOLDOWN", remCD, duration, 0, defIcon
            end
        end

        return "READY", 0, 0, 0, defIcon
    end

    -- =========================================================================
    -- RIPOSIZIONAMENTO DINAMICO NATURALE (CENTRATURA DINAMICA 1-11 ICONE)
    -- =========================================================================
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
        local hasTier = _G.FWHUD_CheckTierSetEquipped and _G.FWHUD_CheckTierSetEquipped()
        local hasEnchants = _G.FWHUD_CheckEnchantsEquipped and _G.FWHUD_CheckEnchantsEquipped()
        local hasGloves = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped(10)
        local hasBoots = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped(8)

        local activeOrder = {}
        if hasT1 then table.insert(activeOrder, "05 - Trinket 1") end
        if hasT2 then table.insert(activeOrder, "06 - Trinket 2") end
        if hasCloak then table.insert(activeOrder, "07 - Cloak") end
        if hasTier then table.insert(activeOrder, "08 - Tier Set") end
        if hasEnchants then table.insert(activeOrder, "09 - Enchants") end
        if hasGloves then table.insert(activeOrder, "10 - Gloves") end
        table.insert(activeOrder, "11 - Death Wish")
        table.insert(activeOrder, "12 - Recklessness")
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

    -- Frame reattivo unificato per aggiornamenti equipaggiamento, cooldown e buff
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
        f.pendingUpdates = 0

        local playerGUID = nil
        f:SetScript("OnEvent", function(self, event, ...)
            if event == "COMBAT_LOG_EVENT_UNFILTERED" then
                local _, subEvent, _, sourceGUID, _, _, _, _, _, _, _, spellId, spellName = ...
                if not playerGUID then playerGUID = UnitGUID("player") end
                if sourceGUID == playerGUID then
                    if subEvent == "SPELL_CAST_SUCCESS" or subEvent == "SPELL_AURA_APPLIED" then
                        local now = GetTime()
                        if spellId == 54861 or spellId == 54858 or spellId == 55016 or spellName == "Nitro Boosts" or spellName == "Acceleratori a Nitro" then
                            _G.FWHUD_ICD[8].lastStart = now
                            _G.FWHUD_ICD[8].lastEnd = now + 180
                            _G.FWHUD_ICD[8].isProc = true
                            if WeakAuras and WeakAuras.ScanEvents then WeakAuras.ScanEvents("FWHUD_ROW_UPDATE") end
                        elseif spellId == 54758 or spellName == "Hyperspeed Acceleration" or spellName == "Acceleratori Ipersonici" then
                            _G.FWHUD_ICD[10].lastStart = now
                            _G.FWHUD_ICD[10].lastEnd = now + 60
                            _G.FWHUD_ICD[10].isProc = true
                            if WeakAuras and WeakAuras.ScanEvents then WeakAuras.ScanEvents("FWHUD_ROW_UPDATE") end
                        end
                    end
                end
                return
            end
            if event == "UNIT_AURA" then
                local unit = ...
                if unit ~= "player" then return end
            end
            _G.FWHUD_BuffCache = nil
            _G.FWHUD_SlotEquipCache = nil
            _G.FWHUD_TierEquipCache = nil
            _G.FWHUD_EnchantEquipCache = nil
            if WeakAuras and WeakAuras.ScanEvents then
                WeakAuras.ScanEvents("FWHUD_ROW_UPDATE")
            end
            _G.FWHUD_UpdateUtilityRowPositions(true)
            self.pendingUpdates = 5
            self:SetScript("OnUpdate", function(sf, el)
                if sf.pendingUpdates and sf.pendingUpdates > 0 then
                    sf.pendingUpdates = sf.pendingUpdates - 1
                    _G.FWHUD_UpdateUtilityRowPositions(true)
                else
                    sf:SetScript("OnUpdate", nil)
                end
            end)
        end)
    end

    _G.FWHUD_CoreInitDone = true
end"""


# =============================================================================
# HELPER PYTHON PER TRIGGER, CUSTOM TEXT, DURATION, ICON
# =============================================================================
def make_slot_custom_text(slot: int) -> str:
    """Testo descrittivo del monile/mantello/guanti/scarpe (%c), con pixel glow su proc attivo e riposizionamento dinamico."""
    return f"""function()
    _G.FWHUD_InitCore = _G.FWHUD_InitCore or {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}
    if not _G.FWHUD_CoreInitDone then _G.FWHUD_InitCore() end
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
    _G.FWHUD_InitCore = _G.FWHUD_InitCore or {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}
    if not _G.FWHUD_CoreInitDone then _G.FWHUD_InitCore() end
    if not _G.FWHUD_CheckSlotEquipped then return false end
    return _G.FWHUD_CheckSlotEquipped({slot})
end"""


def make_slot_untrigger_custom(slot: int) -> str:
    """Untrigger custom quando lo slot non è equipaggiato."""
    return f"""function(event, ...)
    if not _G.FWHUD_CheckSlotEquipped then return true end
    return not _G.FWHUD_CheckSlotEquipped({slot})
end"""


def make_tierset_custom_text() -> str:
    """Testo descrittivo del Tier Set (%c) con cariche/durata e pixel glow su proc."""
    return f"""function()
    _G.FWHUD_InitCore = _G.FWHUD_InitCore or {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}
    if not _G.FWHUD_CoreInitDone then _G.FWHUD_InitCore() end
    if _G.FWHUD_UpdateUtilityRowPositions then
        _G.FWHUD_UpdateUtilityRowPositions()
    end
    if not _G.FWHUD_CheckTierSet then return "" end
    local state, rem, dur, count, icon, subType = _G.FWHUD_CheckTierSet()
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)
    local glowKey = "FWHUD_TIER_GLOW"
    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {{1, 0.85, 0.1, 1}}, 8, 0.25, 10, 2, 0, 0, false, glowKey)
        end
        if count and count > 1 then
            return string.format("|cFFFFFF00x%d %.1fs|r", count, rem)
        elseif rem > 0 then
            return string.format("|cFFFFFF00%.1fs|r", rem)
        end
        return "|cFFFFFF00ON|r"
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, glowKey)
        end
        if state == "ICD" and rem > 0.1 then
            return string.format("%.0f", rem)
        end
        return ""
    end
end"""


def make_tierset_custom_duration() -> str:
    """Durata e scadenza dello swipe per il Tier Set."""
    return """function()
    if not _G.FWHUD_CheckTierSet then return 0, 0 end
    local state, rem, dur = _G.FWHUD_CheckTierSet()
    if (state == "ACTIVE" or state == "ICD") and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_tierset_custom_icon() -> str:
    """Restituisce l'icona del bonus Tier Set attivo o base."""
    return """function()
    if _G.FWHUD_CheckTierSet then
        local state, rem, dur, count, icon = _G.FWHUD_CheckTierSet()
        if icon then return icon end
    end
    return "Interface\\Icons\\Ability_Warrior_Siegebreaker"
end"""


def make_tierset_trigger_custom() -> str:
    """Trigger custom per verificare se almeno un pezzo Tier Set è attivo."""
    return f"""function(event, ...)
    _G.FWHUD_InitCore = _G.FWHUD_InitCore or {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}
    if not _G.FWHUD_CoreInitDone then _G.FWHUD_InitCore() end
    if not _G.FWHUD_CheckTierSetEquipped then return false end
    return _G.FWHUD_CheckTierSetEquipped()
end"""


def make_tierset_untrigger_custom() -> str:
    return """function(event, ...)
    if not _G.FWHUD_CheckTierSetEquipped then return true end
    return not _G.FWHUD_CheckTierSetEquipped()
end"""


def make_enchants_custom_text() -> str:
    """Testo descrittivo incanti arma/anello (%c) con cariche (x2 per Berserking MH+OH) e pixel glow."""
    return f"""function()
    _G.FWHUD_InitCore = _G.FWHUD_InitCore or {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}
    if not _G.FWHUD_CoreInitDone then _G.FWHUD_InitCore() end
    if _G.FWHUD_UpdateUtilityRowPositions then
        _G.FWHUD_UpdateUtilityRowPositions()
    end
    if not _G.FWHUD_CheckEnchants then return "" end
    local state, rem, dur, count, icon, enchName = _G.FWHUD_CheckEnchants()
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)
    local glowKey = "FWHUD_ENCHANT_GLOW"
    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {{1, 0.85, 0.1, 1}}, 8, 0.25, 10, 2, 0, 0, false, glowKey)
        end
        if count and count > 1 then
            return string.format("|cFFFFFF00x%d %.1fs|r", count, rem)
        elseif rem > 0 then
            return string.format("|cFFFFFF00%.1fs|r", rem)
        end
        return "|cFFFFFF00ON|r"
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, glowKey)
        end
        return ""
    end
end"""


def make_enchants_custom_duration() -> str:
    return """function()
    if not _G.FWHUD_CheckEnchants then return 0, 0 end
    local state, rem, dur = _G.FWHUD_CheckEnchants()
    if state == "ACTIVE" and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_enchants_custom_icon() -> str:
    return """function()
    if _G.FWHUD_CheckEnchants then
        local state, rem, dur, count, icon = _G.FWHUD_CheckEnchants()
        if icon then return icon end
    end
    return "Interface\\Icons\\Spell_Nature_BloodLust"
end"""


def make_enchants_trigger_custom() -> str:
    return f"""function(event, ...)
    _G.FWHUD_InitCore = _G.FWHUD_InitCore or {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}
    if not _G.FWHUD_CoreInitDone then _G.FWHUD_InitCore() end
    if not _G.FWHUD_CheckEnchantsEquipped then return false end
    return _G.FWHUD_CheckEnchantsEquipped()
end"""


def make_enchants_untrigger_custom() -> str:
    return """function(event, ...)
    if not _G.FWHUD_CheckEnchantsEquipped then return true end
    return not _G.FWHUD_CheckEnchantsEquipped()
end"""


def make_warrior_spell_custom_text(spell_id: int, buff_id: int, glow_key: str) -> str:
    """Testo descrittivo del cooldown guerriero (%c), con pixel glow su proc attivo e timer cooldown."""
    return f"""function()
    _G.FWHUD_InitCore = _G.FWHUD_InitCore or {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}
    if not _G.FWHUD_CoreInitDone then _G.FWHUD_InitCore() end
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


def make_warrior_spell_trigger_custom(spell_id: int) -> str:
    return f"""function(event, ...)
    _G.FWHUD_InitCore = _G.FWHUD_InitCore or {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}
    if not _G.FWHUD_CoreInitDone then _G.FWHUD_InitCore() end
    return true
end"""


def build_utility_auras() -> list[dict]:
    """
    Costruisce e restituisce le 11 aure della riga utility adattiva centrata a y = -45:
    - 05 - Trinket 1 (Icon, Slot 13)
    - 06 - Trinket 2 (Icon, Slot 14)
    - 07 - Cloak (Icon, Slot 15)
    - 08 - Tier Set (Icon, T10/T8/T7 Proc & ICD)
    - 09 - Enchants (Icon, Berserking MH/OH x1/x2, Executioner, Mongoose, Ashen Band)
    - 10 - Gloves (Icon, Slot 10)
    - 11 - Death Wish (Icon, Spell 12292)
    - 12 - Recklessness (Icon, Spell 1719)
    - 13 - Boots (Icon, Slot 8)
    """
    events_list = "PLAYER_EQUIPMENT_CHANGED,UNIT_INVENTORY_CHANGED,PLAYER_ENTERING_WORLD,ZONE_CHANGED_NEW_AREA,UNIT_AURA,SPELL_UPDATE_COOLDOWN,ACTIONBAR_UPDATE_COOLDOWN,BAG_UPDATE_COOLDOWN,COMBAT_LOG_EVENT_UNFILTERED,FWHUD_ROW_UPDATE"

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
            "xOffset": -112,
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
            "xOffset": -84,
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

        # 08 - Tier Set (T10/T8/T7 Proc & ICD)
        {
            "id": "08 - Tier Set",
            "uid": "FWHUD_UTIL_TIERSET",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -56,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Ability_Warrior_Siegebreaker",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_tierset_custom_text(),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_tierset_trigger_custom(),
                        "customDuration": make_tierset_custom_duration(),
                        "customIcon": make_tierset_custom_icon(),
                    },
                    "untrigger": {
                        "custom": make_tierset_untrigger_custom()
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 09 - Enchants (Berserking MH/OH x1/x2, Executioner, Mongoose, Ashen Band)
        {
            "id": "09 - Enchants",
            "uid": "FWHUD_UTIL_ENCHANTS",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -28,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\Spell_Nature_BloodLust",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_enchants_custom_text(),
            "init_completed": SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_enchants_trigger_custom(),
                        "customDuration": make_enchants_custom_duration(),
                        "customIcon": make_enchants_custom_icon(),
                    },
                    "untrigger": {
                        "custom": make_enchants_untrigger_custom()
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 10 - Gloves (Slot 10)
        {
            "id": "10 - Gloves",
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

        # 11 - Death Wish (Spell 12292)
        {
            "id": "11 - Death Wish",
            "uid": "FWHUD_UTIL_DEATHWISH",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 28,
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
                        "custom": make_warrior_spell_trigger_custom(12292),
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

        # 12 - Recklessness (Spell 1719)
        {
            "id": "12 - Recklessness",
            "uid": "FWHUD_UTIL_RECKLESSNESS",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 56,
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
                        "custom": make_warrior_spell_trigger_custom(1719),
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
