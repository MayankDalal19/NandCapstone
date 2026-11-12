"""Self-tests for assembler.py.   Run:  python tests/test_assembler.py"""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from assembler import assemble


class TestAssembler(unittest.TestCase):
    def test_add_matches_official(self):
        # official Add.hack
        expected = ["0000000000000010", "1110110000010000", "0000000000000011",
                    "1110000010010000", "0000000000000000", "1110001100001000"]
        with open("asm/Add.asm") as f:
            code, errors = assemble(f.read().splitlines())
        self.assertEqual(errors, [])
        self.assertEqual(code, expected)

    def test_labels_and_variables(self):
        src = ["@i", "M=1", "(LOOP)", "@j", "M=1", "@LOOP", "0;JMP"]
        code, errors = assemble(src)
        self.assertEqual(errors, [])
        self.assertEqual(code[0], "0000000000010000")   # i -> 16
        self.assertEqual(code[2], "0000000000010001")   # j -> 17
        self.assertEqual(code[4], "0000000000000010")   # LOOP -> 2

    def test_predefined_symbols(self):
        code, _ = assemble(["@SCREEN", "@KBD", "@R5"])
        self.assertEqual(code, ["0100000000000000", "0110000000000000",
                                "0000000000000101"])

    def test_comments_and_blank_lines(self):
        code, errors = assemble(["// hi", "", "  D = M + 1  // x", ""])
        self.assertEqual(errors, [])
        self.assertEqual(code, ["1111110111010000"])

    # ---- extra feature (K mod 3 = 1): clear messages with line numbers ----
    def test_error_has_line_number(self):
        _, errors = assemble(["@2", "D=A", "// c", "", "D=Q+1", "@3"])
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith("Line 5: invalid instruction"))

    def test_multiple_errors_all_reported(self):
        _, errors = assemble(["D=A;JXX", "@99999", "(bad-label)", "X=D"])
        self.assertEqual(len(errors), 4)
        self.assertEqual([e.split(":")[0] for e in errors],
                         ["Line 1", "Line 2", "Line 3", "Line 4"])

    def test_no_crash_on_garbage(self):
        _, errors = assemble(["@", "===", ";;;", "@-5", "(", "()"])
        self.assertEqual(len(errors), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
