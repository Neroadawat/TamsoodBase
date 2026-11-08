import unittest
from unittest.mock import patch
from src import mysql_store
from src.wsgi import readiness


class MySQLStoreTests(unittest.TestCase):
    def test_unknown_backend_fails_closed(self):
        with patch.dict('os.environ',{'TAMSOOD_DATA_BACKEND':'typo'}):
            with self.assertRaises(RuntimeError):mysql_store.enabled()
            self.assertFalse(readiness())

    def test_mysql_failure_does_not_fall_back(self):
        with patch.dict('os.environ',{'TAMSOOD_DATA_BACKEND':'mysql'}), \
             patch.object(mysql_store,'connect',side_effect=RuntimeError('offline')):
            self.assertFalse(readiness())
            with self.assertRaises(RuntimeError):mysql_store.Connection()

    def test_literal_search_escapes_mysql_wildcards(self):
        self.assertEqual(mysql_store.like('a!%_'),'%a!!!%!_%')

    def test_sqlite_compatible_row_index(self):
        row=mysql_store.Row(a=12,b='x')
        self.assertEqual(row[0],12)
        self.assertEqual(row['b'],'x')

if __name__=='__main__':unittest.main()
