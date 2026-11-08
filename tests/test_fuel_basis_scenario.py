import unittest
from decimal import Decimal
from src.fuel_basis_scenario import fuel_basis
class FuelBasisScenario(unittest.TestCase):
    def test_unknown_denominator_cannot_be_silently_normalized(self):
        with self.assertRaises(ValueError):fuel_basis(1000,39.89,862.79)
    def test_conditional_scenario_energy_mass_replay_and_no_impact_claim(self):
        x=fuel_basis('1000','39.89','862.79',assumption_id='TEST_EXPLICIT_INTERPRETATION',lhv_interpreted_mj_per_kg=True)
        self.assertLess(abs(Decimal(x['mass_kg'])*Decimal('39.89')-1000),Decimal('1e-25'))
        self.assertEqual(x['density_kg_per_litre'],'0.86279');self.assertIsNone(x['CO2e_total']);self.assertFalse(x['emission_factor_eligible']);self.assertFalse(x['existing_model_changed'])
    def test_nonfinite_or_negative_rejected(self):
        for value in ['NaN','Infinity','0','-1']:
            with self.assertRaises(ValueError):fuel_basis(value,39.89,862.79,assumption_id='TEST',lhv_interpreted_mj_per_kg=True)
