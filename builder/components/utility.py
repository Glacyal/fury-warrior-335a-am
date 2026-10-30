"""
Modulo Componente: 05-13 - Utility Row (Warrior Fury)
=====================================================
Gestisce la riga orizzontale di utilità a y = -45 con riposizionamento dinamico
centrato naturale (da 3 a 9 icone) in base all'equipaggiamento e alle abilità:
1. 05 - Trinket 1 warDPS (Slot 13: DBW, STS, Death's Choice, Skull, Scorpion, Mjolnir, ecc. con ICD reale/On-Use)
2. 06 - Trinket 2 warDPS (Slot 14: STS, DBW, Skull, Comet, Grim Toll, Mirror, ecc. con ICD reale/On-Use)
3. 06b - Ring warDPS (Slot 11/12: Ashen Band of Endless Vengeance +480 AP, Eternal Champion +160 AP, 60s ICD)
4. 07 - Cloak warDPS (Slot 15: Swordguard Embroidery +400 AP / Paracadute / Flexweave)
5. 08 - Tier Set warDPS (T10 Siegebreaker/Advantage, T8 Haste, T7 Spirits of the Lost, T9 e combinazioni 2P+2P)
6. 09a - Weapon MH warDPS (Slot 16: Berserking MH +400 AP, Mongoose, Executioner con tracking indipendente)
7. 09b - Weapon OH warDPS (Slot 17: Berserking OH +400 AP, Mongoose, Executioner con tracking indipendente)
8. 10 - Gloves warDPS (Slot 10: Acceleratori Ipersonici Ingegneria +340 Haste per 12s, 60s CD)
9. 11 - Death Wish (Spell ID 12292, durata attiva 30s + cooldown)
10. 12 - Recklessness (Spell ID 1719, 3 cariche critico garantite + cooldown)
11. 13 - Boots warDPS (Slot 8: Acceleratori a Nitro / Nitro Boosts Ingegneria, 180s CD)

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

    _G.FWHUD_VRState = _G.FWHUD_VRState or {
        lastStart = 0,
        lastEnd = 0,
        isUsable = false,
    }

    _G.FWHUD_CheckVictoryRush = _G.FWHUD_CheckVictoryRush or function()
        local now = GetTime()
        local vr = _G.FWHUD_VRState
        if not vr then return false, 0, 0 end
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


    _G.FWHUD_TrinketDB = {
        -- ====================================================================
        -- PHYSICAL / MELEE DPS TRINKETS (WotLK 3.3.5a)
        -- ====================================================================
        -- Deathbringer's Will (Normal 50362, Heroic 50363 - ICC 25 Saurfang)
        [50362] = { keywords = { "taunka", "vrykul", "irondwarf", "deathbringer", "nanodiferro", "forzadel", "agilitadel", "miradel", "volonta" }, spellIds = { [71484] = true, [71485] = true, [71486] = true, [71491] = true, [71492] = true, [71487] = true, [71556] = true, [71557] = true, [71558] = true, [71559] = true, [71560] = true, [71561] = true }, icd = 105, dur = 30 },
        [50363] = { keywords = { "taunka", "vrykul", "irondwarf", "deathbringer", "nanodiferro", "forzadel", "agilitadel", "miradel", "volonta" }, spellIds = { [71484] = true, [71485] = true, [71486] = true, [71491] = true, [71492] = true, [71487] = true, [71556] = true, [71557] = true, [71558] = true, [71559] = true, [71560] = true, [71561] = true }, icd = 105, dur = 30 },

        -- Sharpened Twilight Scale (Normal 54569, Heroic 54590 - RS 25 Halion)
        [54569] = { keywords = { "twilightprecision", "sharpenedtwilight", "twilight", "crepuscolare", "precisione" }, spellIds = { [75473] = true, [75474] = true, [75466] = true, [75456] = true }, icd = 45, dur = 15 },
        [54590] = { keywords = { "twilightprecision", "sharpenedtwilight", "twilight", "crepuscolare", "precisione" }, spellIds = { [75473] = true, [75474] = true, [75466] = true, [75456] = true }, icd = 45, dur = 15 },

        -- Death's Choice / Verdict (Normal Alliance 47115, Normal Horde 47131, Heroic Alliance 47303, Heroic Horde 47464 - ToC 25 Twins)
        [47115] = { keywords = { "paragon", "choice", "verdict", "scelta", "verdetto" }, spellIds = { [67708] = true, [67703] = true, [67707] = true }, icd = 45, dur = 15 },
        [47131] = { keywords = { "paragon", "choice", "verdict", "scelta", "verdetto" }, spellIds = { [67773] = true, [67772] = true, [67771] = true }, icd = 45, dur = 15 },
        [47303] = { keywords = { "paragon", "choice", "verdict", "scelta", "verdetto" }, spellIds = { [67708] = true, [67703] = true, [67707] = true }, icd = 45, dur = 15 },
        [47464] = { keywords = { "paragon", "choice", "verdict", "scelta", "verdetto" }, spellIds = { [67773] = true, [67772] = true, [67771] = true }, icd = 45, dur = 15 },

        -- Whispering Fanged Skull (Normal 50342, Heroic 50343 - ICC 10 Lady Deathwhisper)
        [50342] = { keywords = { "whisperingfangedskull", "fanged", "skull", "teschio", "sussurrante" }, spellIds = { [71541] = true, [71540] = true }, icd = 45, dur = 15 },
        [50343] = { keywords = { "whisperingfangedskull", "fanged", "skull", "teschio", "sussurrante" }, spellIds = { [71541] = true, [71540] = true }, icd = 45, dur = 15 },

        -- Herkuml War Token (50355 - 60 Frost Emblems) - Stacking AP
        [50355] = { keywords = { "herkuml", "token" }, spellIds = { [71396] = true }, icd = 0, dur = 10 },

        -- Needle-Encrusted Scorpion (50198 - Forge of Souls Heroic)
        [50198] = { keywords = { "nowisthetime", "oraeilmomento", "needleencrusted", "scorpion", "scorpione" }, spellIds = { [71403] = true, [71401] = true }, icd = 45, dur = 10 },

        -- Mjolnir Runestone (45931, 45866 - Ulduar 10 Thorim)
        [45931] = { keywords = { "mjolnirrunestone", "runestone", "mjolnir", "pietrarunica" }, spellIds = { [65019] = true, [65014] = true }, icd = 45, dur = 10 },
        [45866] = { keywords = { "mjolnirrunestone", "runestone", "mjolnir", "pietrarunica" }, spellIds = { [65019] = true, [65014] = true }, icd = 45, dur = 10 },

        -- Comet's Trail (45609 - Ulduar 25 Algalon)
        [45609] = { keywords = { "cometstrail", "comet", "cometa" }, spellIds = { [64772] = true }, icd = 45, dur = 10 },

        -- Darkmoon Card: Greatness (44253, 44254, 44255, 42987)
        [44253] = { keywords = { "greatness", "nobilt", "grandezza" }, spellIds = { [60229] = true, [60233] = true, [60234] = true, [60235] = true }, icd = 45, dur = 15 },
        [44254] = { keywords = { "greatness", "nobilt", "grandezza" }, spellIds = { [60229] = true, [60233] = true, [60234] = true, [60235] = true }, icd = 45, dur = 15 },
        [44255] = { keywords = { "greatness", "nobilt", "grandezza" }, spellIds = { [60229] = true, [60233] = true, [60234] = true, [60235] = true }, icd = 45, dur = 15 },
        [42987] = { keywords = { "greatness", "nobilt", "grandezza" }, spellIds = { [60229] = true, [60233] = true, [60234] = true, [60235] = true }, icd = 45, dur = 15 },

        -- Grim Toll (40256 - Naxxramas 25)
        [40256] = { keywords = { "grimtoll", "toll", "rintocco" }, spellIds = { [60486] = true, [60485] = true }, icd = 45, dur = 10 },

        -- Mirror of Truth (40684 - 40 Emblem of Heroism) - Proc: Reflection of Torment / Riflesso del Tormento (+1000 AP)
        [40684] = { keywords = { "reflection", "torment", "riflesso", "tormento", "mirroroftruth", "mirror", "truth", "specchio" }, spellIds = { [60065] = true, [60064] = true }, icd = 45, dur = 10 },

        -- Anvil of Titans (44093 - Wintergrasp PvP) - Proc: Reflection of Torment (+1000 AP)
        [44093] = { keywords = { "reflection", "torment", "riflesso", "tormento", "anvil", "incudine" }, spellIds = { [60065] = true, [60064] = true }, icd = 45, dur = 10 },

        -- Coren's Chromium Coaster (49074 - Brewfest) - Proc: Reflection of Torment (+1000 AP)
        [49074] = { keywords = { "chromium", "coaster", "reflection", "torment", "riflesso", "tormento" }, spellIds = { [60065] = true, [60064] = true, [48480] = true, [60488] = true }, icd = 45, dur = 10 },

        -- Dark-Matter (46038 - Ulduar 10 Algalon)
        [46038] = { keywords = { "darkmatter", "materiaoscura", "dark", "matter" }, spellIds = { [65024] = true, [65023] = true }, icd = 45, dur = 10 },

        -- Banner of Victory (44914 - ToC 5 Normal)
        [44914] = { keywords = { "bannerofvictory", "banner", "victory", "stendardo" }, spellIds = { [67671] = true, [67670] = true }, icd = 45, dur = 10 },

        -- Meteorite Whetstone (37390 - Utgarde Pinnacle Heroic)
        [37390] = { keywords = { "meteorite", "whetstone", "cote" }, spellIds = { [60305] = true, [60304] = true }, icd = 45, dur = 10 },

        -- Vestige of Haldor (37220 - Utgarde Pinnacle Normal)
        [37220] = { keywords = { "haldor" }, spellIds = { [60302] = true, [60301] = true }, icd = 45, dur = 10 },

        -- Feast of the Greatfather (44431 - Winter Veil)
        [44431] = { keywords = { "greatfather", "grandepadre" }, spellIds = { [60490] = true, [60489] = true }, icd = 45, dur = 15 },

        -- Blood of the Old God (45522 - Ulduar 25 Yogg-Saron)
        [45522] = { keywords = { "bloodoftheoldgod", "oldgod", "sangue" }, spellIds = { [64790] = true, [64789] = true }, icd = 45, dur = 10 },

        -- Pyrite Infuser (45286 - Ulduar 10 Flame Leviathan)
        [45286] = { keywords = { "pyriteinfuser", "pyrite", "pirite" }, spellIds = { [65012] = true, [65011] = true }, icd = 45, dur = 10 },

        -- Wrathstone (45263 - Emblem of Conquest) - On-Use
        [45263] = { keywords = { "wrathstone" }, spellIds = { [64765] = true }, icd = 120, dur = 20, onUse = true },

        -- Mark of Supremacy (47734 - Emblem of Triumph) - On-Use
        [47734] = { keywords = { "markofsupremacy", "supremacy" }, spellIds = { [67708] = true, [67706] = true, [67707] = true }, icd = 120, dur = 20, onUse = true },

        -- Incisor Fragment (37723 - Drak'Tharon Keep Heroic) - On-Use
        [37723] = { keywords = { "incisor" }, spellIds = { [60298] = true }, icd = 120, dur = 20, onUse = true },

        -- Loatheb's Shadow (39257 - Naxxramas 10) - On-Use
        [39257] = { keywords = { "loatheb" }, spellIds = { [60314] = true }, icd = 120, dur = 20, onUse = true },

        -- Sphere of Red Dragon's Blood (37111 - Nexus Heroic) - On-Use
        [37111] = { keywords = { "reddragonsblood" }, spellIds = { [60290] = true }, icd = 120, dur = 20, onUse = true },

        -- Victor's Call & Vengeance of the Forsaken (47725, 47948, 47728, 47949 - ToC 10) - On-Use
        [47725] = { keywords = { "victor" }, spellIds = { [67744] = true, [67745] = true }, icd = 120, dur = 20, onUse = true },
        [47948] = { keywords = { "victor" }, spellIds = { [67744] = true, [67745] = true }, icd = 120, dur = 20, onUse = true },
        [47728] = { keywords = { "vengeance", "vendetta" }, spellIds = { [67744] = true, [67745] = true }, icd = 120, dur = 20, onUse = true },
        [47949] = { keywords = { "vengeance", "vendetta" }, spellIds = { [67744] = true, [67745] = true }, icd = 120, dur = 20, onUse = true },

        -- Shard of the Crystal Heart (48722 - Emblem of Triumph) - On-Use Haste
        [48722] = { keywords = { "crystalheart", "shard" }, spellIds = { [67683] = true }, icd = 120, dur = 20, onUse = true },

        -- Bitter Balebrew Charm & Bubbling Brightbrew Charm (49080, 49078, 37863, 37862 - Brewfest) - On-Use
        [49080] = { keywords = { "balebrew", "brightbrew" }, spellIds = { [48480] = true, [51348] = true }, icd = 120, dur = 20, onUse = true },
        [49078] = { keywords = { "balebrew", "brightbrew" }, spellIds = { [48480] = true, [51348] = true }, icd = 120, dur = 20, onUse = true },
        [37863] = { keywords = { "balebrew", "brightbrew" }, spellIds = { [48480] = true, [51348] = true }, icd = 120, dur = 20, onUse = true },
        [37862] = { keywords = { "balebrew", "brightbrew" }, spellIds = { [48480] = true, [51348] = true }, icd = 120, dur = 20, onUse = true },

        -- Tears of the Vanquished (47215 - ToC 5 Normal)
        [47215] = { keywords = { "revitalized" }, spellIds = { [67700] = true }, icd = 45, dur = 0 },

        -- ====================================================================
        -- TANK TRINKETS (WotLK 3.3.5a)
        -- ====================================================================
        -- Juggernaut's Vitality (Normal 47290, Heroic 47451 - ToC 25 Horde) - On-Use Max Health
        [47290] = { keywords = { "juggernaut", "vitality", "vigore" }, spellIds = { [67753] = true }, icd = 180, dur = 15, onUse = true },
        [47451] = { keywords = { "juggernaut", "vitality", "vigore" }, spellIds = { [67752] = true }, icd = 180, dur = 15, onUse = true },

        -- Satrina's Impeding Scarab (Normal 47080, Heroic 47088 - ToC 25 Alliance) - On-Use Max Health
        [47080] = { keywords = { "satrina", "impeding", "scarab", "scarabeo" }, spellIds = { [67694] = true }, icd = 180, dur = 15, onUse = true },
        [47088] = { keywords = { "satrina", "impeding", "scarab", "scarabeo" }, spellIds = { [67693] = true }, icd = 180, dur = 15, onUse = true },

        -- Corroded Skeleton Key (50356 - 60 Frost Emblems) - On-Use Absorbs 6400
        [50356] = { keywords = { "corroded", "skeletonkey", "hardenedskin", "pelleindurita", "chiave" }, spellIds = { [71586] = true }, icd = 120, dur = 10, onUse = true },

        -- Unidentifiable Organ (Normal 50341, Heroic 50344 - ICC 10 Putricide) - Stacking Armor on Melee Hit
        [50341] = { keywords = { "unidentifiableorgan", "organ", "organo" }, spellIds = { [71536] = true, [71578] = true }, icd = 0, dur = 10 },
        [50344] = { keywords = { "unidentifiableorgan", "organ", "organo" }, spellIds = { [71537] = true, [71578] = true }, icd = 0, dur = 10 },

        -- Sindragosa's Flawless Fang (Normal 50361, Heroic 50364 - ICC 25 Sindragosa) - On-Use Resistances
        [50361] = { keywords = { "sindragosa", "fang", "zanna", "aegis", "dalaran" }, spellIds = { [71635] = true }, icd = 60, dur = 10, onUse = true },
        [50364] = { keywords = { "sindragosa", "fang", "zanna", "aegis", "dalaran" }, spellIds = { [71638] = true }, icd = 60, dur = 10, onUse = true },

        -- Glyph of Indomitability (47735 - 50 Emblem of Triumph) - On-Use Dodge
        [47735] = { keywords = { "indomitability", "glyph", "glifo", "indomitable", "indomito" }, spellIds = { [67713] = true }, icd = 120, dur = 20, onUse = true },

        -- The Black Heart (47216 - ToC 5 Normal Black Knight) - Chance on struck +705 Armor
        [47216] = { keywords = { "blackheart", "cuorenero", "parryingarmor", "parrying" }, spellIds = { [67702] = true }, icd = 45, dur = 10 },

        -- Essence of Gossamer (37264 - Azjol-Nerub Heroic Hadronox) - Chance on struck absorb
        [37264] = { keywords = { "gossamer", "tessitura" }, spellIds = { [60295] = true }, icd = 45, dur = 10 },

        -- Lavanthor's Talisman (37844 - Violet Hold Heroic Lavanthor) - On-Use Defense
        [37844] = { keywords = { "lavanthor", "talisman" }, spellIds = { [60307] = true }, icd = 120, dur = 20, onUse = true },

        -- Heart of Iron (45158 - Ulduar 25 Ignis) - On-Use Armor
        [45158] = { keywords = { "heartofiron", "cuorediferro" }, spellIds = { [64761] = true }, icd = 120, dur = 20, onUse = true },

        -- Ick's Rotting Thumb (50235 - Pit of Saron Heroic Ick) - On-Use Max Health
        [50235] = { keywords = { "rottingthumb", "thumb", "pollice" }, spellIds = { [71412] = true }, icd = 180, dur = 15, onUse = true },

        -- Purified Onyxia Blood Talisman (10m 49487, 25m 49308 - Onyxia) - On-Use Armor
        [49487] = { keywords = { "onyxia", "bloodtalisman" }, spellIds = { [67756] = true }, icd = 120, dur = 20, onUse = true },
        [49308] = { keywords = { "onyxia", "bloodtalisman" }, spellIds = { [67757] = true }, icd = 120, dur = 20, onUse = true },

        -- Royal Seal of King Llane (45507 - Ulduar 10 Yogg-Saron) - Chance on melee strike +Armor
        [45507] = { keywords = { "royalseal", "kingllane", "sigilloreale" }, spellIds = { [64784] = true }, icd = 45, dur = 10 },

        -- The General's Heart (45285 - Ulduar 10 General Vezax) - Chance on hit/block +Armor
        [45285] = { keywords = { "general", "generale" }, spellIds = { [64761] = true, [65017] = true }, icd = 45, dur = 10 },

        -- Figurine - Monarch Crab (42341 - Jewelcrafting) - On-Use Dodge
        [42341] = { keywords = { "monarchcrab", "granchio" }, spellIds = { [59706] = true }, icd = 120, dur = 20, onUse = true },

        -- Figurine - Ruby Hare (42345 - Jewelcrafting) - On-Use Run Speed / Health
        [42345] = { keywords = { "rubyhare", "lepre" }, spellIds = { [59703] = true }, icd = 120, dur = 20, onUse = true },

        -- Brawler's Souvenir (37784 - Violet Hold Heroic) - Chance on struck Dodge
        [37784] = { keywords = { "brawler", "souvenir" }, spellIds = { [60293] = true }, icd = 45, dur = 10 },

        -- Seal of the Pantheon (36993 - Halls of Lightning Normal/Heroic Loken) - Chance on struck +Armor
        [36993] = { keywords = { "pantheon" }, spellIds = { [60288] = true }, icd = 45, dur = 10 },

        -- ====================================================================
        -- PVP MEDALLIONS & BATTLEMASTER'S TRINKETS
        -- ====================================================================
        [42122] = { keywords = { "medallion", "medaglione" }, icd = 120, dur = 0, onUse = true },
        [42123] = { keywords = { "medallion", "medaglione" }, icd = 120, dur = 0, onUse = true },
        [51377] = { keywords = { "medallion", "medaglione" }, icd = 120, dur = 0, onUse = true },
        [51378] = { keywords = { "medallion", "medaglione" }, icd = 120, dur = 0, onUse = true },
        [42133] = { keywords = { "battlemaster" }, spellIds = { [59754] = true }, icd = 180, dur = 15, onUse = true },
        [44063] = { keywords = { "battlemaster" }, spellIds = { [59754] = true }, icd = 180, dur = 15, onUse = true },
        [42134] = { keywords = { "battlemaster" }, spellIds = { [59754] = true }, icd = 180, dur = 15, onUse = true },
        [44064] = { keywords = { "battlemaster" }, spellIds = { [59754] = true }, icd = 180, dur = 15, onUse = true },
    }

    _G.FWHUD_AllMeleeKeywords = {
        -- DPS Procs
        "taunka", "vrykul", "irondwarf", "deathbringer", "spezzassedio", "nanodiferro", "volonta",
        "twilight", "sharpened", "crepuscolare", "precision",
        "paragon", "choice", "verdict", "scelta", "verdetto",
        "fanged", "skull", "whispering", "teschio", "sussurrante",
        "scorpion", "needle", "scorpione", "nowisthetime", "oraeilmomento",
        "runestone", "mjolnir", "pietrarunica",
        "comet", "trail", "cometa",
        "greatness", "nobilt", "grandezza",
        "grimtoll", "toll", "rintocco",
        "mirror", "truth", "specchio", "reflection", "torment", "riflesso", "tormento",
        "banner", "victory", "stendardo",
        "meteorite", "whetstone", "cote",
        "haldor", "wrathstone", "supremacy", "incisor", "loatheb",
        "herkuml", "darkmatter", "materiaoscura", "bloodoftheoldgod",
        "pyrite", "pirite", "chromium", "coaster", "balebrew", "brightbrew",
        -- Tank Procs & On-Use
        "juggernaut", "vitality", "vigore",
        "satrina", "impeding", "scarab", "scarabeo",
        "skeleton", "hardened", "skin", "indurita", "chiave",
        "organ", "organo",
        "fang", "zanna", "aegis", "dalaran",
        "indomitable", "indomito", "glyph", "glifo",
        "blackheart", "cuorenero", "parrying",
        "gossamer", "tessitura",
        "lavanthor", "cuorediferro", "heartofiron",
        "rottingthumb", "thumb", "pollice",
        "onyxia", "bloodtalisman", "sigilloreale", "royalseal",
        "monarchcrab", "granchio", "brawler", "pantheon"
    }

    _G.FWHUD_RingDB = {
        -- Ashen Band of Endless Vengeance (Exalted Melee DPS - 277)
        [50402] = { keywords = { "frostforgedchampion" }, spellIds = { [72412] = true, [72414] = true }, icd = 60, dur = 10 },
        -- Ashen Band of Unmatched Vengeance (Revered Melee DPS - 268)
        [50401] = { keywords = { "frostforgedchampion" }, spellIds = { [72412] = true, [72414] = true }, icd = 60, dur = 10 },
        -- Ashen Band of Endless Might (Exalted Tank - 277)
        [50404] = { keywords = { "frostforgeddefender" }, spellIds = { [72410] = true }, icd = 60, dur = 10 },
        -- Band of the Eternal Champion (TBC Hyjal Exalted Melee DPS - 152)
        [29301] = { keywords = { "eternalchampion" }, spellIds = { [35081] = true }, icd = 60, dur = 10 },
    }
    _G.FWHUD_RingState = _G.FWHUD_RingState or { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 }

    _G.FWHUD_WeaponEnchantDB = {
        [3789] = { name = "Berserking", spellId = 59620, dur = 15, icon = "Interface\\Icons\\Spell_Nature_BloodLust", kw = "berserk" },
        [2673] = { name = "Mongoose", spellId = 28093, dur = 15, icon = "Interface\\Icons\\Spell_Nature_PosisonSpike", kw = "mongoose" },
        [3225] = { name = "Executioner", spellId = 42976, dur = 15, icon = "Interface\\Icons\\INV_Sword_48", kw = "executioner" },
        [1900] = { name = "Crusader", spellId = 20007, dur = 15, icon = "Interface\\Icons\\Spell_Holy_BlessingOfStrength", kw = "crusader" },
        [3869] = { name = "Blade Ward", spellId = 64440, dur = 10, icon = "Interface\\Icons\\Ability_Warrior_ShieldReflection", kw = "bladeward" },
        [3870] = { name = "Blood Draining", spellId = 64568, dur = 20, icon = "Interface\\Icons\\Spell_Shadow_BloodBoil", kw = "blooddraining" },
        [3790] = { name = "Black Magic", spellId = 59626, dur = 10, icon = "Interface\\Icons\\Spell_Shadow_Shadowfury", kw = "blackmagic" },
        [3273] = { name = "Deathfrost", spellId = 46578, dur = 8, icon = "Interface\\Icons\\Spell_Frost_FrostBolt02", kw = "deathfrost" },
        [3833] = { name = "Giant Slayer", spellId = 60621, dur = 10, icon = "Interface\\Icons\\Spell_Nature_NatureTouchGrow", kw = "giantslayer" },
        [3834] = { name = "Icebreaker", spellId = 60707, dur = 10, icon = "Interface\\Icons\\Spell_Frost_FrostNova", kw = "icebreaker" },
        [3830] = { name = "Lifeward", spellId = 60691, dur = 10, icon = "Interface\\Icons\\Spell_Holy_Restoration", kw = "lifeward" },
        [1898] = { name = "Unholy Weapon", spellId = 20004, dur = 10, icon = "Interface\\Icons\\Spell_Shadow_ShadowPresence", kw = "unholy" },
        [803]  = { name = "Fiery Weapon", spellId = 13897, dur = 6, icon = "Interface\\Icons\\Spell_Fire_FireEnchantWeapon", kw = "fiery" },
    }
    _G.FWHUD_StaticWeaponEnchants = {
        [3827] = true, -- Massacre (+110 Attack Power 2H)
        [2667] = true, -- Superior Potency (+65 Attack Power 1H)
        [1103] = true, -- Exceptional Agility (+26 Agility)
        [2670] = true, -- Major Agility (+30 Agility 2H)
        [3788] = true, -- Accuracy (+25 Hit & +25 Crit)
        [3731] = true, -- Titanium Weapon Chain (+28 Hit & -50% Disarm)
        [3832] = true, -- Greater Savagery (+85 Attack Power 2H)
        [195]  = true, -- Titanguard (+30 Stamina)
        [2563] = true, -- Superior Striking (+5 Damage)
        [2567] = true, -- Mighty Intellect (+30 Int)
        [3844] = true, -- Exceptional Spellpower (+50 SP)
        [3854] = true, -- Mighty Spellpower (+63 SP)
        [3855] = true, -- Greater Spellpower (+81 SP 2H)
        [0]    = true, -- Nessun incanto
    }
    _G.FWHUD_WeaponState = _G.FWHUD_WeaponState or {
        [16] = { lastStart = 0, lastEnd = 0, isProc = false },
        [17] = { lastStart = 0, lastEnd = 0, isProc = false }
    }

    _G.FWHUD_CloakKeywords = { "swordguard", "spadatesta", "parachute", "flexweave", "flessibile" }
    _G.FWHUD_CloakSpellIds = { [55775] = true, [55767] = true, [54865] = true, [54753] = true }
    _G.FWHUD_CloakEnchantIDs = { [3730] = true, [3605] = true }

    _G.FWHUD_GlovesSpellIds = { [54758] = true }
    _G.FWHUD_GlovesKeywords = { "hyperspeed", "accelerat", "ipersonic", "340 haste" }

    _G.FWHUD_BootsEnchantIDs = {
        [3606] = true, -- Nitro Boosts (Engineering +24 Crit & Active Speed in WotLK 3.3.5a)
        [3601] = true, -- Alternate tinker ID
        [55016] = true, -- Crafting spell
        [54861] = true, -- Buff spell
        [55004] = true, -- Trigger spell
        [54858] = true, -- Item tinker spell
    }
    _G.FWHUD_BootsSpellIds = {
        [54861] = true,
        [55016] = true,
        [55004] = true,
        [54858] = true,
    }
    _G.FWHUD_BootsKeywords = { "nitro", "acceleratori a nitro", "acceleratori di nitro" }

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
                for i = 1, 30 do
                    if not _G["FWHUD_ScanTTTextLeft"..i] then
                        local l = tt:CreateFontString("FWHUD_ScanTTTextLeft"..i, "ARTWORK", "GameTooltipText")
                        local r = tt:CreateFontString("FWHUD_ScanTTTextRight"..i, "ARTWORK", "GameTooltipText")
                        tt:AddFontStrings(l, r)
                    end
                end
                _G.FWHUD_ScanTT = tt
            end
            tt:ClearLines()
            tt:SetInventoryItem("player", s)
            for j = 1, (tt:NumLines() or 0) do
                local line = _G["FWHUD_ScanTTTextLeft"..j]
                local text = line and line:GetText()
                if text then
                    local lt = text:lower()
                    for _, kw in ipairs(keywords) do
                        if lt:find(kw, 1, true) then return true end
                    end
                end
            end
            local regions = { tt:GetRegions() }
            for _, r in ipairs(regions) do
                if r and r.GetObjectType and r:GetObjectType() == "FontString" and r.GetText then
                    local text = r:GetText()
                    if text then
                        local lt = text:lower()
                        for _, kw in ipairs(keywords) do
                            if lt:find(kw, 1, true) then return true end
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

        -- Slot 8 (Boots): Nitro Boosts (Engineering)
        if s == 8 then
            local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
            if buffs then
                if (_G.FWHUD_BootsSpellIds and (buffs.bySpellId[54861] or buffs.bySpellId[54858] or buffs.bySpellId[55016] or buffs.bySpellId[55004])) then
                    cache.isEquipped = true
                    return true
                end
                for _, b in ipairs(buffs.list or {}) do
                    local bName = b.name and b.name:lower() or ""
                    if (b.spellId and _G.FWHUD_BootsSpellIds and _G.FWHUD_BootsSpellIds[b.spellId]) or bName:find("nitro", 1, true) then
                        cache.isEquipped = true
                        return true
                    end
                end
            end
            if enchantID and _G.FWHUD_BootsEnchantIDs and _G.FWHUD_BootsEnchantIDs[enchantID] then
                cache.isEquipped = true
                return true
            end
            local itemStart, itemDur = GetInventoryItemCooldown("player", 8)
            if itemDur and itemDur >= 60 then
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
        local icdState = _G.FWHUD_ICD and _G.FWHUD_ICD[slot]
        if not icdState then
            _G.FWHUD_ICD = _G.FWHUD_ICD or {}
            icdState = { lastStart = 0, lastEnd = 0, isProc = false, lastItemID = 0 }
            _G.FWHUD_ICD[slot] = icdState
        end
        if icdState.lastItemID and itemID and icdState.lastItemID ~= itemID then
            icdState.lastStart = 0
            icdState.lastEnd = 0
            icdState.isProc = false
        end
        if itemID then icdState.lastItemID = itemID end

        local entry = itemID and _G.FWHUD_TrinketDB and _G.FWHUD_TrinketDB[itemID]
        if not entry and itemID and (slot == 13 or slot == 14) then
            local itemName = GetItemInfo and GetItemInfo(itemID)
            if not itemName then
                local link = GetInventoryItemLink("player", slot)
                if link then itemName = link:match("%[(.-)%]") end
            end
            if itemName then
                local inClean = itemName:lower():gsub("[%s%p%c]", "")
                for dbID, dbEntry in pairs(_G.FWHUD_TrinketDB or {}) do
                    if dbEntry.keywords then
                        for _, kw in ipairs(dbEntry.keywords) do
                            local kwClean = kw:lower():gsub("[%s%p%c]", "")
                            if inClean:find(kwClean, 1, true) then
                                entry = dbEntry
                                break
                            end
                        end
                    end
                    if entry then break end
                end
            end
        end
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
                local bName = b.name and b.name:lower() or ""
                if (b.spellId and (b.spellId == 54861 or b.spellId == 54858 or b.spellId == 55016 or b.spellId == 55004)) or
                   bName:find("nitro", 1, true) then
                    isMatch = true
                end
            else
                if entry and b.spellId and entry.spellIds and entry.spellIds[b.spellId] then
                    isMatch = true
                else
                    local bName = b.name
                    if bName then
                        local cName = string.lower(bName):gsub("[%s%p%c]", "")
                        if entry and entry.keywords then
                            for _, kw in ipairs(entry.keywords) do
                                local kwClean = kw:lower():gsub("[%s%p%c]", "")
                                if cName:find(kwClean, 1, true) then isMatch = true break end
                            end
                        end
                        if not isMatch then
                            local otherSlot = (slot == 13 and 14 or 13)
                            local otherID = GetInventoryItemID and GetInventoryItemID("player", otherSlot)
                            local otherEntry = otherID and _G.FWHUD_TrinketDB and _G.FWHUD_TrinketDB[otherID]
                            local isOther = false
                            if otherEntry then
                                if b.spellId and otherEntry.spellIds and otherEntry.spellIds[b.spellId] then
                                    isOther = true
                                elseif otherEntry.keywords then
                                    for _, kw in ipairs(otherEntry.keywords) do
                                        local kwClean = kw:lower():gsub("[%s%p%c]", "")
                                        if cName:find(kwClean, 1, true) then isOther = true break end
                                    end
                                end
                            end
                            if not isOther and _G.FWHUD_AllMeleeKeywords then
                                for _, kw in ipairs(_G.FWHUD_AllMeleeKeywords) do
                                    local kwClean = kw:lower():gsub("[%s%p%c]", "")
                                    if cName:find(kwClean, 1, true) then isMatch = true break end
                                end
                            end
                        end
                    end
                end
                if not isMatch and b.icon and baseIcon and b.icon == baseIcon then
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
        end

        if isOnUseCooldown then
            return finish("COOLDOWN", remItemCD, itemDur, baseIcon)
        end

        if icdState.lastStart > 0 and targetICD > 0 then
            local elapsed = now - icdState.lastStart
            if elapsed < targetICD then
                local remICD = targetICD - elapsed
                return finish("ICD", remICD, targetICD, baseIcon)
            else
                icdState.lastStart = 0
                icdState.timerScheduled = false
            end
        end

        return finish("READY", 0, 0, baseIcon)
    end

    -- =========================================================================
    -- GESTIONE ANELLO CON PROC (ASHEN BAND, ETERNAL CHAMPION)
    -- =========================================================================
    _G.FWHUD_CheckRingEquipped = function()
        local now_r = GetTime()
        local cache = _G.FWHUD_RingEquipCache
        if cache and (now_r - cache.time < 0.25) then
            return cache.isEquipped, cache.slot, cache.itemID
        end
        if not cache then
            cache = { time = 0, isEquipped = false, slot = nil, itemID = nil }
            _G.FWHUD_RingEquipCache = cache
        end
        cache.time = now_r

        for _, s in ipairs({ 11, 12 }) do
            local id = GetInventoryItemID("player", s)
            if not id then
                local link = GetInventoryItemLink("player", s)
                if link then id = tonumber(link:match("item:(%d+)")) end
            end
            if id and _G.FWHUD_RingDB and _G.FWHUD_RingDB[id] then
                cache.isEquipped = true
                cache.slot = s
                cache.itemID = id
                return true, s, id
            end
        end

        local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
        if buffs then
            if buffs.bySpellId[72412] or buffs.bySpellId[72414] or buffs.bySpellId[72410] or buffs.bySpellId[35081] then
                cache.isEquipped = true
                cache.slot = 11
                cache.itemID = 50402
                return true, 11, 50402
            end
        end

        local tt = _G.FWHUD_ScanTT
        if not tt then
            tt = CreateFrame("GameTooltip", "FWHUD_ScanTT", UIParent, "GameTooltipTemplate")
            tt:SetOwner(UIParent, "ANCHOR_NONE")
            _G.FWHUD_ScanTT = tt
        end
        for _, s in ipairs({ 11, 12 }) do
            local id = GetInventoryItemID("player", s)
            if id then
                tt:ClearLines()
                tt:SetInventoryItem("player", s)
                for j = 1, tt:NumLines() do
                    local line = _G["FWHUD_ScanTTTextLeft"..j]
                    local text = line and line:GetText()
                    if text then
                        local lt = text:lower()
                        if lt:find("frostforged") or lt:find("chilling knowledge") or
                           lt:find("attack power by 480") or lt:find("potenza d'attacco di 480") or
                           lt:find("eternal champion") or lt:find("attack power by 160") or lt:find("potenza d'attacco di 160") then
                            cache.isEquipped = true
                            cache.slot = s
                            cache.itemID = id
                            return true, s, id
                        end
                    end
                end
            end
        end

        cache.isEquipped = false
        cache.slot = nil
        cache.itemID = nil
        return false, nil, nil
    end

    _G.FWHUD_CheckRing = function()
        local isEquipped, ringSlot, ringItemID = _G.FWHUD_CheckRingEquipped()
        local defIcon = (ringItemID and GetItemIcon(ringItemID)) or "Interface\\Icons\\INV_Jewelry_Ring_81"
        if not isEquipped then return "NONE", 0, 0, defIcon, false end

        local now_rk = GetTime()
        local state = _G.FWHUD_RingState
        local entry = ringItemID and _G.FWHUD_RingDB and _G.FWHUD_RingDB[ringItemID]
        local targetICD = (entry and entry.icd) or 60
        local defaultDur = (entry and entry.dur) or 10

        if state.lastItemID and ringItemID and state.lastItemID ~= ringItemID then
            state.lastStart = 0
            state.lastEnd = 0
            state.isProc = false
        end
        if ringItemID then state.lastItemID = ringItemID end

        local foundBuff = false
        local remBuff = 0
        local durBuff = defaultDur
        local buffIcon = nil

        local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
        local buffList = buffs and buffs.list or {}

        for _, b in ipairs(buffList) do
            local isMatch = false
            if b.spellId and (b.spellId == 72412 or b.spellId == 72414 or b.spellId == 72410 or b.spellId == 35081) then
                isMatch = true
            elseif b.name then
                local cName = string.lower(b.name):gsub("[%s%p%c]", "")
                if cName:find("frostforgedchampion", 1, true) or cName:find("eternalchampion", 1, true) then
                    isMatch = true
                end
            end

            if isMatch then
                foundBuff = true
                durBuff = (b.duration and b.duration > 0) and b.duration or defaultDur
                remBuff = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now_rk) or durBuff
                buffIcon = b.icon or defIcon
                break
            end
        end

        if foundBuff and remBuff > 0.05 then
            if not state.isProc or (now_rk - state.lastStart > durBuff + 2) then
                state.lastStart = now_rk - (durBuff - remBuff)
                state.lastEnd = state.lastStart + targetICD
                state.isProc = true
            end
            return "ACTIVE", remBuff, durBuff, buffIcon or defIcon, true
        end

        if state.isProc then
            state.isProc = false
        end

        if state.lastStart > 0 and targetICD > 0 then
            local elapsed = now_rk - state.lastStart
            if elapsed < targetICD then
                local remICD = targetICD - elapsed
                if not state.timerScheduled then
                    state.timerScheduled = true
                    local timerAfter = (C_Timer and C_Timer.After) or (_G.C_Timer and _G.C_Timer.After)
                    if timerAfter then
                        timerAfter(remICD + 0.1, function()
                            state.timerScheduled = false
                            if WeakAuras and WeakAuras.ScanEvents then
                                WeakAuras.ScanEvents("FWHUD_ROW_UPDATE")
                            end
                        end)
                    end
                end
                return "ICD", remICD, targetICD, defIcon, true
            else
                state.lastStart = 0
                state.timerScheduled = false
            end
        end

        return "READY", 0, 0, defIcon, true
    end

    -- =========================================================================
    -- GESTIONE TIER SETS WARRIOR DPS (T10, T8, T7, T9)
    -- =========================================================================
    _G.FWHUD_CheckTierSetEquipped = function()
        local now = GetTime()
        local cache = _G.FWHUD_TierEquipCache
        if cache and (now - cache.time < 0.25) then return cache.hasSet end
        if not cache then cache = { time = 0, hasSet = false, t10 = 0, t8 = 0, t7 = 0, t9 = 0 }; _G.FWHUD_TierEquipCache = cache end
        cache.time = now

        local slots = { 1, 3, 5, 7, 10 }
        local t10, t8, t7, t9 = 0, 0, 0, 0
        for _, s in ipairs(slots) do
            local id = GetInventoryItemID and GetInventoryItemID("player", s)
            if not id then
                local link = GetInventoryItemLink("player", s)
                if link then id = tonumber(link:match("item:(%d+)")) end
            end
            if id then
                if _G.FWHUD_T10_Pieces[id] then t10 = t10 + 1
                elseif _G.FWHUD_T8_Pieces[id] then t8 = t8 + 1
                elseif _G.FWHUD_T7_Pieces[id] then t7 = t7 + 1
                elseif _G.FWHUD_T9_Pieces[id] then t9 = t9 + 1
                end
            end
        end
        cache.t10 = t10
        cache.t8 = t8
        cache.t7 = t7
        cache.t9 = t9

        if t10 >= 2 or t8 >= 2 or t7 >= 2 or t9 >= 2 or t7 >= 4 then
            cache.hasSet = true
        else
            local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
            if buffs then
                if buffs.bySpellId[70845] or buffs.bySpellId[70844] or buffs.bySpellId[70846] or buffs.bySpellId[70848]
                   or buffs.bySpellId[64937] or buffs.bySpellId[64938] or buffs.bySpellId[64942]
                   or buffs.bySpellId[60176] then
                    cache.hasSet = true
                else
                    for _, b in ipairs(buffs.list or {}) do
                        if b.name and (b.name:find("Spirits of the Lost") or b.name:find("Spiriti dei Perduti")
                                       or b.name:find("Bleed Cost Reduction")
                                       or b.name:find("Siegebreaker") or b.name:find("Spezzassedio")
                                       or b.name:find("Advantage") or b.name:find("Vantaggio")) then
                            cache.hasSet = true
                            break
                        end
                    end
                end
            end
            if not cache.hasSet then
                cache.hasSet = false
            end
        end
        return cache.hasSet
    end

    _G.FWHUD_CheckTierSet = function()
        local hasSet = _G.FWHUD_CheckTierSetEquipped()
        if not hasSet then
            return "NONE", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_Siegebreaker"
        end
        local now = GetTime()
        local cache = _G.FWHUD_TierEquipCache or {}
        local t10 = cache.t10 or 0
        local t8 = cache.t8 or 0
        local t7 = cache.t7 or 0
        local t9 = cache.t9 or 0

        local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
        local bList = buffs and buffs.list or {}

        -- Scansione dei buff attivi dei tier set (T10-4P, T10-2P, T7-4P, T8-2P)
        local aT10_4P, aT10_2P, aT7_4P, aT8_2P = nil, nil, nil, nil

        for _, b in ipairs(bList) do
            local sId = b.spellId
            local name = b.name or ""

            -- T10 4P: Siegebreaker (Spell 70846, 70848) - 2 cariche, -0.5s GCD
            if sId == 70846 or sId == 70848 or name:find("Siegebreaker") or name:find("Spezzassedio") then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 10
                local dur = (b.duration and b.duration > 0) and b.duration or 10
                aT10_4P = { rem = rem, dur = dur, count = b.count or 2, icon = b.icon or "Interface\\Icons\\Ability_Warrior_Siegebreaker", label = "T10-4P" }

            -- T7 4P: Spirits of the Lost (Spell 60176) - Riduce il costo in rabbia della prossima abilità di 5
            elseif sId == 60176 or name:find("Spirits of the Lost") or name:find("Spiriti dei Perduti") or name:find("Bleed Cost Reduction") then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 10
                local dur = (b.duration and b.duration > 0) and b.duration or 10
                aT7_4P = { rem = rem, dur = dur, count = b.count or 1, icon = b.icon or "Interface\\Icons\\Ability_Warrior_BloodNova", label = "T7-4P" }

            -- T10 2P: Advantage (Spell 70845, 70844) - +16% AP per 10s
            elseif sId == 70845 or sId == 70844 or name:find("Advantage") or name:find("Vantaggio") then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 10
                local dur = (b.duration and b.duration > 0) and b.duration or 10
                aT10_2P = { rem = rem, dur = dur, count = 1, icon = b.icon or "Interface\\Icons\\Ability_Warrior_Riposte", label = "T10-2P" }

            -- T8 2P: Haste Proc (Spell 64937, 64938, 64942) - +150 Haste per 5s
            elseif sId == 64937 or sId == 64938 or sId == 64942 or name:find("T8 2P") then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 5
                local dur = (b.duration and b.duration > 0) and b.duration or 5
                aT8_2P = { rem = rem, dur = dur, count = 1, icon = b.icon or "Interface\\Icons\\Spell_Nature_BloodLust", label = "T8-2P" }
            end
        end

        -- Valutazione dinamica priorità proc attivi
        if aT10_4P and aT10_4P.rem > 0.05 then
            return "ACTIVE", aT10_4P.rem, aT10_4P.dur, aT10_4P.count, aT10_4P.icon, aT10_4P.label
        end
        if aT7_4P and aT7_4P.rem > 0.05 then
            return "ACTIVE", aT7_4P.rem, aT7_4P.dur, aT7_4P.count, aT7_4P.icon, aT7_4P.label
        end
        if aT8_2P and aT10_2P then
            if aT8_2P.rem <= aT10_2P.rem then
                return "ACTIVE", aT8_2P.rem, aT8_2P.dur, aT8_2P.count, aT8_2P.icon, aT8_2P.label
            else
                return "ACTIVE", aT10_2P.rem, aT10_2P.dur, aT10_2P.count, aT10_2P.icon, aT10_2P.label
            end
        end
        if aT8_2P and aT8_2P.rem > 0.05 then
            return "ACTIVE", aT8_2P.rem, aT8_2P.dur, aT8_2P.count, aT8_2P.icon, aT8_2P.label
        end
        if aT10_2P and aT10_2P.rem > 0.05 then
            return "ACTIVE", aT10_2P.rem, aT10_2P.dur, aT10_2P.count, aT10_2P.icon, aT10_2P.label
        end

        -- Stato READY: combinazioni ed equipaggiamento
        if t10 >= 4 then
            return "READY", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_Siegebreaker", "T10 (4P)"
        elseif t10 >= 2 and t8 >= 2 then
            return "READY", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_Siegebreaker", "T10/T8"
        elseif t10 >= 2 and t9 >= 2 then
            return "READY", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_Siegebreaker", "T10/T9"
        elseif t10 >= 2 and t7 >= 2 then
            return "READY", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_Siegebreaker", "T10/T7"
        elseif t10 >= 2 then
            return "READY", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_Siegebreaker", "T10 (2P)"
        elseif t9 >= 4 then
            return "READY", 0, 0, 0, "Interface\\Icons\\INV_Helmet_05", "T9 (4P)"
        elseif t9 >= 2 and t8 >= 2 then
            return "READY", 0, 0, 0, "Interface\\Icons\\INV_Helmet_05", "T9/T8"
        elseif t9 >= 2 then
            return "READY", 0, 0, 0, "Interface\\Icons\\INV_Helmet_05", "T9 (2P)"
        elseif t8 >= 4 then
            return "READY", 0, 0, 0, "Interface\\Icons\\Spell_Nature_BloodLust", "T8 (4P)"
        elseif t8 >= 2 and t7 >= 2 then
            return "READY", 0, 0, 0, "Interface\\Icons\\Spell_Nature_BloodLust", "T8/T7"
        elseif t8 >= 2 then
            return "READY", 0, 0, 0, "Interface\\Icons\\Spell_Nature_BloodLust", "T8 (2P)"
        elseif t7 >= 4 then
            return "READY", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_BloodNova", "T7 (4P)"
        elseif t7 >= 2 then
            return "READY", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_BloodNova", "T7 (2P)"
        end

        return "READY", 0, 0, 0, "Interface\\Icons\\Ability_Warrior_Siegebreaker", "Tier"
    end

    -- =========================================================================
    -- GESTIONE INCANTI ARMA SEPARATI (MH SLOT 16 & OH SLOT 17)
    -- =========================================================================
    _G.FWHUD_CheckWeaponEquipped = function(slot)
        local now_w = GetTime()
        _G.FWHUD_WeaponEquipCache = _G.FWHUD_WeaponEquipCache or {}
        local cache = _G.FWHUD_WeaponEquipCache[slot]
        if cache and (now_w - cache.time < 0.25) then return cache.hasProcEnchant, cache.enchantID end
        if not cache then cache = { time = 0, hasProcEnchant = false, enchantID = nil }; _G.FWHUD_WeaponEquipCache[slot] = cache end
        cache.time = now_w

        local itemID = GetInventoryItemID("player", slot)
        if not itemID then
            local link = GetInventoryItemLink("player", slot)
            if link then itemID = tonumber(link:match("item:(%d+)")) end
        end
        if not itemID or itemID == 0 then
            cache.hasProcEnchant = false
            cache.enchantID = nil
            return false, nil
        end

        local itemLink = GetInventoryItemLink("player", slot)
        local enchantID = itemLink and tonumber(itemLink:match("item:%d+:(%d+)"))
        if enchantID and _G.FWHUD_WeaponEnchantDB and _G.FWHUD_WeaponEnchantDB[enchantID] then
            cache.hasProcEnchant = true
            cache.enchantID = enchantID
            return true, enchantID
        end

        if enchantID and _G.FWHUD_StaticWeaponEnchants and _G.FWHUD_StaticWeaponEnchants[enchantID] then
            cache.hasProcEnchant = false
            cache.enchantID = nil
            return false, nil
        end

        local tt = _G.FWHUD_ScanTT
        if not tt then
            tt = CreateFrame("GameTooltip", "FWHUD_ScanTT", UIParent, "GameTooltipTemplate")
            tt:SetOwner(UIParent, "ANCHOR_NONE")
            _G.FWHUD_ScanTT = tt
        end
        tt:ClearLines()
        tt:SetInventoryItem("player", slot)
        for j = 1, tt:NumLines() do
            local line = _G["FWHUD_ScanTTTextLeft"..j]
            local text = line and line:GetText()
            if text then
                local lt = text:lower()
                if lt:find("berserk") or lt:find("furia") or lt:find("400 attack power") or lt:find("400 potenza d'attacco") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 3789
                    return true, 3789
                elseif lt:find("mongoose") or lt:find("fulminea") or lt:find("120 agility") or lt:find("120 agilit") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 2673
                    return true, 2673
                elseif lt:find("executioner") or lt:find("carnefice") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 3225
                    return true, 3225
                elseif lt:find("crusader") or lt:find("crociato") or lt:find("holy strength") or lt:find("forza sacra") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 1900
                    return true, 1900
                elseif lt:find("blade ward") or lt:find("guardia delle lame") or lt:find("deviazione") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 3869
                    return true, 3869
                elseif lt:find("blood draining") or lt:find("drenaggio del sangue") or lt:find("blood reserve") or lt:find("riserva di sangue") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 3870
                    return true, 3870
                elseif lt:find("black magic") or lt:find("magia nera") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 3790
                    return true, 3790
                elseif lt:find("deathfrost") or lt:find("gelomorte") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 3273
                    return true, 3273
                elseif lt:find("giant slayer") or lt:find("cacciatore di giganti") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 3833
                    return true, 3833
                elseif lt:find("icebreaker") or lt:find("spaccaghiaccio") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 3834
                    return true, 3834
                elseif lt:find("lifeward") or lt:find("salvavita") then
                    cache.hasProcEnchant = true
                    cache.enchantID = 3830
                    return true, 3830
                end
            end
        end

        cache.hasProcEnchant = false
        cache.enchantID = nil
        return false, nil
    end

    _G.FWHUD_CheckWeapon = function(slot)
        local isEquipped, enchantID = _G.FWHUD_CheckWeaponEquipped(slot)
        local slotLabel = (slot == 16 and "MH") or "OH"
        local defIcon = GetInventoryItemTexture("player", slot) or "Interface\\Icons\\Spell_Nature_BloodLust"
        if not isEquipped then return "NONE", 0, 0, defIcon, slotLabel, false end

        local now_wk = GetTime()
        local state = _G.FWHUD_WeaponState[slot]
        local eInfo = enchantID and _G.FWHUD_WeaponEnchantDB[enchantID]
        local targetDur = (eInfo and eInfo.dur) or 15
        local icon = (eInfo and eInfo.icon) or defIcon

        local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
        local bList = buffs and buffs.list or {}

        local isBerserkActive = false
        local berserkRem = 0
        local berserkCount = 0
        local isMongooseActive = false
        local mongooseRem = 0
        local isExecutionerActive = false
        local executionerRem = 0

        for _, b in ipairs(bList) do
            if b.spellId == 59620 or (b.name and (b.name == "Berserking" or b.name == "Furia Berserker")) then
                isBerserkActive = true
                berserkCount = berserkCount + (b.count and b.count > 0 and b.count or 1)
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now_wk) or targetDur
                if rem > berserkRem then berserkRem = rem end
            elseif b.spellId == 28093 or (b.name and b.name:find("Mongoose")) then
                isMongooseActive = true
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now_wk) or 15
                if rem > mongooseRem then mongooseRem = rem end
            elseif b.spellId == 42976 or (b.name and b.name:find("Executioner")) then
                isExecutionerActive = true
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now_wk) or 15
                if rem > executionerRem then executionerRem = rem end
            end
        end

        local isThisSlotActive = false
        local thisRem = 0

        if enchantID == 3789 or (eInfo and eInfo.name == "Berserking") then
            if isBerserkActive and berserkRem > 0.05 then
                local otherSlot = (slot == 16 and 17 or 16)
                local otherEquipped, otherEnchant = _G.FWHUD_CheckWeaponEquipped(otherSlot)
                local otherHasBerserk = otherEquipped and (otherEnchant == 3789)
                if not otherHasBerserk then
                    isThisSlotActive = true
                    thisRem = berserkRem
                else
                    if berserkCount >= 2 then
                        isThisSlotActive = true
                        thisRem = berserkRem
                    else
                        if state.isProc and (state.lastEnd and state.lastEnd > now_wk) then
                            isThisSlotActive = true
                            thisRem = math.min(berserkRem, state.lastEnd - now_wk)
                        elseif not _G.FWHUD_WeaponState[otherSlot].isProc then
                            isThisSlotActive = (slot == 16)
                            thisRem = berserkRem
                        else
                            isThisSlotActive = false
                        end
                    end
                end
            end
        elseif enchantID == 2673 then
            if isMongooseActive and mongooseRem > 0.05 then
                isThisSlotActive = true
                thisRem = mongooseRem
            end
        elseif enchantID == 3225 then
            if isExecutionerActive and executionerRem > 0.05 then
                isThisSlotActive = true
                thisRem = executionerRem
            end
        end

        if isThisSlotActive and thisRem > 0.05 then
            if not state.isProc or (now_wk - state.lastStart > targetDur + 2) then
                state.lastStart = now_wk - (targetDur - thisRem)
                state.lastEnd = now_wk + thisRem
                state.isProc = true
            end
            return "ACTIVE", thisRem, targetDur, icon, slotLabel, true
        end

        if state.isProc then
            state.isProc = false
            state.lastEnd = now_wk
        end

        return "READY", 0, 0, icon, slotLabel, true
    end

    -- =========================================================================
    -- GESTIONE INCANTI ARMA UNIFICATI (FIFO ORDER CON STACK x2 IN ALTO)
    -- =========================================================================
    _G.FWHUD_CheckEnchantsEquipped = function()
        local now = GetTime()
        local cache = _G.FWHUD_EnchantEquipCache
        if cache and (now - cache.time < 0.25) then return cache.hasEnchant end
        if not cache then cache = { time = 0, hasEnchant = false }; _G.FWHUD_EnchantEquipCache = cache end
        cache.time = now

        local hasMH, eMH = false, nil
        if _G.FWHUD_CheckWeaponEquipped then
            hasMH, eMH = _G.FWHUD_CheckWeaponEquipped(16)
        end
        local hasOH, eOH = false, nil
        if _G.FWHUD_CheckWeaponEquipped then
            hasOH, eOH = _G.FWHUD_CheckWeaponEquipped(17)
        end

        if (hasMH and eMH) or (hasOH and eOH) then
            cache.hasEnchant = true
            return true
        end

        -- Fallback: controllo buff da proc di incanto arma attualmente attivi sul giocatore
        local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
        local bList = buffs and buffs.list or {}
        for _, b in ipairs(bList) do
            local sId = b.spellId
            local name = b.name or ""
            if sId == 59620 or sId == 59621 or name == "Berserking" or name == "Furia Berserker" or
               sId == 28093 or name:find("Mongoose") or name:find("Fulminea") or
               sId == 42976 or name:find("Executioner") or name:find("Carnefice") or
               sId == 20007 or name:find("Holy Strength") or name:find("Forza Sacra") or
               sId == 64440 or sId == 64442 or name:find("Blade Ward") or name:find("Deviazione") or
               sId == 64568 or sId == 64569 or name:find("Blood Reserve") or name:find("Riserva di Sangue") or
               sId == 59626 or name:find("Black Magic") or name:find("Magia Nera") then
                cache.hasEnchant = true
                return true
            end
        end

        cache.hasEnchant = false
        return false
    end

    _G.FWHUD_CheckEnchants = function()
        local hasEnchant = _G.FWHUD_CheckEnchantsEquipped and _G.FWHUD_CheckEnchantsEquipped()
        local _, eMH = _G.FWHUD_CheckWeaponEquipped and _G.FWHUD_CheckWeaponEquipped(16)
        local _, eOH = _G.FWHUD_CheckWeaponEquipped and _G.FWHUD_CheckWeaponEquipped(17)
        local activeEID = eMH or eOH
        local eInfo = activeEID and _G.FWHUD_WeaponEnchantDB and _G.FWHUD_WeaponEnchantDB[activeEID]
        local defIcon = (eInfo and eInfo.icon) or GetInventoryItemTexture("player", 16) or GetInventoryItemTexture("player", 17) or "Interface\\Icons\\Spell_Nature_BloodLust"
        if not hasEnchant then
            return "NONE", 0, 0, 0, defIcon
        end

        local now = GetTime()
        local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
        local bList = buffs and buffs.list or {}

        local activeProcs = {}
        local berserkCount = 0

        for _, b in ipairs(bList) do
            local sId = b.spellId
            local name = b.name or ""
            if sId == 59620 or name == "Berserking" or name == "Furia Berserker" then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 15
                local dur = (b.duration and b.duration > 0) and b.duration or 15
                local c = (b.count and b.count > 0) and b.count or 1
                berserkCount = berserkCount + c
                table.insert(activeProcs, {
                    rem = rem,
                    dur = dur,
                    icon = b.icon or "Interface\\Icons\\Spell_Nature_BloodLust",
                    spellId = 59620
                })
            elseif sId == 28093 or name:find("Mongoose") then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 15
                local dur = (b.duration and b.duration > 0) and b.duration or 15
                table.insert(activeProcs, {
                    rem = rem,
                    dur = dur,
                    icon = b.icon or "Interface\\Icons\\Spell_Nature_PosisonSpike",
                    spellId = 28093
                })
            elseif sId == 42976 or name:find("Executioner") then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 15
                local dur = (b.duration and b.duration > 0) and b.duration or 15
                table.insert(activeProcs, {
                    rem = rem,
                    dur = dur,
                    icon = b.icon or "Interface\\Icons\\INV_Sword_48",
                    spellId = 42976
                })
            elseif sId == 59626 or name:find("Black Magic") then
                local rem = (b.expirationTime and b.expirationTime > 0) and (b.expirationTime - now) or 10
                local dur = (b.duration and b.duration > 0) and b.duration or 10
                table.insert(activeProcs, {
                    rem = rem,
                    dur = dur,
                    icon = b.icon or "Interface\\Icons\\Spell_Shadow_Shadowfury",
                    spellId = 59626
                })
            end
        end

        if berserkCount >= 2 and #activeProcs == 1 then
            local r1 = _G.FWHUD_WeaponState[16].isProc and (_G.FWHUD_WeaponState[16].lastEnd - now) or activeProcs[1].rem
            local r2 = _G.FWHUD_WeaponState[17].isProc and (_G.FWHUD_WeaponState[17].lastEnd - now) or activeProcs[1].rem
            activeProcs[1].rem = r1
            table.insert(activeProcs, {
                rem = r2,
                dur = 15,
                icon = activeProcs[1].icon,
                spellId = 59620
            })
        end

        if #activeProcs == 0 then
            for _, s in ipairs({ 16, 17 }) do
                local st = _G.FWHUD_WeaponState[s]
                if st and st.isProc and st.lastEnd and (st.lastEnd - now > 0.05) then
                    table.insert(activeProcs, {
                        rem = st.lastEnd - now,
                        dur = 15,
                        icon = defIcon,
                        spellId = 59620
                    })
                end
            end
        end

        local totalCount = math.max(#activeProcs, berserkCount)

        if #activeProcs > 1 then
            table.sort(activeProcs, function(a, b) return a.rem < b.rem end)
        end

        if #activeProcs > 0 and activeProcs[1].rem > 0.05 then
            local fifo = activeProcs[1]
            return "ACTIVE", fifo.rem, fifo.dur, totalCount, fifo.icon
        end

        return "READY", 0, 0, 0, defIcon
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
        local hasRing = _G.FWHUD_CheckRingEquipped and _G.FWHUD_CheckRingEquipped()
        local hasCloak = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped(15)
        local hasTier = _G.FWHUD_CheckTierSetEquipped and _G.FWHUD_CheckTierSetEquipped()
        local hasEnchant = _G.FWHUD_CheckEnchantsEquipped and _G.FWHUD_CheckEnchantsEquipped()
        local hasGloves = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped(10)
        local hasBoots = _G.FWHUD_CheckSlotEquipped and _G.FWHUD_CheckSlotEquipped(8)

        local activeOrder = {}
        if hasT1 then table.insert(activeOrder, "05 - Trinket 1 warDPS") end
        if hasT2 then table.insert(activeOrder, "06 - Trinket 2 warDPS") end
        if hasRing then table.insert(activeOrder, "06b - Ring warDPS") end
        if hasCloak then table.insert(activeOrder, "07 - Cloak warDPS") end
        if hasTier then table.insert(activeOrder, "08 - Tier Set warDPS") end
        if hasEnchant then table.insert(activeOrder, "09 - Enchants warDPS") end
        if hasGloves then table.insert(activeOrder, "10 - Gloves warDPS") end
        table.insert(activeOrder, "11 - Death Wish")
        table.insert(activeOrder, "12 - Recklessness")
        if hasBoots then table.insert(activeOrder, "13 - Boots warDPS") end

        local N = #activeOrder
        local step = 38
        local targetW = 28
        if N >= 10 then
            step = 27
            targetW = 26
        elseif N == 9 then
            step = 29
            targetW = 28
        elseif N == 8 then
            step = 32
            targetW = 28
        elseif N == 7 then
            step = 38
            targetW = 28
        elseif N == 6 then
            step = 44
            targetW = 28
        elseif N == 5 then
            step = 48
            targetW = 28
        else
            step = 52
            targetW = 28
        end

        for i, id in ipairs(activeOrder) do
            local targetX = math.floor(((i - (N + 1) / 2) * step) + 0.5)
            local regObj = WeakAuras.regions[id]
            local r = regObj and (regObj.region or (regObj.GetPoint and regObj))
            if r and r.ClearAllPoints and r.SetPoint then
                r:ClearAllPoints()
                r:SetPoint("CENTER", group, "CENTER", targetX, -45)
                if r.SetWidth and r.SetHeight then
                    r:SetWidth(targetW)
                    r:SetHeight(targetW)
                end
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
        f:RegisterEvent("SPELL_UPDATE_USABLE")
        f:RegisterEvent("ACTIONBAR_UPDATE_USABLE")
        f:RegisterEvent("UNIT_SPELLCAST_SUCCEEDED")
        f.pendingUpdates = 0

        local playerGUID = nil
        f:SetScript("OnEvent", function(self, event, ...)
            if event == "UNIT_SPELLCAST_SUCCEEDED" then
                local unit, sName, sRank, lId, sId = ...
                if unit == "player" and (sId == 34428 or sName == "Victory Rush" or sName == "Attacco della Vittoria") then
                    local vr = _G.FWHUD_VRState
                    if vr then
                        vr.isUsable = false
                        vr.lastEnd = 0
                    end
                end
                return
            end
            if event == "COMBAT_LOG_EVENT_UNFILTERED" then
                local timestamp, subEvent, sourceGUID, sourceName, sourceFlags, destGUID, destName, destFlags, spellId, spellName = ...
                if not playerGUID then playerGUID = UnitGUID("player") end
                local isPlayer = (destGUID == playerGUID or sourceGUID == playerGUID)
                if isPlayer then
                    local now = GetTime()
                    if subEvent == "PARTY_KILL" and sourceGUID == playerGUID then
                        local vr = _G.FWHUD_VRState
                        if vr then
                            vr.lastStart = now
                            vr.lastEnd = now + 20.0
                            vr.isUsable = true
                        end
                    end
                    if (subEvent == "SPELL_CAST_SUCCESS") and sourceGUID == playerGUID and (spellId == 34428 or spellName == "Victory Rush" or spellName == "Attacco della Vittoria") then
                        local vr = _G.FWHUD_VRState
                        if vr then
                            vr.isUsable = false
                            vr.lastEnd = 0
                        end
                    end
                    if subEvent == "SPELL_CAST_SUCCESS" or subEvent == "SPELL_AURA_APPLIED" or subEvent == "SPELL_AURA_REFRESH" then
                        -- Check Trinkets Proc (slot 13 & 14)
                        for _, s in ipairs({ 13, 14 }) do
                            local tID = GetInventoryItemID and GetInventoryItemID("player", s)
                            local tEntry = tID and _G.FWHUD_TrinketDB and _G.FWHUD_TrinketDB[tID]
                            local isTMatch = false
                            if tEntry then
                                if spellId and tEntry.spellIds and tEntry.spellIds[spellId] then
                                    isTMatch = true
                                elseif spellName and tEntry.keywords then
                                    local snClean = spellName:lower():gsub("[%s%p%c]", "")
                                    for _, kw in ipairs(tEntry.keywords) do
                                        if snClean:find(kw:lower():gsub("[%s%p%c]", ""), 1, true) then
                                            isTMatch = true
                                            break
                                        end
                                    end
                                end
                            end
                            if isTMatch then
                                local sICD = _G.FWHUD_ICD and _G.FWHUD_ICD[s]
                                if sICD then
                                    sICD.lastStart = now
                                    sICD.lastEnd = now + (tEntry.icd or 45)
                                    sICD.isProc = true
                                    if WeakAuras and WeakAuras.ScanEvents then
                                        WeakAuras.ScanEvents("FWHUD_ROW_UPDATE")
                                    end
                                end
                            end
                        end

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
                        elseif spellId == 72412 or spellId == 72414 or spellId == 72410 or spellId == 35081 or spellName == "Frostforged Champion" or spellName == "Campione Forgiagelo" or spellName == "Eternal Champion" then
                            _G.FWHUD_RingState.lastStart = now
                            _G.FWHUD_RingState.lastEnd = now + 60
                            _G.FWHUD_RingState.isProc = true
                            if WeakAuras and WeakAuras.ScanEvents then WeakAuras.ScanEvents("FWHUD_ROW_UPDATE") end
                        elseif spellId == 59620 or spellName == "Berserking" or spellName == "Furia Berserker" then
                            local s16Active = _G.FWHUD_WeaponState[16].isProc and (_G.FWHUD_WeaponState[16].lastEnd > now)
                            local s17Active = _G.FWHUD_WeaponState[17].isProc and (_G.FWHUD_WeaponState[17].lastEnd > now)
                            if s16Active and not s17Active then
                                _G.FWHUD_WeaponState[17].lastStart = now
                                _G.FWHUD_WeaponState[17].lastEnd = now + 15
                                _G.FWHUD_WeaponState[17].isProc = true
                            elseif not s16Active then
                                _G.FWHUD_WeaponState[16].lastStart = now
                                _G.FWHUD_WeaponState[16].lastEnd = now + 15
                                _G.FWHUD_WeaponState[16].isProc = true
                            else
                                local targetSlot = (_G.FWHUD_WeaponState[16].lastEnd <= _G.FWHUD_WeaponState[17].lastEnd) and 16 or 17
                                _G.FWHUD_WeaponState[targetSlot].lastStart = now
                                _G.FWHUD_WeaponState[targetSlot].lastEnd = now + 15
                                _G.FWHUD_WeaponState[targetSlot].isProc = true
                            end
                            if WeakAuras and WeakAuras.ScanEvents then WeakAuras.ScanEvents("FWHUD_ROW_UPDATE") end
                        end
                    elseif subEvent == "SPELL_AURA_REMOVED" then
                        for _, s in ipairs({ 13, 14 }) do
                            local tID = GetInventoryItemID and GetInventoryItemID("player", s)
                            local tEntry = tID and _G.FWHUD_TrinketDB and _G.FWHUD_TrinketDB[tID]
                            local isTMatch = false
                            if tEntry then
                                if spellId and tEntry.spellIds and tEntry.spellIds[spellId] then
                                    isTMatch = true
                                elseif spellName and tEntry.keywords then
                                    local snClean = spellName:lower():gsub("[%s%p%c]", "")
                                    for _, kw in ipairs(tEntry.keywords) do
                                        if snClean:find(kw:lower():gsub("[%s%p%c]", ""), 1, true) then
                                            isTMatch = true
                                            break
                                        end
                                    end
                                end
                            elseif spellName and _G.FWHUD_AllMeleeKeywords then
                                local snClean = spellName:lower():gsub("[%s%p%c]", "")
                                for _, kw in ipairs(_G.FWHUD_AllMeleeKeywords) do
                                    if snClean:find(kw:lower():gsub("[%s%p%c]", ""), 1, true) then
                                        isTMatch = true
                                        break
                                    end
                                end
                            end
                            if isTMatch then
                                local sICD = _G.FWHUD_ICD and _G.FWHUD_ICD[s]
                                if sICD then
                                    sICD.isProc = false
                                    if WeakAuras and WeakAuras.ScanEvents then
                                        WeakAuras.ScanEvents("FWHUD_ROW_UPDATE")
                                    end
                                end
                            end
                        end
                        if spellId == 59620 or spellName == "Berserking" or spellName == "Furia Berserker" then
                            local buffs = _G.FWHUD_GetPlayerBuffs and _G.FWHUD_GetPlayerBuffs()
                            local bCount = 0
                            if buffs then
                                for _, b in ipairs(buffs.list or {}) do
                                    if b.spellId == 59620 or (b.name and (b.name == "Berserking" or b.name == "Furia Berserker")) then
                                        bCount = bCount + (b.count and b.count > 0 and b.count or 1)
                                    end
                                end
                            end
                            if bCount == 0 then
                                _G.FWHUD_WeaponState[16].isProc = false
                                _G.FWHUD_WeaponState[17].isProc = false
                            elseif bCount == 1 then
                                if _G.FWHUD_WeaponState[16].lastEnd <= _G.FWHUD_WeaponState[17].lastEnd then
                                    _G.FWHUD_WeaponState[16].isProc = false
                                else
                                    _G.FWHUD_WeaponState[17].isProc = false
                                end
                            end
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
            _G.FWHUD_WeaponEquipCache = nil
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
def make_ring_custom_text() -> str:
    """Testo descrittivo del proc dell'anello (%c), con pixel glow su proc attivo e timer ICD."""
    return """function()
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if _G.FWHUD_UpdateUtilityRowPositions then
        _G.FWHUD_UpdateUtilityRowPositions()
    end
    if not _G.FWHUD_CheckRing then return "" end
    local state, rem, dur, icon, isEquipped = _G.FWHUD_CheckRing()
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)
    local glowKey = "FWHUD_RING_GLOW"
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


def make_ring_custom_duration() -> str:
    """Durata e scadenza dello swipe di ricarica/ICD per l'anello."""
    return """function()
    if not _G.FWHUD_CheckRing then return 0, 0 end
    local state, rem, dur = _G.FWHUD_CheckRing()
    if (state == "ACTIVE" or state == "ICD" or state == "COOLDOWN") and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_ring_custom_icon() -> str:
    """Icona dinamica dell'anello equipaggiato o del proc attivo."""
    return """function()
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if _G.FWHUD_CheckRing then
        local state, rem, dur, icon = _G.FWHUD_CheckRing()
        if icon then return icon end
    end
    return "Interface\\Icons\\INV_Jewelry_Ring_81"
end"""


