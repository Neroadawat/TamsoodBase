import copy
import json
import unittest
from pathlib import Path
from scripts.build_case_study_metadata import project,ROOT


class CaseMetadataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact=json.loads((ROOT/'build/thai-fame-activity-chain/scenarios.json').read_text(encoding='utf8'))
        cls.store=json.loads((ROOT/'evidence/activity-model-store.json').read_text(encoding='utf8'))

    def test_projection_is_exact_and_excludes_restricted_quantities(self):
        data=project(self.artifact,self.store)
        self.assertEqual(data,json.loads((ROOT/'web/case-study.json').read_text(encoding='utf8')))
        self.assertEqual(set(data['public_activity_kg']),{'CPO','RBDPO'})
        def keys(value):
            if isinstance(value,dict):
                for k,v in value.items():yield k;yield from keys(v)
            elif isinstance(value,list):
                for v in value:yield from keys(v)
        self.assertFalse({'rows','observations','raw_value','scaled_amount','payload_json'}&set(keys(data)))
        self.assertFalse(data['private_inventory_included'])
        self.assertTrue(all(d['state']=='OPEN' for d in data['open_decisions']))

    def test_unsealed_store_and_changed_licensed_quantities_rejected(self):
        with self.assertRaises(ValueError):project(self.artifact,dict(self.store,sealed=False))
        bad=copy.deepcopy(self.artifact);bad['baseline']['physical_demand_kg']['CPO']='999'
        with self.assertRaises(ValueError):project(bad,self.store)


if __name__=='__main__':unittest.main()
