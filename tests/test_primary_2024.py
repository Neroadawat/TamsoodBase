from types import SimpleNamespace
import unittest
from scripts.compare_nso_primary_2024 import compare,SPECS

class PrimaryComparisonTests(unittest.TestCase):
    def fixture(self):
        values={'DF1':'BALANCE 2024','DW2':'unit ktoe','DW24':'TOTAL PRIMARY ENERGY SUPPLY','U7':'รวม'};rows=[]
        for label,cell,header,expected in SPECS:
            values[header]=expected;values[cell]=-23 if label=='ก๊าซโซลีนธรรมชาติ' else 47
            rows.append(dict(table_id='13.5',reference_year=2024,label=label,unit='10^3 ton of oil equivalent',raw_value=str(values[cell]),amount=str(values[cell]),measure='quantity',observation_id=cell,source_sha256='source'))
        sheet=lambda:{k:SimpleNamespace(value=v) for k,v in values.items()}
        return values,rows,sheet
    def test_signed_value_and_rounded_total_separate_from_exact(self):
        values,rows,sheet=self.fixture()
        # Excel cached numeric values are int/float, not Python Decimal.
        values['DT24']=47.4
        result=compare(sheet(),rows)
        total=next(r for r in result if r['label']=='รวมยอด')
        self.assertFalse(total['exact_displayed_value_match']);self.assertTrue(total['within_display_rounding'])
        self.assertEqual(next(r for r in result if r['label']=='ก๊าซโซลีนธรรมชาติ')['dede_value'],'-23')
    def test_adjacent_wrong_fuel_header_fails(self):
        values,rows,sheet=self.fixture();values['E5']='พีต'
        with self.assertRaises(ValueError):compare(sheet(),rows)
    def test_boolean_not_numeric_and_year_guard(self):
        values,rows,sheet=self.fixture();values['E24']=True
        with self.assertRaises(ValueError):compare(sheet(),rows)
        values['E24']=47;values['DF1']='BALANCE 2023'
        with self.assertRaises(ValueError):compare(sheet(),rows)