def make_ring_trigger_custom() -> str:
    """Trigger custom per verificare se un anello con proc è equipaggiato."""
    return """function(event, ...)
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if not _G.FWHUD_CheckRingEquipped then return false end
    return _G.FWHUD_CheckRingEquipped()
end"""


def make_ring_untrigger_custom() -> str:
    """Untrigger custom per l'anello con proc."""
    return """function(event, ...)
    if not _G.FWHUD_CheckRingEquipped then return true end
    return not _G.FWHUD_CheckRingEquipped()
end"""


def make_weapon_custom_text(slot: int) -> str:
    """Testo descrittivo dell'incanto arma (%c) per slot 16 (MH) o 17 (OH), con pixel glow su proc attivo."""
    return f"""function()
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if _G.FWHUD_UpdateUtilityRowPositions then
        _G.FWHUD_UpdateUtilityRowPositions()
    end
    if not _G.FWHUD_CheckWeapon then return "" end
    local state, rem, dur, icon, slotLabel = _G.FWHUD_CheckWeapon({slot})
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)
    local glowKey = "FWHUD_WEAPON_{slot}_GLOW"
    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {{{{1, 0.45, 0.1, 1}}}}, 8, 0.25, 10, 2, 0, 0, false, glowKey)
        end
        return string.format("|cFFFFFF00%.1fs|r", rem)
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, glowKey)
        end
        return ""
    end
end"""


