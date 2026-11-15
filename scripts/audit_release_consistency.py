"""Create a local release-candidate manifest; recorded deploy evidence is not live health."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(root):
    def read(name):
        return json.loads((root/name).read_text(encoding='utf8'))

    checks = []
    def check(name, passed, severity='ERROR'):
        checks.append({'check': name, 'passed': bool(passed), 'severity': severity})

    upstream = read('build/upstream-inventory/report.json')
    conversion = read('build/product-inventory/report.json')
    public = read('web/upstream-inventory.json')
    reviewed = read('evidence/upstream-inventory-review.json')
    check('upstream_matches_reviewed_evidence', upstream == reviewed)
    source = root/'data/raw/mdpi-9415/pdf-v3/source.pdf'
    check('retained_pdf_hash', sha(source) == upstream['source']['sha256'])
    source4 = root/'data/raw/mdpi-9415/table4-dom.json'
    check('retained_table4_hash', sha(source4) == conversion['source_snapshot_sha256'])
    # Check the complete public projection, not only quantities or row counts.
    from scripts.build_public_upstream import public_snapshot
    check('public_projection_all_fields', public == public_snapshot(upstream))

    build = read('build/frontend/build-manifest.json')
    check('frontend_private_data_excluded', build.get('containsPrivateResearchData') is False and build.get('containsRawDocuments') is False)
    allowed = {'index.html','ask.html','style.css','api.js','app.js','favicon.svg','upstream-inventory.json','case-study.js','case-study.json','discovery.js','story.js','theme.css','design-refresh.css','noto-sans-thai-06310198b08f.woff2','FONT-LICENSE.txt','config.js'}
    names = [entry['path'] for entry in build['files']]
    check('frontend_asset_allowlist', len(names) == len(set(names)) and set(names) == allowed)
    packaged_proxy=root/'build/vercel-upload/api/[route].js'
    check('packaged_proxy_matches_source',packaged_proxy.exists() and packaged_proxy.read_bytes()==(root/'api/[route].js').read_bytes())
    for entry in build['files']:
        name = entry['path']
        if name not in allowed:
            continue
        output = root/'build/frontend'/name
        check('frontend_build_hash:'+name, output.exists() and sha(output) == entry['sha256'])
        if name != 'config.js':
            check('frontend_source_matches_build:'+name, output.exists() and output.read_bytes() == (root/'web'/name).read_bytes())

    srs = read('evidence/srs-current-review.json')
    pdf = root/Path(srs['artifact'].replace('\\','/'))
    check('srs_markdown_matches_rendered_source', sha(root/'docs/submission/SRS.md') == srs['source_sha256'])
    check('srs_pdf_matches_evidence', pdf.exists() and sha(pdf) == srs['sha256'])
    check('srs_all_pages_rendered', srs['pages'] == srs['rendered_pages'])
    versioned_evidence='evidence/versioned-inventory.json'
    if (root/versioned_evidence).exists():
        versioned=read(versioned_evidence)
        candidate=root/versioned['candidate_path']
        check('versioned_review_artifact_hash',candidate.exists() and sha(candidate)==versioned['candidate_sha256'])
    model_evidence='evidence/activity-model-store.json'
    if (root/model_evidence).exists():
        model=read(model_evidence)
        check('activity_model_store_hash',sha(root/model['database'])==model['database_sha256'])
        chain=read('build/thai-fame-activity-chain/scenarios.json')
        check('activity_model_input_hash',sha(root/'build/thai-fame-activity-chain/scenarios.json')==model['input_manifest']['input_artifact_sha256'])
        from scripts.build_case_study_metadata import project
        check('public_case_metadata_all_fields',read('web/case-study.json')==project(chain,model))
    # These attest only the last recorded release, never the current EC2/Vercel state.
    backend = read('evidence/ec2-upgrade.json')
    frontend_evidence = 'evidence/current-frontend-release.json' if (root/'evidence/current-frontend-release.json').exists() else 'evidence/upstream-export-review.json'
    frontend = read(frontend_evidence)
    if 'public_snapshot_id' in frontend:
        check('recorded_frontend_snapshot_version', frontend['public_snapshot_id'] == public['public_snapshot_id'])
    tracked = ['docs/submission/SRS.md','web/upstream-inventory.json',
               'build/upstream-inventory/report.json','build/product-inventory/report.json',
               'evidence/ec2-upgrade.json',frontend_evidence,'api/[route].js',
               'sql/mysql/api-schema.sql','sql/mysql/supplemental-schema.sql',
               'docs/inventory-flow-registry.json']
    if (root/versioned_evidence).exists():tracked.append(versioned_evidence)
    if (root/model_evidence).exists():tracked.extend([model_evidence,'web/case-study.json',
        'build/thai-fame-activity-chain/scenarios.json','scripts/build_case_study_metadata.py'])
    files = [{'path': name, 'sha256': sha(root/name)} for name in tracked]
    identity = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {'scope': 'LOCAL_RELEASE_CANDIDATE_CONSISTENCY_NOT_LIVE_RUNTIME_ATTESTATION',
            'candidate_id': identity, 'files': files, 'checks': checks,
            'passed': all(c['passed'] for c in checks if c['severity'] == 'ERROR'),
            'recorded_deployments': {'backend_release': backend['release'],
                                     'frontend_deployment_id': frontend['deployment_id'],
                                     'live_rechecked_this_run': False},
            'dataset_counts': {'upstream_observations': len(upstream['rows']),
                               'conversion_observations': len(conversion['rows'])},
            'limitations': ['Not a signed final release', 'No scientific completeness certification',
                            'No production migration or deployment performed',
                            'Team review and source/model gaps remain open']}


def main():
    result = inspect(ROOT)
    out = ROOT/'build/release-candidate'
    out.mkdir(parents=True, exist_ok=True)
    body = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
    (out/'manifest.json').write_text(body, encoding='utf8')
    (ROOT/'evidence/release-consistency.json').write_text(body, encoding='utf8')
    print(json.dumps({'passed': result['passed'], 'checks': len(result['checks']),
                      'failed': [c['check'] for c in result['checks'] if not c['passed']]}))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
