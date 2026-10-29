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
    assert bs_act["triggers"][1]["trigger"]["check"] == "update", "Battle Shout Active deve usare check: update per reattivita istantanea"

    bs_off = c_map.get("02 - Battle Shout - OFF")
    assert bs_off is not None, "Missing 02 - Battle Shout - OFF"
    assert bs_off["parent"] == "02 - Battle Shout"
    assert bs_off["desaturate"] is True
    assert bs_off["color"] == [0.6, 0.6, 0.6, 0.8]
    assert bs_off["triggers"][1]["trigger"]["check"] == "update", "Battle Shout OFF deve usare check: update per reattivita istantanea"
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
    assert cs_act["displayIcon"] == "Interface\\Icons\\Ability_Warrior_CommandingShout", f"Invalid icon for CS Active: {cs_act.get('displayIcon')}"
    assert cs_act["triggers"][1]["trigger"]["check"] == "update", "Commanding Shout Active deve usare check: update per reattivita istantanea"

    cs_off = c_map.get("03 - Commanding Shout - OFF")
    assert cs_off is not None, "Missing 03 - Commanding Shout - OFF"
    assert cs_off["parent"] == "03 - Commanding Shout"
    assert cs_off["desaturate"] is True
    assert cs_off["displayIcon"] == "Interface\\Icons\\Ability_Warrior_CommandingShout", f"Invalid icon for CS OFF: {cs_off.get('displayIcon')}"
    assert cs_off["triggers"][1]["trigger"]["check"] == "update", "Commanding Shout OFF deve usare check: update per reattivita istantanea"
    subtext_cs_off = cs_off["subRegions"][1]["text_text"]
    assert "OFF" in subtext_cs_off, f"Missing OFF label in CS OFF: {subtext_cs_off}"

    # 5. Texture & Spell ID Integrity (No Cataclysm Rallying Cry or typos)
    auras_str = str(auras)
    assert "Ability_Warrior_RallyingCry" not in auras_str, "Rallying Cry non esiste in 3.3.5a (aggiunto in 4.1.0)"
    assert "Spell_Holy_GreaterBlessingofMount" not in auras_str, "Spell_Holy_GreaterBlessingofMount non esiste in 3.3.5a"
    assert "Spell_Shadow_BloodPact" not in auras_str, "Spell_Shadow_BloodPact non esiste in 3.3.5a (usare Spell_Shadow_BloodBoil o GetSpellInfo)"

    # 6. Berserker Stance Parent Group
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
    assert stance_warn["subRegions"][1]["text_fontSize"] == 8, f"Expected font_size 8 for STANCE, got {stance_warn['subRegions'][1].get('text_fontSize')}"

    # 7. Check Raid Substitutes in SHARED_WARRIOR_BUFFS_LUA
    assert "hasBoM" in SHARED_WARRIOR_BUFFS_LUA, "Manca controllo BoM in SHARED_WARRIOR_BUFFS_LUA"
    assert "Greater Blessing of Might" in SHARED_WARRIOR_BUFFS_LUA
    assert "hasBloodPact" in SHARED_WARRIOR_BUFFS_LUA, "Manca controllo Blood Pact in SHARED_WARRIOR_BUFFS_LUA"
    assert "Patto di Sangue" in SHARED_WARRIOR_BUFFS_LUA
    assert "47439" in SHARED_WARRIOR_BUFFS_LUA, "Manca spellId 47439 (Commanding Shout Rank 2) in SHARED_WARRIOR_BUFFS_LUA"
    assert "bomIcon" in SHARED_WARRIOR_BUFFS_LUA, "Manca cattura dinamica bomIcon in SHARED_WARRIOR_BUFFS_LUA"
    assert "csIcon" in SHARED_WARRIOR_BUFFS_LUA, "Manca cattura dinamica csIcon in SHARED_WARRIOR_BUFFS_LUA"

    print("[OK] Battle Shout, Commanding Shout e Berserker Stance validati con successo (check update, icone 3.3.5a corrette).")
    print("[PASS] test_buffs.py superato con successo!")

if __name__ == "__main__":
    run_tests()
