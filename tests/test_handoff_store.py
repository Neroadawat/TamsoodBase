import sqlite3
import unittest
from contextlib import closing
from scripts.build_handoff_store import SCHEMA, verify_existing_release


def fixture():
    con = sqlite3.connect(':memory:')
    con.executescript(SCHEMA)
    con.execute('INSERT INTO source VALUES(?)', ('source-fixture',))
    con.execute('INSERT INTO process VALUES(?,?,?)', ('process-fixture', 'source-fixture', 'Reviewed process'))
    con.execute('INSERT INTO observation VALUES(?,?,?,?,?,?,?,?,?)',
                ('observation-fixture', 'foreground', 'source-fixture', 'process-fixture', '1.00', None, 'HOLD', 1, '{}'))
    con.execute('INSERT INTO card_observation VALUES(?,?)', ('card-fixture', 'observation-fixture'))
    con.commit()
    return con


class ExistingReleaseTests(unittest.TestCase):
    def test_identical_release_is_reusable_without_writes(self):
        with closing(fixture()) as prior, closing(fixture()) as expected:
            before = list(prior.iterdump())
            verify_existing_release(prior, expected)
            self.assertEqual(list(prior.iterdump()), before)
            self.assertEqual(prior.total_changes, 4)

    def test_changes_to_every_lineage_table_are_rejected_without_repair(self):
        for sql in ('DELETE FROM card_observation',
                    "UPDATE process SET name='Changed process'",
                    "UPDATE observation SET amount='2.00'",
                    "INSERT INTO source VALUES('extra-source-fixture')"):
            with self.subTest(sql=sql), closing(fixture()) as prior, closing(fixture()) as expected:
                prior.execute(sql)
                prior.commit()
                before = list(prior.iterdump())
                with self.assertRaisesRegex(ValueError, 'Existing immutable release differs'):
                    verify_existing_release(prior, expected)
                self.assertEqual(list(prior.iterdump()), before)

    def test_schema_change_is_rejected_even_with_identical_observation_values(self):
        with closing(fixture()) as prior, closing(fixture()) as expected:
            prior.execute('ALTER TABLE process ADD COLUMN unreviewed TEXT')
            with self.assertRaisesRegex(ValueError, 'process'):
                verify_existing_release(prior, expected)


if __name__ == '__main__':
    unittest.main()
