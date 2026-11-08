import unittest
from scripts.review_inventory_allocation import verify_shares

class AllocationReviewTests(unittest.TestCase):
    def test_reported_percentages_sum_without_applying_to_quantities(self):
        self.assertTrue(verify_shares({'FAME':'70','Glycerine':'30'}))
        self.assertTrue(verify_shares({'CPO':'92','Kernel':'6','Shell':'2'}))
    def test_incomplete_or_nonfinite_factors_rejected(self):
        for shares in ({'one':'92'},{'one':'-1','two':'101'},{'one':'NaN'},{'one':'Infinity'},{}):
            with self.assertRaises(ValueError):verify_shares(shares)
