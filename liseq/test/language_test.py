import unittest
from liseq.core import transpiler


class Language_test(unittest.TestCase):
    def test_types(self):
        self.assertEqual('"string"', transpiler('("string")'))
        self.assertEqual('"string"', transpiler("(:string)"))
        self.assertEqual("s3..4", transpiler("(.. s3 4)"))
        self.assertEqual("so..l", transpiler("(.. so l)"))
        self.assertEqual("s3..4", transpiler("(s (.. 3 4))"))
        self.assertEqual("so..l", transpiler("(from so l)"))
        self.assertEqual("s3..4", transpiler("(s (to 3 4))"))
        self.assertEqual("il+1", transpiler("(i (+ l 1)))"))
        self.assertEqual("^foovar", transpiler("(foovar)"))
        self.assertEqual('@foovar("oui")', transpiler('(fctcall foovar "oui")'))
        self.assertEqual('concat(^foovar,"oui")', transpiler('(concat foovar "oui")'))
        self.assertEqual("3", transpiler("(3)"))

    # TODO: Goto test
    # TODO: macro test
    # TODO: Tset tests


if __name__ == "__main__":
    unittest.main()
