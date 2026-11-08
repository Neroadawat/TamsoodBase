import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


def node_path():
    node=shutil.which('node')
    if not node:
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
        if bundled.is_file():node=str(bundled)
    return node


class FrontendTests(unittest.TestCase):
    def test_discovery_lossless_routes_comparison_and_concurrent_status(self):
        result=subprocess.run([self.node,str(ROOT/'tests/discovery-contract.cjs')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_story_and_motion_behavior(self):
        for name in ('fuel-story-behavior.cjs','motion-behavior.cjs'):
            result=subprocess.run([self.node,str(ROOT/'tests'/name)],capture_output=True,text=True,encoding='utf-8',timeout=20)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_friendly_statistics_semantics_and_actual_summary(self):
        result=subprocess.run([self.node,str(ROOT/'tests/friendly-stats-behavior.cjs')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_case_study_contract_and_readable_precision(self):
        result=subprocess.run([self.node,str(ROOT/'tests/case-study-behavior.cjs')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_public_build_rejects_nested_restricted_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for directory in ('scripts','web'):(root/directory).mkdir()
            shutil.copyfile(ROOT/'scripts/build_frontend.mjs',root/'scripts/build_frontend.mjs')
            for name in ('index.html','style.css','api.js','app.js','favicon.svg','upstream-inventory.json','case-study.js','case-study.json','discovery.js','story.js','theme.css','noto-sans-thai-06310198b08f.woff2','FONT-LICENSE.txt'):
                shutil.copyfile(ROOT/'web'/name,root/'web'/name)
            target=root/'web/case-study.json'
            data=json.loads(target.read_text(encoding='utf-8'))
            data['components'][0]['rows']=[{'amount':'123','unit':'kg'}]
            target.write_text(json.dumps(data),encoding='utf-8')
            result=subprocess.run([self.node,str(root/'scripts/build_frontend.mjs')],capture_output=True,text=True,timeout=20)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Private case inventory',result.stderr)
            self.assertFalse((root/'build/frontend/case-study.json').exists())

    def test_upstream_snapshot_retry_and_filter(self):
        result=subprocess.run([self.node,str(ROOT/'tests/upstream-ux-behavior.cjs')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_evidence_navigation_and_demo_controls(self):
        result=subprocess.run([self.node,str(ROOT/'tests/evidence-ux-behavior.cjs')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_inventory_process_context_selection(self):
        result=subprocess.run([self.node,str(ROOT/'tests/inventory-ux-behavior.cjs')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_catalog_filters_counts_and_layout(self):
        result=subprocess.run([self.node,str(ROOT/'tests/catalog-ux-behavior.cjs')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_lazy_views_retry_failed_loads(self):
        result=subprocess.run([self.node,str(ROOT/'tests/web-lazy-behavior.cjs')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def setUp(self):
        self.node=node_path()
        if not self.node:self.skipTest('Node.js required')

    def test_transport_and_configuration_failures(self):
        result=subprocess.run([self.node,str(ROOT/'tests/frontend-api-behavior.cjs')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_deployment_build_only_copies_public_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for directory in ('scripts','web'):(root/directory).mkdir()
            shutil.copyfile(ROOT/'scripts/build_frontend.mjs',root/'scripts/build_frontend.mjs')
            for name in ('index.html','style.css','api.js','app.js','favicon.svg','upstream-inventory.json','case-study.js','case-study.json','discovery.js','story.js','theme.css','noto-sans-thai-06310198b08f.woff2','FONT-LICENSE.txt'):
                shutil.copyfile(ROOT/'web'/name,root/'web'/name)
            (root/'web/secret.json').write_text('do not copy')
            env=os.environ|{'VERCEL':'1','TAMSOOD_API_BASE_URL':'https://api.example.com'}
            result=subprocess.run([self.node,str(root/'scripts/build_frontend.mjs')],env=env,capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)
            out=root/'build/frontend'
            self.assertEqual({p.name for p in out.iterdir()},{'index.html','style.css','api.js','app.js','favicon.svg','upstream-inventory.json','case-study.js','case-study.json','discovery.js','story.js','theme.css','noto-sans-thai-06310198b08f.woff2','FONT-LICENSE.txt','config.js','build-manifest.json'})
            manifest=json.loads((out/'build-manifest.json').read_text())
            self.assertTrue(manifest['containsSourceData'])
            self.assertFalse(manifest['containsPrivateResearchData'])
            self.assertFalse(manifest['containsRawDocuments'])
            self.assertEqual(manifest['publicSnapshotLicence'],'CC BY 4.0')
            self.assertIn('https://api.example.com',(out/'config.js').read_text())
            missing=subprocess.run([self.node,str(root/'scripts/build_frontend.mjs')],env=env|{'TAMSOOD_API_BASE_URL':''},capture_output=True,text=True,timeout=20)
            self.assertNotEqual(missing.returncode,0)
            unsafe=subprocess.run([self.node,str(root/'scripts/build_frontend.mjs')],env=env|{'TAMSOOD_API_BASE_URL':'http://54.206.67.32:8765'},capture_output=True,text=True,timeout=20)
            self.assertNotEqual(unsafe.returncode,0)
            proxy=subprocess.run([self.node,str(root/'scripts/build_frontend.mjs')],env=env|{'TAMSOOD_API_BASE_URL':'','TAMSOOD_DEPLOY_MODE':'proxy'},capture_output=True,text=True,timeout=20)
            self.assertEqual(proxy.returncode,0,proxy.stderr)
            self.assertIn('"apiBaseUrl":""',(out/'config.js').read_text())
            self.assertNotIn('loginUrl',(out/'config.js').read_text())

    def test_vercel_source_allowlist_excludes_private_and_data_files(self):
        git=shutil.which('git')
        if not git:self.skipTest('Git required for ignore-pattern test')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            subprocess.run([git,'init','--quiet',str(root)],check=True,capture_output=True)
            paths=['vercel.json','web/index.html','web/config.js','web/upstream-inventory.json','web/secret.json','scripts/build_frontend.mjs',
                   'scripts/mysql_workspace.py','.local/key.pem','data/raw/source.csv','build/frontend/private.json','api/[route].js','api/private.json']
            for name in paths:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
            ignored=subprocess.run([git,'-C',str(root),'-c','core.excludesFile='+str(ROOT/'.vercelignore'),
                'check-ignore','--no-index',*paths],capture_output=True,text=True,check=True).stdout.splitlines()
            self.assertEqual(set(ignored),set(paths)-{'vercel.json','web/index.html','web/config.js','web/upstream-inventory.json','scripts/build_frontend.mjs','api/[route].js'})
