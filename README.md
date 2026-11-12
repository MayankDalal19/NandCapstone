# Capstone Project – Make the Computer Draw a Box
**Course:** Nand to Tetris – I (ETCCNT301), School of Engineering & Technology, K.R. Mangalam University
**Roll no:** 2501350094  **K = 94**

| Item | Value | How it is calculated |
|---|---|---|
| K | **94** | last two digits of roll no |
| Assembler extra feature | **K mod 3 = 1** → clear error message with line number | 94 mod 3 = 1 |
| Box start row | **94** | = K |
| Box height | **20 rows** (rows 94 … 113) | fixed |
| Box width | **48 pixels = 3 words** | 16 × ((94 mod 4) + 1) = 16 × 3 |
| Start address | **19392** | SCREEN + 32 × 94 = 16384 + 3008 |

---

## Folder layout

```
capstone/
├── README.md              <- this file
├── assembler.py           <- Part B: Python Hack assembler (two-pass)
├── hdl/
│   ├── CPU.hdl            <- Part A
│   ├── Memory.hdl         <- Part A
│   └── Computer.hdl       <- Part A
├── asm/
│   ├── Add.asm  Max.asm  Rect.asm     <- test programs for the assembler
│   └── Pong.asm           <- copy from official nand2tetris (not included)
├── official/              <- .hack files from the OFFICIAL assembler (for comparison)
├── box/
│   ├── Box.asm            <- Part C: the box program
│   └── Box.hack           <- made with MY assembler
├── tests/
│   ├── test_assembler.py  <- unit tests (incl. the extra feature)
│   └── compare.py         <- compares my output with the official output
└── screenshots/           <- put your screenshots here for the report
```

---

## Part A – The computer (hdl/)

Copy `CPU.hdl`, `Memory.hdl`, `Computer.hdl` into your `projects/05` folder of the nand2tetris tools (or load them from here) and run the **official** test scripts in the Hardware Simulator.

**How each chip works**

* **CPU.hdl** – bit 15 of the instruction tells A-instruction (0) or C-instruction (1).
  * A register gets either the instruction (A-instr) or the ALU output (C-instr with d1 = 1).
  * ALU's `y` input is A or M, chosen by bit 12 (the `a` bit); bits 11…6 are the ALU control bits.
  * D register loads when d2 = 1, `writeM` = d3 (both only for C-instructions).
  * Jump = (j1 AND out<0) OR (j2 AND out=0) OR (j3 AND out>0), only for C-instructions. The PC loads A when jump is true, otherwise it counts up; `reset` sends it to 0.
* **Memory.hdl** – 15-bit address: `address[14]=0` → RAM16K (0–16383); `address[14..13]=10` → Screen (16384–24575); `address[14..13]=11` → Keyboard (24576).
* **Computer.hdl** – ROM32K feeds instructions to the CPU; the CPU reads/writes Memory.

**Run & record** (take one screenshot each → `screenshots/`)

| Test | Result | Screenshot |
|---|---|---|
| CPU.tst | ☐ pass | `screenshots/CPU.png` |
| Memory.tst | ☐ pass | `screenshots/Memory.png` |
| ComputerAdd.tst | ☐ pass | `screenshots/ComputerAdd.png` |
| ComputerMax.tst | ☐ pass | `screenshots/ComputerMax.png` |
| ComputerRect.tst | ☐ pass | `screenshots/ComputerRect.png` |

> If any older chip of yours fails, you may use the built-in version – write which one in the report.

---

## Part B – The assembler (assembler.py)

```
python assembler.py asm/Add.asm        # creates asm/Add.hack
python assembler.py asm/Max.asm
python assembler.py asm/Rect.asm
python assembler.py asm/Pong.asm       # after copying Pong.asm into asm/
```

**How it works**

1. **First reading** – remove comments and spaces; skip blank lines; for every `(LABEL)` store the number of the *next real instruction* in the symbol table.
2. **Second reading** – A-instruction `@x` → `0` + 15-bit number (a symbol is looked up; a new symbol is a *variable* and gets RAM 16, 17, 18, …). C-instruction → `111` + comp(7) + dest(3) + jump(3) using lookup tables.
3. Predefined symbols: `R0–R15, SP, LCL, ARG, THIS, THAT, SCREEN, KBD`.

**Extra feature (K mod 3 = 1) – clear error messages**
Wrong lines never crash the assembler. It collects every error with the *original source line number*, prints them, and does not write a broken `.hack` file:

```
$ python assembler.py bad.asm
Line 3: invalid instruction 'D=Q+1' (unknown computation 'Q+1')
Line 4: invalid instruction '@' has no value
Line 5: invalid instruction 'M=D;JXX' (unknown jump 'JXX')
3 error(s) found - no .hack file written.
```

It also reports: bad labels, labels defined twice, numbers above 32767, unknown dest/jump.

**Test it**

```
python tests/test_assembler.py                 # unit tests (7 tests)
```

Compare with the official assembler: assemble each program with the official tool, copy the resulting `.hack` files into `official/`, then:

```
python tests/compare.py --all
# or one file:
python tests/compare.py asm/Max.asm official/Max.hack
```
On Windows you can also use `fc asm\Max.hack official\Max.hack`.

| Program | Output matches official? |
|---|---|
| Add.asm | ☐ |
| Max.asm | ☐ |
| Rect.asm | ☐ |
| Pong.asm | ☐ |

---

## Part C – The box (box/Box.asm)

**Idea (pseudo-code)**
```
forever:
    color = (KBD != 0) ? -1 : 0         // -1 = 16 black pixels, 0 = white
    addr  = 19392                        // row 94, first word
    repeat 20 times (rows):
        p = addr
        repeat 3 times (words):          // 3 words = 48 pixels
            RAM[p] = color ; p++
        addr = addr + 32                 // next screen row
```
* One screen row = 32 words, one word = 16 pixels → row *r* starts at `SCREEN + 32*r`.
* While a key is held the box is painted black; when it is released the same area is painted white (box disappears).

**Build with MY assembler (not the official one)**
```
python assembler.py box/Box.asm box/Box.hack
```
Then in the **CPU Emulator**: Load Program → `box/Box.hack` → set *Animate* to "No animation" / run, set Screen to "Enabled", click inside the emulator and hold a key → take a screenshot → `screenshots/Box.png`.

I checked `Box.hack` with a small Python simulation of the Hack CPU: with a key pressed, exactly rows 94–113 × words 0–2 are set to `0xFFFF` (60 words); with no key, the screen stays empty.

**Viva ideas** – to move the box down change `@19392` (32 × new row + 16384); to make it wider change `@3` (cols); taller → change `@20` (rows).

---

## Submission checklist
- [ ] `capstone/` folder in lab GitHub repo: HDL files, `assembler.py`, `Box.asm`, `Box.hack`
- [ ] Screenshots: 5 test results, official-vs-mine comparison, box
- [ ] Short report (3–4 pages) – **to be written later**: name, roll no, K = 94, box size (48 × 20), screenshots, one mistake I fixed
- [ ] Be ready to explain every file in the viva
