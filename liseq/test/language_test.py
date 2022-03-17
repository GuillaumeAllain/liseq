import unittest
from liseq.core import transpiler


class Language_test(unittest.TestCase):
    def test_var_attribution_simple(self):
        self.assertEqual("^foovar == 3", transpiler("(set foovar 3)"))

    def test_var_attribution_complex(self):
        self.assertEqual(
            "^foovar == (^barvar + 3) / 3",
            transpiler("(set foovar (/ (+ barvar 3) 3))"),
        )

    def test_database(self):
        self.assertEqual("(x ri fl)", transpiler("(eva x ri fl)"))
        self.assertEqual("(xob f3)", transpiler("(eva xob f3)"))

    def test_special_calls(self):
        self.assertEqual("b^foobar", transpiler("(b foobar)"))
        self.assertEqual("a^foobar", transpiler("(a foobar)"))
        self.assertEqual("f3", transpiler("(f 3)"))
        self.assertEqual("sa", transpiler("(s a)"))

    def test_declare(self):
        self.assertEqual("lcl num ^foovar", transpiler("(local num foovar)"))
        self.assertEqual("num ^foovar", transpiler("(num foovar)"))
        self.assertEqual(("num ^foovar(3,4) ^barvar(3,4)"),(transpiler("((. num 3 4) foovar barvar)")))
        self.assertEqual(("num ^foovar(3,4) ^barvar(4,5)"),(transpiler("(num (. foovar 3 4) (. barvar 4 5))")))
        self.assertEqual("lcl num ^foovar(3)", transpiler("(local (. num 3) foovar)"))
        self.assertEqual("lcl num ^foovar(4)", transpiler("(local num (. foovar 4))"))
        self.assertEqual(
            "lcl num ^foovar(2,5)", transpiler("(local num (. foovar 2 5))")
        )
        self.assertEqual(
            "lcl num ^foovar(3,4)", transpiler("(local (. num 3 4) foovar)")
        )
        self.assertEqual(
            sorted("lcl num ^foovar(3,4) ^barvar(3,4)"),
            sorted(transpiler("(local (. num 3 4) foovar barvar)")),
        )

        self.assertEqual(
            sorted("lcl num ^foovar ^barvar"),
            sorted(transpiler("(local num foovar barvar)")),
        )
        self.assertEqual(
            sorted("lcl num ^foovar(3) ^barvar(4)"),
            sorted(transpiler("(local num (. foovar 3) (. barvar 4))")),
        )

    def test_attribution_declare(self):
        self.assertEqual(
            "lcl num ^foovar\n^foovar == 3", transpiler("(var num foovar 3)")
        )
        self.assertEqual(
            "lcl num ^foovar\n^foovar(3,5) == 3",
            transpiler("(var num (. foovar 3 5) 3)"),
        )
        self.assertEqual(
            "lcl num ^foovar(3,5)\n^foovar == 3",
            transpiler("(var (. num 3 5) foovar 3)"),
        )
        self.assertEqual(
            sorted("lcl num ^foovar ^barvar\n^foovar == 3\n^barvar == 4"),
            sorted(transpiler("(var num foovar 3)(var num barvar 4)")),
        )
        self.assertEqual(
            sorted("lcl num ^foovar(3,10) ^barvar(4,5)\n^foovar == 3\n^barvar == 4"),
            sorted(transpiler("(var (. num 3 10) foovar 3)(var (. num 4 5) barvar 4)")),
        )
        self.assertEqual(
            "lcl str ^foovar\n^foovar == 3", transpiler("(var str foovar 3)")
        )
        self.assertEqual(
            "lcl str ^foovar\n^foovar(3,5) == 3",
            transpiler("(var str (. foovar 3 5) 3)"),
        )
        self.assertEqual(
            "lcl str ^foovar(3,5)\n^foovar == 3",
            transpiler("(var (. str 3 5) foovar 3)"),
        )
        self.assertEqual(
            sorted("lcl str ^foovar ^barvar\n^foovar == 3\n^barvar == 4"),
            sorted(transpiler("(var str foovar 3)(var str barvar 4)")),
        )
        self.assertEqual(
            sorted("lcl str ^foovar(3,10) ^barvar(4,5)\n^foovar == 3\n^barvar == 4"),
            sorted(transpiler("(var (. str 3 10) foovar 3)(var (. str 4 5) barvar 4)")),
        )

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

    def test_var(self):
        # TODO: Var tests
        pass

    def test_tset(self):
        # TODO: Tset tests
        pass


if __name__ == "__main__":
    unittest.main()
