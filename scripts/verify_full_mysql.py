"""Exercise full MySQL import twice and compare every numeric/raw row."""
import hashlib
import json
import os
import secrets
import sqlite3
import subprocess
import time
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def verify():
    name='tamsood-full-check-'+secrets.token_hex(5);password=secrets.token_urlsafe(24)
    env=os.environ|{'MYSQL_ROOT_PASSWORD':password}
    expected=json.loads((ROOT/'build/full-mysql-expected.json').read_text())
    data=(ROOT/'build/full-mysql.sql').read_bytes()
    schema=(ROOT/'sql/mysql/full-schema.sql').read_bytes()

    def docker(*args,input=None,check=True,timeout=180):
        result=subprocess.run(['docker',*args],input=input,capture_output=True,env=env,timeout=timeout)
        if check and result.returncode:
            raise RuntimeError(result.stderr.decode('utf-8',errors='replace').replace(password,'[redacted]'))
        return result

    def query(sql,check=True):
        return docker('exec','-i','-e','MYSQL_PWD='+password,name,'mysql','-h127.0.0.1','--protocol=TCP',
            '-uroot','--default-character-set=utf8mb4','--batch','--skip-column-names','--raw',
            input=sql.encode('utf-8') if isinstance(sql,str) else sql,check=check)

    started=False
    try:
        docker('run','--pull=never','--detach','--name',name,'--network','none','-e','MYSQL_ROOT_PASSWORD','mysql:8.1')
        started=True;deadline=time.monotonic()+100
        while query('SELECT 1;',False).returncode:
            if time.monotonic()>deadline: raise RuntimeError('MySQL readiness timed out')
            time.sleep(2)
        query(schema)
        for attempt in (1,2):
            before=time.perf_counter();query(data);print(f'Full import {attempt}: passed ({time.perf_counter()-before:.2f}s)',flush=True)
        output=query('USE tamsood_research; SELECT snapshot_id,source_line,amount,status FROM observation JOIN duplicate_disposition USING(snapshot_id,source_line) ORDER BY snapshot_id,source_line;').stdout.decode('utf-8')
        actual={}
        for line in output.splitlines():
            sid,line_no,amount,status=line.split('\t');actual[(sid,int(line_no))]=(Decimal(amount),status)
        expected_rows={(sid,line):(Decimal(amount),status) for sid,line,amount,status in expected['rows']}
        if actual!=expected_rows: raise AssertionError('Full numeric/disposition round-trip mismatch')
        run=expected['run_id']
        con=sqlite3.connect(ROOT/'build/dmf'/run/'candidates.sqlite');con.row_factory=sqlite3.Row
        manifest=json.loads((ROOT/'data/raw/dmf'/run/'manifest.json').read_text(encoding='utf-8'))
        snapshots={hashlib.sha256((e['package']+e['csv_sha256']+e['metadata_sha256']).encode()).hexdigest():e['package'] for e in manifest['packages']}
        original={(r['package'],r['source_line']):json.loads(r['raw_json']) for r in con.execute('SELECT * FROM staging')}
        raw_output=query('USE tamsood_research; SELECT snapshot_id,source_line,raw_json FROM source_record ORDER BY snapshot_id,source_line;').stdout.decode('utf-8')
        restored={}
        for line in raw_output.splitlines():
            sid,line_no,payload=line.split('\t',2);restored[(snapshots[sid],int(line_no))]=json.loads(payload)
        if original!=restored: raise AssertionError('Raw JSON round-trip mismatch')
        counts=query('USE tamsood_research; SELECT (SELECT COUNT(*) FROM source_record),(SELECT COUNT(*) FROM observation),(SELECT COUNT(*) FROM rejected_record),(SELECT COUNT(*) FROM deduplicated_pending);').stdout.decode().strip()
        want=f"{len(original)}\t{len(expected_rows)}\t{con.execute('SELECT COUNT(*) FROM rejected').fetchone()[0]}\t{con.execute('SELECT COUNT(*) FROM deduplicated_candidates').fetchone()[0]}"
        if counts!=want: raise AssertionError('Full import row count mismatch')
        con.close()
        failures={
            'negative_amount':("UPDATE observation SET amount=-1 LIMIT 1",'3819'),
            'invalid_production_days':("UPDATE observation SET production_days=32 LIMIT 1",'3819'),
            'unreviewed_promotion':("UPDATE observation SET review_status='ACCEPTED' LIMIT 1",'3819'),
            'guessed_time_basis':("UPDATE observation SET unit_time_basis='PER_DAY' LIMIT 1",'3819'),
            'duplicate_primary_key':('INSERT INTO observation SELECT * FROM observation LIMIT 1','1062'),
            'missing_context':("UPDATE observation SET context_id=REPEAT('f',64) LIMIT 1",'1452')}
        for label,(statement,code) in failures.items():
            result=query('USE tamsood_research; '+statement+';',False)
            if result.returncode==0 or code.encode() not in result.stderr: raise AssertionError(label+' did not fail as expected')
        query((ROOT/'sql/mysql/full-queries.sql').read_bytes())
        sample_query="SELECT COUNT(*) FROM observation WHERE period_start='2026-01-01'"
        plan=query('USE tamsood_research; EXPLAIN '+sample_query+';').stdout.decode()
        if 'ix_period_context' not in plan: raise AssertionError('Expected period index not used')
        report={'checked_at':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            'mysql_version':query('SELECT VERSION();').stdout.decode().strip(),'run_id':run,
            'source_rows_roundtrip_verified':len(original),'observation_decimals_verified':len(actual),
            'all_dispositions_verified':True,'imports_run':2,'idempotence_verified':True,
            'constraint_checks':list(failures),'indexed_period_query_plan':plan.strip(),
            'export_sql_sha256':hashlib.sha256(data).hexdigest(),'schema_sha256':hashlib.sha256(schema).hexdigest(),
            'competition_accepted':0,'limitations':['Source numerical accuracy not certified by storage round-trip','LCI eligibility and historical time basis pending']}
        (ROOT/'build/full-mysql-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    finally:
        if started: docker('rm','--force','--volumes',name)


if __name__=='__main__': verify()
