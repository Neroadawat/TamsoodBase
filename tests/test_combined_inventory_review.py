import copy
import json
import unittest
from scripts.build_combined_inventory_review import ROOT, build_review


class CombinedReviewTests(unittest.TestCase):
    def setUp(self):
        self.up = json.loads((ROOT/'build/upstream-inventory/report.json').read_text(encoding='utf8'))
        self.base = json.loads((ROOT/'build/product-inventory/report.json').read_text(encoding='utf8'))

    def test_lossless_all_rows_and_distinct_bases(self):
        result = build_review(self.up, self.base)
        self.assertEqual([m['source'] for m in result['mappings']], self.up['rows']+self.base['rows'])
        self.assertEqual(result['profiles'][0]['reference_basis'], ['1000', 'kg'])
        self.assertEqual(result['profiles'][3]['reference_basis'], ['1000', 'MJ fuel'])
        self.assertTrue(all(not p['model_ready'] for p in result['profiles']))

    def test_reject_duplicate_context_and_premature_allocation(self):
        for kind in ('duplicate', 'basis', 'allocation', 'missing_hold'):
            up = copy.deepcopy(self.up)
            if kind == 'duplicate': up['rows'][1]['observation_id'] = up['rows'][0]['observation_id']
            if kind == 'basis': up['rows'][1]['reference_unit'] = 'MJ fuel'
            if kind == 'allocation': up['rows'][1]['allocation_applied_by_this_project'] = True
            if kind == 'missing_hold': up['rows'][0]['status'] = 'ACCEPTED'
            with self.subTest(kind=kind), self.assertRaises(ValueError): build_review(up, self.base)
