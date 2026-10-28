import os
import re
import sys

def strip_lua(code):
    code = re.sub(r'--\[\[.*?\]\]', '', code, flags=re.DOTALL)
    code = re.sub(r'--.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'\[\[.*?\]\]', '""', code, flags=re.DOTALL)
    code = re.sub(r'"(\\.|[^"])*"', '""', code)
    code = re.sub(r"'(\\.|[^'])*'", "''", code)
    return code

def verify_lua(code, name):
    stripped = strip_lua(code)
    tokens = re.findall(r'\b(function|if|do|while|repeat|end|until)\b', stripped)
    depth = 0
    for t in tokens:
        if t in ('function', 'if', 'do', 'while', 'repeat'):
            depth += 1
        elif t in ('end', 'until'):
            depth -= 1
        if depth < 0:
            print(f"[-] Errore di sintassi in {name}: terminatore inatteso '{t}'")
            return False
    if depth != 0:
        print(f"[-] Errore di sintassi in {name}: blocchi non bilanciati (depth = {depth})")
        return False
    return True

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_passed = True

    # Verifica blocchi Lua embedded nella WeakAura
    sys.path.insert(0, root_dir)
    from builder.tree import build_wa_tree
    tree = build_wa_tree()

    count = 0
    
    # Check root actions
    root_act = tree.get("d", {}).get("actions", {})
    init_custom = root_act.get("init", {}).get("custom")
    if init_custom and isinstance(init_custom, str):
        count += 1
        ok = verify_lua(init_custom, "Root -> actions.init.custom")
        if not ok: all_passed = False

    all_items = [tree["d"]] + tree["c"]
    for child in all_items:
        cid = child.get("id", "Unknown")
        # Check actions.init.custom
        actions = child.get("actions", {})
        init_c = actions.get("init", {}).get("custom")
        if init_c and isinstance(init_c, str):
            count += 1
            ok = verify_lua(init_c, f"{cid} -> actions.init.custom")
            if not ok: all_passed = False

        # Check triggers
        triggers = child.get("triggers", {})
        for k, v in triggers.items():
            if isinstance(v, dict):
                trig = v.get("trigger", {})
                for field in ("custom", "customDuration", "customIcon", "customOverlay"):
                    code = trig.get(field)
                    if code and isinstance(code, str):
                        count += 1
                        ok = verify_lua(code, f"{cid} -> Trigger {k} {field}")
                        if not ok: all_passed = False

                untrig = v.get("untrigger", {})
                custom_untrig = untrig.get("custom")
                if custom_untrig and isinstance(custom_untrig, str):
                    count += 1
                    ok = verify_lua(custom_untrig, f"{cid} -> Untrigger {k}")
                    if not ok: all_passed = False

        # Check customText
        ctext = child.get("customText")
        if ctext and isinstance(ctext, str):
            count += 1
            ok = verify_lua(ctext, f"{cid} -> customText")
            if not ok: all_passed = False

        # Check init_completed
        init_c = child.get("init_completed")
        if init_c and isinstance(init_c, str):
            count += 1
            ok = verify_lua(init_c, f"{cid} -> init_completed")
            if not ok: all_passed = False

    print(f"[OK] Validati {count} blocchi di codice Lua incorporati.")
    if not all_passed:
        sys.exit(1)
    print("[PASS] test_lua.py superato con successo!")

if __name__ == "__main__":
    run_tests()
