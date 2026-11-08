import sys,unittest
from pathlib import Path
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_nso_remaining import percentage

class PercentageAuditTests(unittest.TestCase):
    def test_display_rounding(self):
        self.assertTrue(percentage(Decimal(1),Decimal(3),Decimal('33.33333333'))[1])
    def test_material_difference_rejected(self):
        self.assertFalse(percentage(Decimal(1),Decimal(3),Decimal('33.3333'))[1])
    def test_zero_denominator_rejected(self):
        with self.assertRaises(ValueError):percentage(Decimal(1),Decimal(0),Decimal(0))
