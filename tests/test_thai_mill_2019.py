import unittest
from decimal import Decimal
from scripts.review_thai_mill_2019 import build


class ThaiMill2019Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=build()

    def test_complete_selected_table_and_plant_identity(self):
        rows=self.result['observations']
        self.assertEqual(len(rows),90)
        self.assertEqual(len({r['id'] for r in rows}),90)
        for plant in range(1,7):
            subset=[r for r in rows if r['mill']==f'Mill {plant}']
            self.assertEqual(len(subset),15)
            self.assertTrue(all(r['reference_amount']=='1000' and r['reference_product']=='CPO'
                                for r in subset))
        self.assertEqual(self.result['FFB_per_CPO_by_mill']['Mill 1'],'6.93')
        self.assertEqual(self.result['FFB_per_CPO_by_mill']['Mill 6'],'5.65')

    def test_reported_zeros_kept_but_no_false_elementary_emission(self):
        rows=self.result['observations']
        zeros=[r for r in rows if Decimal(r['amount'])==0]
        self.assertEqual(len(zeros),7)
        self.assertTrue(all(r['raw_value']=='0' for r in zeros))
        pome=[r for r in rows if r['flow']=='Treated POME']
        self.assertEqual(len(pome),6)
        self.assertTrue(all(r['role']=='TREATED_WASTEWATER_OUTPUT' and not r['elementary_flow'] for r in pome))

    def test_no_silent_2020_merge_or_background_credit(self):
        self.assertFalse(self.result['compatibility']['linked_to_2020'])
        self.assertFalse(self.result['full_lifecycle_inventory'])
        self.assertTrue(all(not r['model_applied'] for r in self.result['observations']))
        self.assertTrue(all(r['source_sha256'] and r['source_url'] and r['pdf_page']==11
                            for r in self.result['observations']))


if __name__=='__main__':unittest.main()
