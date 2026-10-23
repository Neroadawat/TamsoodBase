import unittest
from src.review_dmf import classify


class DuplicateDispositionTests(unittest.TestCase):
    def test_exact_copies_choose_stable_lowest_line(self):
        rows=[{'source_line':9,'raw_json':'{"OIL":"1","DAYSOFPRODUCE":"30"}'},
              {'source_line':3,'raw_json':'{"DAYSOFPRODUCE":"30","OIL":"1"}'}]
        self.assertEqual(classify(rows),{9:('EXCLUDE_EXACT_COPY',3),3:('EXACT_REPRESENTATIVE',None)})

    def test_same_amount_different_days_holds_both(self):
        rows=[{'source_line':3,'raw_json':'{"OIL":"1","DAYSOFPRODUCE":"30"}'},
              {'source_line':4,'raw_json':'{"OIL":"1","DAYSOFPRODUCE":"31"}'}]
        self.assertEqual(set(classify(rows).values()),{('HOLD_CONFLICT',None)})

    def test_conflict_does_not_choose_first_or_last(self):
        rows=[{'source_line':3,'raw_json':'{"OIL":"1"}'},
              {'source_line':4,'raw_json':'{"OIL":"2"}'},
              {'source_line':5,'raw_json':'{"OIL":"1"}'}]
        self.assertTrue(all(status=='HOLD_CONFLICT' for status,_ in classify(rows).values()))
