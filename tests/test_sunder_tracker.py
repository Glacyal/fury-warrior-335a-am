import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.components.sunder import build_sunder_auras

    auras = build_sunder_auras()
    assert len(auras) == 1, f"Expected 1 aura in sunder tracker, got {len(auras)}"

    sunder = auras[0]
    assert sunder["id"] == "19 - Sunder Armor Tracker"
    assert sunder["xOffset"] == 169
    assert sunder["yOffset"] == 45
    assert sunder["width"] == 32
    assert sunder["height"] == 32

    # Check Lua trigger logic
    trig = sunder["triggers"][1]["trigger"]["custom"]
    assert "47467" in trig, "Manca ID 47467 (Sunder Armor) nel trigger"
    assert "8647" in trig or "Expose Armor" in trig, "Manca rilevamento Expose Armor nel trigger"
    assert "UnitAffectingCombat" in trig, "Manca controllo inCombat per allerta cariche mancanti"

    print("[OK] Componente Sunder Armor Tracker verificato con successo.")
    print("[PASS] test_sunder_tracker.py superato con successo!")

if __name__ == "__main__":
    run_tests()
