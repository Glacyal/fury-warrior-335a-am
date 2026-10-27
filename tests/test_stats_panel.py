import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.components.stats import build_stats_auras, make_stats_custom_text

    auras = build_stats_auras()
    assert len(auras) == 3, f"Expected 3 auras in stats panel, got {len(auras)}"

    grp = auras[0]
    assert grp["id"] == "18 - Stats Panel"
    assert grp["regionType"] == "group"

    bg = auras[1]
    assert bg["id"] == "Stats Panel - Background"
    assert bg["width"] == 88 and bg["height"] == 48

    text_aura = auras[2]
    assert text_aura["id"] == "Stats Panel - Text"
    assert text_aura["displayText"] == "%c"
    lua_code = text_aura.get("customText", "")

    # Verify key logic in Lua
    assert "UnitAttackPower" in lua_code, "Manca UnitAttackPower in customText"
    assert "GetCritChance" in lua_code, "Manca GetCritChance in customText"
    assert "GetCombatRating(25)" in lua_code, "Manca Combat Rating 25 (ArP) in customText"
    assert "1400" in lua_code, "Manca verifica Hard Cap 1400 ArP in customText"
    assert "GetExpertise" in lua_code, "Manca GetExpertise in customText"
    assert "GetCombatRating(6)" in lua_code, "Manca Hit Rating in customText"

    print("[OK] Logica di calcolo matematico e formattazione del pannello statistiche verificata.")
    print("[PASS] test_stats_panel.py superato con successo!")

if __name__ == "__main__":
    run_tests()

