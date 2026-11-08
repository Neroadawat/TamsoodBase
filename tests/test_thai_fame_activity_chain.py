import copy
import json
from decimal import Decimal
import unittest
from scripts.build_thai_fame_activity_chain import ROOT,build,review_ffb_distance
from scripts.review_thai_mill_2019 import build as review_mills


class ThaiFameChainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.combined=json.loads((ROOT/'build/combined-inventory-review/review.json').read_text(encoding='utf8'))
        cls.mills=review_mills()

    def test_all_six_scenarios_balance_and_preserve_every_source_field(self):
        expected=[m['source'] for m in self.combined['mappings'] if m['source']['process'] in ['FFB','RBDPO','FAME']]
        for i in range(1,7):
            model=build(self.combined,self.mills,f'Mill {i}')
            original=expected+[r for r in self.mills['observations'] if r['mill']==f'Mill {i}']
            actual=[r['source'] for r in model['rows']]
            self.assertEqual(len(actual),55)
            self.assertTrue(all(r in actual for r in original))
            for edge in model['physical_transfer_candidates']:
                self.assertEqual(Decimal(edge['supplied_kg']),Decimal(edge['consumed_kg']))
                self.assertFalse(edge['burden_link_applied'])
            self.assertEqual(model['physical_demand_kg']['CPO'],'27.0600')
            self.assertEqual(sum(r['scaled_amount'] is None for r in model['rows']),1)

    def test_baseline_is_explicit_scenario_not_fake_complete_result(self):
        model=build(self.combined,self.mills)
        self.assertEqual(Decimal(model['physical_demand_kg']['FFB']),Decimal('187.5258'))
        self.assertFalse(model['selection']['national_average'])
        self.assertIsNone(model['CO2e_total'])
        self.assertFalse(model['full_lifecycle_inventory'])
        self.assertEqual(model['allocation']['status'],'UNRESOLVED_NOT_APPLIED')
        self.assertIn('Thai_background_exchanges_and_rights',model['open_gates'])

    def test_unit_or_basis_change_and_synthetic_mill_rejected(self):
        with self.assertRaises(ValueError):build(self.combined,self.mills,'average')
        for key,val in [('unit','m3'),('reference_amount','1')]:
            bad=copy.deepcopy(self.combined)
            row=next(m['source'] for m in bad['mappings']
                     if m['source']['process']=='FAME' and m['source']['flow']=='RBDPO')
            row[key]=val
            with self.assertRaises(ValueError):build(bad,self.mills)

    def test_transport_estimate_is_not_return_zero_or_emissions(self):
        source=review_ffb_distance()
        model=build(self.combined,self.mills,ffb_distance=source)
        first=model['transport_legs'][0]
        self.assertEqual(Decimal(first['loaded_tkm']),Decimal('0.937629'))
        self.assertIsNone(first['empty_return'])
        self.assertIsNone(first['provider'])
        self.assertFalse(first['emissions_applied'])
        self.assertTrue(all(r['distance_km'] is None for r in model['transport_legs'][1:]))
        bad=dict(source,source_sha256='invalid')
        with self.assertRaises(ValueError):build(self.combined,self.mills,ffb_distance=bad)


if __name__=='__main__':unittest.main()
