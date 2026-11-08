"""Measure actual Explorer queries in an isolated SQLite copy before adding indexes."""
import hashlib
import json
import sqlite3
import statistics
import sys
import tempfile
import time
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.explorer import FIELDS, FROM, selection
from src.explorer_indexes import INDEX_SQL


def fingerprint(con):
    digest=hashlib.sha256()
    for table in ('resource','staging','candidate','rejected','duplicate_disposition'):
        order='package' if table=='resource' else 'package,source_line'
        for row in con.execute('SELECT * FROM '+table+' ORDER BY '+order):
            digest.update(json.dumps([table,*row],ensure_ascii=False,separators=(',',':')).encode())
    return digest.hexdigest()


def measured(con, statement, values):
    rows=con.execute(statement,values).fetchall();times=[]
    for _ in range(25):
        start=time.perf_counter();actual=con.execute(statement,values).fetchall()
        times.append((time.perf_counter()-start)*1000)
        if actual!=rows:raise ValueError('Nondeterministic query result')
    return rows,{'median_ms':round(statistics.median(times),3),'rows':len(rows),
                 'plan':[r[3] for r in con.execute('EXPLAIN QUERY PLAN '+statement,values)]}


def main():
    run=json.loads((ROOT/'data/raw/dmf/latest.json').read_bytes())['run_id']
    database=ROOT/'build/dmf'/run/'candidates.sqlite'
    parent=ROOT/'build/handoff';parent.mkdir(parents=True,exist_ok=True)
    queries=[]
    for label,params,export in [('page_all',{},False),('page_year_product',{'product':'production-oil','year':'2024'},False),
                                ('export_filtered',{'product':'production-oil','year':'2024'},True)]:
        where,values=selection(params)
        order='c.package,c.year_ce DESC,c.month DESC,c.source_line' if export else 'c.year_ce DESC,c.month DESC,c.package,c.source_line'
        queries.append((label,'SELECT '+FIELDS+FROM+where+' ORDER BY '+order+' LIMIT ?',values+[5001 if export else 30]))
    with closing(sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)) as original:
        before_hash=fingerprint(original)
        with tempfile.TemporaryDirectory(prefix='query-plans-',dir=parent) as temporary:
            directory=Path(temporary).resolve()
            if not directory.is_relative_to(parent.resolve()):raise ValueError('Unexpected temporary directory')
            with closing(sqlite3.connect(directory/'copy.sqlite')) as copy:
                original.backup(copy)
                # Make repeat runs comparable after the real database already has these indexes.
                # Drop only this audit's indexes, and only in the disposable copy.
                for name in ('ix_candidate_recent','ix_candidate_package_recent','ix_candidate_identity'):
                    copy.execute('DROP INDEX IF EXISTS '+name)
                copy.commit()
                baseline={name:measured(copy,statement,values) for name,statement,values in queries}
                for statement in INDEX_SQL:copy.execute(statement)
                copy.commit()
                checks=[]
                for name,statement,values in queries:
                    rows,after=measured(copy,statement,values);prior,stats=baseline[name]
                    if rows!=prior:raise ValueError('Indexed query changed selected rows/order')
                    checks.append({'query':name,'before':stats,'after':after,'rows_identical':True})
                if fingerprint(copy)!=before_hash:raise ValueError('Index creation changed data')
    # Only verified index DDL is applied; no record UPDATE/DELETE or production connection.
    with closing(sqlite3.connect(database)) as con:
        if fingerprint(con)!=before_hash:raise ValueError('Data changed concurrently; do not apply')
        for statement in INDEX_SQL:con.execute(statement)
        con.commit()
        if fingerprint(con)!=before_hash or con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
            raise ValueError('Post-index integrity differs')
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'LOCAL_SQLITE_QUERY_PLANS_NOT_PRODUCTION',
            'database':database.relative_to(ROOT).as_posix(),'data_sha256_before_and_after':before_hash,
            'statements':list(INDEX_SQL),'checks':checks,'original_records_unchanged':True,
            'applied_to_local_database':True,'production_changed':False,'passed':True,
            'limits':['25 repetitions per query on a warm local copy; no universal performance claim.']}
    (ROOT/'evidence/local-query-plans-2026-11-08.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
