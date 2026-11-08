import unittest
from scripts.compare_data_models import project, graph_query, project_inventory, inventory_query


def fixture():
    return {'observation_id':'synthetic-fixture','decision':'ACCEPTED_REFERENCE',
            'is_normalized_lci_exchange':False,'pdf_sha256':'fixture-hash',
            'publisher':'fixture-publisher','source_url':'https://example.org/fixture',
            'reference_year':2024,'rights_status':'NOT_CLEARED'}


class ProjectionTests(unittest.TestCase):
    def test_inventory_preserves_basis_decimal_and_exchange_identity(self):
        row={'observation_id':'synthetic-inventory','status':'SOURCE_REPORTED_PRODUCT_INVENTORY','direction':'INPUT','process':'TEST','flow':'Fuel','unit':'kg','source_snapshot_sha256':'fixture-source','source_url':'https://example.org/table','doi':'fixture-doi','licence':'fixture','reference_amount':'1000','reference_unit':'MJ fuel','boundary':'fixture foreground','geography':'Thailand','allocation':'no additional allocation','data_period':None,'amount':'0.0012300'}
        graph=project_inventory([row])
        self.assertEqual(inventory_query(graph,'TEST','INPUT'),['synthetic-inventory'])
        self.assertEqual(inventory_query(graph,'TEST','OUTPUT'),[])
        self.assertEqual(graph['nodes']['exchange:synthetic-inventory']['properties']['amount'],'0.0012300')
        self.assertIsNone(graph['nodes']['exchange:synthetic-inventory']['properties']['data_period'])
        with self.assertRaises(ValueError):project_inventory([row,row])
        with self.assertRaises(ValueError):project_inventory([row,row|{'observation_id':'other','reference_amount':'1'}])

    def test_duplicate_or_ineligible_records_cannot_inflate_graph(self):
        row=fixture()
        with self.assertRaises(ValueError):project([row,row])
        for change in [{'decision':'HOLD_CONTEXT'},{'is_normalized_lci_exchange':True}]:
            with self.assertRaises(ValueError):project([row|change])

    def test_provenance_identity_conflict_and_query_scope(self):
        row=fixture();graph=project([row])
        self.assertEqual(graph_query(graph,'fixture-publisher',2024),['synthetic-fixture'])
        self.assertEqual(graph_query(graph,'other',2024),[])
        self.assertEqual(graph_query(graph,'fixture-publisher',2023),[])
        self.assertEqual(graph['nodes']['observation:synthetic-fixture']['properties']['rights_status'],'NOT_CLEARED')
        with self.assertRaises(ValueError):project([row,row|{'observation_id':'second-fixture','source_url':'https://example.org/conflicting-source'}])
