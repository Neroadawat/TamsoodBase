import unittest
from scripts.review_thai_use_treatment import review


class ThaiUseTreatmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=review()

    def test_four_flows_normalize_without_fossil_double_count(self):
        rows=self.result['use_observations']
        self.assertEqual({r['source_flow']:r['amount_kg'] for r in rows},
                         {'CO2':'2.78','CO':'0.0075','NOx':'0.029','PM_UNSPECIFIED':'0.0013'})
        self.assertFalse(self.result['reported_fossil_CO2_subset']['add_to_total_CO2'])

    def test_qualitative_treatment_not_fake_emissions(self):
        self.assertEqual(len(self.result['treatment_scenarios']),4)
        self.assertFalse(self.result['review']['treatment_quantities_available'])
        self.assertFalse(self.result['full_lifecycle_inventory'])

    def test_context_and_rights_remain_unlinked(self):
        self.assertFalse(self.result['merged_into_2020'])
        for row in self.result['use_observations']:
            self.assertEqual(row['reference_unit'],'litre biodiesel')
            self.assertEqual(row['rights_status'],'NOT_CLEARED')
            self.assertIsNone(row['measurement_year'])
            self.assertIsNone(row['global_flow_id'])


if __name__=='__main__':unittest.main()
