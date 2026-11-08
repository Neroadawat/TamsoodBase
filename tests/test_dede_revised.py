import unittest
from types import SimpleNamespace
from decimal import Decimal
from scripts.compare_nso_dede_revised import manufacturing_total


class RevisedDedeTests(unittest.TestCase):
    def sheet(self,**changes):
        values=dict(DF1='TABLE THAILAND ENERGY BALANCE, 2024',DW2='unit : ktoe',A52=' อุตสาหกรรมการผลิต',DW52=' MANUFACTURING',DT9='GRAND TOTAL',DT52=30350)
        values.update(changes)
        return {k:SimpleNamespace(value=v) for k,v in values.items()}

    def test_total_with_valid_context(self):
        self.assertEqual(manufacturing_total(self.sheet()),Decimal('30350'))

    def test_shifted_context_or_uncached_formula_rejected(self):
        for change in [dict(DW52='INDUSTRY'),dict(DW2='GWh'),dict(DF1='2023'),dict(DT9='COMMERCIAL TOTAL'),dict(DT52='=SUM(A1:A2)'),dict(DT52=None)]:
            with self.assertRaises(ValueError):manufacturing_total(self.sheet(**change))
