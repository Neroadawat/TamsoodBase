import copy
import json
import sqlite3
import unittest
from decimal import Decimal,localcontext
from scripts.build_activity_model_store import ROOT,inputs
from src.activity_model_store import initialize,persist,audit,canonical


class ActivityStoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact,cls.manifest=inputs()
        cls.schema=(ROOT/'sql/activity-model-review.sql').read_text(encoding='utf8')

    def connection(self):
        c=sqlite3.connect(':memory:');self.addCleanup(c.close);initialize(c,self.schema);return c

    def test_all_sources_results_and_run_manifests_replay(self):
        c=self.connection();persist(c,self.artifact,self.manifest)
        report=audit(c)
        self.assertEqual(report['result_rows_replayed'],330)
        self.assertEqual(report['source_observations'],130)
        self.assertEqual(report['dataset_versions'],9)
        self.assertEqual(report['held_results'],6)
        cases=[self.artifact['baseline']]+self.artifact['alternatives']
        for case in cases:
            actual=c.execute('''SELECT s.payload_json,r.scaled_amount,r.status FROM result_exchange r
              JOIN source_observation s USING(observation_id)
              JOIN scenario_case k USING(scenario_id) WHERE k.scenario_key=?''',(case['scenario_id'],)).fetchall()
            expected=[(canonical(r['source']),r['scaled_amount'],r['status']) for r in case['rows']]
            self.assertCountEqual(actual,expected)
        self.assertTrue(all(json.loads(r[0])['implementation_sha256']==self.manifest['implementation_sha256']
                            for r in c.execute('SELECT manifest_json FROM calculation_run')))

    def test_sealed_release_rejects_mutation_and_late_append(self):
        c=self.connection();release=persist(c,self.artifact,self.manifest)
        with c:c.execute('INSERT INTO release_seal VALUES(?)',(release,))
        for sql in ["UPDATE source_observation SET amount='999'",'DELETE FROM calculation_run',
                    "INSERT INTO required_decision SELECT scenario_id,'late','OPEN' FROM scenario_case LIMIT 1"]:
            with self.assertRaisesRegex(sqlite3.IntegrityError,'Immutable|Sealed'):c.execute(sql)
        self.assertEqual(audit(c)['result_rows_replayed'],330)

    def test_wrong_process_membership_rolls_back_entire_release(self):
        c=self.connection();bad=copy.deepcopy(self.artifact)
        fame=next(r['source']['observation_id'] for r in bad['baseline']['rows'] if r['component']=='FAME')
        bad['baseline']['physical_transfer_candidates'][0]['provider_output_id']=fame
        with self.assertRaisesRegex(ValueError,'membership'):persist(c,bad,self.manifest)
        for table in ['release_manifest','source_observation','calculation_run','scenario_case']:
            self.assertEqual(c.execute('SELECT count(*) FROM '+table).fetchone()[0],0)

    def test_scaled_result_tampering_rejected_before_write(self):
        c=self.connection();bad=copy.deepcopy(self.artifact)
        row=next(r for r in bad['baseline']['rows'] if r['scaled_amount'] is not None)
        row['scaled_amount']='999'
        with self.assertRaisesRegex(ValueError,'Scaled quantity'):persist(c,bad,self.manifest)
        self.assertEqual(c.execute('SELECT count(*) FROM release_manifest').fetchone()[0],0)

    def test_typed_source_disagreement_rejected(self):
        c=self.connection();source=self.artifact['baseline']['rows'][0]['source']
        with self.assertRaisesRegex(sqlite3.IntegrityError,'CHECK'):
            c.execute('INSERT INTO source_observation VALUES(?,?,?,?)',('TEST_ONLY','999',source['unit'],canonical(source)))

    def test_missing_null_or_nontext_amount_rejected(self):
        for value in ({'unit':'kg'},{'amount':None,'unit':'kg'},{'amount':12,'unit':'kg'}):
            c=self.connection()
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute('INSERT INTO source_observation VALUES(?,?,?,?)',('fixture','12','kg',canonical(value)))

    def test_source_membership_trigger_rejects_cross_process(self):
        c=self.connection()
        source={'amount':'12','unit':'kg','process':'FAME'}
        c.execute('INSERT INTO source_observation VALUES(?,?,?,?)',('fixture','12','kg',canonical(source)))
        c.execute('INSERT INTO process_dataset_version VALUES(?,?,?)',('CPO-fixture','CPO',1))
        with self.assertRaisesRegex(sqlite3.IntegrityError,'membership'):
            c.execute('INSERT INTO dataset_exchange VALUES(?,?)',('CPO-fixture','fixture'))

    def test_empty_or_incomplete_release_rejected(self):
        c=self.connection()
        with self.assertRaisesRegex(ValueError,'Incomplete'):audit(c)
        persist(c,self.artifact,self.manifest)
        # Fault injection in an isolated database: remove guard, then remove one result.
        c.execute('DROP TRIGGER immutable_result_exchange_delete')
        c.execute('DELETE FROM result_exchange WHERE rowid=(SELECT min(rowid) FROM result_exchange)')
        with self.assertRaisesRegex(ValueError,'Incomplete'):audit(c)

    def test_unexpected_orphan_source_rejected_at_release_acceptance(self):
        c=self.connection();persist(c,self.artifact,self.manifest)
        source=self.artifact['baseline']['rows'][1]['source']
        c.execute('INSERT INTO source_observation VALUES(?,?,?,?)',('extra-fixture',source['amount'],source['unit'],canonical(source)))
        with self.assertRaisesRegex(ValueError,'Incomplete'):audit(c)

    def test_coherent_row_scaling_cannot_hide_stale_provider_quantities(self):
        c=self.connection();bad=copy.deepcopy(self.artifact)
        case=bad['baseline']
        with localcontext() as context:
            context.prec=100
            factor=str(Decimal(case['component_scale_factors']['CPO'])*2)
            case['component_scale_factors']['CPO']=factor
            for row in case['rows']:
                if row['component']=='CPO':
                    row['scale_factor']=factor
                    if row['scaled_amount'] is not None:row['scaled_amount']=str(Decimal(row['source']['amount'])*Decimal(factor))
        with self.assertRaisesRegex(ValueError,'Provider quantity'):persist(c,bad,self.manifest)

    def test_missing_duplicate_extra_or_wrong_direction_edges_rejected(self):
        for mutate in ('missing','duplicate','direction','unit'):
            bad=copy.deepcopy(self.artifact);case=bad['baseline']
            if mutate=='missing':case['physical_transfer_candidates'].pop()
            elif mutate=='duplicate':case['physical_transfer_candidates'].append(case['physical_transfer_candidates'][0])
            else:
                oid=case['physical_transfer_candidates'][0]['provider_output_id']
                row=next(r for r in case['rows'] if r['source'].get('observation_id',r['source'].get('id'))==oid)
                row['source']['direction' if mutate=='direction' else 'unit']='INPUT' if mutate=='direction' else 'ton'
            with self.assertRaises(ValueError):persist(self.connection(),bad,self.manifest)


if __name__=='__main__':unittest.main()
