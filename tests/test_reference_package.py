import hashlib
import json
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path


@unittest.skipUnless(Path('build/reusable/reference-data-local.zip').exists(),'Reference package required')
class ReferencePackageTests(unittest.TestCase):
    def test_package_hashes_and_sqlite_usable_subset(self):
        with zipfile.ZipFile('build/reusable/reference-data-local.zip') as archive:
            manifest=json.loads(archive.read('package-manifest.json'))
            for name,expected in manifest['files'].items():
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(),expected)
            self.assertFalse(any(name.endswith('.pdf') or '.local' in name or '.env' in name for name in archive.namelist()))
            rows=json.loads(archive.read('accepted-reference.json'))
            self.assertEqual(len(rows),manifest['accepted_reference'])
            self.assertTrue(all(r['decision']=='ACCEPTED_REFERENCE' for r in rows))
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'reference.sqlite';path.write_bytes(archive.read('reference.sqlite'))
                con=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
                self.assertEqual(con.execute('SELECT COUNT(*) FROM accepted_reference WHERE release_id=?',(manifest['release_id'],)).fetchone()[0],len(rows))
                self.assertEqual(con.execute('SELECT COUNT(*) FROM reference_catalog WHERE release_id=?',(manifest['release_id'],)).fetchone()[0],len(rows)+manifest['held_context'])
                con.close()
