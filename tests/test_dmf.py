import unittest
from src.process_dmf import validate


class DmfValidationTests(unittest.TestCase):
    def row(self, **changes):
        return dict(YEAR='2567',MONTH='2',BLOCK_TYPE='บนบก',BLOCK='',
                    SOURCE_GROUP='sample',OIL='0',DAYSOFPRODUCE='29') | changes

    def test_leap_year_and_optional_block(self):
        self.assertEqual(validate(self.row(),'OIL'),[])

    def test_impossible_days(self):
        self.assertIn('invalid_days_of_production',validate(self.row(YEAR='2566'),'OIL'))

    def test_invalid_month(self):
        self.assertTrue(validate(self.row(MONTH='13'),'OIL'))

    def test_missing_is_not_zero(self):
        self.assertIn('invalid_amount',validate(self.row(OIL=''),'OIL'))

    def test_non_finite(self):
        self.assertIn('invalid_amount',validate(self.row(OIL='NaN'),'OIL'))

    def test_unknown_area(self):
        self.assertIn('unknown_area',validate(self.row(BLOCK_TYPE='unknown'),'OIL'))
