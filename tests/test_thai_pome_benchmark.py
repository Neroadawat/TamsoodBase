import unittest
from decimal import Decimal
from scripts.review_thai_pome_benchmark import review


class ThaiPomeBenchmarkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=review()

    def test_all_operating_points_match_source(self):
        self.assertEqual(self.result['treatment']['operating_points'],
          [['14','2.43','70','95','70.03'],['10','5.09','68','95','69.29'],
           ['7','6.50','65','96','66.83'],['6.5','8.70','65','93','66.41']])

    def test_generation_is_not_emissions_or_net_credit(self):
        t=self.result['treatment'];self.assertIsNone(t['fugitive_CH4_emission'])
        self.assertIsNone(t['net_electricity_export_per_m3'])
        self.assertIsNone(t['wastewater_per_FAME_reference_unit'])
        self.assertEqual(Decimal(t['derived_gross_electricity_per_wastewater']['amount']),Decimal('20')*Decimal('2.5'))
        self.assertFalse(t['linked_to_FAME'])

    def test_benchmark_is_separate_and_not_claimed_full_lci(self):
        b=self.result['benchmark']
        self.assertEqual(Decimal(b['WTT'])+Decimal(b['TTW']),Decimal(b['WTW']))
        self.assertFalse(b['applied_as_factor']);self.assertFalse(self.result['full_lifecycle_inventory'])


if __name__=='__main__':unittest.main()
