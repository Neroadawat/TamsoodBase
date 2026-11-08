import unittest
from pathlib import Path
from scripts.package_backend import ROOT,deploy_files


@unittest.skipUnless((ROOT/'data/raw/dmf/latest.json').exists(),'Local deployment artifacts required')
class BackendPackageTests(unittest.TestCase):
    def test_deployment_allowlist_excludes_keys_and_raw_documents(self):
        names={p.relative_to(ROOT).as_posix() for p in deploy_files()}
        self.assertIn('src/wsgi.py',names)
        self.assertIn('web/upstream-inventory.json',names)
        self.assertIn('build/reusable/reference.sqlite',names)
        self.assertTrue(all(not n.startswith('.local/') and not n.endswith(('.pem','.pdf','.csv','.xlsx','.xls')) for n in names))
        self.assertTrue(all(n.endswith('.metadata.json') or n=='data/raw/dmf/latest.json' for n in names if n.startswith('data/raw/')))
