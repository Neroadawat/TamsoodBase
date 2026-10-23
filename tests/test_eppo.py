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
