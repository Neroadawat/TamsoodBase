import json
import unittest
from pathlib import Path
from src.sprc_report import table_row,rounding_overlap


class SPRCParsingTests(unittest.TestCase):
    def test_gri_prefix_and_exact_year_count(self):
        self.assertEqual(table_row('302-1 Natural Gas GJ 1,234 2 3 4','Natural Gas','GJ')[1],['1,234','2','3','4'])
        with self.assertRaises(ValueError): table_row('Natural Gas GJ 1 2 3','Natural Gas','GJ')

    def test_rounding_can_explain_small_display_difference(self):
        self.assertTrue(rounding_overlap('2,876,031','1','2.88','1000000'))
        self.assertFalse(rounding_overlap('3,044,250','1','3.06','1000000'))

    def test_water_qualifiers_not_silently_dropped(self):
        with self.assertRaises(ValueError): table_row('Fresh water by throughput m3 1 2 3 4','Fresh water','m3')


@unittest.skipUnless(Path('build/sprc-report/report.json').exists(),'SPRC build required')
class SPRCIntegrationTests(unittest.TestCase):
    def test_findings_preserve_both_sources_without_promotion(self):
        report=json.loads(Path('build/sprc-report/report.json').read_text(encoding='utf-8'))
        self.assertEqual(len(report['rows']),53)
        self.assertEqual(len(report['issues']),2)
        self.assertTrue(all(not r['automatic_merge_allowed'] and r['preferred_source'] is None for r in report['issues']))
        self.assertTrue(all(not r['competition_accepted'] for r in report['rows']))
        self.assertEqual(len(report['arithmetic_checks']),8)
        self.assertTrue(all(c['result']=='WITHIN_DISPLAY_ROUNDING' for c in report['arithmetic_checks']))
