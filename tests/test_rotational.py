import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.components.rotational import build_rotational_auras, SHARED_SWING_TIMER_LUA

    auras = build_rotational_auras()
    assert len(auras) == 5, f"Expected 5 auras in rotational bar, got {len(auras)}"

    grp = auras[0]
    assert grp["id"] == "15 - Rotational Bar"
    assert grp["regionType"] == "group"
    assert len(grp["controlledChildren"]) == 4

    bg = auras[1]
    assert bg["width"] == 278 and bg["height"] == 7

    mh = auras[2]
    assert mh["id"] == "Rotational Bar - MH Swing"
    assert mh["width"] == 137 and mh["height"] == 5
    assert mh["xOffset"] == -70.5

    oh = auras[3]
    assert oh["id"] == "Rotational Bar - OH Swing"
    assert oh["width"] == 137 and oh["height"] == 5
    assert oh["xOffset"] == 70.5

    hsq = auras[4]
    assert hsq["id"] == "Rotational Bar - HS Queued"
    assert hsq["width"] == 278 and hsq["height"] == 7

    # Verify swing lua logic
    assert "SWING_DAMAGE" in SHARED_SWING_TIMER_LUA, "Manca evento SWING_DAMAGE in swing timer"
    assert "IsCurrentSpell" in SHARED_SWING_TIMER_LUA, "Manca IsCurrentSpell in swing timer"
    assert "47450" in SHARED_SWING_TIMER_LUA, "Manca Spell ID 47450 (Heroic Strike) in swing timer"
    assert "47520" in SHARED_SWING_TIMER_LUA, "Manca Spell ID 47520 (Cleave) in swing timer"

    print("[OK] Componente Rotational Bar (Dual Swing & HS Queued) verificato con successo.")
    print("[PASS] test_rotational.py superato con successo!")

if __name__ == "__main__":
    run_tests()
