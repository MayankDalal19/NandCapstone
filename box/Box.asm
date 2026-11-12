// Box.asm  -  Roll no 2501350094, K = 94
//   start row   = K                  = 94
//   height      = 20 rows            (rows 94 .. 113)
//   width       = 16*((K mod 4)+1)   = 16*3 = 48 pixels = 3 words
//   start addr  = SCREEN + 32*94     = 16384 + 3008 = 19392
//
// While any key is pressed -> black box.  No key -> box is white (disappears).

(MAIN)
    @KBD
    D=M
    @BLACK
    D;JNE           // key pressed -> go to BLACK

    @color
    M=0             // no key -> colour = white (0)
    @DRAW
    0;JMP

(BLACK)
    @color
    M=-1            // key -> colour = black (all 16 bits = 1)

(DRAW)
    @19392          // address of row 94, column 0
    D=A
    @addr
    M=D             // addr = first word of current row

    @20
    D=A
    @rows
    M=D             // rows = 20 rows still to draw

(ROWLOOP)
    @3
    D=A
    @cols
    M=D             // cols = 3 words per row

    @addr
    D=M
    @p
    M=D             // p = pointer to current word

(COLLOOP)
    @color
    D=M
    @p
    A=M
    M=D             // RAM[p] = colour

    @p
    M=M+1           // next word in this row

    @cols
    MD=M-1          // cols--
    @COLLOOP
    D;JGT           // more words in this row?

    @32
    D=A
    @addr
    M=D+M           // addr += 32  (next screen row)

    @rows
    MD=M-1          // rows--
    @ROWLOOP
    D;JGT           // more rows?

    @MAIN
    0;JMP           // check keyboard again
