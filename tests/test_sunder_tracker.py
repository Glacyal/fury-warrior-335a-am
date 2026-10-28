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

    # Check customStacks in trigger
    assert "customStacks" in sunder["triggers"][1]["trigger"], "Manca customStacks in trigger 1"
    stacks_fn = sunder["triggers"][1]["trigger"]["customStacks"]
    assert "47467" in stacks_fn, "customStacks deve tracciare spellId 47467"

    # Check customText logic (returns timerText, centerText)
    custom_text = sunder["customText"]
    assert "OFF" in custom_text, "customText deve mostrare 'OFF' quando manca Sunder"
    assert "MISSING" not in custom_text, "customText NON deve piu contenere 'MISSING' (richiesto solo 'OFF')"
    assert "return timerText, centerText" in custom_text, "customText deve restituire timerText e centerText per %c1 e %c2"

    # Check subRegions configuration
    subregs = sunder.get("subRegions", [])
    assert len(subregs) >= 3, f"Previste almeno 3 subRegions (background + 2 testi), trovate {len(subregs)}"
    
    # Subregion 1: timer/status at INNER_BOTTOM (%c1)
    sub1 = subregs[1]
    assert sub1.get("type") == "subtext", "subRegion[1] deve essere subtext"
    assert sub1.get("text_text") == "%c1", f"subRegion[1] text deve essere %c1, trovato {sub1.get('text_text')}"
    assert sub1.get("text_anchorPoint") == "INNER_BOTTOM", f"subRegion[1] deve essere INNER_BOTTOM, trovato {sub1.get('text_anchorPoint')}"
    assert sub1.get("text_fontSize") == 10, f"subRegion[1] font_size deve essere 10, trovato {sub1.get('text_fontSize')}"

    # Subregion 2: stacks at CENTER (%c2)
    sub2 = subregs[2]
    assert sub2.get("type") == "subtext", "subRegion[2] deve essere subtext"
    assert sub2.get("text_text") == "%c2", f"subRegion[2] text deve essere %c2, trovato {sub2.get('text_text')}"
    assert sub2.get("text_anchorPoint") == "CENTER", f"subRegion[2] deve essere CENTER, trovato {sub2.get('text_anchorPoint')}"
    assert sub2.get("text_fontSize") == 14, f"subRegion[2] font_size deve essere 14, trovato {sub2.get('text_fontSize')}"

    print("[OK] Componente Sunder Armor Tracker verificato con successo (solo OFF, timer alla base, cariche al centro).")
    print("[PASS] test_sunder_tracker.py superato con successo!")

if __name__ == "__main__":
    run_tests()

