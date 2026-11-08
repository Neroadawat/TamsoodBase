"""Restore only exact recorded public snapshots; never synthesize missing raw data."""
import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def restore_live_product(offline=False):
    from src.inventory_scope import validate_process_context
    path = ROOT / 'build/product-inventory/report.json'
    url = 'https://tamsoodbase.vercel.app/api/product-inventory'
    try:
        if path.exists(): body = path.read_bytes()
        else:
            if offline:return {'restored':False,'status':'MISSING_CACHED_API_COPY_OFFLINE'}
            with urlopen(url, timeout=20) as response: body = response.read(2_000_001)
        report = json.loads(body)
        recorded = json.loads((ROOT / 'evidence/product-inventory.json').read_bytes())
        if len(body) > 2_000_000: raise ValueError('Response too large')
        for key in ('doi', 'source_snapshot_sha256', 'context_sha256', 'source_reported_inventory_count', 'excluded_count'):
            if report[key] != recorded[key]: raise ValueError('Source metadata differs')
        validate_process_context(report['rows'])
        if len(report['rows']) != 16 or any(r['licence'] != 'CC BY 4.0' or r['data_period'] is not None for r in report['rows']):
            raise ValueError('Unexpected inventory scope')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists(): path.write_bytes(body)
        return {'restored': True, 'rows': 16, 'api_url': url, 'response_sha256': hashlib.sha256(body).hexdigest(),
                'restoration_kind': 'VALIDATED_LIVE_API_COPY_NOT_ORIGINAL_DOM_REPLAY'}
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {'restored': False, 'error_type': type(error).__name__}