def make_weapon_custom_duration(slot: int) -> str:
    """Durata e scadenza dello swipe di proc attivo per l'arma indicata."""
    return f"""function()
    if not _G.FWHUD_CheckWeapon then return 0, 0 end
    local state, rem, dur = _G.FWHUD_CheckWeapon({slot})
    if state == "ACTIVE" and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_weapon_custom_icon(slot: int) -> str:
    """Icona dinamica dell'arma equipaggiata o dell'incanto attivo."""
    return f"""function()
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if _G.FWHUD_CheckWeapon then
        local state, rem, dur, icon = _G.FWHUD_CheckWeapon({slot})
        if icon then return icon end
    end
    return GetInventoryItemTexture("player", {slot}) or "Interface\\Icons\\Spell_Nature_BloodLust"
end"""


def make_weapon_trigger_custom(slot: int) -> str:
    """Trigger custom per verificare se l'arma nello slot 16 o 17 è equipaggiata con incanto."""
    return f"""function(event, ...)
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if not _G.FWHUD_CheckWeaponEquipped then return false end
    local hasW = _G.FWHUD_CheckWeaponEquipped({slot})
    return hasW == true
end"""


def make_weapon_untrigger_custom(slot: int) -> str:
    """Untrigger custom per l'arma."""
    return f"""function(event, ...)
    if not _G.FWHUD_CheckWeaponEquipped then return true end
    local hasW = _G.FWHUD_CheckWeaponEquipped({slot})
    return not hasW
end"""


