import json
import shutil
import tempfile
import unittest
import hashlib
from pathlib import Path
from scripts.audit_release_consistency import ROOT, inspect


class ReleaseConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        evidence = json.loads((ROOT/'evidence/release-consistency.json').read_text(encoding='utf8'))
        names = {entry['path'] for entry in evidence['files']}
        if 'evidence/versioned-inventory.json' in names:
            versioned=json.loads((ROOT/'evidence/versioned-inventory.json').read_text(encoding='utf8'))
            names.add(versioned['candidate_path'])
        if 'evidence/activity-model-store.json' in names:
            model=json.loads((ROOT/'evidence/activity-model-store.json').read_text(encoding='utf8'))
            names.add(model['database'])
        names.update(['evidence/upstream-inventory-review.json','evidence/srs-current-review.json',
                      'build/vercel-upload/api/[route].js',
                      'data/raw/mdpi-9415/pdf-v3/source.pdf','data/raw/mdpi-9415/table4-dom.json',
                      'build/frontend/build-manifest.json','output/pdf/TamsoodBase-SRS-review.pdf'])
        for name in ('index.html','ask.html','style.css','api.js','app.js','favicon.svg','upstream-inventory.json','case-study.js','case-study.json','config.js','discovery.js','story.js','theme.css','design-refresh.css','noto-sans-thai-06310198b08f.woff2','FONT-LICENSE.txt'):
            names.update(['web/'+name,'build/frontend/'+name])
        for name in names:
            target = self.root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, target)
        # Isolate the unit fixture from an intentionally unbuilt working tree.
        # The actual release command still checks real build/source parity.
        manifest_path=self.root/'build/frontend/build-manifest.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf8'))
        for entry in manifest['files']:
            if entry['path']!='config.js':shutil.copyfile(self.root/'web'/entry['path'],self.root/'build/frontend'/entry['path'])
            body=(self.root/'build/frontend'/entry['path']).read_bytes()
            entry['sha256']=hashlib.sha256(body).hexdigest();entry['bytes']=len(body)
        manifest_path.write_text(json.dumps(manifest),encoding='utf8')
        shutil.copyfile(self.root/'api/[route].js',self.root/'build/vercel-upload/api/[route].js')

    def test_candidate_reports_actual_document_state_without_claiming_live_health(self):
        result = inspect(self.root)
        document=json.loads((self.root/'evidence/srs-current-review.json').read_text(encoding='utf8'))
        current_hash=hashlib.sha256((self.root/'docs/submission/SRS.md').read_bytes()).hexdigest()
        checks={c['check']:c['passed'] for c in result['checks']}
        self.assertEqual(checks['srs_markdown_matches_rendered_source'],current_hash==document['source_sha256'])
        self.assertTrue(all(ok for name,ok in checks.items() if name!='srs_markdown_matches_rendered_source'))
        self.assertFalse(result['recorded_deployments']['live_rechecked_this_run'])

    def test_stale_build_detected(self):
        path = self.root/'web/app.js'
        path.write_text(path.read_text(encoding='utf8')+'\n// changed\n', encoding='utf8')
        result = inspect(self.root)
        self.assertFalse(result['passed'])
        self.assertIn('frontend_source_matches_build:app.js', [c['check'] for c in result['checks'] if not c['passed']])

    def test_wrong_public_context_detected_even_if_amount_unchanged(self):
        path = self.root/'web/upstream-inventory.json'
        body = json.loads(path.read_text(encoding='utf8'))
        body['rows'][0]['reference_unit'] = 'MJ fuel'
        path.write_text(json.dumps(body), encoding='utf8')
        self.assertFalse(inspect(self.root)['passed'])

    def test_stale_document_render_detected(self):
        path = self.root/'docs/submission/SRS.md'
        path.write_text(path.read_text(encoding='utf8')+'\nChanged after render\n', encoding='utf8')
        result = inspect(self.root)
        self.assertFalse(result['passed'])
        self.assertIn('srs_markdown_matches_rendered_source', [c['check'] for c in result['checks'] if not c['passed']])