def corporate_cache():
    folder=ROOT/'build/reusable'
    try:
        manifest=json.loads((folder/'manifest.json').read_bytes())
        if (manifest['source_observations'],manifest['accepted_reference'],manifest['held_context'],manifest['reextracted_pdf_records'])!=(101,97,4,101):return None
        if manifest['redistribution_status']!='NOT_CLEARED' or manifest['normalized_lci_exchanges']!=0:return None
        if hashlib.sha256((ROOT/'docs/team-data-policy.md').read_bytes()).hexdigest()!=manifest['policy_sha256']:return None
        if hashlib.sha256((ROOT/'sql/mysql/reusable-schema.sql').read_bytes()).hexdigest()!=manifest['schema_sha256']:return None
        if set(manifest['implementation_sha256'])!={'build_reusable.py','trace_report.py','report_pilot.py','sprc_report.py'}:return None
        for name,digest in manifest['implementation_sha256'].items():
            if name not in ('build_reusable.py','trace_report.py','report_pilot.py','sprc_report.py'):return None
            if hashlib.sha256((ROOT/'src'/name).read_bytes()).hexdigest()!=digest:return None
        if set(manifest['files'])!={'accepted-reference.json','all-reference.json','accepted-reference.csv','reference.sqlite','load-mysql.sql'}:return None
        for name,digest in manifest['files'].items():
            if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=digest:return None
        with closing(sqlite3.connect((folder/'reference.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as con:
            if con.execute('PRAGMA quick_check').fetchone()[0]!='ok' or con.execute('PRAGMA foreign_key_check').fetchall():return None
            decisions=dict(con.execute('SELECT decision,COUNT(*) FROM reference_catalog GROUP BY decision'))
            if decisions!={'ACCEPTED_REFERENCE':97,'HOLD_CONTEXT':4}:return None
            if set(r[0] for r in con.execute('SELECT document_id FROM document'))!=set(manifest['source_document_hashes']):return None
            con.row_factory=sqlite3.Row
            rows=[dict(row) for row in con.execute('SELECT * FROM reference_catalog ORDER BY reference_year DESC,publisher,source_metric_id')]
            for row in rows:
                row.update(redistribution_status='NOT_CLEARED',is_normalized_lci_exchange=False,reference_product_amount=None,allocation_method=None)
            if rows!=json.loads((folder/'all-reference.json').read_bytes()):return None
        return manifest
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error):return None


def restore_corporate(offline=False,pdf_python=None):
    from scripts.acquire_thaioil import acquire
    sources={'thaioil':'thaioil-pilot-review-2026-10-22.json','sprc':'sprc-review-2026-10-22.json'}
    verified=[]
    try:
        for company,evidence in sources.items():
            recorded=json.loads((ROOT/'evidence'/evidence).read_bytes())
            folder=ROOT/'data/raw'/company/'2024';path=folder/'sustainability-report.pdf'
            if not path.exists():
                if offline:return {'restored':False,'status':'SOURCE_MISSING_OFFLINE','source':company}
                acquire(company,expected_sha256=recorded['pdf_sha256'])
            if hashlib.sha256(path.read_bytes()).hexdigest()!=recorded['pdf_sha256']:
                raise ValueError('Original Corporate source differs')
            acquisition=json.loads((folder/'manifest.json').read_bytes())
            if acquisition['sha256']!=recorded['pdf_sha256'] or acquisition['source_url']!=recorded['source_url']:
                raise ValueError('Corporate source manifest differs')
            verified.append(recorded['pdf_sha256'])
        cached=corporate_cache()
        if cached is not None and cached['source_document_hashes']==verified:
            return {'restored':True,'status':'VERIFIED_CACHED_RELEASE','release_id':cached['release_id'],
                    'rows':101,'accepted_reference':97,'held_context':4,'redistribution_status':'NOT_CLEARED'}
        command=[sys.executable,'-X','utf8',str(ROOT/'scripts/run_reference.py')]
        if pdf_python:command+=['--pdf-python',str(pdf_python)]
        completed=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=180)
        logs=ROOT/'build/handoff';logs.mkdir(parents=True,exist_ok=True)
        (logs/'prepare-corporate.log').write_bytes(completed.stdout+completed.stderr)
        cached=corporate_cache()
        if completed.returncode or cached is None or cached['source_document_hashes']!=verified:
            raise ValueError('Corporate rebuild not verified; inspect prepare-corporate.log')
        return {'restored':True,'status':'REBUILT_AND_VERIFIED','release_id':cached['release_id'],
                'rows':101,'accepted_reference':97,'held_context':4,'redistribution_status':'NOT_CLEARED'}
    except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as error:
        return {'restored':False,'status':'CORPORATE_RESTORE_FAILED','error_type':type(error).__name__}


def prepare_dmf(offline=False,acquire_if_missing=False):
    missing=not (ROOT/'data/raw/dmf/latest.json').is_file()
    if missing and (offline or not acquire_if_missing):
        return {'passed':False,'mode':'SOURCE_MISSING_NO_ACQUISITION'}
    command=[sys.executable,'-X','utf8',str(ROOT/'scripts/run_pipeline.py')]
    if missing:command.append('--acquire')
    logs=ROOT/'build/handoff';logs.mkdir(parents=True,exist_ok=True)
    try:result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=180)
    except (OSError,subprocess.TimeoutExpired) as error:
        return {'passed':False,'mode':'DMF_PREPARATION_FAILED','error_type':type(error).__name__}
    (logs/'prepare-dmf.log').write_bytes(result.stdout+result.stderr)
    return {'passed':result.returncode==0,'mode':'NEW_OFFICIAL_SNAPSHOT_REQUIRES_REVIEW' if missing else 'OFFLINE_RETAINED_SOURCE_ONLY'}


