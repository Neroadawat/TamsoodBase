import unittest
import copy
import json
from scripts.screen_thai_carbon import ROOT, reviewed_factor, verify_selected_row
from src.thai_carbon import screen_activity


class ThaiCarbonTest(unittest.TestCase):
    def test_actual_factor_decimal_and_scope(self):
        f=reviewed_factor();r=screen_activity('1000','kg',f)
        self.assertEqual(r['result'],'1037.2000')
        self.assertFalse(r['full_lifecycle_result']);self.assertIsNone(r['direct_CO2_kg'])
        self.assertFalse(r['strict_all_inputs_thai_verified'])

    def test_no_implicit_unit_or_foreign_provider(self):
        f=reviewed_factor()
        with self.assertRaises(ValueError):screen_activity('1','litre',f)
        f['geography']='US'
        with self.assertRaises(ValueError):screen_activity('1','kg',f)

    def test_thai_publisher_not_thai_data_and_invalid_activity(self):
        f=reviewed_factor();f['provenance_class']='IPCC_DEFAULT'
        with self.assertRaises(ValueError):screen_activity('1','kg',f)
        f=reviewed_factor()
        for x in ('-1','NaN','Infinity',1,'1e1000000'):
            with self.assertRaises(ValueError):screen_activity(x,'kg',f)

    def test_all_seven_cells_bound_to_html(self):
        raw=ROOT/'data/raw/tgo-cfp-2026-11-03'
        html=(raw/'page.html').read_text(encoding='utf8')
        selected=json.loads((raw/'selected-row.json').read_text(encoding='utf8'))
        for i in range(7):
            changed=copy.deepcopy(selected);changed[0][i]+=' changed'
            with self.assertRaises(ValueError):verify_selected_row(html,changed)

    def test_large_plain_decimal_does_not_silently_round(self):
        result=screen_activity('10000000000000000000000000001','kg',reviewed_factor())
        self.assertEqual(result['result'],'10372000000000000000000000001.0372')


if __name__=='__main__':unittest.main()
