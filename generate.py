import os
from builder.core import generate_wa_string
from builder.tree import build_wa_tree

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "IMPORT_STRING.txt")
    wa_tree = build_wa_tree()
    wa_string = generate_wa_string(wa_tree)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(wa_string)
    print(f"Generated !WA:1! String successfully! Length: {len(wa_string)}")
