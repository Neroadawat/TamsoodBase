import copy
import json
import unittest
from scripts.build_boundary_coverage import ROOT, coverage


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        def read(name): return json.loads((ROOT/name).read_text(encoding='utf8'))
        self.up = read('build/upstream-inventory/report.json')
        self.base = read('build/product-inventory/report.json')
        self.provider = read('evidence/upstream-provider-review.json')

    def test_all_source_ids_and_holds_preserved_without_fake_completeness(self):
        result = coverage(self.up,self.base,self.provider)
        ids = [i for p in result['profiles'] for i in p['observation_ids']]
        self.assertEqual(set(ids), {r['observation_id'] for r in self.up['rows']+self.base['rows']})
        self.assertEqual(len(ids),58)
        self.assertEqual(sum(len(p['held_observation_ids']) for p in result['profiles']),1)
        self.assertIsNone(result['quantitative_completeness_percent'])
        self.assertTrue(all(p['quality']['quality_score'] is None and not p['model_ready'] for p in result['profiles']))

    def test_reject_applied_or_mismatched_provider_even_if_names_look_valid(self):
        for change in ('applied','wrong_identity'):
            candidate = copy.deepcopy(self.provider)
            if change=='applied': candidate['provider_candidates'][0]['scaling_applied']=True
            else: candidate['provider_candidates'][0]['consumer_observation_id']=self.up['rows'][0]['observation_id']
            with self.subTest(change=change), self.assertRaises(ValueError): coverage(self.up,self.base,candidate)
