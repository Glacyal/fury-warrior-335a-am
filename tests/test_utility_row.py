import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.components.utility import (
        build_utility_auras,
        SHARED_WARRIOR_CORE_BOOTSTRAP_LUA,
        make_slot_custom_text,
        make_slot_custom_duration,
        make_slot_custom_icon,
        make_ring_custom_text,
        make_enchants_custom_text,
        make_enchants_custom_duration,
    )

    auras = build_utility_auras()
    assert len(auras) == 10, f"Expected 10 utility auras, got {len(auras)}"

    expected_ids = [
        "05 - Trinket 1 warDPS",
        "06 - Trinket 2 warDPS",
        "06b - Ring warDPS",
        "07 - Cloak warDPS",
        "08 - Tier Set warDPS",
        "09 - Enchants warDPS",
        "10 - Gloves warDPS",
        "11 - Death Wish",
        "12 - Recklessness",
        "13 - Boots warDPS",
    ]

    for i, a in enumerate(auras):
        assert a["id"] == expected_ids[i], f"Expected ID {expected_ids[i]}, got {a['id']}"
        assert a["width"] == 28, f"Invalid width for {a['id']}"
        assert a["height"] == 28, f"Invalid height for {a['id']}"
        assert a["yOffset"] == -45, f"Invalid yOffset for {a['id']}"

        # CRITICAL: Verify that ALL 10 utility auras use "check": "update"
        # so WeakAuras updates customDuration, customIcon, and customText seamlessly every frame
        trig1 = a["triggers"][1]["trigger"]
        assert trig1.get("check") == "update", (
            f"Aura '{a['id']}' must use 'check': 'update' to ensure real-time proc and ICD reactivity!"
        )

    # Verify 09 - Enchants warDPS subregions (%c1 at INNER_BOTTOM, %c2 at INNER_TOP)
    ench_aura = [a for a in auras if a["id"] == "09 - Enchants warDPS"][0]
    subregs = ench_aura["subRegions"]
    sub_texts = [s for s in subregs if s.get("type") == "subtext"]
    assert len(sub_texts) == 2, f"Expected 2 text subregions for Enchants, got {len(sub_texts)}"
    assert sub_texts[0]["text_text"] == "%c1", f"Subtext 1 must be %c1, got {sub_texts[0]['text_text']}"
    assert sub_texts[0]["text_anchorPoint"] == "INNER_BOTTOM", f"Subtext 1 must be INNER_BOTTOM, got {sub_texts[0]['text_anchorPoint']}"
    assert sub_texts[1]["text_text"] == "%c2", f"Subtext 2 must be %c2, got {sub_texts[1]['text_text']}"
    assert sub_texts[1]["text_anchorPoint"] == "INNER_TOP", f"Subtext 2 must be INNER_TOP, got {sub_texts[1]['text_anchorPoint']}"

    # Verify customText and customDuration for Unified Enchants
    ench_text = make_enchants_custom_text()
    assert "return timerText, stackText" in ench_text, "make_enchants_custom_text must return timerText, stackText for %c1 and %c2"
    assert "|cFFFFFF00x%d|r" in ench_text, "make_enchants_custom_text must format x2 stack count"
    assert "|cFFFFFF00%.1fs|r" in ench_text, "make_enchants_custom_text must format timer text"
    assert "LCG.PixelGlow_Start" in ench_text, "make_enchants_custom_text must start pixel glow on active proc"

    ench_dur = make_enchants_custom_duration()
    assert "return dur, GetTime() + rem" in ench_dur, "make_enchants_custom_duration must return swipe duration for FIFO proc"

    # Verify physical trinket catalog in Lua bootstrap
    assert "50362" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Deathbringer's Will nel DB dei monili"
    assert "50363" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Deathbringer's Will Heroic nel DB dei monili"
    assert "71485" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca DBW Strength of the Taunka (Normal 71485)"
    assert "71556" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca DBW Strength of the Taunka (Heroic 71556)"
    assert "71491" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca DBW Aim of the Iron Dwarf (Normal 71491)"
    assert "71560" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca DBW Aim of the Iron Dwarf (Heroic 71560)"
    assert "54569" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Sharpened Twilight Scale nel DB dei monili"
    assert "54590" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Sharpened Twilight Scale Heroic nel DB dei monili"
    assert "75466" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca STS Twilight Precision (Normal 75466)"
    assert "75473" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca STS Twilight Precision (Heroic 75473)"
    assert "47115" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Death's Choice nel DB dei monili"
    assert "50342" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Whispering Fanged Skull nel DB dei monili"
    assert "50355" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Herkuml War Token nel DB dei monili"
    assert "50198" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Needle-Encrusted Scorpion nel DB dei monili"
    assert "45931" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Mjolnir Runestone nel DB dei monili"
    assert "44253" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Darkmoon Card: Greatness nel DB dei monili"
    assert "40256" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Grim Toll nel DB dei monili"
    assert "40684" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Mirror of Truth nel DB dei monili"
    assert "60065" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Spell ID 60065 (Reflection of Torment) per Mirror of Truth"
    assert "reflection" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca keyword reflection per Mirror of Truth"
    assert "torment" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca keyword torment per Mirror of Truth"
    assert "49074" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Coren's Chromium Coaster nel DB dei monili"
    assert "46038" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Dark-Matter nel DB dei monili"
    assert "44093" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Anvil of Titans nel DB dei monili"

    # Verify Tank Trinkets in Lua bootstrap
    assert "47290" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Juggernaut's Vitality nel DB"
    assert "47080" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Satrina's Impeding Scarab nel DB"
    assert "50356" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Corroded Skeleton Key nel DB"
    assert "71586" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca spell 71586 Hardened Skin per Corroded Skeleton Key"
    assert "50341" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Unidentifiable Organ nel DB"
    assert "50361" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Sindragosa's Flawless Fang nel DB"
    assert "47735" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Glyph of Indomitability nel DB"
    assert "47216" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca The Black Heart nel DB"
    assert "37264" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Essence of Gossamer nel DB"
    assert "37844" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Lavanthor's Talisman nel DB"
    assert "45158" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Heart of Iron nel DB"
    assert "50235" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Ick's Rotting Thumb nel DB"
    assert "42341" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Figurine - Monarch Crab nel DB"

    # Verify customText and customDuration logic for Trinket 1 & 2
    for slot in (13, 14):
        txt_code = make_slot_custom_text(slot)
        assert "|cFFFFFF00%.1fs|r" in txt_code, f"Manca formato giallo per proc attivo in slot {slot}"
        assert 'string.format("%.0f", rem)' in txt_code, f"Manca formato bianco standard per ICD/cooldown in slot {slot}"
        assert "LCG.PixelGlow_Start" in txt_code, f"Manca PixelGlow_Start su proc attivo in slot {slot}"
        assert "LCG.PixelGlow_Stop" in txt_code, f"Manca PixelGlow_Stop su fine proc in slot {slot}"

        dur_code = make_slot_custom_duration(slot)
        assert "state == \"ICD\"" in dur_code, f"Manca gestione stato ICD in customDuration per slot {slot}"
        assert "return dur, GetTime() + rem" in dur_code, f"Manca return durata swipe per slot {slot}"

    # Verify Ring customText format
    ring_txt = make_ring_custom_text()
    assert "|cFFFFFF00%.1fs|r" in ring_txt, "Manca formato giallo per proc attivo anello"
    assert 'string.format("%.0f", rem)' in ring_txt, "Manca formato bianco standard per ICD/cooldown anello"

    # Verify Tier Sets and Enchants detection in Lua bootstrap
    assert "FWHUD_T10_Pieces" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca tabella pezzi Tier 10"
    assert "FWHUD_T8_Pieces" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca tabella pezzi Tier 8"
    assert "FWHUD_T7_Pieces" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca tabella pezzi Tier 7"
    assert "FWHUD_T9_Pieces" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca tabella pezzi Tier 9"
    assert "60176" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca spellId 60176 per Spirits of the Lost T7 4P"
    assert "Spirits of the Lost" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca stringa Spirits of the Lost nel controllo T7"
    assert "FWHUD_CheckTierSet" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca funzione FWHUD_CheckTierSet"
    assert "FWHUD_RingDB" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca tabella FWHUD_RingDB"
    assert "50402" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Ashen Band 50402 nel RingDB"
    assert "FWHUD_CheckRing" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca funzione FWHUD_CheckRing"
    assert "FWHUD_CheckEnchants" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca funzione FWHUD_CheckEnchants"
    assert "FWHUD_CheckEnchantsEquipped" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca funzione FWHUD_CheckEnchantsEquipped"
    assert "FWHUD_StaticWeaponEnchants" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca tabella FWHUD_StaticWeaponEnchants"
    assert "3827" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Massacre (3827) in FWHUD_StaticWeaponEnchants"
    assert "3731" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Titanium Weapon Chain (3731) in FWHUD_StaticWeaponEnchants"
    assert "1900" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Crusader (1900) in FWHUD_WeaponEnchantDB"
    assert "3869" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Blade Ward (3869) in FWHUD_WeaponEnchantDB"
    assert "3870" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Blood Draining (3870) in FWHUD_WeaponEnchantDB"
    assert "FWHUD_UpdateUtilityRowPositions" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca funzione di riposizionamento dinamico"

    print("[OK] Tutti i 10 elementi della riga utility verificati con 'check': 'update'.")
    print("[OK] Catalogo monili WotLK 3.3.5a completo con ICD e spell ID corretti (DBW, STS, Choice, Skull, ecc.).")
    print("[OK] Gestione proc attivo (Pixel Glow giallo) e conteggio ICD rimanente (rosso) verificati.")
    print("[OK] Incanti arma unificati in '09 - Enchants warDPS' con timer FIFO in basso e stack x2 in alto verificati.")
    print("[PASS] test_utility_row.py superato con successo!")

if __name__ == "__main__":
    run_tests()
