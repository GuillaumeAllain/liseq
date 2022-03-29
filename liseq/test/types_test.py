import unittest
from liseq.core import transpiler


class Types_test(unittest.TestCase):
    def test_string(self):
        self.assertEqual(
            '"salut"',
            transpiler('"salut"'),
        )
        self.assertEqual(
            '"salut"',
            transpiler('("salut")'),
        )

    def test_surface(self):
        self.assertEqual(
            "s3",
            transpiler("(s 3)"),
        )
        self.assertEqual(
            "sa",
            transpiler("(s a)"),
        )
        self.assertEqual(
            "s^surf",
            transpiler("(s surf)"),
        )
        self.assertEqual("s3..4", transpiler("(.. (s 3) 4)"))
        self.assertEqual("so..l", transpiler("(.. (s o) l)"))
        self.assertEqual("s3..4", transpiler("(s (.. 3 4))"))
        self.assertEqual("so..l", transpiler("(from (s o) l)"))
        self.assertEqual("s3..4", transpiler("(s (to 3 4))"))
        self.assertEqual("il+1", transpiler("(+ (i l) 1)"))

    def test_others(self):
        self.assertEqual(
            "a3",
            transpiler("(a 3)"),
        )
        self.assertEqual(
            "fl",
            transpiler("(f l)"),
        )
        self.assertEqual(
            "z^last",
            transpiler("(z last)"),
        )

    def test_database(self):
        self.assertEqual(
            "(efl)",
            transpiler("(database efl)"),
        )
        self.assertEqual(
            "(thi s3)",
            transpiler("(database thi (s 3))"),
        )

    # def test_types(self):
    #     self.assertEqual("il+1", transpiler("(i (+ l 1)))"))
    #     self.assertEqual("^foovar", transpiler("(foovar)"))
    #     self.assertEqual('@foovar("oui")', transpiler('(fctcall foovar "oui")'))
    #     self.assertEqual('concat(^foovar,"oui")', transpiler('(concat foovar "oui")'))
    #     self.assertEqual("3", transpiler("(3)"))


if __name__ == "__main__":
    unittest.main()
