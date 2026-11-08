import copy
import json
import unittest
from scripts.build_lifecycle_candidate import ROOT, build
from src.lifecycle_model import validate_lifecycle


class LifecycleTest(unittest.TestCase):
    def setUp(self):
        self.review=json.loads((ROOT/'build/combined-inventory-review/review.json').read_text(encoding='utf8'))
        self.model=build(self.review)

    def test_source_payloads_and_route(self):
        expected=[m['source'] for m in self.review['mappings'] if m['process']!='H-FAME']
        self.assertEqual(self.model['source_observations'],expected)
        self.assertEqual(len(expected),52)
        self.assertFalse(validate_lifecycle(self.model)['model_ready'])

    def test_false_full_claim_and_duplicate_stage_count_rejected(self):
        bad=copy.deepcopy(self.model);bad['full_lifecycle_inventory']=True
        with self.assertRaises(ValueError):validate_lifecycle(bad)
        bad=copy.deepcopy(self.model)
        bad['stages'][1]['observation_ids'].append(bad['stages'][0]['observation_ids'][0])
        with self.assertRaises(ValueError):validate_lifecycle(bad)

    def test_missing_cannot_become_zero_or_unexplained_exclusion(self):
        bad=copy.deepcopy(self.model);bad['parameters'][0]['value']='0'
        with self.assertRaises(ValueError):validate_lifecycle(bad)
        bad=copy.deepcopy(self.model);bad['stages'][-1]['status']='EXCLUDED_WITH_REASON'
        with self.assertRaises(ValueError):validate_lifecycle(bad)

    def test_assumption_is_visible_and_not_measured(self):
        bad=copy.deepcopy(self.model)
        bad['parameters'][0].update(value='5',status='SCENARIO_ASSUMPTION',evidence='TEST ONLY rationale')
        self.assertTrue(validate_lifecycle(bad)['scenario_assumptions_present'])
        bad['source_measured_complete']=True
        with self.assertRaises(ValueError):validate_lifecycle(bad)

    def test_unknown_or_omitted_source_rejected(self):
        bad=copy.deepcopy(self.model);bad['stages'][0]['observation_ids'][0]='invented'
        with self.assertRaises(ValueError):validate_lifecycle(bad)
        bad=copy.deepcopy(self.model);bad['stages'][0]['observation_ids'].pop()
        with self.assertRaises(ValueError):validate_lifecycle(bad)

    def test_missing_decisions_cannot_be_deleted_to_gain_readiness(self):
        bad=copy.deepcopy(self.model);bad['parameters']=[]
        result=validate_lifecycle(bad)
        self.assertFalse(result['model_ready'])
        self.assertEqual(sum(b['kind']=='REQUIRED_PARAMETER_ABSENT'
                             for b in result['readiness_blockers']),7)

    def test_declared_gate_labels_do_not_clear_source_hold(self):
        bad=copy.deepcopy(self.model)
        bad['gates']={g:'VERIFIED' for g in bad['gates']}
        result=validate_lifecycle(bad)
        kinds={b['kind'] for b in result['readiness_blockers']}
        self.assertIn('SOURCE_UNIT_MISSING',kinds)
        self.assertIn('SOURCE_UNRESOLVED',kinds)
        self.assertIn('GATE_EVIDENCE_MISSING',kinds)
        bad['full_lifecycle_inventory']=True
        with self.assertRaises(ValueError):validate_lifecycle(bad)

    def test_duplicate_parameter_is_rejected(self):
        bad=copy.deepcopy(self.model)
        bad['parameters'].append(copy.deepcopy(bad['parameters'][0]))
        with self.assertRaises(ValueError):validate_lifecycle(bad)

    def test_both_snapshot_formats_preserve_provenance(self):
        blockers=validate_lifecycle(self.model)['readiness_blockers']
        self.assertFalse(any(b['kind']=='SOURCE_PROVENANCE_MISSING' for b in blockers))
        bad=copy.deepcopy(self.model)
        bad['source_observations'][-1]['source_snapshot_sha256']='not-a-hash'
        self.assertTrue(any(b['kind']=='SOURCE_PROVENANCE_MISSING'
                            for b in validate_lifecycle(bad)['readiness_blockers']))

    def test_free_text_gate_evidence_does_not_resolve_a_decision(self):
        bad=copy.deepcopy(self.model)
        gate=next(iter(bad['gates']))
        bad['gates'][gate]='VERIFIED';bad['gate_evidence']={gate:'someone said approved'}
        result=validate_lifecycle(bad)
        self.assertIn({'kind':'GATE_DECISION_UNRESOLVED','id':gate},result['readiness_blockers'])


if __name__=='__main__':unittest.main()
