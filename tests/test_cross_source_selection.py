import unittest
from scripts.compare_nso_doeb import matching_rows


class Sheet:
    def __init__(self,rows):self.rows=[['header','label',0]]+rows;self.nrows=len(self.rows)
    def cell_value(self,i,j):return self.rows[i][j]


class ComparisonSelectionTests(unittest.TestCase):
    def test_exact_sulfur_label_year_and_unit_only(self):
        row=dict(table_id='13.8',unit='Thousand litre',label='น้ำมันดีเซลกำมะถันสูง',reference_year=2024)
        sheet=Sheet([[2567,row['label'],26.119],[2566,row['label'],80.194]])
        self.assertEqual(matching_rows(row,sheet),[1])
        self.assertEqual(matching_rows(row|dict(unit='Thousand kilogram'),sheet),[])
        self.assertEqual(matching_rows(row|dict(reference_year=2025),sheet),[])
        self.assertEqual(matching_rows(row|dict(label='น้ำมันดีเซลหมุนเร็วธรรมดา'),sheet),[])
        with self.assertRaises(ValueError):matching_rows(row,Sheet([[2567,row['label'],1],[2567,row['label'],2]]))

    def test_spacing_and_case_are_not_fuel_reclassification(self):
        row=dict(table_id='13.8',unit='Thousand litre',label='น้ำมันดีเซลพื้นฐาน (10 PPM)',reference_year=2023)
        self.assertEqual(matching_rows(row,Sheet([[2566,'น้ำมันดีเซลพื้นฐาน (10 ppm)',1]])),[1])
        self.assertEqual(matching_rows(row,Sheet([[2566,'น้ำมันดีเซลพื้นฐาน (50 ppm)',1]])),[])
        row['label']='น้ำมันดีเซลหมุนเร็ว บี 7'
        self.assertEqual(matching_rows(row,Sheet([[2566,'น้ำมันดีเซล หมุนเร็ว บี 7 ',1]])),[1])
        self.assertEqual(matching_rows(row,Sheet([[2566,'น้ำมันดีเซลหมุนเร็วธรรมดา',1]])),[])
