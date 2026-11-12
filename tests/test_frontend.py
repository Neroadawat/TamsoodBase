import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
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
    def test_gemini_privacy_notice_distinguishes_billing_terms(self):
        page=(ROOT/'web/ask.html').read_text(encoding='utf-8')
        self.assertIn('สถานะ Billing ของ Google Cloud Project ที่ผูกกับ API key',page)
        self.assertIn('ทีมยังไม่ได้ตรวจยืนยัน',page)
        self.assertIn('อาจใช้คำถามและคำตอบเพื่อพัฒนาบริการ',page)
        self.assertIn('จะไม่ใช้คำถามและคำตอบเพื่อปรับปรุงผลิตภัณฑ์',page)
        self.assertIn('ไม่ใช่การรับรองว่าไม่มีการตรวจเพื่อป้องกันการใช้งานผิดนโยบาย',page)
        self.assertIn('https://ai.google.dev/gemini-api/terms',page)
        self.assertIn('https://ai.google.dev/gemini-api/docs/billing',page)

    def test_restricted_dataset_api_has_clear_user_facing_banner(self):
        app=(ROOT/'web/app.js').read_text(encoding='utf-8')
        api=(ROOT/'web/api.js').read_text(encoding='utf-8')
        self.assertIn("state==='restricted'",api)
        self.assertIn('ปิดการโหลดข้อมูลจากฐานข้อมูลชั่วคราวระหว่างตรวจสอบสิทธิ์เผยแพร่',app)

    def test_closed_rag_status_matches_disabled_question_controls(self):
        page=(ROOT/'web/ask.html').read_text(encoding='utf-8')
        self.assertIn('privacy-tag privacy-tag--closed',page)
        self.assertIn('ยังปิดการถามผ่านเว็บไซต์',page)
        self.assertIn('ยังไม่เปิดให้ถามผ่านเว็บไซต์',page)
        self.assertIn('id="question" required maxlength="500" rows="2" disabled',page)
        self.assertIn("privacyTag.classList.remove('privacy-tag--closed')",page)

    def test_rag_review_does_not_overwrite_later_search(self):
        result=subprocess.run([self.node,str(ROOT/'tests/rag-ui-behavior.cjs')],capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

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
            for directory in ('scripts','web','docs/rag'):(root/directory).mkdir(parents=True)
            shutil.copyfile(ROOT/'scripts/build_frontend.mjs',root/'scripts/build_frontend.mjs')
            shutil.copyfile(ROOT/'docs/rag/public-release-manifest.json',root/'docs/rag/public-release-manifest.json')
            shutil.copyfile(ROOT/'docs/rag/required-release-gates.json',root/'docs/rag/required-release-gates.json')
            shutil.copyfile(ROOT/'docs/rag/public-evidence.json',root/'docs/rag/public-evidence.json')
            shutil.copyfile(ROOT/'docs/rag/statistical-facts.json',root/'docs/rag/statistical-facts.json')
            for name in ('index.html','ask.html','style.css','api.js','app.js','favicon.svg','upstream-inventory.json','case-study.js','case-study.json','discovery.js','story.js','theme.css','design-refresh.css','noto-sans-thai-06310198b08f.woff2','FONT-LICENSE.txt'):
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
            for directory in ('scripts','web','docs/rag'):(root/directory).mkdir(parents=True)
            shutil.copyfile(ROOT/'scripts/build_frontend.mjs',root/'scripts/build_frontend.mjs')
            shutil.copyfile(ROOT/'docs/rag/public-release-manifest.json',root/'docs/rag/public-release-manifest.json')
            shutil.copyfile(ROOT/'docs/rag/required-release-gates.json',root/'docs/rag/required-release-gates.json')
            shutil.copyfile(ROOT/'docs/rag/public-evidence.json',root/'docs/rag/public-evidence.json')
            shutil.copyfile(ROOT/'docs/rag/statistical-facts.json',root/'docs/rag/statistical-facts.json')
            shutil.copyfile(ROOT/'docs/rag/vercel-preview-corpus.json',root/'docs/rag/vercel-preview-corpus.json')
            for name in ('index.html','ask.html','style.css','api.js','app.js','favicon.svg','upstream-inventory.json','case-study.js','case-study.json','discovery.js','story.js','theme.css','design-refresh.css','noto-sans-thai-06310198b08f.woff2','FONT-LICENSE.txt'):
                shutil.copyfile(ROOT/'web'/name,root/'web'/name)
            (root/'web/secret.json').write_text('do not copy')
            env=os.environ|{'VERCEL':'1','TAMSOOD_API_BASE_URL':'https://api.example.com'}
            result=subprocess.run([self.node,str(root/'scripts/build_frontend.mjs')],env=env,capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)
            out=root/'build/frontend'
            self.assertEqual({p.name for p in out.iterdir()},{'index.html','ask.html','style.css','api.js','app.js','favicon.svg','upstream-inventory.json','case-study.js','case-study.json','discovery.js','story.js','theme.css','design-refresh.css','noto-sans-thai-06310198b08f.woff2','FONT-LICENSE.txt','config.js','build-manifest.json'})
            public_ask=(out/'ask.html').read_text(encoding='utf-8')
            self.assertIn('เก็บคำถาม บริบท และคำตอบไว้ 55 วัน',public_ask)
            self.assertIn('https://ai.google.dev/gemini-api/docs/usage-policies',public_ask)
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
            # Public chat: builds only with the exact knowledge pack the owner released.
            chat_env=env|{'TAMSOOD_API_BASE_URL':'','TAMSOOD_DEPLOY_MODE':'proxy','TAMSOOD_RAG_PUBLIC_ENABLED':'true'}
            no_pack=subprocess.run([self.node,str(root/'scripts/build_frontend.mjs')],env=chat_env,capture_output=True,text=True,timeout=20)
            self.assertNotEqual(no_pack.returncode,0,'the chat UI must not ship without its knowledge pack')
            shutil.copyfile(ROOT/'docs/rag/knowledge-pack.json',root/'docs/rag/knowledge-pack.json')
            public_rag=subprocess.run([self.node,str(root/'scripts/build_frontend.mjs')],env=chat_env,capture_output=True,text=True,timeout=20)
            self.assertEqual(public_rag.returncode,0,public_rag.stderr)
            self.assertIn('"publicRagEnabled":true',(out/'config.js').read_text())
            self.assertIn('"ragMode":"public"',(out/'config.js').read_text())
            manifest_path=root/'docs/rag/public-release-manifest.json'
            original=json.loads(manifest_path.read_text(encoding='utf-8'))
            def blocked(change):
                manifest=json.loads(json.dumps(original))
                change(manifest)
                manifest_path.write_text(json.dumps(manifest),encoding='utf-8')
                run=subprocess.run([self.node,str(root/'scripts/build_frontend.mjs')],env=chat_env,capture_output=True,text=True,timeout=20)
                self.assertNotEqual(run.returncode,0)
                self.assertIn('Public chat build blocked',run.stderr)
            blocked(lambda m:m['knowledge_pack'].update(content_sha256='0'*64))
            blocked(lambda m:m.update(status='HOLD_RIGHTS_REVIEW'))
            blocked(lambda m:m.pop('owner_decision'))
            blocked(lambda m:m.update(external_llm_allowed=False))
            pack_path=root/'docs/rag/knowledge-pack.json'
            pack=json.loads(pack_path.read_text(encoding='utf-8'))
            pack['contains_company_report_values']=True
            pack_path.write_text(json.dumps(pack),encoding='utf-8')
            manifest_path.write_text(json.dumps(original),encoding='utf-8')
            company_values=subprocess.run([self.node,str(root/'scripts/build_frontend.mjs')],env=chat_env,capture_output=True,text=True,timeout=20)
            self.assertNotEqual(company_values.returncode,0,'a pack holding company-report values must never ship')

    def test_vercel_source_allowlist_excludes_private_and_data_files(self):
        git=shutil.which('git')
        if not git:self.skipTest('Git required for ignore-pattern test')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            subprocess.run([git,'init','--quiet',str(root)],check=True,capture_output=True)
            paths=['vercel.json','web/index.html','web/config.js','web/upstream-inventory.json','web/secret.json','scripts/build_frontend.mjs',
                   'scripts/mysql_workspace.py','.local/key.pem','data/raw/source.csv','build/frontend/private.json','api/[route].js','api/rag/ask.js','api/private.json']
            for name in paths:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
            ignored=subprocess.run([git,'-C',str(root),'-c','core.excludesFile='+str(ROOT/'.vercelignore'),
                'check-ignore','--no-index',*paths],capture_output=True,text=True,check=True).stdout.splitlines()
            self.assertEqual(set(ignored),set(paths)-{'vercel.json','web/index.html','web/config.js','web/upstream-inventory.json','scripts/build_frontend.mjs','api/[route].js','api/rag/ask.js'})


class ReportedResultsBlockTests(unittest.TestCase):
    def test_b100_reported_results_match_the_knowledge_pack(self):
        result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/build_reported_results_html.py'),'--check'],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)
        page=(ROOT/'web/index.html').read_text(encoding='utf-8')
        block=page[page.index('<!-- reported-results:start -->'):page.index('<!-- reported-results:end -->')]
        self.assertIn('ไม่ใช่ผลที่ TamsoodBase คำนวณเอง',block)
        self.assertIn('https://doi.org/10.3390/su12229415',block)
        self.assertIn('ยังคำนวณ CO₂e รวมไม่ได้',page)