def make_slot_custom_text(slot: int) -> str:
    """Testo descrittivo del monile/mantello/guanti/scarpe (%c), con pixel glow su proc attivo e riposizionamento dinamico."""
    bootstrap = f"""    _G.FWHUD_InitCore = _G.FWHUD_InitCore or {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}
    if not _G.FWHUD_CoreInitDone then _G.FWHUD_InitCore() end""" if slot == 13 else """    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end"""
    return f"""function()
{bootstrap}
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
    bootstrap = f"""    _G.FWHUD_InitCore = _G.FWHUD_InitCore or {SHARED_WARRIOR_CORE_BOOTSTRAP_LUA}
    if not _G.FWHUD_CoreInitDone then _G.FWHUD_InitCore() end""" if slot == 13 else """    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end"""
    return f"""function(event, ...)
{bootstrap}
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
    return """function()
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if _G.FWHUD_UpdateUtilityRowPositions then
        _G.FWHUD_UpdateUtilityRowPositions()
    end
    if not _G.FWHUD_CheckTierSet then return "" end
    local state, rem, dur, count, icon, subType = _G.FWHUD_CheckTierSet()
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)
    local glowKey = "FWHUD_TIER_GLOW"
    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {1, 0.85, 0.1, 1}, 8, 0.25, 10, 2, 0, 0, false, glowKey)
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
    return """function(event, ...)
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if not _G.FWHUD_CheckTierSetEquipped then return false end
    return _G.FWHUD_CheckTierSetEquipped()
