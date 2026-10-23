"""Audit current technical artifacts separately from the unresolved final gates."""
import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import zipfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_files(root):
    # An explicit allowlist prevents .local, raw PDFs, .env and generated DBs leaking.
    allowed={'.py','.md','.json','.sql','.csv'}
    paths=[root/'README.md',root/'.gitignore',root/'requirements-report.txt']
    for directory in ('src','scripts','tests','docs','sql','evidence','examples','.vscode'):
        paths.extend(p for p in (root/directory).rglob('*') if p.is_file() and p.suffix in allowed
                     and not p.is_symlink() and p.resolve().is_relative_to(root.resolve()))
    return sorted(set(p for p in paths if p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root.resolve())))


def audit(run_tests=False,package=False):
    checks=[]
    def check(name,ok,detail): checks.append({'name':name,'passed':bool(ok),'detail':detail})
    for filename in ('README.md','docs/tasks.json','docs/acceptance-rules.md','docs/domain-review-packet.md',
                     'docs/database-design.md','docs/data-dictionary.md','sql/mysql/full-schema.sql'):
        check('artifact:'+filename,(ROOT/filename).is_file(),filename)
    try:
        run=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
        raw=ROOT/'data/raw/dmf'/run;manifest=json.loads((raw/'manifest.json').read_text(encoding='utf-8'))
        for item in manifest['packages']:
            for suffix,key in [('.csv','csv_sha256'),('.metadata.json','metadata_sha256')]:
                check('hash:'+item['package']+suffix,digest(raw/(item['package']+suffix))==item[key],item[key])
        with sqlite3.connect((ROOT/'build/dmf'/run/'candidates.sqlite').as_uri()+'?mode=ro',uri=True) as con:
            check('sqlite_integrity',con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite')
            check('sqlite_foreign_keys',not con.execute('PRAGMA foreign_key_check').fetchall(),'SQLite')
            counts={table:con.execute('SELECT COUNT(*) FROM '+table).fetchone()[0] for table in ('staging','candidate','rejected','duplicate_disposition')}
            check('dmf_row_accounting',counts['staging']==counts['candidate']+counts['rejected'] and counts['candidate']==counts['duplicate_disposition'],counts)
    except (OSError,ValueError,KeyError,sqlite3.Error) as error: check('dmf_available',False,str(error))
    for folder_name,publisher in [('report-pilot','thaioil'),('sprc-report','sprc')]:
        try:
            folder=ROOT/'build'/folder_name;r=json.loads((folder/'report.json').read_text(encoding='utf-8'))
            check('report_hash:'+publisher,digest(ROOT/'data/raw'/publisher/'2024/sustainability-report.pdf')==r['pdf_sha256'],r['pdf_sha256'])
            identities={(row['metric_id'],row['year']) for row in r['rows']}
            check('report_identity:'+publisher,len(identities)==len(r['rows'])==r['row_count'],r['row_count'])
            check('report_no_promotion:'+publisher,r['competition_accepted']==0 and all(not row['competition_accepted'] for row in r['rows']),'Pending review')
            verification=json.loads((folder/'mysql-verification.json').read_text())
            check('report_mysql_evidence:'+publisher,verification['pdf_sha256']==r['pdf_sha256'] and verification.get('report_json_sha256')==digest(folder/'report.json') and verification['numeric_values_checked']==len(r['rows']) and verification.get('metadata_records_checked')==len(r['rows']) and verification['result']=='passed','Stored verification tied to report hash; not a live MySQL query')
        except (OSError,ValueError,KeyError) as error: check('report_available:'+publisher,False,str(error))
    tasks=json.loads((ROOT/'docs/tasks.json').read_text(encoding='utf-8'))['tasks'];ids={task['id'] for task in tasks}
    try:
        folder=ROOT/'build/reusable';manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        check('reference_policy_hash',digest(ROOT/'docs/team-data-policy.md')==manifest['policy_sha256'],'Team-defined use case, no external approval required')
        check('reference_schema_hash',digest(ROOT/'sql/mysql/reusable-schema.sql')==manifest['schema_sha256'],'Typed relational schema')
        for name,expected in manifest['implementation_sha256'].items(): check('reference_implementation:'+name,digest(ROOT/'src'/name)==expected,expected)
        for name,expected in manifest['files'].items(): check('reference_artifact:'+name,digest(folder/name)==expected,expected)
        verification=json.loads((folder/'mysql-verification.json').read_text())
        check('reference_mysql_roundtrip',verification['release_id']==manifest['release_id'] and verification['records_checked']==manifest['source_observations'] and verification['export_manifest_sha256']==digest(folder/'manifest.json') and verification['result']=='passed','Current release verified against MySQL')
        restored=json.loads((ROOT/'evidence/reference-package-verification.json').read_text())
        check('reference_package_restore',restored['release_id']==manifest['release_id'] and restored['package_sha256']==digest(folder/'reference-data-local.zip') and restored['result']=='passed' and restored.get('mysql_clean_restore',{}).get('result')=='passed','Isolated client + fresh MySQL database restore; not a fresh OS install')
    except (OSError,ValueError,KeyError) as error: check('reference_release_available',False,str(error))
    check('task_dependencies',len(ids)==len(tasks) and all(set(t['dependencies'])<=ids for t in tasks),'Unique task IDs and known dependencies')
    if run_tests:
        result=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        log=ROOT/'build/release-tests.log';log.parent.mkdir(exist_ok=True);log.write_text(result.stdout+result.stderr,encoding='utf-8')
        check('tests',result.returncode==0,'See build/release-tests.log')
    gates=json.loads((ROOT/'docs/review-decisions.json').read_text(encoding='utf-8'))['gates']
    unresolved=[g for g in gates if g['status']!='VERIFIED' or not g['evidence']
                or any(not (ROOT/p).is_file() or not (ROOT/p).resolve().is_relative_to(ROOT.resolve()) for p in g['evidence'])]
    files=selected_files(ROOT)
    manifest={'scope':'INTERNAL_REVIEW_CODE_DOCS_EVIDENCE_ONLY','contains_raw_data':False,
       'files':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':digest(p),'bytes':p.stat().st_size} for p in files]}
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'technical_pass':all(c['passed'] for c in checks),
        'reference_release_ready':all(c['passed'] for c in checks if c['name'].startswith('reference_')),
        'submission_ready':all(c['passed'] for c in checks) and not unresolved,'checks':checks,
        'unresolved_gates':unresolved,'competition_accepted':0,'manifest_file_count':len(files),
        'note':'Technical pass does not verify external source accuracy, licensing or MTEC acceptance'}
    out=ROOT/'build/release';out.mkdir(parents=True,exist_ok=True)
    (out/'readiness.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    if package:
        if not report['technical_pass']: raise RuntimeError('Technical audit failed; package not created')
        with zipfile.ZipFile(out/'internal-review.zip','w',zipfile.ZIP_DEFLATED) as archive:
            for path in files: archive.write(path,str(path.relative_to(ROOT)))
            archive.write(out/'source-manifest.json','source-manifest.json')
            archive.write(out/'readiness.json','readiness.json')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False,indent=2))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--tests',action='store_true');parser.add_argument('--package',action='store_true');args=parser.parse_args()
    result=audit(args.tests,args.package)
    if not result['technical_pass']: sys.exit(1)
