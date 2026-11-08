import copy
from decimal import Decimal
import unittest
from scripts.review_thai_mill_2019 import build
from src.mill_inventory_scaling import scale_mill


class MillScalingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.review=build()

    def test_source_reference_and_fractional_demand_conserve_quantities(self):
        for plant in range(1,7):
            at_reference=scale_mill(self.review,f'Mill {plant}','1000')
            small=scale_mill(self.review,f'Mill {plant}','1.25')
            original=[r for r in self.review['observations'] if r['mill']==f'Mill {plant}']
            self.assertEqual([r['source'] for r in at_reference['rows']],original)
            for base,ref,scaled in zip(original,at_reference['rows'],small['rows']):
                self.assertEqual(Decimal(ref['scaled_amount']),Decimal(base['amount']))
                self.assertEqual(Decimal(scaled['scaled_amount'])*800,Decimal(base['amount']))
            self.assertEqual(len(small['rows']),15)

    def test_unsafe_input_and_mixed_bases_rejected(self):
        for quantity in ['0','-1','NaN','Infinity','1e3','1,000','1.0000000000001']:
            with self.assertRaises(ValueError):scale_mill(self.review,'Mill 1',quantity)
        with self.assertRaises(ValueError):scale_mill(self.review,'average','1000')
        for key,value in [('reference_unit','MJ'),('source_sha256','wrong')]:
            bad=copy.deepcopy(self.review);bad['observations'][0][key]=value
            with self.assertRaises(ValueError):scale_mill(bad,'Mill 1','1000')
        bad=copy.deepcopy(self.review);bad['observations'].pop(0)
        with self.assertRaises(ValueError):scale_mill(bad,'Mill 1','1000')

    def test_no_emissions_or_credit_claim_from_activity_scaling(self):
        result=scale_mill(self.review,'Mill 3','1000')
        self.assertIsNone(result['CO2e_total'])
        self.assertFalse(result['full_lifecycle_inventory'])
        self.assertFalse(result['allocation_applied'])
        self.assertFalse(result['background_provider_applied'])
        self.assertFalse(result['avoided_product_credit_applied'])
        self.assertEqual(result['rights_status'],'NOT_CLEARED')


if __name__=='__main__':unittest.main()
