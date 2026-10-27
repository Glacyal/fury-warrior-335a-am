import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.tree import build_wa_tree

    tree = build_wa_tree()
    root = tree["d"]
    assert root["scale"] == 1.2, f"Invalid root scale: {root.get('scale')}"
    assert root["xOffset"] == 0, f"Invalid root xOffset: {root.get('xOffset')}"
    assert root["yOffset"] == -190, f"Invalid root yOffset: {root.get('yOffset')}"
    assert root["anchorPoint"] == "CENTER", f"Invalid anchorPoint: {root.get('anchorPoint')}"

    c_map = {item["id"]: item for item in tree["c"]}

    # Check 14 - Rage Bar
    rage_bar = c_map.get("14 - Rage Bar")
    assert rage_bar is not None, "Missing 14 - Rage Bar"
    assert rage_bar["width"] == 278, f"Invalid Rage Bar width: {rage_bar.get('width')}"
    assert rage_bar["height"] == 14, f"Invalid Rage Bar height: {rage_bar.get('height')}"
    assert rage_bar["yOffset"] == -20, f"Invalid Rage Bar yOffset: {rage_bar.get('yOffset')}"

    # Check 16 - Castbar warDPS
    castbar = c_map.get("16 - Castbar warDPS")
    assert castbar is not None, "Missing 16 - Castbar warDPS"
    assert castbar["width"] == 278, f"Invalid Castbar width: {castbar.get('width')}"
    assert castbar["height"] == 20, f"Invalid Castbar height: {castbar.get('height')}"
    assert castbar["yOffset"] == 8, f"Invalid Castbar yOffset: {castbar.get('yOffset')}"

    # Check Rotational Bar Background
    rot_bg = c_map.get("Rotational Bar - Background")
    assert rot_bg is not None, "Missing Rotational Bar - Background"
    assert rot_bg["width"] == 278, f"Invalid Rotational Bar Background width: {rot_bg.get('width')}"
    assert rot_bg["height"] == 7, f"Invalid Rotational Bar Background height: {rot_bg.get('height')}"

    # Check 18 - Stats Panel Background warDPS
    stats_bg = c_map.get("Stats Panel - Background warDPS")
    assert stats_bg is not None, "Missing Stats Panel - Background warDPS"
    assert stats_bg["width"] == 88, f"Invalid Stats Panel Background width: {stats_bg.get('width')}"
    assert stats_bg["height"] == 48, f"Invalid Stats Panel Background height: {stats_bg.get('height')}"

    # Check 19 - Sunder Armor Tracker
    sunder = c_map.get("19 - Sunder Armor Tracker")
    assert sunder is not None, "Missing 19 - Sunder Armor Tracker"
    assert sunder["xOffset"] == 169, f"Invalid Sunder Tracker xOffset: {sunder.get('xOffset')}"
    assert sunder["yOffset"] == 45, f"Invalid Sunder Tracker yOffset: {sunder.get('yOffset')}"

    print("[OK] Tutte le dimensioni geometriche e coordinate a schermo sono verificate al millimetro.")
    print("[PASS] test_tree_layout.py superato con successo!")

if __name__ == "__main__":
    run_tests()
