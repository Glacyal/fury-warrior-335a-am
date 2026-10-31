"""
Test di Validazione e Integrità per il Componente 01 - Procs warDPS (Task 50)
=============================================================================
Verifica:
1. Numero e ordine delle aure in 01 - Procs warDPS (8 totali: 1 DG + 7 aure figlie).
2. Posizionamento di 'Weapon Desync Alert' immediatamente a destra di 'Execute Usable'.
3. Configurazione grafica (Ability_DualWield, 34x34px, Pixel Glow rosso, testo SYNC rosso).
4. Logica Lua custom (combat, living enemy target, OH speed, soglia delta < 0.30s).
"""
import os
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)
    from builder.components.procs import build_procs_auras

    auras = build_procs_auras()
    assert len(auras) == 8, f"Attese 8 aure in build_procs_auras, trovate {len(auras)}"

    dg = auras[0]
    assert dg["id"] == "01 - Procs warDPS"
    assert dg["uid"] == "FWHUD_PROCS_DG"
    assert dg["regionType"] == "dynamicgroup"
    assert dg["grow"] == "HORIZONTAL"
    assert dg["align"] == "CENTER"
    assert dg["space"] == 6
    assert dg["yOffset"] == 52

    expected_children = [
        "Bloodsurge",
        "Victory Rush",
        "Flurry",
        "Wrecking Crew",
        "Rend",
        "Execute Usable",
        "Weapon Desync Alert",
    ]
    assert dg["controlledChildren"] == expected_children, (
        f"controlledChildren non corrispondente: {dg['controlledChildren']}"
    )

    # Verifica indice immediato a destra di Execute Usable
    exec_idx = dg["controlledChildren"].index("Execute Usable")
    desync_idx = dg["controlledChildren"].index("Weapon Desync Alert")
    assert desync_idx == exec_idx + 1, (
        f"Weapon Desync Alert deve essere immediatamente a destra di Execute Usable (trovato a {desync_idx} vs {exec_idx})"
    )

    auras_map = {a["id"]: a for a in auras[1:]}

    # Verifica Weapon Desync Alert
    desync = auras_map.get("Weapon Desync Alert")
    assert desync is not None, "Manca aura 'Weapon Desync Alert' in build_procs_auras"
    assert desync["uid"] == "FWHUD_PROC_DESYNC", f"UID errato: {desync.get('uid')}"
    assert desync["parent"] == "01 - Procs warDPS"
    assert desync["regionType"] == "icon"
    assert desync["width"] == 34 and desync["height"] == 34
    assert desync["displayIcon"] == "Interface\\Icons\\Ability_DualWield"
    assert desync["auto"] is False

    # Verifica Pixel Glow rosso
    start_act = desync.get("actions", {}).get("start", {})
    assert start_act.get("do_glow") is True, "actions.start do_glow non è True"
    assert start_act.get("glow_type") == "Pixel", "glow_type non è Pixel"
    assert start_act.get("glow_color") == [1.0, 0.2, 0.2, 1.0], f"Colore glow errato: {start_act.get('glow_color')}"

    # Verifica subRegion SYNC rossa
    sub_texts = desync.get("subRegions", [])
    sync_sub = next((s for s in sub_texts if s.get("text_text") == "SYNC"), None)
    assert sync_sub is not None, "Manca subRegion con testo 'SYNC'"
    assert sync_sub.get("text_color") == [1.0, 0.2, 0.2, 1.0], f"Colore testo SYNC errato: {sync_sub.get('text_color')}"
    assert sync_sub.get("text_anchorPoint") == "INNER_BOTTOM"
    assert sync_sub.get("text_fontSize") == 11

    # Verifica Trigger Lua (< 0.30s)
    trig_custom = desync["triggers"][1]["trigger"]["custom"]
    assert "UnitAffectingCombat" in trig_custom, "Trigger manca controllo UnitAffectingCombat"
    assert "UnitAttackSpeed" in trig_custom, "Trigger manca controllo UnitAttackSpeed per OH"
    assert "FWHUD_GetSwing" in trig_custom, "Trigger manca chiamata _G.FWHUD_GetSwing"
    assert "delta < 0.30" in trig_custom, "Trigger manca soglia temporale delta < 0.30s"

    # Verifica Untrigger Lua (>= 0.30s)
    untrig_custom = desync["triggers"][1]["untrigger"]["custom"]
    assert "delta >= 0.30" in untrig_custom, "Untrigger manca soglia complementare delta >= 0.30s"

    print("[OK] Componente 01 - Procs warDPS e Task 50 (Weapon Desync Alert) validati con successo.")
    print("[PASS] test_procs.py superato con successo!")

if __name__ == "__main__":
    run_tests()

