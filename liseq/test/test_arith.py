import unittest
from liseq.core import transpiler


class Arith_test(unittest.TestCase):
    def test_add(self):
        self.assertEqual(transpiler("(+ 1 2)"), "(1 + 2)")
        self.assertEqual(transpiler("(+ 1 (+ 2 3))"), "(1 + ((2 + 3)))")

    def test_sub(self):
        self.assertEqual(transpiler("(- 1 2)"), "(1 - 2)")
        self.assertEqual(transpiler("(- 1 (- 2 3))"), "(1 - ((2 - 3)))")

    def test_mul(self):
        self.assertEqual(transpiler("(* 1 2)"), "(1 * 2)")
        self.assertEqual(transpiler("(* 1 (* 2 3))"), "(1 * ((2 * 3)))")

    def test_div(self):
        self.assertEqual(transpiler("(/ 1 2)"), "(1 / 2)")
        self.assertEqual(transpiler("(/ 1 (/ 2 3))"), "(1 / ((2 / 3)))")

    def test_surf(self):
        self.assertEqual(transpiler("(.. s 3)"), "s..3")
        self.assertEqual(transpiler("(.. s l)"), "s..l")
        self.assertEqual(transpiler("(.. s (var surf))"), "s..^surf")

    def test_eq(self):
        self.assertEqual(transpiler("(eq 10 30)"), "(10 = 30)")
        self.assertEqual(transpiler("(eq 10 (var salut))"), "(10 = ^salut)")

    def test_neq(self):
        self.assertEqual(transpiler("(neq 10 30)"), "(10 <> 30)")
        self.assertEqual(transpiler("(neq 10 (var salut))"), "(10 <> ^salut)")

    def test_close(self):
        self.assertEqual(transpiler("(>< 10 30)"), "(absf((10 - 30)) <= 1e-6)")


if __name__ == "__main__":
    unittest.main()
