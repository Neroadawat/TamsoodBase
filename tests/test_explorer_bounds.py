"""Isolated boundary fixtures, never a replacement for actual source snapshots."""
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from src import explorer


class ExplorerBoundsTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        folder=self.root/'data/raw/dmf/fixture';folder.mkdir(parents=True)
        self.metadata=folder/'production-oil.metadata.json'
        self.metadata.write_text(json.dumps({'result':{'unit_of_multiplier':'ล้าน'}}),encoding='utf-8')
        self.database_path=self.root/'fixture.sqlite'
        with closing(sqlite3.connect(self.database_path)) as con,con:
            con.executescript('''
              CREATE TABLE resource(package TEXT PRIMARY KEY,metadata_unit TEXT,url TEXT,csv_sha256 TEXT,acquired_at TEXT);
              CREATE TABLE candidate(package TEXT,source_line INTEGER,year_ce INTEGER,month INTEGER,area TEXT,
                block_label TEXT,source_group TEXT,raw_value TEXT,amount_column TEXT,review_status TEXT,
                PRIMARY KEY(package,source_line));
              CREATE TABLE duplicate_disposition(package TEXT,source_line INTEGER,status TEXT,
                PRIMARY KEY(package,source_line));
              INSERT INTO resource VALUES('production-oil','บาร์เรล','https://example.invalid/fixture','fixture-hash','fixture-only');
            ''')
            con.executemany('INSERT INTO candidate VALUES(?,?,?,?,?,?,?,?,?,?)',
                [('production-oil',i+2,2024,1,'บนบก','','fixture','0.08','OIL','PENDING') for i in range(5001)])
            con.executemany('INSERT INTO duplicate_disposition VALUES(?,?,?)',
                [('production-oil',i+2,'SINGLETON') for i in range(5001)])
        self.statements=[]
        def database():
            con=sqlite3.connect(self.database_path);con.row_factory=sqlite3.Row
            con.set_trace_callback(self.statements.append)
            return 'fixture',con
        for replacement in (patch.object(explorer,'ROOT',self.root),
                            patch.object(explorer,'database',side_effect=database),
                            patch.object(explorer.mysql_store,'enabled',return_value=False)):
            replacement.start();self.addCleanup(replacement.stop)

    def test_5001_is_rejected_before_fetching_record_payloads(self):
        with self.assertRaisesRegex(ValueError,'exceeds 5000'):
            explorer.records({},export=True)
        self.assertEqual(len(self.statements),1)
        self.assertIn('SELECT COUNT(*) FROM (SELECT 1',self.statements[0])

    def test_exactly_5000_is_allowed_and_preserves_provenance_and_order(self):
        with closing(sqlite3.connect(self.database_path)) as con,con:
            con.execute('DELETE FROM candidate WHERE source_line=5002')
            con.execute('DELETE FROM duplicate_disposition WHERE source_line=5002')
        rows=explorer.records({},export=True)
        self.assertEqual(len(rows),5000)
        self.assertEqual([r['source_line'] for r in rows],list(range(2,5002)))
        self.assertTrue(all(r['raw_value']=='0.08' and r['unit_label']=='ล้านบาร์เรล'
                            and r['unit_time_basis']=='UNCONFIRMED' and r['review_status']=='PENDING'
                            and r['csv_sha256']=='fixture-hash' for r in rows))

    def test_probe_uses_same_visibility_filters_as_export(self):
        with closing(sqlite3.connect(self.database_path)) as con,con:
            con.execute("UPDATE duplicate_disposition SET status='EXCLUDE_EXACT_COPY' WHERE source_line>3")
        self.assertEqual(len(explorer.records({},export=True)),2)
        with self.assertRaisesRegex(ValueError,'exceeds 5000'):
            explorer.records({'status':'all'},export=True)
        with self.assertRaises(ValueError):explorer.records({'product':'unknown'},export=True)

    def test_metadata_is_shared_only_within_one_request(self):
        original=Path.read_bytes;reads=[]
        def tracked(path):
            if path==self.metadata:reads.append(path)
            return original(path)
        with patch.object(Path,'read_bytes',tracked):
            first=explorer.records({})
            self.assertEqual(len(first['rows']),30)
            self.assertEqual(len(reads),1)
            self.metadata.write_text(json.dumps({'result':{'unit_of_multiplier':'พัน'}}),encoding='utf-8')
            second=explorer.records({})
            self.assertEqual(len(reads),2)
        self.assertEqual(first['rows'][0]['unit_label'],'ล้านบาร์เรล')
        self.assertEqual(second['rows'][0]['unit_label'],'พันบาร์เรล')


if __name__=='__main__':unittest.main()
