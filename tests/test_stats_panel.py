import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.components.stats import build_stats_auras, make_stats_custom_text

    auras = build_stats_auras()
    assert len(auras) == 3, f"Expected 3 auras in stats panel, got {len(auras)}"

    grp = auras[0]
    assert grp["id"] == "18 - Stats Panel warDPS"
    assert grp["regionType"] == "group"

    bg = auras[1]
    assert bg["id"] == "Stats Panel - Background warDPS"
    assert bg["width"] == 88 and bg["height"] == 60, f"Expected 88x60, got {bg['width']}x{bg['height']}"

    text_aura = auras[2]
    assert text_aura["id"] == "Stats Panel - Text warDPS"
    assert text_aura["displayText"] == "%c"
    lua_code = text_aura.get("customText", "")

    # Verify key logic in Lua
    assert "UnitAttackPower" in lua_code, "Manca UnitAttackPower in customText"
    assert "GetCritChance" in lua_code, "Manca GetCritChance in customText"
    assert "Heart of the Crusader" in lua_code, "Manca Heart of the Crusader debuff in customText"
    assert "Master Poisoner" in lua_code, "Manca Master Poisoner debuff in customText"
    assert "Totem of Wrath" in lua_code, "Manca Totem of Wrath debuff in customText"

    # Haste checks
    assert "GetCombatRatingBonus(18)" in lua_code, "Manca GetCombatRatingBonus(18) (Melee Haste) in customText"
    assert "Windfury Totem" in lua_code, "Manca Windfury Totem in customText"
    assert "Improved Icy Talons" in lua_code, "Manca Improved Icy Talons in customText"
    assert "Swift Retribution" in lua_code, "Manca Swift Retribution in customText"
    assert "Flurry" in lua_code, "Manca Flurry in customText"
    assert "Bloodlust" in lua_code, "Manca Bloodlust in customText"
    assert "Power Infusion" not in lua_code, "Power Infusion non deve influire sulla Melee Haste del Warrior"
    assert "10060" not in lua_code, "Spell ID 10060 (Power Infusion) non deve influire sulla Melee Haste del Warrior"

    # ArP and Hit/Exp checks
    assert "GetCombatRating(25)" in lua_code, "Manca Combat Rating 25 (ArP) in customText"
    assert "1400" in lua_code, "Manca verifica Hard Cap 1400 ArP in customText"
    assert "GetCombatRating(6)" in lua_code, "Manca Hit Rating in customText"
    assert "Heroic Presence" in lua_code, "Manca Heroic Presence (Draenei hit) in customText"
    assert "GetExpertise" in lua_code, "Manca GetExpertise in customText"

    print("[OK] Logica di calcolo matematico, buff, debuff, totem e formattazione Haste verificata.")
    print("[PASS] test_stats_panel.py superato con successo!")

if __name__ == "__main__":
    run_tests()
