import unittest
from scripts.extract_upstream_inventory import amount,table_rows

class UpstreamInventoryTests(unittest.TestCase):
    def test_scientific_notation_preserves_exponent(self):
        self.assertEqual(amount('2.08 × 10−4'),'0.000208')
        self.assertEqual(amount('5.46×10 −5'),'0.0000546')
    def test_missing_unit_is_not_inferred(self):
        text='Table 1. Life cycle inventory of 1000 kg FFB production.\nInput\nLand seeding 0.48\nOutput\nFFB 1000 kg'
        rows=table_rows(text,1,'FFB');self.assertIsNone(rows[0]['unit']);self.assertEqual(rows[0]['amount'],'0.48')
    def test_subscript_line_is_not_an_observation(self):
        text='Table1. Lifecycleinventoryof1000kgFFBproduction.\nInput\nP O Fertiliser 4.42 kg\n2 5\nOutput\nFFB 1000 kg'
        self.assertEqual(len(table_rows(text,1,'FFB')),2)
    def test_wrong_product_basis_rejected(self):
        with self.assertRaises(ValueError):table_rows('Table 3. Life cycle inventory of 1000 MJ RBDPO production.',3,'RBDPO')
