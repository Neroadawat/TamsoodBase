import importlib.util
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit_normalization', ROOT/'scripts/audit_normalization.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


@unittest.skipUnless((ROOT/'build/reusable/reference.sqlite').is_file(),'Local corporate reference database required')
class NormalizationTest(unittest.TestCase):
    def test_candidate_lossless_and_constraints(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'candidate.sqlite'
            result = audit.build(ROOT/'build/reusable/reference.sqlite', path)
            self.assertEqual(result['counts'], {'reference_catalog': 101, 'accepted_reference': 97})
            with closing(sqlite3.connect(path)) as db:
                db.execute('PRAGMA foreign_keys=ON')
                self.assertNotIn('document_id', [r[1] for r in db.execute('PRAGMA table_info(metric)')])
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute("UPDATE metric SET context_id='missing-context'")
                db.rollback()

    def test_source_overwrite_refused(self):
        path = ROOT/'build/reusable/reference.sqlite'
        with self.assertRaises(ValueError):
            audit.build(path, path)

    def test_inconsistent_source_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'source.sqlite'
            source.write_bytes((ROOT/'build/reusable/reference.sqlite').read_bytes())
            with closing(sqlite3.connect(source)) as db:
                db.execute("UPDATE metric SET document_id='wrong-document'")
                db.commit()
            with self.assertRaisesRegex(ValueError, 'integrity|inconsistency'):
                audit.build(source, Path(tmp)/'candidate.sqlite')
