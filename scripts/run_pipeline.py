"""One command for the current DMF project pipeline, offline by default."""
import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(acquire=False,mysql=False):
    if not acquire and not (ROOT/'data/raw/dmf/latest.json').exists():
        raise FileNotFoundError('No local snapshot. Run: python -X utf8 scripts/run_pipeline.py --acquire')
    log_dir=ROOT/'build/pipeline-logs'
    log_dir.mkdir(parents=True,exist_ok=True)
    stages = ([('acquire','src/acquire_dmf.py')] if acquire else []) + [
        ('process','src/process_dmf.py'),('review','src/review_dmf.py'),
        ('export-mysql','src/export_full_mysql.py')]
    if mysql: stages.append(('load-mysql','scripts/mysql_workspace.py'))
    for name,path in stages:
        result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/path)],cwd=ROOT,
                              capture_output=True,text=True,encoding='utf-8')
        (log_dir/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
        if result.returncode:
            raise RuntimeError(f'{name} failed; see {log_dir/(name+".log")}')
        print(name+': passed')
    run_id=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
    output=ROOT/'build/dmf'/run_id
    quality=json.loads((output/'quality-report.json').read_text(encoding='utf-8'))
    review=json.loads((output/'review-report.json').read_text(encoding='utf-8'))
    with sqlite3.connect(output/'candidates.sqlite') as con:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or con.execute('PRAGMA foreign_key_check').fetchall():
            raise RuntimeError('SQLite integrity check failed')
        staging=con.execute('SELECT COUNT(*) FROM staging').fetchone()[0]
        candidates=con.execute('SELECT COUNT(*) FROM candidate').fetchone()[0]
        rejected=con.execute('SELECT COUNT(*) FROM rejected').fetchone()[0]
        dispositions=con.execute('SELECT COUNT(*) FROM duplicate_disposition').fetchone()[0]
        selected=con.execute('SELECT COUNT(*) FROM deduplicated_candidates').fetchone()[0]
        if not (staging==candidates+rejected==quality['raw_rows'] and dispositions==candidates
                and selected==review['deduplicated_candidates_pending_review']):
            raise RuntimeError('Row accounting failed')
    status={'checked_at':datetime.now(timezone.utc).isoformat(),'run_id':run_id,
            'original_rows':staging,'structural_pass':candidates,'rejected':rejected,
            'pending_after_duplicate_review':selected,'dispositions':review['total_row_dispositions'],
            'competition_accepted':review['competition_accepted'],
            'numeric_spotchecks':review['unit_review'],'integrity_check':'passed','row_accounting':'passed'}
    (ROOT/'build/project-status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(status,ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire',action='store_true',help='Download a new official snapshot before processing')
    parser.add_argument('--mysql',action='store_true',help='Also load the owned persistent Docker MySQL workspace')
    args=parser.parse_args();run(args.acquire,args.mysql)
