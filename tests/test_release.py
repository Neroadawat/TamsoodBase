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
