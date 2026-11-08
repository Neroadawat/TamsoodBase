import unittest
from src.reported_balance import reported_balance
class ReportedBalance(unittest.TestCase):
 def test_credit_and_display_rounding(self):
  rows=[{'id':str(i),'value':v} for i,v in enumerate(['454.6','10.2','-125.4','3119.4'])]
  r=reported_balance(rows,'3458.7');self.assertEqual(r['difference'],'0.1');self.assertTrue(r['within_display_rounding']);self.assertFalse(r['reported_value_overwritten'])
 def test_parent_child_and_duplicates_rejected(self):
  with self.assertRaises(ValueError):reported_balance([{'id':'farm','value':'100'},{'id':'fert','value':'30','ancestor_ids':['farm']}],'130')
  with self.assertRaises(ValueError):reported_balance([{'id':'a','value':'1'},{'id':'a','value':'1'}],'2')
 def test_material_discrepancy_and_nonfinite(self):
  self.assertFalse(reported_balance([{'id':'a','value':'100'}],'99')['within_display_rounding'])
  with self.assertRaises(ValueError):reported_balance([{'id':'a','value':'NaN'}],'0')