end"""


def make_tierset_untrigger_custom() -> str:
    return """function(event, ...)
    if not _G.FWHUD_CheckTierSetEquipped then return true end
    return not _G.FWHUD_CheckTierSetEquipped()
end"""


def make_enchants_custom_text() -> str:
    """Testo descrittivo incanti arma unificati: timer FIFO in basso (%c1), cariche (x2) in alto (%c2), con pixel glow."""
    return """function()
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if _G.FWHUD_UpdateUtilityRowPositions then
        _G.FWHUD_UpdateUtilityRowPositions()
    end
    if not _G.FWHUD_CheckEnchants then return "", "" end
    local state, rem, dur, count, icon = _G.FWHUD_CheckEnchants()
    local LCG = LibStub and LibStub("LibCustomGlow-1.0", true)
    local glowKey = "FWHUD_ENCHANT_GLOW"
    local timerText = ""
    local stackText = ""

    if state == "ACTIVE" then
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Start(aura_env.region, {1, 0.85, 0.1, 1}, 8, 0.25, 10, 2, 0, 0, false, glowKey)
        end
        if count and count > 1 then
            stackText = string.format("|cFFFFFF00x%d|r", count)
        end
        if rem > 0 then
            timerText = string.format("|cFFFFFF00%.1fs|r", rem)
        end
    else
        if LCG and aura_env and aura_env.region then
            LCG.PixelGlow_Stop(aura_env.region, glowKey)
        end
    end

    return timerText, stackText
