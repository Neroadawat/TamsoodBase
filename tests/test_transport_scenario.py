import unittest
from src.transport_scenario import freight_scenario
class FreightScenario(unittest.TestCase):
    def factor(self):return dict(id='TEST',activity_unit='tkm',value='0.0546',geography='TH',provenance_class='THAI_NATIONAL_LCI_REPORTED',result_unit='kgCO2e',method='TEST_ONLY',version='TEST_ONLY',source_url='https://example.org/fixture',source_sha256='a'*64,locator='TEST_ONLY')
    def test_tkm_and_loading_not_applied_twice(self):
        r=freight_scenario('1000','100',self.factor(),assumption_id='TEST_ONLY');self.assertEqual(r['tkm'],'100');self.assertEqual(r['screening']['result'],'5.4600');self.assertFalse(r['empty_return_added']);self.assertFalse(r['full_transport_inventory']);self.assertFalse(r['combined_with_biodiesel_factor'])
    def test_km_unit_and_missing_assumption_are_rejected(self):
        f=self.factor();f['activity_unit']='km'
        with self.assertRaises(ValueError):freight_scenario('1000','100',f,assumption_id='TEST')
        with self.assertRaises(ValueError):freight_scenario('1000','100',self.factor(),assumption_id='')
