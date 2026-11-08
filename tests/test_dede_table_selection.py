import unittest
from decimal import Decimal
from scripts.compare_nso_dede_tables import annual_line,amount
class TableSelectionTests(unittest.TestCase):
    def test_negative_supply_sign(self):
        _,raw=annual_line('ก๊าซ (68) (70) (43) (2) (22) NATURAL GASOLINE','NATURAL GASOLINE')
        self.assertEqual(amount(raw[-1]),Decimal('-22'))
    def test_exact_english_label_not_prefix(self):
        with self.assertRaises(ValueError):annual_line('1 2 3 4 5 NATURAL GASOLINE','NATURAL GAS')
    def test_reject_ambiguous_repeated_row(self):
        with self.assertRaises(ValueError):annual_line('1 2 3 4 5 TOTAL\n1 2 3 4 5 TOTAL','TOTAL')
