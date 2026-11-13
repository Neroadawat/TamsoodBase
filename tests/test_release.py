import tempfile
import unittest
from pathlib import Path
from scripts.check_release import selected_files
from scripts.task_board import render_text


class ReleaseBoundaryTests(unittest.TestCase):
    def test_board_is_rendered_from_structured_task_status(self):
        data={'tasks':[dict(id='T01',priority='P0',status='DONE',title='Check',done_when='Evidence verified',evidence='docs/check.md',dependencies=[])]}
        before=render_text(data)
        self.assertIn('DONE 1',before)
        data['tasks'][0]['status']='IN_PROGRESS'
        after=render_text(data)
        self.assertNotEqual(before,after)
        self.assertIn('DONE 0',after)

    def test_package_allowlist_excludes_credentials_raw_and_databases(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ('README.md','src/ok.py','docs/ok.md','evidence/check.json','tests/web-check.cjs',
                         '.local/mysql-workspace.json','.env','data/raw/source.pdf',
                         'build/private.sqlite','docs/accidental.pdf','src/__pycache__/cache.pyc'):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('test',encoding='utf-8')
            names={p.relative_to(root).as_posix() for p in selected_files(root)}
            self.assertEqual(names,{'README.md','src/ok.py','docs/ok.md','evidence/check.json','tests/web-check.cjs'})

    def test_web_assets_included_but_not_private_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'web').mkdir()
            for name in ['index.html','app.js','style.css','favicon.svg','secret.json','source.pdf']:
                (root/'web'/name).write_text('test',encoding='utf-8')
            self.assertEqual({p.name for p in selected_files(root)},{'index.html','app.js','style.css','favicon.svg'})


class AcceptanceLedgerTests(unittest.TestCase):
    def test_ledger_is_current_and_reconciles(self):
        import json, subprocess, sys
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        result=subprocess.run([sys.executable,'-X','utf8',str(root/'scripts/build_acceptance_ledger.py'),'--check'],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)
        ledger=json.loads((root/'docs/acceptance-ledger.json').read_text(encoding='utf-8'))
        self.assertEqual(ledger['accepted_total'],sum(layer['accepted'] for layer in ledger['layers']))
        for layer in ledger['layers']:
            self.assertEqual(layer['source_rows'],layer['accepted']+sum(item['count'] for item in layer['held']),layer['dataset'])
        dmf=ledger['layers'][0]
        # The data page shows "unique rows minus 4"; keep that constant tied to the ledger.
        held_after_dedup=sum(item['count'] for item in dmf['held'] if item['reason'].startswith(('HOLD_MAGNITUDE','HOLD_UNIT_LABEL')))
        self.assertEqual(held_after_dedup,4)
        self.assertIn('deduplicated_candidates_pending_review-4',(root/'web/app.js').read_text(encoding='utf-8'))
