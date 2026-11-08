import unittest
from scripts.compare_nso_dede_historical import cells

class Page:
    def __init__(self,bad_total=False,bad_year=False):self.bad_total=bad_total;self.bad_year=bad_year
    def extract_text(self):return 'TABLE 14 MANUFACTURING SECTOR unit ktoe'
    def extract_words(self):
        words=[]
        for y,top,values in [(2022,691,['8,413','3,734','6,868','6,878','6,283','-','32,176']),(2023,718,['7,022','3,682','6,611','6,950','6,335','-','30,600'])]:
            if self.bad_total:values[-1]='30,601'
            tokens=[str(y+543+int(self.bad_year)),*values,str(y)]
            words.extend({'text':s,'top':top,'x0':x} for s,x in zip(tokens,[38,88,139,191,250,307,393,464,523]))
        return words

class HistoricalTests(unittest.TestCase):
    def test_extract_both_years(self):self.assertEqual(str(cells(Page())[2023][-1][1]),'30600')
    def test_total_guard(self):
        with self.assertRaises(ValueError):cells(Page(bad_total=True))
    def test_be_ce_guard(self):
        with self.assertRaises(ValueError):cells(Page(bad_year=True))
