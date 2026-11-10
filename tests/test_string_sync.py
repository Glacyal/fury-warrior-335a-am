import os
import re
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    from builder.core import generate_wa_string
    from builder.tree import build_wa_tree

    v5_path = os.path.join(root_dir, "IMPORT_STRING_v5.21.8.txt")
    legacy_path = os.path.join(root_dir, "IMPORT_STRING.txt")
    docs_path = os.path.join(root_dir, "docs", "index.html")

    assert os.path.exists(v5_path), "File IMPORT_STRING_v5.21.8.txt non trovato!"
    assert os.path.exists(docs_path), "File docs/index.html non trovato!"

    with open(v5_path, "r", encoding="utf-8") as f:
        wa_str = f.read().strip()

    tree_v5 = build_wa_tree("5.21.8")
    generated_v5 = generate_wa_string(tree_v5).strip()
    assert wa_str == generated_v5, "IMPORT_STRING_v5.21.8.txt non corrisponde all'output di build_wa_tree('5.21.8')!"
    assert wa_str.startswith("!WA:1!"), "La stringa non inizia con il prefisso ufficiale !WA:1!"
    assert tree_v5["w"] == "5.21.8", "La versione 'w' deve essere '5.21.8'"
    assert tree_v5["d"]["internalVersion"] == 90, "internalVersion della radice deve essere 90"
    assert len(wa_str) > 10000, f"Lunghezza stringa anomala: {len(wa_str)} caratteri"

    with open(docs_path, "r", encoding="utf-8") as f:
        html = f.read()

    m = re.search(r'<textarea id="hiddenWaString"[^>]*>(.*?)</textarea>', html, re.DOTALL)
    assert m is not None, "Textarea con id 'hiddenWaString' non trovata in docs/index.html!"
    embedded_str = m.group(1).strip()

    assert wa_str == embedded_str, "Discrepanza tra IMPORT_STRING_v5.21.8.txt e la stringa in docs/index.html!"

    print(f"[OK] Stringa v5.21.8+ verificata: {len(wa_str)} caratteri, sincronizzazione 100% con docs/index.html.")
    print("[PASS] test_string_sync.py superato con successo!")

if __name__ == "__main__":
    run_tests()

