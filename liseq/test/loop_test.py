import unittest
from liseq.core import transpiler


class Loop_test(unittest.TestCase):
    def test_if_1arg(self):
        self.assertEqual("if foo = 3\nend if", transpiler("(if (== foo 3))"))

    def test_if_2arg(self):
        self.assertEqual(
            "if foo = 2\n    ^barvar == 2\n    ^barvar == ^barvar + 1\nend if",
            transpiler("(if (== foo 2) ((var barvar 2)(var barvar (+ barvar 1))))"),
        )

    def test_if_2argelse(self):
        self.assertEqual(
            "if foo = 2\n    ^barvar == 2\n"
            "    ^barvar == ^barvar + 1\nelse\n    ^barvar == 3\nend if",
            transpiler(
                "(if (== foo 2) ((var barvar 2)(var barvar (+ barvar 1))) (var barvar 3))"
            ),
        )

    def test_if_4argelse(self):
        self.assertEqual(
            "if foo = 2"
            "\n    ^barvar == 2\n    ^barvar == ^barvar + 1\n"
            "else if foo = 3"
            "\n    ^barvar == 3\n    ^barvar == ^barvar + 2\n"
            "else\n    ^barvar == 3\nend if",
            transpiler(
                "(if (== foo 2) ((var barvar 2)(var barvar (+ barvar 1)))"
                " (== foo 3) ((var barvar 3)(var barvar (+ barvar 2))) (var barvar 3))"
            ),
        )

    def test_if_4arg(self):
        self.assertEqual(
            "if foo = 2"
            "\n    ^barvar == 2\n    ^barvar == ^barvar + 1\n"
            "else if foo = 3"
            "\n    ^barvar == 3\n    ^barvar == ^barvar + 2\nend if",
            transpiler(
                "(if (== foo 2) ((var barvar 2)(var barvar (+ barvar 1)))"
                " (== foo 3) ((var barvar 3)(var barvar (+ barvar 2))))"
            ),
        )

    def test_chained_if(self):
        self.assertEqual(
            "if foo = 3\n    if foo = 2\n        wri true\n    end if\nend if",
            transpiler("(if (== foo 3) (if (== foo 2) (wri true)))"),
        )

    def test_for_empty(self):
        self.assertEqual("for ^i 1 10 3\nend for", transpiler("(for [i 1 10 3])"))

    def test_for_args(self):
        self.assertEqual(
            "for ^i 1 10 3\n    wri 4\n    ^foovar == 3\nend for",
            transpiler("(for [i 1 10 3] (wri 4) (var foovar 3))"),
        )

    def test_chained_for_args(self):
        self.assertEqual(
            "if true\n    for ^i 1 10 3"
            "\n        wri 4\n        ^foovar == 3"
            "\n    end for\nend if",
            transpiler("(if true (for [i 1 10 3] (wri 4) (var foovar 3)))"),
        )

    def test_unt(self):
        self.assertEqual(
            "unt\n"
            "    rea u^datafile ^x ^y\n"
            "    if not(eofile)\n"
            "        in savedata ^x ^y\n"
            "    end if\n"
            "end unt eofile",
            transpiler(
                "(unt eofile (rea (u datafile) ^x ^y) (if (not eofile) (in savedata ^x ^y)))"
            ),
        )


if __name__ == "__main__":
    unittest.main()
