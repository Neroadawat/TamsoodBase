import unittest
from decimal import Decimal, localcontext
from src.ethanol_demo import molasses_e10_basis

class EthanolDemoBasis(unittest.TestCase):
    def test_equal_distance_and_blend_close_without_duplicating_products(self):
        r=molasses_e10_basis('13.46',assumption_id='TEST')
        self.assertEqual(r['gasoline_equivalent_litres'],'1')
        with localcontext() as ctx:
            ctx.prec=40
            blend=Decimal(r['E10_litres'])
            self.assertLess(abs(blend*Decimal('13.31')-Decimal('13.46')),Decimal('1e-35'))
            self.assertLess(abs(Decimal(r['ethanol_blending_feed_litres'])+Decimal(r['gasoline_blending_feed_litres'])-blend),Decimal('1e-35'))
        self.assertIsNone(r['CO2e_total']);self.assertFalse(r['full_lifecycle_lci'])
    def test_physical_cane_is_not_cut_by_economic_allocation(self):
        r=molasses_e10_basis('1353.627',assumption_id='TEST')
        cane=next(x for x in r['physical_flows'] if x['name']=='cane_stalk')
        self.assertEqual(Decimal(cane['amount']),Decimal('1000'))
        self.assertFalse(r['economic_allocation']['applied_to_physical_flows'])
        self.assertFalse(r['mass_balance_closed'])
    def test_missing_assumption_nonfinite_float_zero_and_negative_rejected(self):
        for value in ['NaN','Infinity','0','-1',13.46]:
            with self.assertRaises(ValueError):molasses_e10_basis(value,assumption_id='TEST')
        with self.assertRaises(ValueError):molasses_e10_basis('1',assumption_id='')
