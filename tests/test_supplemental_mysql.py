import unittest
from scripts.load_supplemental_mysql import decimal_value, literal


class SupplementalSQLTests(unittest.TestCase):
    def test_exact_decimal_and_negative_supply(self):
        self.assertEqual(decimal_value('-123.4500'), '-123.4500')
        self.assertEqual(decimal_value('0.000000000001'), '0.000000000001')
        for value in ['NaN', 'Infinity', '1000000000000000000', '0.0000000000001']:
            with self.assertRaises(ValueError):
                decimal_value(value)

    def test_sql_literal_preserves_unicode_and_quotes(self):
        text = "น้ำมัน ' \\ \n"
        encoded = literal(text).split("X'")[1].split("'")[0]
        self.assertEqual(bytes.fromhex(encoded).decode('utf-8'), text)
        self.assertEqual(literal(None), 'NULL')
