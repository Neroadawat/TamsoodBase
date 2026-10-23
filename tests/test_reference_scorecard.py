import copy
import json
import unittest
from pathlib import Path
from scripts.reference_scorecard import measure


@unittest.skipUnless(Path('build/reusable/all-reference.json').exists(),'Reference release required')
class ScorecardTests(unittest.TestCase):
    def setUp(self):
        self.rows=json.loads(Path('build/reusable/all-reference.json').read_text(encoding='utf-8'))
        self.manifest=json.loads(Path('build/reusable/manifest.json').read_text(encoding='utf-8'))

    def test_actual_release(self):
        report=measure(self.rows,self.manifest)
        self.assertTrue(report['passed'])
        self.assertEqual(report['publishers'],2)
        self.assertEqual(report['accepted_reference'],97)

    def test_corruption_is_detected(self):
        for field,value,check in [('source_scope','', 'required_context_complete'),
                                  ('scaled_amount','999999999','exact_scale_arithmetic'),
                                  ('release_id','wrong','release_membership'),
                                  ('trace_verification','unchecked','trace_marker_complete')]:
            rows=copy.deepcopy(self.rows);rows[0][field]=value
            self.assertFalse(measure(rows,self.manifest)['checks'][check])
        rows=copy.deepcopy(self.rows);rows.append(rows[0])
        self.assertFalse(measure(rows,self.manifest)['checks']['unique_observation_ids'])
