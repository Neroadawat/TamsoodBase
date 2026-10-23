import json
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.audit_dataset_layers import ROOT,audit_layers


@unittest.skipUnless((ROOT/'build/nso/nso.sqlite').exists(),'Local NSO artifacts required')
class DatasetAuditTests(unittest.TestCase):
    def test_stale_sql_and_changed_row_are_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for folder in ['build/nso','data/raw/nso','evidence','sql/mysql']:
                shutil.copytree(ROOT/folder,root/folder)
            checks={c['name']:c['passed'] for c in audit_layers(root)}
            self.assertTrue(checks['layer_nso_mysql_evidence'])
            path=root/'build/nso/report.json';report=json.loads(path.read_text(encoding='utf-8'))
            report['rows'][0]['status']='ACCEPTED_LCI';report['rows'][0]['amount']='999999'
            path.write_text(json.dumps(report,ensure_ascii=False),encoding='utf-8')
            checks={c['name']:c['passed'] for c in audit_layers(root)}
            for name in ['status','sqlite_payload','mysql_evidence']:
                self.assertFalse(checks['layer_nso_'+name])
