import unittest
from decimal import Decimal
from src.ethanol_proxy_scenario import scenario

def calculate(*args, mass_rows=None, **kwargs):
    if mass_rows is None:
        mass_rows = [dict(flow=flow, amount=amount, unit="t/day", locator="test", role="BOUNDARY_FLOW") for flow, amount in [("fuel_ethanol", "118.35"), ("molasses", "532.45")]]
    return scenario(*args, mass_rows=mass_rows, production_L_day="150000", energy_basis_L_day="150000", **kwargs)
class EthanolProxy(unittest.TestCase):
 def rows(self):return [dict(route='molasses',flow='electricity',unit='kWh/day',range=['22000','44000'],locator='TEST/table'),dict(route='molasses',flow='steam',unit='t/day',range=['200','400'],locator='TEST/table')]
 def factor(self):return dict(id='TEST',activity_unit='tkm',value='0.0546',geography='TH',provenance_class='THAI_NATIONAL_LCI_REPORTED',result_unit='kgCO2e',method='TEST_ONLY',version='TEST_ONLY',source_url='https://example.org/fixture',source_sha256='a'*64,locator='TEST_ONLY')
 def test_source_scale_recovered_and_no_total(self):
  r=calculate('150000',self.rows(),self.factor(),distance_km='50',assumption_id='TEST_ONLY');self.assertEqual([Decimal(x) for x in r['energy']['electricity']['amount_range']],[Decimal(22000),Decimal(44000)]);self.assertEqual(Decimal(r['freight'][0]['mass_kg']),Decimal('118350'));self.assertEqual(Decimal(r['freight'][1]['tkm']),Decimal('26622.5'));self.assertIsNone(r['CO2e_total']);self.assertFalse(r['freight_legs_additive'])
 def test_invalid_units_duplicates_and_missing_assumption(self):
  rows=self.rows();rows[0]['unit']='MJ/day'
  with self.assertRaises(ValueError):calculate('1',rows,self.factor(),distance_km='50',assumption_id='TEST')
  with self.assertRaises(ValueError):calculate('1',self.rows()+self.rows(),self.factor(),distance_km='50',assumption_id='TEST')
  with self.assertRaises(ValueError):calculate('1',self.rows(),self.factor(),distance_km='50',assumption_id='')

 def test_reviewed_mass_changes_freight(self):
  rows = [dict(flow=flow, amount=amount, unit='t/day', locator='test', role='BOUNDARY_FLOW')
          for flow, amount in [('fuel_ethanol', '118.35'), ('molasses', '600')]]
  result = calculate('150000', self.rows(), self.factor(), distance_km='50',
                     assumption_id='TEST_ONLY', mass_rows=rows)
  self.assertEqual(Decimal(result['freight'][1]['tkm']), Decimal('30000'))

 def test_unreviewed_edits_to_mass_and_energy_are_rejected(self):
  import hashlib
  import json
  import tempfile
  from pathlib import Path
  from scripts.build_ethanol_proxy_scenario import reviewed_inputs
  names = ['evidence/dede-molasses-balance.json', 'evidence/dede-ethanol-survey-review.json',
           'build/transport-sensitivity/report.json']
  original = b'{"fixture": true}'
  with tempfile.TemporaryDirectory() as directory:
   target = Path(directory)
   for name in names:
    (target / name).parent.mkdir(parents=True, exist_ok=True)
    (target / name).write_bytes(original)
   manifest = {'approval_scope': 'INTERNAL_SOURCE_REVIEW',
               'sha256': {name: hashlib.sha256(original).hexdigest() for name in names}}
   (target / 'evidence/ethanol-reviewed-inputs.json').write_text(json.dumps(manifest), encoding='utf-8')
   reviewed_inputs(target)
   for name in names[:2]:
    (target / name).write_bytes(original + b' ')
    with self.assertRaisesRegex(ValueError, 'Reviewed input hash mismatch'):
     reviewed_inputs(target)
    (target / name).write_bytes(original)
