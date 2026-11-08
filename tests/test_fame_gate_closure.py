import unittest
from decimal import Decimal
from scripts.review_fame_gate_closure import build,checked_passage,compact,ROOT


class FameGateClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=build()

    def test_explicit_method_is_not_permission_to_reallocate(self):
        d=next(d for d in self.report['decisions'] if d['id']=='allocation')
        self.assertEqual(sum(map(Decimal,d['source_reported_factor'].values())),Decimal(1))
        self.assertFalse(d['factor_applied'])
        self.assertEqual(d['status'],'BLOCKED_TABLE_BASIS_UNKNOWN')
        self.assertIsNone(self.report['CO2e_total'])
        self.assertEqual(self.report['new_burden_links_applied'],0)

    def test_every_required_gate_has_a_specific_evidence_requirement(self):
        self.assertEqual({d['id'] for d in self.report['decisions']},{'allocation','compatibility','transport','use','waste','background'})
        self.assertTrue(all(d['required_evidence'] for d in self.report['decisions']))
        self.assertEqual(len(self.report['source_evidence']),7)
        self.assertFalse(self.report['full_lifecycle_inventory'])
        self.assertEqual(self.report['new_source_screen']['numeric_rows_imported'],0)

    def test_missing_source_passage_fails_instead_of_guessing(self):
        with self.assertRaises(ValueError):
            checked_passage(ROOT/'data/raw/mdpi-9415/pdf-v3/source.pdf',7,'Imaginary explicit unallocated table statement')
        self.assertEqual(compact('efﬁciency  70 %'),compact('efficiency70%'))


if __name__=='__main__':unittest.main()
