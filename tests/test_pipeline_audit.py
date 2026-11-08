import json
from pathlib import Path
import shutil
import tempfile
import unittest
from scripts.audit_pipeline import ROOT, keyed, replay_sources


class PipelineAuditTests(unittest.TestCase):
    def test_duplicate_identities_are_never_silently_discarded(self):
        with self.assertRaisesRegex(ValueError,'Duplicate observation'):
            keyed([{'observation_id':'fixture'},{'observation_id':'fixture'}])

    @unittest.skipUnless(all((ROOT/p).exists() for p in ('build/nso/report.json','build/eppo/report.json','build/product-inventory/report.json','data/raw/nso','data/raw/eppo','data/raw/mdpi-9415')),'All three local snapshot layers required')
    def test_report_corruption_detected_by_original_source_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for folder in ('build/nso','build/eppo','build/product-inventory','data/raw/nso','data/raw/eppo','data/raw/mdpi-9415'):
                shutil.copytree(ROOT/folder,root/folder)
            p=root/'build/nso/report.json';report=json.loads(p.read_text(encoding='utf-8'))
            report['rows'][0]['source_column']=999
            p.write_text(json.dumps(report,ensure_ascii=False),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'NSO source-to-report'):
                replay_sources(root)
