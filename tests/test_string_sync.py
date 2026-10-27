import os
import re
import sys

def run_tests():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    import_path = os.path.join(root_dir, "IMPORT_STRING.txt")
    docs_path = os.path.join(root_dir, "docs", "index.html")

    assert os.path.exists(import_path), "File IMPORT_STRING.txt non trovato!"
    assert os.path.exists(docs_path), "File docs/index.html non trovato!"

    with open(import_path, "r", encoding="utf-8") as f:
        wa_str = f.read().strip()

    assert wa_str.startswith("!WA:1!"), "La stringa non inizia con il prefisso ufficiale !WA:1!"
    assert len(wa_str) > 10000, f"Lunghezza stringa anomala: {len(wa_str)} caratteri"

    with open(docs_path, "r", encoding="utf-8") as f:
        html = f.read()

    m = re.search(r'<textarea id="hiddenWaString"[^>]*>(.*?)</textarea>', html, re.DOTALL)
    assert m is not None, "Textarea con id 'hiddenWaString' non trovata in docs/index.html!"
    embedded_str = m.group(1).strip()

    assert wa_str == embedded_str, "Discrepanza tra IMPORT_STRING.txt e la stringa in docs/index.html!"

    print(f"[OK] Stringa verificata: {len(wa_str)} caratteri, sincronizzazione 100% con docs/index.html.")
    print("[PASS] test_string_sync.py superato con successo!")

if __name__ == "__main__":
    run_tests()

