import unittest
from decimal import Decimal
from src.export_full_mysql import exact_decimal, text_sql, snapshot_id
from src.review_dmf import investigation


class FullMySQLTests(unittest.TestCase):
    def test_decimal_preserves_source_precision(self):
        for value in ('0','12345.1234567890','0.000000000001','999999999999999999.999999999999'):
            self.assertEqual(Decimal(exact_decimal(value)),Decimal(value))

    def test_decimal_refuses_rounding_overflow_and_nonfinite(self):
        for value in ('0.0000000000001','1000000000000000000','-1','NaN','Infinity'):
            with self.subTest(value=value),self.assertRaises(ValueError): exact_decimal(value)

    def test_sql_text_cannot_escape_literal(self):
        value="ไทย'); DROP TABLE observation; --"
        self.assertEqual(text_sql(value),"CONVERT(X'"+value.encode().hex()+"' USING utf8mb4)")

    def test_snapshot_identity_includes_metadata(self):
        entry={'package':'oil','csv_sha256':'abc','metadata_sha256':'def'}
        self.assertNotEqual(snapshot_id(entry),snapshot_id(entry|{'metadata_sha256':'changed'}))

    def test_calendar_pattern_never_promotes_or_merges(self):
        common={'identity_sha256':'x','package':'oil','source_group':'field','year_ce':2024,'month':2}
        rows=[common|{'source_line':2,'production_days':'7'},common|{'source_line':3,'production_days':'22'}]
        result=investigation(rows)
        self.assertEqual(result['pattern'],'POSSIBLE_SUBPERIOD')
        self.assertEqual(result['calendar_days'],29)
        self.assertEqual(result['disposition'],'HOLD_CONFLICT')
        self.assertFalse(result['automatic_merge_allowed'])
