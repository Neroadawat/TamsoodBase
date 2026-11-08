import hashlib
import unittest
from scripts.import_eppo import parse


class EppoTests(unittest.TestCase):
    def source(self,body):
        return dict(sha256=hashlib.sha256(body).hexdigest(),originating_agency='DOEB',url='https://example.org',acquired_at='2026-10-23',license_label='Open Data Common')

    def test_rate_unit_and_zero_preserved(self):
        body=b'Year,Month,Company,Quantity,UNIT\n2024,February,SPRC,0,BBL/DAY\n'
        r=parse(body,'11_13',self.source(body))[0]
        self.assertEqual((r['amount'],r['unit'],r['month']),('0','BBL/DAY',2))
        self.assertFalse(r['is_normalized_lci_exchange'])
        self.assertEqual(r['source_line'],2)

    def test_wrong_unit_duplicate_and_missing_rejected(self):
        header='Year,Month,Product,Quantity,UNIT\n'
        line='2024,January,DIESEL,1.250,Million Litres\n'
        for text in [header+line+line,header+line.replace('Million Litres','BBL/DAY'),header+line.replace('1.250','n.a.')]:
            body=text.encode()
            with self.assertRaises(ValueError):parse(body,'11_14',self.source(body))

    def test_changed_snapshot_rejected(self):
        body=b'Year,Month,Product,Quantity,UNIT\n2024,January,DIESEL,1.250,Million Litres\n'
        with self.assertRaises(ValueError):parse(body+b'\n','11_14',self.source(body))

    def test_real_filtered_pagination_and_literal_query(self):
        from pathlib import Path
        if not Path('build/eppo/report.json').exists():self.skipTest('Local snapshots required')
        from src.explorer import eppo_records
        first=eppo_records(dict(dataset='11_13',year='2024',page='1'))
        second=eppo_records(dict(dataset='11_13',year='2024',page='2'))
        self.assertFalse({r['observation_id'] for r in first['rows']} & {r['observation_id'] for r in second['rows']})
        sprc=eppo_records(dict(dataset='11_13',year='2024',q='SPRC'))
        self.assertEqual(sprc['total'],12)
        self.assertTrue(all(r['subject']=='SPRC' and r['unit']=='BBL/DAY' for r in sprc['rows']))
        self.assertEqual(eppo_records(dict(q="' OR 1=1 --"))['total'],0)
        for params in [dict(page='0'),dict(dataset='unknown'),dict(year='NaN')]:
            with self.assertRaises(ValueError):eppo_records(params)

    def test_roundtrip_detects_typed_metadata_and_extra_rows(self):
        import json
        import sqlite3
        from scripts.import_eppo import verify_roundtrip
        con=sqlite3.connect(':memory:')
        self.addCleanup(con.close)
        con.executescript('CREATE TABLE source_snapshot(snapshot_id TEXT,dataset_id TEXT,url TEXT,payload TEXT); CREATE TABLE observation(observation_id TEXT,snapshot_id TEXT,reference_year INTEGER,month INTEGER,subject TEXT,amount TEXT,unit TEXT,payload TEXT);')
        rows=[];manifest={'resources':{}}
        for dataset,subject,unit in [('11_13','Company','BBL/DAY'),('11_14','Product','Million Litres')]:
            body=f'Year,Month,{subject},Quantity,UNIT\n2024,January,TEST,1,{unit}\n'.encode()
            source=self.source(body);manifest['resources'][dataset]=source
            row=parse(body,dataset,source)[0];rows.append(row)
            con.execute('INSERT INTO source_snapshot VALUES (?,?,?,?)',(source['sha256'],dataset,source['url'],json.dumps(source)))
            con.execute('INSERT INTO observation VALUES (?,?,?,?,?,?,?,?)',(row['observation_id'],row['source_sha256'],2024,1,'TEST','1',unit,json.dumps(row)))
        con.commit()
        verify_roundtrip(con,rows,manifest)
        for column,value in [('reference_year',2025),('month',2),('subject','WRONG'),('amount','2'),('unit','WRONG')]:
            with self.subTest(column=column):
                con.execute('UPDATE observation SET '+column+'=?',(value,))
                with self.assertRaisesRegex(ValueError,'roundtrip'):verify_roundtrip(con,rows,manifest)
                con.rollback()
        con.execute("UPDATE source_snapshot SET url='https://wrong.example'")
        with self.assertRaisesRegex(ValueError,'snapshot'):verify_roundtrip(con,rows,manifest)
        con.rollback()
        con.execute("INSERT INTO observation SELECT 'extra',snapshot_id,reference_year,month,subject,amount,unit,payload FROM observation LIMIT 1")
        with self.assertRaisesRegex(ValueError,'roundtrip'):verify_roundtrip(con,rows,manifest)
