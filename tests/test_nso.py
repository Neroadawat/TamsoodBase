import json
import unittest
from pathlib import Path
from scripts.import_nso import parse,unit_for,BASE
from scripts.review_nso import totals


class NsoTests(unittest.TestCase):
    def test_footnote_changes_dimension(self):
        self.assertEqual(unit_for('13.8',['LPG(1)']),'Thousand kilogram')
        self.assertEqual(unit_for('13.8',['น้ำมันเบนซิน']),'Thousand litre')
        self.assertEqual(unit_for('13.10',['ร้อยละ']),'percent')
        self.assertEqual(unit_for('13.7',['มูลค่า (ล้านบาท)']),'Million Baht')

    @unittest.skipUnless(Path('data/raw/nso/yearbook-2026/T_13.6_2026.csv').exists(),'NSO snapshot required')
    def test_reparse_actual_and_reject_corrupt_cell(self):
        body=Path('data/raw/nso/yearbook-2026/T_13.6_2026.csv').read_bytes()
        rows=parse(body,'13.6',BASE+'File_SYB/2026/13/T_13.6_2026.csv')
        self.assertEqual(len(rows),69)
        target=next(r for r in rows if r['measure']=='การผลิต' and r['label']=='รวมยอด' and r['reference_year']==2024)
        self.assertEqual(target['amount'],'65315')
        self.assertEqual(target['source_column'],5)
        self.assertEqual(target['unit'],'Million litre')
        with self.assertRaises(ValueError):parse(body.replace(b'65315',b'n.a.'),'13.6','source')
        # Entire rows of missing markers must not disappear silently as footnotes.
        with self.assertRaises(ValueError):
            parse(body.replace(b'57338,63228,65315',b'n.a.,n.a.,n.a.'),'13.6','source')
        with self.assertRaises(ValueError):parse(body.replace(b'2567 (2024)',b'2566 (2024)'),'13.6','source')

    @unittest.skipUnless(Path('build/nso/report.json').exists(),'NSO build required')
    def test_dimensions_and_negative_supply_preserved(self):
        report=json.loads(Path('build/nso/report.json').read_text(encoding='utf-8'))
        self.assertEqual(report['row_count'],273)
        self.assertEqual(len({r['observation_id'] for r in report['rows']}),273)
        negative=[r for r in report['rows'] if r['amount'].startswith('-')]
        self.assertEqual(len(negative),6)
        self.assertTrue(all(r['table_id']=='13.5' for r in negative))
        mass=[r for r in report['rows'] if r['table_id']=='13.8' and r['unit']=='Thousand kilogram']
        self.assertEqual(len(mass),12)

    @unittest.skipUnless(Path('build/nso/report.json').exists(),'NSO build required')
    def test_totals_and_corrupted_component(self):
        report=json.loads(Path('build/nso/report.json').read_text(encoding='utf-8'))
        checks=totals(report['rows'])
        self.assertEqual(len(checks),18)
        self.assertTrue(all(c['passed'] for c in checks))
        row=next(r for r in report['rows'] if r['table_id']=='13.6' and r['label']!='รวมยอด')
        row['amount']='999999'
        self.assertFalse(all(c['passed'] for c in totals(report['rows'])))
