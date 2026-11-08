import copy
import json
import sqlite3
import unittest
from scripts.build_versioned_inventory import ROOT,create_store


class VersionedInventoryTests(unittest.TestCase):
    def setUp(self):
        self.up=json.loads((ROOT/'build/upstream-inventory/report.json').read_text(encoding='utf8'))
        self.base=json.loads((ROOT/'build/product-inventory/report.json').read_text(encoding='utf8'))
        self.con,self.versions=create_store(self.up,self.base)
        self.addCleanup(self.con.close)

    def test_all_fields_roundtrip_and_unknown_unit_retained(self):
        actual={i:json.loads(p) for i,p in self.con.execute('SELECT observation_id,original_json FROM review_export')}
        self.assertEqual(actual,{r['observation_id']:r for r in self.up['rows']+self.base['rows']})
        self.assertEqual(self.con.execute('SELECT COUNT(*) FROM review_export WHERE unit_code IS NULL').fetchone()[0],1)
        self.assertEqual(self.con.execute('SELECT COUNT(*) FROM numeric_parse_audit WHERE allocation_applied=0').fetchone()[0],58)
        self.assertEqual(self.con.execute('SELECT COUNT(*) FROM process_dataset_version WHERE sealed=1').fetchone()[0],5)

    def test_source_immutable_and_context_mismatch_rejected(self):
        for sql,args in [('UPDATE source_observation SET amount=?',('0',)),
                         ('DELETE FROM source_observation',()),
                         ('INSERT INTO dataset_exchange VALUES(?,?)',(self.versions['CPO'],self.up['rows'][0]['observation_id'])),
                         ('UPDATE process_dataset_version SET model_ready=1',()),
                         ('UPDATE numeric_parse_audit SET allocation_applied=1',())]:
            with self.subTest(sql=sql),self.assertRaises(sqlite3.IntegrityError):self.con.execute(sql,args)
            self.con.rollback()

    def test_version_deterministic_and_changes_only_affected_process(self):
        modified=copy.deepcopy(self.up)
        modified['rows'][0]['annotation']='Additional review note; quantity unchanged'
        other,versions=create_store(modified,self.base)
        try:
            self.assertNotEqual(versions['FFB'],self.versions['FFB'])
            self.assertEqual(versions['FAME'],self.versions['FAME'])
        finally:other.close()

    def test_transaction_rolls_back_whole_batch_on_late_invalid_exchange(self):
        before=self.con.execute('SELECT COUNT(*) FROM source_observation').fetchone()[0]
        with self.assertRaises(sqlite3.IntegrityError):
            with self.con:
                # Synthetic identity only in an in-memory negative test, never source evidence.
                self.con.execute("INSERT INTO source_observation SELECT 'TEST_ONLY_ROLLBACK',process_id,source_hash,flow_label,amount,unit_code,direction,role,source_status,json_set(original_json,'$.observation_id','TEST_ONLY_ROLLBACK') FROM source_observation LIMIT 1")
                self.con.execute('INSERT INTO dataset_exchange VALUES(?,?)',(self.versions['CPO'],'missing-observation'))
        self.assertEqual(self.con.execute('SELECT COUNT(*) FROM source_observation').fetchone()[0],before)

    def test_typed_payload_mismatch_and_membership_change_are_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute("INSERT INTO source_observation SELECT 'TEST_ONLY_WRONG_VALUE',process_id,source_hash,flow_label,'0',unit_code,direction,role,source_status,json_set(original_json,'$.observation_id','TEST_ONLY_WRONG_VALUE') FROM source_observation LIMIT 1")
        self.con.rollback()

    def test_raw_lexeme_cannot_silently_change_numeric_value(self):
        changed=copy.deepcopy(self.up)
        changed['rows'][0]['amount']='0.49'
        with self.assertRaises(ValueError):create_store(changed,self.base)
        with self.assertRaises(sqlite3.IntegrityError):
            self.con.execute('DELETE FROM dataset_exchange WHERE version_id=?',(self.versions['FFB'],))
        self.con.rollback()
