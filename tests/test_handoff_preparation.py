import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from scripts import prepare_handoff_runtime as preparation


class PreparationTests(unittest.TestCase):
    def test_offline_missing_sources_do_not_fetch_or_synthesize(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);folder=root/'evidence';folder.mkdir()
            (folder/'thaioil-pilot-review-2026-10-22.json').write_text(json.dumps({'pdf_sha256':'0'*64,'source_url':'https://example.invalid/fixture'}))
            with patch.object(preparation,'ROOT',root),patch('scripts.acquire_thaioil.acquire') as acquire:
                result=preparation.restore_corporate(offline=True)
                self.assertFalse(result['restored']);self.assertEqual(result['status'],'SOURCE_MISSING_OFFLINE')
                acquire.assert_not_called();self.assertFalse((root/'data').exists())

    def test_offline_missing_inventory_does_not_open_network(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(preparation,'ROOT',Path(temporary)),patch.object(preparation,'urlopen') as network:
            self.assertFalse(preparation.restore_live_product(offline=True)['restored'])
            network.assert_not_called()

    def test_incomplete_cache_is_not_reported_ready(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(preparation,'ROOT',Path(temporary)):
            self.assertIsNone(preparation.corporate_cache())

    def test_offline_missing_dmf_never_acquires_even_with_acquisition_flag(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(preparation,'ROOT',Path(temporary)),patch.object(preparation.subprocess,'run') as process:
            result=preparation.prepare_dmf(offline=True,acquire_if_missing=True)
            self.assertFalse(result['passed']);process.assert_not_called()

    def test_offline_missing_image_cannot_trigger_pull_or_lab_creation(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(preparation,'ROOT',Path(temporary)),patch.object(preparation.subprocess,'run',return_value=SimpleNamespace(returncode=1)) as process:
            result=preparation.prepare_labs(offline=True)
            self.assertEqual(result['status'],'OFFLINE_IMAGE_MISSING')
            self.assertEqual(process.call_count,1)
            self.assertEqual(process.call_args.args[0],['docker','image','inspect','mysql:8.1'])


if __name__=='__main__':unittest.main()
