import unittest
from scripts.build_domain_factor_review import build


class DomainFactorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows={r['row_number']:r for r in build()['factors']}

    def test_lpg_different_processes_remain_distinct(self):
        self.assertEqual(self.rows[32]['process_family'],'GAS_SEPARATION')
        self.assertEqual(self.rows[37]['process_family'],'REFINING')
        self.assertNotEqual(self.rows[32]['value'],self.rows[37]['value'])

    def test_imported_mixes_and_unverified_origins_not_applied(self):
        for i in (33,34,35):
            self.assertEqual(self.rows[i]['admission_status'],'HOLD_EXPLICIT_IMPORTED_MIX')
        for row in self.rows.values():
            self.assertFalse(row['model_applied'])
            self.assertFalse(row['strict_all_inputs_thai_verified'])

    def test_co2_product_factor_is_not_direct_emission_or_gwp(self):
        row=self.rows[28]
        self.assertEqual(row['role'],'PRODUCT_SUPPLY')
        self.assertFalse(row['direct_emission_factor'])
        self.assertEqual(row['value'],'1.0017')
        self.assertEqual(self.rows[33]['activity_unit'],'kg')
        self.assertEqual(self.rows[34]['activity_unit'],'m3')


if __name__=='__main__':unittest.main()
