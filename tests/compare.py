"""Compare MY assembler with the OFFICIAL assembler.

Usage (from the capstone folder):
    python tests/compare.py asm/Add.asm official/Add.hack
or compare everything in official/ at once:
    python tests/compare.py --all
"""
import glob, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from assembler import assemble


def compare(asm_path, official_path):
    with open(asm_path) as f:
        code, errors = assemble(f.read().splitlines())
    if errors:
        print(f"FAIL {asm_path}: " + "; ".join(errors)); return False
    with open(official_path) as f:
        expected = [l.strip() for l in f if l.strip()]
    if code == expected:
        print(f"PASS {os.path.basename(asm_path)}: {len(code)} lines identical"); return True
    print(f"FAIL {os.path.basename(asm_path)}: lengths {len(code)} vs {len(expected)}")
    for i, (a, b) in enumerate(zip(code, expected), 1):
        if a != b:
            print(f"  first difference at line {i}:\n    mine    : {a}\n    official: {b}"); break
    return False


if __name__ == "__main__":
    if sys.argv[1:] == ["--all"]:
        ok = True
        for h in sorted(glob.glob("official/*.hack")):
            name = os.path.splitext(os.path.basename(h))[0]
            a = f"asm/{name}.asm"
            if os.path.exists(a):
                ok &= compare(a, h)
            else:
                print(f"SKIP {name}: {a} not found")
        sys.exit(0 if ok else 1)
    elif len(sys.argv) == 3:
        sys.exit(0 if compare(sys.argv[1], sys.argv[2]) else 1)
    else:
        print(__doc__)
