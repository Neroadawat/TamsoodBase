"""Download identity/size guards using isolated bytes, never source-data substitutes."""
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import acquire_thaioil


class Response(io.BytesIO):
    url=acquire_thaioil.URL
    headers={}


class ReportAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        replacement=patch.object(acquire_thaioil,'ROOT',self.root)
        replacement.start();self.addCleanup(replacement.stop)
        self.target=self.root/'data/raw/thaioil/2024/sustainability-report.pdf'

    def test_recorded_hash_mismatch_writes_no_source_or_manifest(self):
        with patch.object(acquire_thaioil.urllib.request,'urlopen',return_value=Response(b'%PDF-fixture')):
            with self.assertRaisesRegex(ValueError,'recorded source'):
                acquire_thaioil.acquire(expected_sha256='0'*64)
        self.assertFalse(self.target.exists());self.assertFalse(self.target.with_name('manifest.json').exists())

    def test_matching_bytes_preserve_restricted_reuse_status_and_do_not_overwrite(self):
        body=b'%PDF-isolated-unit-fixture';digest=hashlib.sha256(body).hexdigest()
        with patch.object(acquire_thaioil.urllib.request,'urlopen',return_value=Response(body)):
            acquire_thaioil.acquire(expected_sha256=digest)
        self.assertEqual(self.target.read_bytes(),body)
        manifest=json.loads(self.target.with_name('manifest.json').read_bytes())
        self.assertEqual(manifest['sha256'],digest);self.assertFalse(manifest['redistribute_raw'])
        self.assertEqual(manifest['rights_status'],'public_readable_reuse_not_confirmed')
        changed=b'%PDF-new-fixture'
        with patch.object(acquire_thaioil.urllib.request,'urlopen',return_value=Response(changed)):
            with self.assertRaisesRegex(ValueError,'preserve the old snapshot'):acquire_thaioil.acquire()
        self.assertEqual(self.target.read_bytes(),body)

    def test_invalid_hash_and_oversized_download_fail_before_write(self):
        with patch.object(acquire_thaioil.urllib.request,'urlopen') as network:
            with self.assertRaises(ValueError):acquire_thaioil.acquire(expected_sha256='not-a-hash')
            network.assert_not_called()
        with patch.object(acquire_thaioil,'MAX_PDF_BYTES',8), \
             patch.object(acquire_thaioil.urllib.request,'urlopen',return_value=Response(b'%PDF-'+b'x'*10)):
            with self.assertRaisesRegex(ValueError,'bounded download'):acquire_thaioil.acquire()
        self.assertFalse(self.target.exists())


if __name__=='__main__':unittest.main()
