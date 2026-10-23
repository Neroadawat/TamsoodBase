import csv
import io
import unittest
from pathlib import Path
from src.explorer import ROOT,records,detail,csv_export,selection


class ExplorerFilterTests(unittest.TestCase):
    def test_invalid_filters_rejected(self):
        for params in ({'product':'anything'},{'year':'2026 OR 1=1'},{'status':'ACCEPTED'},{'area':'anything'}):
            with self.subTest(params=params),self.assertRaises(ValueError): selection(params)


@unittest.skipUnless((ROOT/'data/raw/dmf/latest.json').exists(),'Local DMF snapshot required')
class ExplorerIntegrationTests(unittest.TestCase):
    def test_gas_multiplier_and_uncertain_time_preserved(self):
        row=records({'product':'production-natural-gas','q':'น้ำพอง','year':'2026'})['rows'][0]
        self.assertEqual(row['metadata_multiplier'],'ล้าน')
        self.assertEqual(row['unit_label'],'ล้านลูกบาศก์ฟุต')
        self.assertEqual(row['unit_time_basis'],'UNCONFIRMED')
        full=detail(row['package'],row['source_line'])
        self.assertEqual(full['raw_fields']['GAS'],row['raw_value'])

    def test_query_is_literal_not_sql(self):
        self.assertEqual(records({'q':"' OR 1=1 --"})['total'],0)

    def test_conflicting_members_are_all_visible(self):
        rows=records({'status':'HOLD_CONFLICT'})['rows']
        full=detail(rows[0]['package'],rows[0]['source_line'])
        self.assertGreater(len(full['related']),1)
        self.assertTrue(all(r['status']=='HOLD_CONFLICT' for r in full['related']))
        self.assertEqual(full['conflict_investigation']['disposition'],'HOLD_CONFLICT')
        self.assertFalse(full['conflict_investigation']['automatic_merge_allowed'])

    def test_csv_has_provenance_and_no_acceptance_promotion(self):
        rows=records({'product':'production-natural-gas','q':'น้ำพอง','year':'2026'})['rows']
        result=list(csv.DictReader(io.StringIO(csv_export(rows).decode('utf-8-sig'))))
        self.assertEqual(len(result),len(rows))
        self.assertTrue(all(r['review_status']=='PENDING' and r['csv_sha256'] and r['snapshot_run_id'] for r in result))
