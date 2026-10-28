import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.components.buffs import build_buffs_auras, SHARED_WARRIOR_BUFFS_LUA

    auras = build_buffs_auras()
    c_map = {a["id"]: a for a in auras}

    # 1. Battle Shout Parent Group
    bs_grp = c_map.get("02 - Battle Shout")
    assert bs_grp is not None, "Missing 02 - Battle Shout group"
    assert bs_grp["xOffset"] == -222, f"Invalid xOffset for BS: {bs_grp.get('xOffset')}"
    assert bs_grp["yOffset"] == 0, f"Invalid yOffset for BS: {bs_grp.get('yOffset')}"
    assert bs_grp["controlledChildren"] == ["02 - Battle Shout - Active", "02 - Battle Shout - OFF"]

    # 2. Battle Shout Active & OFF
    bs_act = c_map.get("02 - Battle Shout - Active")
    assert bs_act is not None, "Missing 02 - Battle Shout - Active"
    assert bs_act["parent"] == "02 - Battle Shout"
    assert bs_act["cooldown"] is True
    assert bs_act["cooldownSwipe"] is True

    bs_off = c_map.get("02 - Battle Shout - OFF")
    assert bs_off is not None, "Missing 02 - Battle Shout - OFF"
    assert bs_off["parent"] == "02 - Battle Shout"
    assert bs_off["desaturate"] is True
    assert bs_off["color"] == [0.6, 0.6, 0.6, 0.8]
    subtext_off = bs_off["subRegions"][1]["text_text"]
    assert "OFF" in subtext_off, f"Missing OFF label in BS OFF: {subtext_off}"

    # 3. Commanding Shout Parent Group
    cs_grp = c_map.get("03 - Commanding Shout")
    assert cs_grp is not None, "Missing 03 - Commanding Shout group"
    assert cs_grp["xOffset"] == -190, f"Invalid xOffset for CS: {cs_grp.get('xOffset')}"
    assert cs_grp["yOffset"] == 0, f"Invalid yOffset for CS: {cs_grp.get('yOffset')}"
    assert cs_grp["controlledChildren"] == ["03 - Commanding Shout - Active", "03 - Commanding Shout - OFF"]

    # 4. Commanding Shout Active & OFF
    cs_act = c_map.get("03 - Commanding Shout - Active")
    assert cs_act is not None, "Missing 03 - Commanding Shout - Active"
    assert cs_act["parent"] == "03 - Commanding Shout"

    cs_off = c_map.get("03 - Commanding Shout - OFF")
    assert cs_off is not None, "Missing 03 - Commanding Shout - OFF"
    assert cs_off["parent"] == "03 - Commanding Shout"
    assert cs_off["desaturate"] is True
    subtext_cs_off = cs_off["subRegions"][1]["text_text"]
    assert "OFF" in subtext_cs_off, f"Missing OFF label in CS OFF: {subtext_cs_off}"

    # 5. Berserker Stance Parent Group
    stance_grp = c_map.get("04 - Berserker Stance")
    assert stance_grp is not None, "Missing 04 - Berserker Stance group"
    assert stance_grp["xOffset"] == -158, f"Invalid xOffset for Stance: {stance_grp.get('xOffset')}"
    assert stance_grp["yOffset"] == 0, f"Invalid yOffset for Stance: {stance_grp.get('yOffset')}"

    stance_warn = c_map.get("04 - Berserker Stance - OutOfStance")
    assert stance_warn is not None, "Missing 04 - Berserker Stance - OutOfStance"
    trig_lua = stance_warn["triggers"][1]["trigger"]["custom"]
    assert "GetShapeshiftForm()" in trig_lua
    assert "form ~= 3" in trig_lua
    assert "UnitAffectingCombat(\"player\")" in trig_lua

    # 6. Check Raid Substitutes in SHARED_WARRIOR_BUFFS_LUA
    assert "hasBoM" in SHARED_WARRIOR_BUFFS_LUA, "Manca controllo BoM in SHARED_WARRIOR_BUFFS_LUA"
    assert "Greater Blessing of Might" in SHARED_WARRIOR_BUFFS_LUA
    assert "hasBloodPact" in SHARED_WARRIOR_BUFFS_LUA, "Manca controllo Blood Pact in SHARED_WARRIOR_BUFFS_LUA"
    assert "Patto di Sangue" in SHARED_WARRIOR_BUFFS_LUA

    print("[OK] Battle Shout, Commanding Shout e Berserker Stance validati con successo.")
    print("[PASS] test_buffs.py superato con successo!")

if __name__ == "__main__":
    run_tests()

