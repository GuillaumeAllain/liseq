import unittest
from liseq.core import transpiler


class Set_test(unittest.TestCase):
    def test_number_var_attribution(self):
        self.assertEqual("^foovar == 3", transpiler("(setq foovar 3)"))
        self.assertEqual("^i == 3", transpiler("(setq i 3)"))

    def test_number_var_attribution_multiple(self):
        self.assertEqual(
            "^foovar == 3\n^barvar == 4", transpiler("(setq foovar 3 barvar 4)")
        )
        self.assertEqual(
            '^foovar == 3\n^barvar == "huit"',
            transpiler('(setq foovar 3 barvar "huit")'),
        )

    def test_number_var_attribution_array(self):
        self.assertEqual("^foovar(3) == 3", transpiler("(setq (nth foovar 3) 3)"))
        self.assertEqual(
            '^foovar(3,4) == "neuf"', transpiler('(setq (nth foovar 3 4) "neuf")')
        )

    def test_number_var_attribution_multiple_array(self):
        self.assertEqual(
            '^foovar(3) == 3\n^barvar(4,5) == "huit"',
            transpiler('(setq (nth foovar 3) 3 (nth barvar 4 5) "huit")'),
        )

    def test_var_declaration_attribution(self):
        self.assertEqual(
            "lcl num ^foovar\n^foovar == 3", transpiler("(setq (num foovar) 3)")
        )
        self.assertEqual('lcl str ^i\n^i == "bar"', transpiler('(setq (str i) "bar")'))

    def test_var_declaration_attribution_array(self):
        self.assertEqual(
            "lcl num ^foovar(3)\n^foovar(3) == 3",
            transpiler("(setq (num (nth foovar 3)) 3)"),
        )
        self.assertEqual(
            'lcl str ^foovar(3,4)\n^foovar(3,4) == "huit"',
            transpiler('(setq (str (nth foovar 3 4)) "huit")'),
        )

    def test_database_attribution(self):
        self.assertEqual("thi 10", transpiler("(setd thi 10)"))
        self.assertEqual("thi s1 10", transpiler("(setd (thi s1) 10)"))
        self.assertEqual("thi s1 ^surf", transpiler("(setd (thi s1) (var surf))"))
        self.assertEqual(
            "thi s^surf ^thickness", transpiler("(setd (thi (s ^surf)) (var thickness))")
        )
        self.assertEqual("thi s3 ^surf", transpiler("(setd (thi (s 3)) ^surf)"))

    # def test_function_definition(self):

    def test_function(self):
        self.assertEqual(
            "fct @test(num ^arg1)\n" "end fct ^outputvar",
            transpiler("(defun test ((num arg1)) (outputvar))"),
        )
        self.assertEqual(
            "fct @test(num ^arg1)\n" "end fct ^outputvar",
            transpiler("(defun test (^arg1) (outputvar))"),
        )
        self.assertEqual(
            "fct @test(num ^arg1(3,4), str ^arg2(3))\n" "end fct ^arg1",
            transpiler("(defun test ((num (nth arg1 3 4))(str (nth arg2 3))) (arg1))"),
        )
        self.assertEqual(
            "fct @test(num ^arg1(10), str ^arg2(3))\n"
            "    lcl num ^outputvar\n    ^outputvar == 0\n"
            "end fct ^outputvar",
            transpiler(
                "(defun test ((num (nth arg1 10))(str (nth arg2 3))) (setq (num outputvar) 0) (outputvar))"
            ),
        )
        self.assertEqual(
            sorted(
                "fct @test(num ^arg1(10), str ^arg2(3))\n"
                "    lcl num ^scope1 ^scope2(3,4)\n"
                "    lcl str ^scope3\n"
                '    ^scope3 == "test"\n'
                "end fct ^outputvar"
            ),
            sorted(
                transpiler(
                    "(defun test ((num (nth arg1 10))(str (nth arg2 3)))"
                    ' (local num scope1 (. scope2 3 4)) (setq (str scope3) "test") (outputvar))'
                )
            ),
        )

    def test_declare(self):
        self.assertEqual("lcl num ^foovar", transpiler("(local num foovar)"))
        self.assertEqual("lcl num ^foovar", transpiler("(num foovar)"))
        # self.assertEqual(("num ^foovar(3,4) ^barvar(3,4)"),(transpiler("((. num 3 4) foovar barvar)")))
        self.assertEqual(
            set("lcl num ^foovar(3,4) ^barvar(4,5)"),
            set(transpiler("(num (. foovar 3 4) (. barvar 4 5))")),
        )
        self.assertEqual("lcl num ^foovar(4)", transpiler("(local num (. foovar 4))"))
        self.assertEqual(
            "lcl num ^foovar(2,5)", transpiler("(local num (. foovar 2 5))")
        )
        self.assertEqual(
            sorted("lcl num ^foovar ^barvar"),
            sorted(transpiler("(local num foovar barvar)")),
        )
        self.assertEqual(
            sorted("lcl num ^foovar(3) ^barvar(4)"),
            sorted(transpiler("(local num (. foovar 3) (. barvar 4))")),
        )

if __name__ == "__main__":
    unittest.main()
