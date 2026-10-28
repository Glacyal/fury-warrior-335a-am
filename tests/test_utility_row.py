import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.components.utility import build_utility_auras, SHARED_WARRIOR_CORE_BOOTSTRAP_LUA

    auras = build_utility_auras()
    assert len(auras) == 11, f"Expected 11 utility auras, got {len(auras)}"

    expected_ids = [
        "05 - Trinket 1 warDPS",
        "06 - Trinket 2 warDPS",
        "06b - Ring warDPS",
        "07 - Cloak warDPS",
        "08 - Tier Set warDPS",
        "09a - Weapon MH warDPS",
        "09b - Weapon OH warDPS",
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

    # Verify physical trinket catalog in Lua bootstrap
    assert "50362" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Deathbringer's Will nel DB dei monili"
    assert "54569" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Sharpened Twilight Scale nel DB dei monili"
    assert "47115" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Death's Choice nel DB dei monili"
    assert "50342" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Whispering Fanged Skull nel DB dei monili"
    assert "50355" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Herkuml War Token nel DB dei monili"
    assert "50198" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Needle-Encrusted Scorpion nel DB dei monili"
    assert "45931" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Mjolnir Runestone nel DB dei monili"
    assert "44253" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Darkmoon Card: Greatness nel DB dei monili"
    assert "40256" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Grim Toll nel DB dei monili"
    assert "40684" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Mirror of Truth nel DB dei monili"

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
    assert "FWHUD_WeaponEnchantDB" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca FWHUD_WeaponEnchantDB"
    assert "FWHUD_CheckWeapon" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca funzione FWHUD_CheckWeapon"
    assert "FWHUD_UpdateUtilityRowPositions" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca funzione di riposizionamento dinamico"

    print("[OK] Tutti gli 11 elementi della riga utility e il catalogo Tier Sets/Trinkets verificati con successo.")
    print("[PASS] test_utility_row.py superato con successo!")

if __name__ == "__main__":
    run_tests()
