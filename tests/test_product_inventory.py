import copy
import hashlib
import json
import unittest
from pathlib import Path
from scripts.build_product_inventory import extract


@unittest.skipUnless(Path('data/raw/mdpi-9415/table4-dom.json').exists(),'Publisher DOM snapshot required')
class ProductInventoryTests(unittest.TestCase):
    def setUp(self):
        root=Path('data/raw/mdpi-9415');body=(root/'table4-dom.json').read_bytes()
        self.table=json.loads(body);self.context=(root/'article-visible.txt').read_text(encoding='utf-8');self.digest=hashlib.sha256(body).hexdigest()

    def test_basis_geography_blanks_and_footnote(self):
        rows,excluded=extract(self.table,self.context,self.digest)
        self.assertEqual(len(rows),16);self.assertEqual(len(excluded),8)
        self.assertTrue(all(r['process']!='BHD' and r['reference_amount']=='1000' and r['reference_unit']=='MJ fuel' for r in rows))
        row=next(r for r in rows if r['process']=='H-FAME' and r['flow']=='Electricity (CHP Biomass)')
        self.assertEqual(row['amount'],'0.08');self.assertIsNotNone(row['annotation'])
        self.assertTrue(all(r['data_period'] is None for r in rows))
        self.assertEqual(next(r for r in rows if r['process']=='FAME' and r['role']=='REFERENCE_PRODUCT')['amount'],'26.3')

    def test_changed_header_or_invalid_cell_rejected(self):
        bad=copy.deepcopy(self.table);bad['rows'][0][2]['text']='Unknown'
        with self.assertRaises(ValueError):extract(bad,self.context,self.digest)
        bad=copy.deepcopy(self.table);bad['rows'][2][2]['text']='n.a.'
        with self.assertRaises(ValueError):extract(bad,self.context,self.digest)
