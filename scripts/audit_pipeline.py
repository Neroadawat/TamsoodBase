"""Offline end-to-end replay. Live data stays unchanged; no acquisition or deployment."""
import argparse
from collections import Counter
from contextlib import closing, redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def keyed(rows):
    result={r['observation_id']:r for r in rows}
    if len(result)!=len(rows):raise ValueError('Duplicate observation identity')
    return result


def require(condition, message):
    if not condition:raise ValueError(message)


def replay_dmf(root):
    from src import process_dmf, review_dmf
    run=json.loads((root/'data/raw/dmf/latest.json').read_text())['run_id']
    require(isinstance(run,str) and bool(run) and '/' not in run and '\\' not in run and run not in ('.','..'),'Unsafe DMF run ID')
    raw=root/'data/raw/dmf'/run
    manifest=process_dmf.validate_snapshot(raw,run)
    original=root/'build/dmf'/run/'candidates.sqlite'
    before=digest(original)
    with tempfile.TemporaryDirectory(prefix='tamsood-audit-') as tmp:
        temporary=Path(tmp)
        shutil.copytree(raw,temporary/'data/raw/dmf'/run)
        shutil.copyfile(root/'data/raw/dmf/latest.json',temporary/'data/raw/dmf/latest.json')
        (temporary/'evidence').mkdir()
        shutil.copyfile(root/'evidence/dmf-report-2026-01-sample.json',temporary/'evidence/dmf-report-2026-01-sample.json')
        with patch.object(process_dmf,'ROOT',temporary), patch.object(review_dmf,'ROOT',temporary), redirect_stdout(io.StringIO()):
            quality=process_dmf.process(run)
            review=review_dmf.review()
        counts={}
        with closing(sqlite3.connect(original.resolve().as_uri()+'?mode=ro',uri=True)) as live, closing(sqlite3.connect(temporary/'build/dmf'/run/'candidates.sqlite')) as replay:
            for table in ('resource','staging','candidate','rejected','duplicate_disposition'):
                expected=sorted(live.execute('SELECT * FROM '+table).fetchall())
                actual=sorted(replay.execute('SELECT * FROM '+table).fetchall())
                require(expected==actual, 'DMF replay differs: '+table)
                counts[table]=len(actual)
            require(not replay.execute('PRAGMA foreign_key_check').fetchall(),'DMF replay foreign keys')
        for name, actual in (('quality-report.json',quality),('review-report.json',review)):
            expected=json.loads((root/'build/dmf'/run/name).read_text(encoding='utf-8'))
            require(expected==actual,'DMF '+name+' differs')
    require(before==digest(original),'Live DMF database changed')
    return dict(run_id=run,source_packages=len(manifest['packages']),table_counts=counts,
        full_row_and_report_equality=True,live_database_unchanged=True,
        pending_after_deduplication=review['deduplicated_candidates_pending_review'])


def replay_sources(root):
    from scripts.import_nso import parse as parse_nso, TABLES, BASE
    from scripts.import_eppo import parse as parse_eppo, SPECS
    from scripts.build_product_inventory import extract
    from scripts.review_nso import totals
    reports={name:json.loads((root/'build'/folder/'report.json').read_text(encoding='utf-8')) for name,folder in
             [('nso','nso'),('eppo','eppo'),('inventory','product-inventory')]}
    rows=[]
    for table in TABLES:
        body=(root/f'data/raw/nso/yearbook-2026/T_{table}_2026.csv').read_bytes()
        rows.extend(parse_nso(body,table,BASE+f'File_SYB/2026/13/T_{table}_2026.csv'))
    require(keyed(rows)==keyed(reports['nso']['rows']),'NSO source-to-report replay differs')
    checks=totals(rows)
    require(all(c['passed'] for c in checks),'NSO additive checks failed')
    manifest=json.loads((root/'data/raw/eppo/manifest.json').read_text(encoding='utf-8'))
    eppo=[]
    for dataset in SPECS:
        source=manifest['resources'][dataset]
        eppo.extend(parse_eppo((root/'data/raw/eppo'/source['filename']).read_bytes(),dataset,source))
    require(keyed(eppo)==keyed(reports['eppo']['rows']),'EPPO source-to-report replay differs')
    raw=root/'data/raw/mdpi-9415'
    body=(raw/'table4-dom.json').read_bytes()
    inventory,excluded=extract(json.loads(body),(raw/'article-visible.txt').read_text(encoding='utf-8'),hashlib.sha256(body).hexdigest())
    require(keyed(inventory)==keyed(reports['inventory']['rows']),'Inventory source-to-report replay differs')
    require(keyed(excluded)==keyed(reports['inventory']['excluded_rows']),'Inventory excluded-cell replay differs')
    return dict(nso=len(rows),nso_additive_checks=len(checks),eppo=len(eppo),
                inventory=len(inventory),excluded_inventory_cells=len(excluded),full_source_report_payload_equality=True)


