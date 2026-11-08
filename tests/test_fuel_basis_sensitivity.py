import unittest
from decimal import Decimal,localcontext
from scripts.build_fuel_basis_sensitivity import build
from src.thai_carbon import screen_activity
class FuelSensitivity(unittest.TestCase):
    def test_two_scenarios_exact_product_no_sum_or_carbon_saving_claim(self):
        r=build();self.assertEqual(len(r['cases']),2)
        for case in r['cases']:
            with localcontext() as ctx:
                ctx.prec=210
                self.assertEqual(Decimal(case['screening']['result']),Decimal(case['activity_mass_kg'])*Decimal('1.0372'))
        self.assertFalse(r['combined_with_foreground']);self.assertFalse(r['full_lifecycle_inventory']);self.assertIsNone(r['full_lifecycle_CO2e_total']);self.assertIsNone(r['tailpipe_CO2_kg']);self.assertFalse(r['strict_all_inputs_thai_verified']);self.assertIn('NOT demonstrated carbon saving',r['interpretation'])
    def test_stationary_cfo_factor_cannot_enter_thai_lci_screening(self):
        with self.assertRaises(ValueError):screen_activity('1','Liter',{'geography':'TH','provenance_class':'TGO_CFO_IPCC_DEFAULT_STATIONARY','value':'1.64961846'})
