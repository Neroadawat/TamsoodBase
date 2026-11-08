import unittest
from decimal import Decimal
from scripts.build_thai_gsp_review import build


class ThaiGspTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=build();cls.rows=cls.result['observations']

    def test_unit_and_detailed_co2_not_summary_replacement(self):
        co2={r['plant']:r for r in self.rows if r['flow']=='CO2'}
        self.assertEqual(co2['GSP3']['amount'],'62600')
        self.assertEqual(co2['GSP3']['raw_value'],'6.26E+04')
        self.assertEqual(co2['GSP3']['unit'],'mg')
        self.assertEqual(Decimal(co2['GSP1']['amount'])/Decimal('1000000'),Decimal('0.048'))

    def test_dash_is_not_zero_and_scope_not_expanded(self):
        held=[r for r in self.rows if r['amount'] is None]
        self.assertEqual(len(held),1)
        self.assertEqual((held[0]['plant'],held[0]['flow']),('GSP3','Electricity EGAT'))
        self.assertEqual(held[0]['raw_value'],'-')
        for row in self.rows:
            self.assertFalse(row['full_lifecycle_inventory']);self.assertFalse(row['model_applied'])
            self.assertIsNone(row['measurement_period'])

    def test_provenance_and_source_conflict_retained(self):
        self.assertEqual(len(self.rows),42)
        for row in self.rows:
            self.assertTrue(row['source_sha256']);self.assertIn(row['chapter_pdf_page'],(4,6,9))
            self.assertEqual(row['rights_status'],'NOT_CLEARED')
        self.assertEqual(self.result['comparison']['capacity_status'],'UNRESOLVED_SOURCE_CONFLICT')


if __name__=='__main__':unittest.main()