def prepare_labs(offline=False):
    folder=ROOT/'build/handoff';folder.mkdir(parents=True,exist_ok=True)
    results=[]
    if offline:
        for image in ('mysql:8.1','neo4j:5.26.32-community'):
            try:probe=subprocess.run(['docker','image','inspect',image],capture_output=True,timeout=15)
            except (OSError,subprocess.TimeoutExpired) as error:
                return {'passed':False,'status':'DOCKER_UNAVAILABLE','error_type':type(error).__name__}
            if probe.returncode:return {'passed':False,'status':'OFFLINE_IMAGE_MISSING','image':image}
    for name in ('build_handoff_store.py','verify_handoff_engines.py','verify_handoff_dmf_mysql.py','verify_handoff_corporate_mysql.py'):
        try:result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts'/name)],cwd=ROOT,capture_output=True,timeout=240)
        except (OSError,subprocess.TimeoutExpired) as error:
            results.append({'stage':name,'passed':False,'error_type':type(error).__name__});break
        (folder/('prepare-'+name+'.log')).write_bytes(result.stdout+result.stderr)
        results.append({'stage':name,'passed':result.returncode==0})
        if result.returncode:break
    return {'passed':len(results)==4 and all(r['passed'] for r in results),'stages':results,
            'scope':'OWNER_MARKED_LOCAL_LABS_ONLY_NO_PRODUCTION'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore-corporate',action='store_true',help='Fetch only recorded PDF bytes if missing, and verify/rebuild the local reference release.')
    parser.add_argument('--build-dmf',action='store_true',help='Rebuild the offline DMF pipeline from existing real raw files.')
    parser.add_argument('--acquire-dmf-if-missing',action='store_true',help='Acquire a new official DMF snapshot only if no local snapshot exists; implies --build-dmf. This is not an exact old snapshot restoration.')
    parser.add_argument('--verify-labs',action='store_true',help='Build and verify owner-marked isolated MySQL/Neo4j labs; Docker and the required images must be available.')
    parser.add_argument('--offline',action='store_true',help='Use retained source files only; do not request any network data.')
    parser.add_argument('--pdf-python',type=Path,help='Python with pypdf for Corporate extraction; otherwise use run_reference auto-detection.')
    args=parser.parse_args()
    recorded = json.loads((ROOT / 'evidence/nso-acquisition.json').read_bytes())
    target = ROOT / 'data/raw/nso/yearbook-2026'
    target.mkdir(parents=True, exist_ok=True)

    def fetch(item):
        table, source = item
        path = target / f'T_{table}_2026.csv'
        result = {'table': table, 'source_url': source['url'], 'expected_sha256': source['sha256']}
        try:
            if path.exists():
                body = path.read_bytes()
            else:
                if args.offline:
                    result.update(restored=False,status='SOURCE_MISSING_OFFLINE');return result
                with urlopen(Request(source['url'], headers={'User-Agent': 'TamsoodBase source verification'}), timeout=18) as response:
                    body = response.read(4_000_001)
            digest = hashlib.sha256(body).hexdigest()
            if len(body) > 4_000_000 or digest != source['sha256']:
                result.update(restored=False, status='HASH_OR_SIZE_MISMATCH', actual_sha256=digest)
            else:
                if not path.exists(): path.write_bytes(body)
                result.update(restored=True, status='EXACT_RECORDED_BYTES', bytes=len(body))
        except (OSError, ValueError) as error:
            result.update(restored=False, status='ACQUISITION_FAILED', error_type=type(error).__name__)
        return result

    with ThreadPoolExecutor(max_workers=5) as executor:
        checks = list(executor.map(fetch, recorded['resources'].items()))
    imported = False
    if all(c['restored'] for c in checks):
        manifest = {'acquisition_method': 'HTTP restoration checked against recorded snapshot hashes',
                    'resources': recorded['resources'],
                    'restoration_checked_at': datetime.now(timezone.utc).isoformat()}
        if not (target / 'manifest.json').exists():
            (target / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        completed = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scripts/import_nso.py')],
                                   cwd=ROOT, capture_output=True, timeout=30)
        imported = completed.returncode == 0
    # These prerequisite files are inspected only. No attempt to guess credentials.
    product = restore_live_product(args.offline)
    corporate=restore_corporate(args.offline,args.pdf_python) if args.restore_corporate else {'restored':corporate_cache() is not None,'status':'NOT_REQUESTED'}
    dmf_build=None
    if args.build_dmf or args.acquire_dmf_if_missing:
        dmf_build=prepare_dmf(args.offline,args.acquire_dmf_if_missing)
    prerequisites = {name: (ROOT / name).exists() for name in (
        'data/raw/dmf/latest.json', 'data/raw/mdpi-9415/table4-dom.json',
        'data/raw/mdpi-9415/article-visible.txt', 'build/reusable/all-reference.json',
        'build/eppo/report.json', 'build/nso/report.json', 'build/product-inventory/report.json')}
    requested_passed=imported and product['restored'] and (not args.restore_corporate or corporate['restored']) and (dmf_build is None or dmf_build['passed'])
    labs=prepare_labs(args.offline) if args.verify_labs and requested_passed else None
    if args.verify_labs:requested_passed=requested_passed and labs is not None and labs['passed']
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'nso': checks,
              'nso_imported': imported, 'product_inventory': product, 'corporate':corporate,
              'dmf_build':dmf_build,'labs':labs,'offline':args.offline,'prerequisites': prerequisites,
              'gemini_key_present':bool(os.environ.get('GEMINI_API_KEY','').strip()),'gemini_called':False,
              'dmf_pipeline_available': (ROOT / 'build/project-status.json').exists(),
              'requested_steps_passed':requested_passed,
              'full_runtime_restored': all(prerequisites.values()) and requested_passed, 'production_changed': False}
    (ROOT / 'evidence/handoff-runtime-2026-11-08.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not requested_passed:raise SystemExit(1)


if __name__ == '__main__': main()
