import unittest
import json
from decimal import Decimal
from pathlib import Path
from src.report_pilot import extract_values


class ReportParsingTests(unittest.TestCase):
    def test_four_year_columns_keep_raw_precision(self):
        _,values=extract_values('  • Fuel oil   Million GJ   4.30 4.27 4.94 4.69','Fuel oil','Million GJ')
        self.assertEqual(values,['4.30','4.27','4.94','4.69'])

    def test_censored_or_missing_value_is_not_zero(self):
        for line in ('LPG Million GJ Less than 0.01 0 0 0','LPG Million GJ 0 0 0','LPG Million GJ 0 NAP 0 0'):
            with self.subTest(line=line),self.assertRaises(ValueError): extract_values(line,'LPG','Million GJ')

    def test_duplicate_rows_are_not_selected_arbitrarily(self):
        with self.assertRaises(ValueError): extract_values('X GJ 1 2 3 4\nX GJ 5 6 7 8','X','GJ')

    def test_similar_label_does_not_match(self):
        with self.assertRaises(ValueError): extract_values('Fuel gas Million GJ 1 2 3 4','Fuel oil','Million GJ')


@unittest.skipUnless(Path('build/report-pilot/report.json').exists(),'Local report build required')
class ReportIntegrationTests(unittest.TestCase):
    def test_scaled_values_keep_boundary_and_no_acceptance(self):
        report=json.loads(Path('build/report-pilot/report.json').read_text(encoding='utf-8'))
        self.assertEqual(len(report['rows']),48)
        self.assertEqual(len({(r['metric_id'],r['year']) for r in report['rows']}),48)
        for row in report['rows']:
            self.assertEqual(Decimal(row['normalized_value']),Decimal(row['value'])*Decimal(row['scale_factor']))
            self.assertFalse(row['competition_accepted'])
            self.assertIsNone(row['reference_product_amount'])
            self.assertEqual(row['pdf_sha256'],report['pdf_sha256'])
            self.assertTrue(row['boundary'])
