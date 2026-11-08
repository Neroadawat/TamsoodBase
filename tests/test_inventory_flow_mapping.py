import copy,json,unittest
from pathlib import Path
from scripts.build_inventory_model_review import map_flows

class FlowMappingTests(unittest.TestCase):
    def setUp(self):
        self.registry=json.loads(Path('docs/inventory-flow-registry.json').read_text(encoding='utf8'))
        self.row=dict(doi='10.3390/su12229415',flow='Tap water',unit='m3',amount='0.40',observation_id='water',source_row=3,source_column=3)
    def test_preserves_source_and_does_not_infer_environmental_withdrawal(self):
        before=copy.deepcopy(self.row);result=map_flows([self.row],self.registry)[0]
        self.assertEqual(result['classification'],'UTILITY');self.assertEqual(result['provider_status'],'NOT_LINKED')
        self.assertEqual(self.row,before)
    def test_unknown_label_wrong_unit_and_doi_rejected(self):
        for change in [dict(flow='freshwater'),dict(unit='kg'),dict(doi='other')]:
            with self.assertRaises(ValueError):map_flows([self.row|change],self.registry)
    def test_duplicate_registry_and_inferred_compartment_rejected(self):
        bad=copy.deepcopy(self.registry);bad['flows'].append(bad['flows'][0])
        with self.assertRaises(ValueError):map_flows([self.row],bad)
        bad=copy.deepcopy(self.registry);next(f for f in bad['flows'] if f['source_label']=='Tap water')['compartment']='water'
        with self.assertRaises(ValueError):map_flows([self.row],bad)
