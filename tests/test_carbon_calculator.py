import unittest
from src.carbon_calculator import characterize,partial_sum
class CarbonCalculator(unittest.TestCase):
 def setUp(self):
  self.source=dict(source_url='https://example.org/test-only',source_sha256='a'*64,locator='TEST')
  self.cf=dict(self.source,method_id='TEST_GWP100',horizon_years=100,gases={'CO2_fossil':'1','CH4_biogenic':'23','N2O':'296'})
 def row(self,coverage='pond',mass='2',gas='CH4_biogenic'):
  return characterize(mass,'kg',gas,self.cf,basis_id='TEST_FU',coverage_id=coverage,source=self.source)
 def test_known_mass_and_partial_sum(self):
  self.assertEqual(self.row()['amount_kgCO2e'],'46')
  r=partial_sum([self.row(),self.row('N2O','1','N2O')]);self.assertEqual(r['partial_kgCO2e'],'342');self.assertIsNone(r['CO2e_total'])
 def test_no_second_gwp_or_ambiguous_gas_origin(self):
  with self.assertRaises(ValueError):characterize('1','kgCO2e','CH4_biogenic',self.cf,basis_id='x',coverage_id='x',source=self.source)
  with self.assertRaises(ValueError):self.row(gas='CH4')
  with self.assertRaises(ValueError):self.row(gas='CO2_biogenic')
 def test_duplicate_aggregate_and_mixed_basis_method_rejected(self):
  with self.assertRaises(ValueError):partial_sum([self.row(),self.row()])
  a=self.row('a');b=self.row('b');b['coverage_ids']=['a','b']
  with self.assertRaises(ValueError):partial_sum([a,b])
  for field in ['basis_id','method_id']:
   b=self.row('b');b[field]='OTHER'
   with self.assertRaises(ValueError):partial_sum([a,b])
 def test_missing_provenance_and_nonfinite_rejected(self):
  bad=dict(self.source,source_sha256='not-a-hash')
  with self.assertRaises(ValueError):characterize('1','kg','N2O',self.cf,basis_id='x',coverage_id='x',source=bad)
  for value in ['NaN','Infinity','-1',1.2]:
   with self.assertRaises(ValueError):self.row(mass=value)
