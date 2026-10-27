import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.components.utility import build_utility_auras, SHARED_WARRIOR_CORE_BOOTSTRAP_LUA

    auras = build_utility_auras()
    assert len(auras) == 9, f"Expected 9 utility auras, got {len(auras)}"

    expected_ids = [
        "05 - Trinket 1",
        "06 - Trinket 2",
        "07 - Cloak",
        "08 - Death Wish",
        "09 - Gloves",
        "10 - Recklessness",
        "11 - Shattering Throw",
        "12 - Enraged Regeneration",
        "13 - Boots",
    ]

    for i, a in enumerate(auras):
        assert a["id"] == expected_ids[i], f"Expected ID {expected_ids[i]}, got {a['id']}"
        assert a["width"] == 28, f"Invalid width for {a['id']}"
        assert a["height"] == 28, f"Invalid height for {a['id']}"
        assert a["yOffset"] == -45, f"Invalid yOffset for {a['id']}"

    # Verify trinket DB in Lua bootstrap
    assert "50362" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Deathbringer's Will nel DB dei monili"
    assert "54569" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca Sharpened Twilight Scale nel DB dei monili"
    assert "FWHUD_UpdateUtilityRowPositions" in SHARED_WARRIOR_CORE_BOOTSTRAP_LUA, "Manca funzione di riposizionamento dinamico"

    print("[OK] Tutti i 9 elementi della riga utility adattiva verificati con successo.")
    print("[PASS] test_utility_row.py superato con successo!")

if __name__ == "__main__":
    run_tests()

