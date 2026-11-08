import sqlite3,unittest
from pathlib import Path
from decimal import Decimal
from src.decimal_projection import sql_decimal
from src.review_workflow import transition
class ReviewContracts(unittest.TestCase):
    def test_decimal_never_rounds_or_uses_float(self):
        self.assertEqual(sql_decimal('1.2300'),'1.23');self.assertEqual(Decimal(sql_decimal('0.000000000000000000000000000001')),Decimal('1e-30'))
        self.assertIsNone(sql_decimal('0.'+'1'*31));self.assertIsNone(sql_decimal('9'*36))
        for x in ['NaN','Infinity','invalid',1.2]:
            with self.assertRaises(ValueError):sql_decimal(x)
    def test_workflow_roles_rights_concurrency_and_append_only(self):
        c=sqlite3.connect(':memory:');self.addCleanup(c.close);c.executescript(Path('sql/review-workflow.sql').read_text());c.execute('INSERT INTO review_release(id,content_sha256,scope) VALUES(?,?,?)',('fixture','a'*64,'PUBLIC_METADATA'));c.commit()
        args=dict(actor='TEST_FIXTURE_NOT_REAL_REVIEWER',role='editor',evidence_sha256='b'*64,reason='TEST_ONLY')
        transition(c,'fixture','IN_REVIEW',0,**args)
        with self.assertRaises(ValueError):transition(c,'fixture','DRAFT',0,**args)
        args['role']='reviewer'
        with self.assertRaises(ValueError):transition(c,'fixture','PUBLISHED',1,**args)
        self.assertEqual(c.execute('SELECT count(*) FROM review_event').fetchone()[0],1)
        transition(c,'fixture','PUBLISHED',1,rights_cleared=True,**args)
        transition(c,'fixture','RETRACTED',2,**args)
        with self.assertRaises(sqlite3.IntegrityError):c.execute('DELETE FROM review_event')
        with self.assertRaises(sqlite3.IntegrityError):c.execute("UPDATE review_release SET state='DRAFT'")
    def test_workflow_cannot_approve_science_or_publish_internal(self):
        c=sqlite3.connect(':memory:');self.addCleanup(c.close);c.executescript(Path('sql/review-workflow.sql').read_text());c.execute('INSERT INTO review_release(id,content_sha256,scope) VALUES(?,?,?)',('fixture','a'*64,'INTERNAL_ACTIVITY_REVIEW'));c.commit()
        args=dict(actor='TEST_FIXTURE_ONLY',role='editor',evidence_sha256='c'*64,reason='TEST_ONLY');transition(c,'fixture','IN_REVIEW',0,**args);args['role']='reviewer'
        with self.assertRaises(ValueError):transition(c,'fixture','PUBLISHED',1,rights_cleared=True,**args)
        with self.assertRaises(ValueError):transition(c,'fixture','PUBLISHED',1,scientific_claim=True,**args)
