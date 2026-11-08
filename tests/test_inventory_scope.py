import copy,json,unittest
from pathlib import Path
from src.inventory_scope import validate_process_context,study_scope

class InventoryScopeTests(unittest.TestCase):
    def setUp(self):
        self.rows=[dict(observation_id='in',process='FAME',reference_amount='1000',reference_unit='MJ fuel',boundary='Foreground conversion',geography='Thailand',technology_level='Commercial plant study',publication_year=2020,data_period=None,allocation='Source method unresolved',doi='10.3390/su12229415',source_snapshot_sha256='abc',flow='Oil',amount='30',unit='kg',direction='INPUT',role='INPUT',is_full_lci_dataset=False)]
        self.rows.append(self.rows[0]|dict(observation_id='out',flow='FAME',amount='26.3',direction='OUTPUT',role='REFERENCE_PRODUCT'))

    def test_scope_keeps_product_and_energy_basis_distinct(self):
        result=validate_process_context(self.rows)[0]
        self.assertEqual(result['reference_basis']['unit'],'MJ fuel')
        self.assertEqual(result['reference_product']['amount'],'26.3')
        self.assertFalse(result['full_lifecycle_inventory'])

    def test_mixed_basis_year_boundary_or_source_rejected(self):
        for field,value in [('reference_amount','1'),('reference_unit','kg'),('boundary','Full lifecycle'),('data_period','2024'),('source_snapshot_sha256','other')]:
            with self.subTest(field=field):
                bad=copy.deepcopy(self.rows);bad[1][field]=value
                with self.assertRaises(ValueError):validate_process_context(bad)

    def test_duplicate_identity_and_reference_product_rejected(self):
        for extra in (self.rows[0],self.rows[1]|dict(observation_id='second-product')):
            with self.assertRaises(ValueError):validate_process_context(self.rows+[extra])

    def test_invalid_quantity_direction_or_full_claim_rejected(self):
        for field,value in [('reference_amount','0'),('reference_amount','NaN'),('reference_amount','Infinity')]:
            bad=[r|{field:value} for r in self.rows]
            with self.assertRaises(ValueError):validate_process_context(bad)
        for change in (dict(direction='INPUT'),dict(is_full_lci_dataset=True)):
            bad=copy.deepcopy(self.rows);bad[1].update(change)
            with self.assertRaises(ValueError):validate_process_context(bad)

    def test_study_scope_requires_evidence(self):
        with self.assertRaises(ValueError):study_scope(self.rows,'No confirmed functional unit')
