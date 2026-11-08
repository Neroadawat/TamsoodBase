from types import SimpleNamespace
import unittest
from scripts.compare_nso_dede_components import SPECS, UNIT, compare


class ComponentComparisonTests(unittest.TestCase):
    def fixture(self):
        values=dict(DF1='THAILAND ENERGY BALANCE 2024',DW2='unit: ktoe',A52='อุตสาหกรรมการผลิต',DW52='MANUFACTURING',DT9='GRAND TOTAL',DT52=30350)
        rows=[]
        for i,((label,cell,header_cell,header),value) in enumerate(zip(SPECS,[6970,3186,6631,7163,6400])):
            values[cell]=value;values[header_cell]=header
            rows.append(dict(table_id='13.10',reference_year=2024,measure='จำนวน',label=label,unit=UNIT,amount=str(value),
                observation_id='synthetic-'+str(i),source_sha256='fixture',source_line=i+2,source_column=5))
        return {k:SimpleNamespace(value=v) for k,v in values.items()},rows

    def test_five_distinct_quantities_not_percentages(self):
        sheet,rows=self.fixture()
        result=compare(sheet,rows+[r|{'measure':'ร้อยละ','unit':'percent'} for r in rows])
        self.assertEqual(len(result),5)
        self.assertTrue(all(r['exact_displayed_value_match'] for r in result))

    def test_wrong_headers_units_years_and_missing_cache_fail(self):
        for field,value in [('W9','LIGNITE'),('DF1','2023'),('AG52',None),('BR52',True)]:
            sheet,rows=self.fixture();sheet[field]=SimpleNamespace(value=value)
            with self.assertRaises(ValueError):compare(sheet,rows)
        sheet,rows=self.fixture();rows[0]['unit']='percent'
        with self.assertRaises(ValueError):compare(sheet,rows)

    def test_difference_is_reported_without_correcting_source(self):
        sheet,rows=self.fixture();rows[0]['amount']='6971'
        result=compare(sheet,rows)
        self.assertEqual(result[0]['difference_nso_minus_revised'],'1')
        self.assertFalse(result[0]['exact_displayed_value_match'])
        self.assertEqual(rows[0]['amount'],'6971')
