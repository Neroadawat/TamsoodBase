import copy,json,unittest
import hashlib
from pathlib import Path
from scripts.build_public_upstream import public_snapshot

@unittest.skipUnless(Path('build/upstream-inventory/report.json').exists(),'Reviewed upstream report required')
class PublicUpstreamTests(unittest.TestCase):
    def setUp(self):self.report=json.loads(Path('build/upstream-inventory/report.json').read_text(encoding='utf8'))
    def test_only_reviewed_public_facts_and_attribution(self):
        result=public_snapshot(self.report)
        self.assertEqual(len(result['rows']),42);self.assertEqual(sum(r['unit'] is None for r in result['rows']),1)
        self.assertEqual(result['licence'],'CC BY 4.0');self.assertFalse(result['raw_document_included'])
        self.assertFalse(result['model_ready']);self.assertNotIn('raw_line',result['rows'][0])
        for old,new in zip(self.report['rows'],result['rows']):
            self.assertEqual(old['amount'],new['amount']);self.assertEqual(old['source_url'],new['source_url'])
    def test_profile_separates_source_checks_from_model_readiness(self):
        profiles=public_snapshot(self.report)['process_profiles']
        self.assertEqual(profiles['FFB']['held_rows'],1)
        self.assertFalse(profiles['CPO']['model_ready']);self.assertTrue(profiles['CPO']['source_cells_verified'])
        self.assertIsNone(profiles['CPO']['quality_score']);self.assertIsNone(profiles['CPO']['measurement_period'])
        self.assertTrue(any('FFB' in reason for reason in profiles['CPO']['open_issues']))
    def test_version_covers_profiles_and_rows_and_quality_keeps_unknowns(self):
        result=public_snapshot(self.report)
        version=result.pop('public_snapshot_id')
        self.assertEqual(version,hashlib.sha256(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest())
        self.assertEqual(result['process_profiles']['FFB']['quality_dimensions']['measurement_period'],'ต้นฉบับไม่ระบุช่วงปีที่วัด')
        self.assertTrue(result['process_profiles']['CPO']['boundary']['excluded_from_imported_model'])
        self.assertEqual(len(result['rows']),42)
    def test_unknown_rights_changed_source_or_hold_rejected(self):
        for target,change in [('rights',None),('source',None),('hold',None)]:
            bad=copy.deepcopy(self.report)
            if target=='rights':bad['source']['rights_status']='NOT_CLEARED'
            if target=='source':bad['rows'][0]['doi']='other'
            if target=='hold':bad['rows'][0]['status']='SOURCE_REPORTED_UPSTREAM_CANDIDATE'
            with self.assertRaises(ValueError):public_snapshot(bad)
