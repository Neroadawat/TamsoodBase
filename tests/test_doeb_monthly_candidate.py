import unittest
from scripts.check_doeb_monthly_candidate import inspect_rows


def row(month,amount='1'):
    return {'YEAR_ID':'2568','MONTH_ID':str(month),'QTY':amount,'UNIT':'พันลิตรต่อเดือน',
            'DATAOWNER':'กรมธุรกิจพลังงาน','ENTREPRENEUR':'ISOLATED_TEST_FIXTURE'}


class MonthlyIntakeTests(unittest.TestCase):
    def test_partial_year_is_not_extrapolated(self):
        result=inspect_rows([row(month) for month in range(1,6)],2025,'Thousand litre')
        self.assertEqual(result['months_missing'],list(range(6,13)))
        self.assertIn('INCOMPLETE_CALENDAR_YEAR',result['blockers'])
        self.assertIsNone(result['annual_amount']);self.assertFalse(result['admitted_to_comparison'])

    def test_repeated_rows_are_not_silently_dropped(self):
        rows=[row(month) for month in range(1,13)];rows.append(dict(rows[0]))
        result=inspect_rows(rows,2025,'Thousand litre')
        self.assertEqual(result['repeated_source_row_extras'],1);self.assertEqual(len(rows),13)
        self.assertFalse(result['deduplication_applied']);self.assertFalse(result['ready_for_further_scope_review'])

    def test_volume_does_not_become_mass_and_complete_months_are_not_acceptance(self):
        rows=[row(month) for month in range(1,13)]
        mass=inspect_rows(rows,2025,'Ton')
        self.assertIn('UNIT_MAPPING_UNRESOLVED_OR_INCOMPATIBLE',mass['blockers'])
        volume=inspect_rows(rows,2025,'Thousand litre')
        self.assertTrue(volume['ready_for_further_scope_review'])
        self.assertFalse(volume['admitted_to_comparison']);self.assertIsNone(volume['annual_amount'])

    def test_invalid_cells_are_reported_not_skipped_as_zero(self):
        result=inspect_rows([row(1,'NaN'),row(13),row(2,'')],2025,'Thousand litre')
        self.assertEqual(result['invalid_source_lines'],[2,3,4])
        self.assertIn('INVALID_SOURCE_YEAR_MONTH_OR_QUANTITY',result['blockers'])


if __name__=='__main__':unittest.main()
