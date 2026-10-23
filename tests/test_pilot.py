import sqlite3
import unittest
from src.pilot import ROOT, validate


class ValidationTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(record_id='test', period='2026-01', area='onshore', block='E5',
                   field='test', fuel='natural_gas', raw_value='0.00',
                   unit='million_ft3_per_day', evidence_locator='test cell')
        return row | changes

    def test_zero_is_valid_not_missing(self):
        self.assertEqual(validate(self.row()), [])

    def test_bad_numeric_values(self):
        for value in ('', '-1', 'NaN', 'Infinity', 'unknown'):
            with self.subTest(value=value):
                self.assertTrue(validate(self.row(raw_value=value)))

    def test_context_required(self):
        for change in ({'period': '2026-13'}, {'unit': 'barrel'}, {'evidence_locator': ''}):
            self.assertTrue(validate(self.row(**change)))

    def test_database_constraints(self):
        con = sqlite3.connect(':memory:')
        con.executescript((ROOT / 'sql/schema.sql').read_text())
        with self.assertRaises(sqlite3.IntegrityError):
            con.execute('INSERT INTO batch VALUES (?,?,?,?,?,?,?)', ('x','missing','a','b','c','date','test'))
        con.close()


if __name__ == '__main__':
    unittest.main()
