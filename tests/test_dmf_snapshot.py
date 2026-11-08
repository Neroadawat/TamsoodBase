"""Synthetic fixtures test rejection paths; these are not project source records."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from src.process_dmf import BASE, COLUMNS, validate_snapshot


class SnapshotPreflightTests(unittest.TestCase):
    def make_snapshot(self, root):
        manifest={'run_id':'fixture','complete':True,'packages':[]}
        for name, columns in COLUMNS.items():
            csv_body=(','.join(BASE+list(columns)+['DAYSOFPRODUCE'])+'\n').encode('cp874')
            metadata=json.dumps({'success':True,'result':{'id':name,'resources':[{'id':name+'-csv','format':'CSV'}]}}).encode()
            (root/(name+'.csv')).write_bytes(csv_body)
            (root/(name+'.metadata.json')).write_bytes(metadata)
            manifest['packages'].append(dict(package=name,package_id=name,resource_id=name+'-csv',
                csv_bytes=len(csv_body),csv_sha256=hashlib.sha256(csv_body).hexdigest(),metadata_sha256=hashlib.sha256(metadata).hexdigest()))
        return manifest

    def test_complete_flag_cannot_hide_missing_or_duplicate_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);manifest=self.make_snapshot(root)
            for packages in (manifest['packages'][:-1], manifest['packages'][:-1]+[manifest['packages'][0]]):
                (root/'manifest.json').write_text(json.dumps(manifest|{'packages':packages}))
                with self.assertRaisesRegex(ValueError,'exactly once'):
                    validate_snapshot(root,'fixture')

    def test_identity_bytes_and_hash_checked_before_processing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);manifest=self.make_snapshot(root)
            (root/'manifest.json').write_text(json.dumps(manifest))
            self.assertEqual(validate_snapshot(root,'fixture')['run_id'],'fixture')
            with self.assertRaisesRegex(ValueError,'run ID'):
                validate_snapshot(root,'other-run')
            manifest['packages'][0]['csv_bytes']+=1
            (root/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'byte count'):
                validate_snapshot(root,'fixture')
            manifest['packages'][0]['csv_bytes']-=1
            manifest['packages'][0]['package_id']='wrong-package'
            (root/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'metadata identity'):
                validate_snapshot(root,'fixture')