def check_reference(root, pdf=False):
    from scripts.reference_scorecard import measure
    from src import reusable_api
    from src.wsgi import readiness
    from src import explorer
    folder=root/'build/reusable'
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    rows=json.loads((folder/'all-reference.json').read_text(encoding='utf-8'))
    require(measure(rows,manifest)['passed'],'Corporate scorecard failed')
    with patch.object(reusable_api,'ROOT',root):
        actual=reusable_api.catalog({'decision':'all'},export=True)
        require(keyed(actual['rows'])==keyed(rows),'Reference API export differs from all-reference artifact')
        count=reusable_api.catalog({})['total']
        require(count==manifest['accepted_reference'],'Default reference count differs')
        require(reusable_api.catalog({'decision':'HOLD_CONTEXT'})['total']==manifest['held_context'],'Held count differs')
    with patch.object(explorer,'ROOT',root):require(readiness(),'Backend readiness failed')
    traced=0
    if pdf:
        from src import trace_report
        with patch.object(trace_report,'ROOT',root):
            for source,(folder_name,_) in trace_report.SOURCES.items():
                report=json.loads((root/'build'/folder_name/'report.json').read_text(encoding='utf-8'))
                for row in report['rows']:
                    trace_report.trace(source,row['metric_id'],row['year'])
                    traced+=1
    return dict(release_id=manifest['release_id'],source_observations=len(rows),accepted_reference=count,
                held_context=manifest['held_context'],full_api_export_equal=True,
                pdf_records_reextracted=traced,pdf_reextraction_requested=pdf,backend_ready=True)


def audit(root=ROOT, pdf=False):
    from scripts.audit_dataset_layers import audit_layers
    stages=[]
    for name,work in [('dmf_full_replay',lambda:replay_dmf(root)),
                      ('source_report_replay',lambda:replay_sources(root)),
                      ('reference_api_and_pdf',lambda:check_reference(root,pdf)),
                      ('typed_database_layers',lambda:audit_layers(root))]:
        print('Checking '+name+'...',flush=True)
        try:
            detail=work()
            if isinstance(detail,list):require(all(c['passed'] for c in detail),'Dataset layer checks failed')
            stages.append(dict(stage=name,passed=True,detail=detail))
        except Exception as error:
            stages.append(dict(stage=name,passed=False,error=type(error).__name__+': '+str(error)))
    return dict(checked_at=datetime.now(timezone.utc).isoformat(),passed=all(s['passed'] for s in stages),stages=stages,
        implementation_sha256={p:digest(root/p) for p in ['src/process_dmf.py','scripts/audit_dataset_layers.py','scripts/audit_pipeline.py','src/wsgi.py']},
        limitations=['Offline parser replay checks reproducibility, not independent publisher measurement accuracy',
                     'PDF re-extraction is optional and its actual count is recorded',
                     'No live MySQL, remote EC2, S3, human contribution or public deployment is certified by this audit',
                     'ACCEPTED_REFERENCE remains separate from normalized LCI; rights statuses are unchanged'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pdf',action='store_true');args=parser.parse_args()
    result=audit(pdf=args.pdf)
    target=ROOT/'evidence/pipeline-audit.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
