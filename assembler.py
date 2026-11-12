#!/usr/bin/env python3
"""
Hack Assembler  -  Nand to Tetris I capstone
Roll no 2501350094  (K = 94, K mod 3 = 1)

Extra feature for K mod 3 = 1:
    For a wrong line, print a clear message with the line number
    (e.g.  "Line 7: invalid instruction") instead of crashing.

Usage:
    python assembler.py Prog.asm            -> writes Prog.hack
    python assembler.py Prog.asm Out.hack   -> writes Out.hack

Two readings of the file:
    First reading : remove comments / blank lines, record where each (LABEL) is.
    Second reading: turn every instruction into 16 bits; new variables get
                    RAM addresses 16, 17, 18, ...
"""
import re
import sys

# ---------------------------------------------------------------- tables
COMP = {
    # a = 0
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    # a = 1
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111",
}
JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}
PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
}
PREDEFINED.update({f"R{i}": i for i in range(16)})

SYMBOL_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


def clean(line):
    """Remove comment and ALL whitespace from one source line."""
    line = line.split("//", 1)[0]
    return "".join(line.split())


# ---------------------------------------------------------------- passes
def first_pass(lines, errors):
    """Collect labels. Returns (symbols, instruction_list).
    instruction_list = [(source_line_number, cleaned_text), ...]"""
    symbols = dict(PREDEFINED)
    instructions = []
    for lineno, raw in enumerate(lines, start=1):
        text = clean(raw)
        if not text:
            continue
        if text.startswith("("):
            if not (text.endswith(")") and SYMBOL_RE.match(text[1:-1])):
                errors.append(f"Line {lineno}: invalid label '{raw.strip()}'")
                continue
            name = text[1:-1]
            if name in symbols:
                errors.append(f"Line {lineno}: label '{name}' is already defined")
                continue
            symbols[name] = len(instructions)  # address of the NEXT instruction
        else:
            instructions.append((lineno, text))
    return symbols, instructions


def encode_a(text, lineno, symbols, state, errors):
    value = text[1:]
    if value == "":
        errors.append(f"Line {lineno}: invalid instruction '@' has no value")
        return None
    if value.isdigit():
        number = int(value)
        if number > 32767:
            errors.append(f"Line {lineno}: number {number} is too big "
                          f"(A-instruction must be 0..32767)")
            return None
    elif SYMBOL_RE.match(value):
        if value not in symbols:               # new variable
            symbols[value] = state["next_var"]
            state["next_var"] += 1
        number = symbols[value]
    else:
        errors.append(f"Line {lineno}: invalid instruction '{text}' "
                      f"(bad symbol or number after '@')")
        return None
    return format(number, "016b")


def encode_c(text, lineno, errors):
    dest, jump, comp = "", "", text
    if text.count("=") > 1 or text.count(";") > 1:
        errors.append(f"Line {lineno}: invalid instruction '{text}' "
                      f"(too many '=' or ';')")
        return None
    if "=" in comp:
        dest, comp = comp.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)

    if comp not in COMP:
        errors.append(f"Line {lineno}: invalid instruction '{text}' "
                      f"(unknown computation '{comp}')")
        return None
    if dest not in DEST:
        errors.append(f"Line {lineno}: invalid instruction '{text}' "
                      f"(unknown destination '{dest}')")
        return None
    if jump not in JUMP:
        errors.append(f"Line {lineno}: invalid instruction '{text}' "
                      f"(unknown jump '{jump}')")
        return None
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def second_pass(symbols, instructions, errors):
    state = {"next_var": 16}
    out = []
    for lineno, text in instructions:
        word = (encode_a(text, lineno, symbols, state, errors)
                if text.startswith("@") else encode_c(text, lineno, errors))
        if word is not None:
            out.append(word)
    return out


def assemble(lines):
    """Assemble a list of source lines.
    Returns (machine_code_lines, error_messages)."""
    errors = []
    symbols, instructions = first_pass(lines, errors)
    code = second_pass(symbols, instructions, errors)
    errors.sort(key=lambda e: int(e.split(":")[0].split()[1]))
    return code, errors


# ---------------------------------------------------------------- main
def main(argv):
    if len(argv) not in (2, 3):
        print("Usage: python assembler.py Prog.asm [Prog.hack]")
        return 2
    src = argv[1]
    dst = argv[2] if len(argv) == 3 else re.sub(r"\.asm$", "", src) + ".hack"
    try:
        with open(src, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as e:
        print(f"Cannot open '{src}': {e.strerror}")
        return 2

    code, errors = assemble(lines)
    if errors:
        for e in errors:
            print(e)
        print(f"{len(errors)} error(s) found - no .hack file written.")
        return 1

    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(code) + "\n")
    print(f"OK: {src} -> {dst}  ({len(code)} instructions)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