end"""


def make_enchants_custom_duration() -> str:
    """Durata e scadenza dello swipe per il proc FIFO dell'incanto arma."""
    return """function()
    if not _G.FWHUD_CheckEnchants then return 0, 0 end
    local state, rem, dur = _G.FWHUD_CheckEnchants()
    if state == "ACTIVE" and rem > 0 and dur > 0 then
        return dur, GetTime() + rem
    end
    return 0, 0
end"""


def make_enchants_custom_icon() -> str:
    """Icona dinamica dell'incanto attivo (Berserking, Mongoose, Executioner) o dell'arma principale."""
    return """function()
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    if _G.FWHUD_CheckEnchants then
        local state, rem, dur, count, icon = _G.FWHUD_CheckEnchants()
        if icon then return icon end
    end
    return GetInventoryItemTexture("player", 16) or "Interface\\Icons\\Spell_Nature_BloodLust"
end"""


def make_enchants_trigger_custom() -> str:
    return """function(event, ...)
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
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


def make_warrior_spell_trigger_custom(spell_id: int) -> str:
    return """function(event, ...)
    if not _G.FWHUD_CoreInitDone and _G.FWHUD_InitCore then _G.FWHUD_InitCore() end
    return true
end"""


def build_utility_auras() -> list[dict]:
    """
    Costruisce e restituisce le 11 aure della riga utility adattiva centrata a y = -45:
    - 05 - Trinket 1 warDPS (Icon, Slot 13)
    - 06 - Trinket 2 warDPS (Icon, Slot 14)
    - 06b - Ring warDPS (Icon, Slot 11/12 - Ashen Band / Eternal Champion)
    - 07 - Cloak warDPS (Icon, Slot 15)
    - 08 - Tier Set warDPS (Icon, T10/T8/T7 Proc & Combinazioni 2P+2P)
    - 09a - Weapon MH warDPS (Icon, Slot 16 - Berserking MH, Mongoose, Executioner)
    - 09b - Weapon OH warDPS (Icon, Slot 17 - Berserking OH, Mongoose, Executioner)
    - 10 - Gloves warDPS (Icon, Slot 10)
    - 11 - Death Wish (Icon, Spell 12292)
    - 12 - Recklessness (Icon, Spell 1719)
    - 13 - Boots warDPS (Icon, Slot 8)
    """
    events_list = "PLAYER_EQUIPMENT_CHANGED,UNIT_INVENTORY_CHANGED,PLAYER_ENTERING_WORLD,ZONE_CHANGED_NEW_AREA,UNIT_AURA,SPELL_UPDATE_COOLDOWN,ACTIONBAR_UPDATE_COOLDOWN,BAG_UPDATE_COOLDOWN,COMBAT_LOG_EVENT_UNFILTERED,FWHUD_ROW_UPDATE"

    return [
        # 05 - Trinket 1 warDPS (Slot 13)
        {
            "id": "05 - Trinket 1 warDPS",
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

        # 06 - Trinket 2 warDPS (Slot 14)
        {
            "id": "06 - Trinket 2 warDPS",
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

        # 06b - Ring warDPS (Slot 11 or 12 - Ashen Band / Eternal Champion)
        {
            "id": "06b - Ring warDPS",
            "uid": "FWHUD_UTIL_RING",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -84,
            "yOffset": -45,
            "width": 28,
            "height": 28,
            "displayIcon": "Interface\\Icons\\INV_Jewelry_Ring_81",
            "cooldown": True,
            "cooldownSwipe": True,
            "cooldownEdge": True,
            "cooldownTextDisabled": True,
            "inverse": False,
            "customTextUpdate": "update",
            "customText": make_ring_custom_text(),
            "triggers": {
                1: {
                    "trigger": {
                        "type": "custom",
                        "custom_type": "status",
                        "check": "update",
                        "events": events_list,
                        "custom": make_ring_trigger_custom(),
                        "customDuration": make_ring_custom_duration(),
                        "customIcon": make_ring_custom_icon(),
                    },
                    "untrigger": {
                        "custom": make_ring_untrigger_custom()
                    }
                },
                "activeTriggerMode": -10,
            },
            "subRegions": [
                {"type": "subbackground"},
                make_subtext("%c", justify="CENTER", anchor_point="CENTER", font_size=10),
            ],
        },

        # 07 - Cloak warDPS (Slot 15)
        {
            "id": "07 - Cloak warDPS",
            "uid": "FWHUD_UTIL_CLOAK",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -56,
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

        # 08 - Tier Set warDPS (T10/T8/T7 Proc & ICD)
        {
            "id": "08 - Tier Set warDPS",
            "uid": "FWHUD_UTIL_TIERSET",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": -28,
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

        # 09 - Enchants warDPS (Slot 16/17: Unified Weapon Enchants with FIFO timer & x2 on top)
        {
            "id": "09 - Enchants warDPS",
            "uid": "FWHUD_UTIL_ENCHANTS",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 0,
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
                make_subtext("%c1", justify="CENTER", anchor_point="INNER_BOTTOM", font_size=10, y_offset=0),
                make_subtext("%c2", justify="CENTER", anchor_point="INNER_TOP", font_size=11, y_offset=-1),
            ],
        },

        # 10 - Gloves warDPS (Slot 10)
        {
            "id": "10 - Gloves warDPS",
            "uid": "FWHUD_UTIL_GLOVES",
            "parent": "Class Warrior (Fury)",
            "regionType": "icon",
            "internalVersion": 52,
            "xOffset": 56,
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
            "xOffset": 84,
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
            "xOffset": 112,
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

        # 13 - Boots warDPS (Slot 8)
        {
            "id": "13 - Boots warDPS",
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
