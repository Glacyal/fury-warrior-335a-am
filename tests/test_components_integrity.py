import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.tree import build_wa_tree

    tree = build_wa_tree()
    root = tree["d"]
    assert root["id"] == "Class Warrior (Fury)", f"Invalid root id: {root.get('id')}"
    assert root["uid"] == "FWHUD_ROOT", f"Invalid root uid: {root.get('uid')}"
    assert root["internalVersion"] == 52, f"Invalid internalVersion: {root.get('internalVersion')}"

    expected_children = [
        "01 - Procs",
        "02 - Battle Shout",
        "03 - Commanding Shout",
        "04 - Berserker Stance",
        "05 - Trinket 1",
        "06 - Trinket 2",
        "07 - Cloak",
        "08 - Tier Set",
        "09 - Enchants",
        "10 - Gloves",
        "11 - Death Wish",
        "12 - Recklessness",
        "13 - Boots",
        "14 - Rage Bar",
        "15 - Rotational Bar",
        "16 - Castbar",
        "17 - Alerts",
        "18 - Stats Panel",
        "19 - Sunder Armor Tracker",
    ]

    ctrl = root["controlledChildren"]
    assert len(ctrl) == 19, f"Expected 19 controlled children, got {len(ctrl)}"
    for exp in expected_children:
        assert exp in ctrl, f"Missing child in root controlledChildren: {exp}"

    # Verify all children in tree['c']
    children_map = {c["id"]: c for c in tree["c"]}
    uids = set()

    for item in tree["c"]:
        cid = item.get("id")
        uid = item.get("uid")
        assert cid, "Item missing 'id'"
        assert uid, f"Item {cid} missing 'uid'"
        assert uid not in uids, f"Duplicate UID detected: {uid}"
        uids.add(uid)
        assert uid.startswith("FWHUD_"), f"UID {uid} does not start with 'FWHUD_'"
        assert item.get("internalVersion") == 52, f"Item {cid} internalVersion != 52"

        # Check load conditions (Warrior Class + Rampage Talent ID 64)
        load = item.get("load", {})
        assert load.get("use_class") is True, f"Item {cid} load use_class is not True"
        assert load.get("class", {}).get("single") == "WARRIOR", f"Item {cid} load class != WARRIOR"
        assert load.get("use_talent") is True, f"Item {cid} load use_talent is not True"
        assert load.get("talent", {}).get("single") == 64, f"Item {cid} load talent != 64 (Rampage)"
        assert load.get("talent", {}).get("multi", {}).get(64) is True, f"Item {cid} load talent multi[64] is not True"

    # Check root load conditions
    root_load = root.get("load", {})
    assert root_load.get("use_class") is True, "Root load use_class is not True"
    assert root_load.get("class", {}).get("single") == "WARRIOR", "Root load class != WARRIOR"
    assert root_load.get("use_talent") is True, "Root load use_talent is not True"
    assert root_load.get("talent", {}).get("single") == 64, "Root load talent != 64 (Rampage)"
    assert root_load.get("talent", {}).get("multi", {}).get(64) is True, "Root load talent multi[64] is not True"

    print(f"[OK] Validati {len(tree['c'])} nodi e 21 moduli di primo livello.")
    print("[PASS] test_components_integrity.py superato con successo!")

if __name__ == "__main__":
    run_tests()
