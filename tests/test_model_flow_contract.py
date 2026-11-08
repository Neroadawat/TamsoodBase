import unittest
from scripts.build_model_flow_contract import build


class ModelFlowContractTest(unittest.TestCase):
    def test_all_sources_preserved_without_invented_elementary_or_cf_mapping(self):
        report=build()
        self.assertEqual(len(report['flows']),130)
        self.assertEqual(len({r['observation_id'] for r in report['flows']}),130)
        self.assertTrue(all(not r['eligible_for_LCIA'] and r['characterization_factor'] is None and r['compartment'] is None for r in report['flows']))
        self.assertIsNone(report['CO2e_total'])
        self.assertFalse(report['uncertainty']['scenario_variation_is_confidence_interval'])
        self.assertFalse(report['independent_balance']['performed'])
