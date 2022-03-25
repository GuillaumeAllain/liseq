import unittest
from liseq.core import transpiler


class Set_test(unittest.TestCase):
    def test_number_var_attribution(self):
        self.assertEqual("^foovar == 3", transpiler("(setq foovar 3)"))
        self.assertEqual("^i == 3", transpiler("(setq i 3)"))

    def test_var_declaration_attribution(self):
        self.assertEqual("num ^foovar\n^foovar == 3", transpiler("(setq (num foovar) 3)"))
        self.assertEqual('str ^i\n^i == "bar"', transpiler('(setq (str i) "bar")'))

if __name__ == "__main__":
    unittest.main()
