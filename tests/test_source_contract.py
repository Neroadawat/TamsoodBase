import unittest
from scripts.build_source_contract import source_id


class SourceContractTests(unittest.TestCase):
    def test_identity_is_source_specific(self):
        self.assertEqual(source_id('nso',{'table_id':'13.10'}),'NSO-SYB2026-13.10')
        self.assertEqual(source_id('dmf',{'package':'production-natural-gas'}),'DMF-CKAN-GAS')
        self.assertEqual(source_id('eppo',{'dataset_id':'11_13'}),'EPPO-11_13')

    def test_unknown_sources_not_guessed(self):
        with self.assertRaises(ValueError):source_id('corporate',{'source_url':'https://example.org/sprc.pdf'})
        with self.assertRaises(ValueError):source_id('inventory',{'doi':'unknown','table_id':'4'})
