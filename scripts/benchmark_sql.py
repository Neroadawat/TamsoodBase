"""Read-only SQL plan measurements over real local data, excluding Docker overhead."""
import hashlib
import json
import re
import statistics
import subprocess
from datetime import datetime,timezone
from pathlib import Path

if __package__:
    from .mysql_workspace import ROOT,CONFIG,NAME,OWNER
else:
    from mysql_workspace import ROOT,CONFIG,NAME,OWNER


def root_time(plan):
    match=re.search(r'actual time=([0-9.eE+-]+)\.\.([0-9.eE+-]+) rows=([0-9.eE+-]+) loops=(\d+)',plan)
    if not match: raise ValueError('Actual server timing not found in EXPLAIN ANALYZE')
    return float(match[2])


def benchmark():
    config=json.loads(CONFIG.read_text());password=config['password']
    info=subprocess.run(['docker','inspect',NAME],capture_output=True,check=True)
    details=json.loads(info.stdout)[0]
    if (details['Config']['Labels'] or {}).get('org.tamsood.workspace')!=OWNER or config['owner']!=OWNER:
        raise RuntimeError('Not the owned workspace')
    def query(sql):
        command=['docker','exec','-i','-e','MYSQL_PWD='+password,NAME,'mysql','-h127.0.0.1','--protocol=TCP',
                 '-uroot','--default-character-set=utf8mb4','--batch','--raw','--skip-column-names']
        result=subprocess.run(command,input=sql.encode('utf-8'),capture_output=True,timeout=60)
        if result.returncode: raise RuntimeError(result.stderr.decode(errors='replace').replace(password,'[redacted]'))
        return result.stdout.decode('utf-8').strip()
    period='2026-01-01'
    projection='snapshot_id,source_line,context_id,amount'
    queries={
        'optimizer_choice':f"SELECT {projection} FROM tamsood_research.observation WHERE period_start='{period}'",
        'period_index_ignored':f"SELECT {projection} FROM tamsood_research.observation IGNORE INDEX(ix_period_context) WHERE period_start='{period}'"}
    results={name:query(sql+';').splitlines() for name,sql in queries.items()}
    if sorted(results['optimizer_choice'])!=sorted(results['period_index_ignored']): raise RuntimeError('Query results differ')
    plans={name:[] for name in queries};times={name:[] for name in queries}
    # Warm both variants once. Alternate measurement order to reduce order bias.
    for sql in queries.values(): query('EXPLAIN ANALYZE '+sql+';')
    names=list(queries)
    for iteration in range(5):
        for name in names if iteration%2==0 else reversed(names):
            plan=query('EXPLAIN ANALYZE '+queries[name]+';');plans[name].append(plan);times[name].append(root_time(plan))
    release=json.loads((ROOT/'build/reusable/manifest.json').read_text(encoding='utf-8'))['release_id']
    if not re.fullmatch('[0-9a-f]{64}',release): raise ValueError('Invalid release ID')
    reference_query="SELECT publisher,label,reference_year,scaled_amount,unit_code FROM tamsood_reusable.accepted_reference WHERE release_id='"+release+"' AND reference_year=2024 AND data_kind='REPORTED_INTENSITY'"
    reference_result=query(reference_query+';').splitlines()
    reference_plan=query('EXPLAIN ANALYZE '+reference_query+';')
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'server_version':query('SELECT VERSION();'),
        'dmf_stored_observations':int(query('SELECT COUNT(*) FROM tamsood_research.observation;')),
        'workload':'Period lookup over stored DMF observations; no amount aggregation',
        'period':period,'result_rows':len(results['optimizer_choice']),'equal_results':True,
        'result_sha256':hashlib.sha256('\n'.join(sorted(results['optimizer_choice'])).encode()).hexdigest(),
        'measurement':'EXPLAIN ANALYZE root iterator actual end time, milliseconds; Docker/client latency excluded',
        'repetitions':5,'warmup_per_variant':1,'order':'alternating',
        'variants':{name:{'sql':queries[name],'server_ms':times[name],'median_server_ms':statistics.median(times[name]),'plan':plans[name][-1]} for name in queries},
        'reference_use_case':{'release_id':release,'sql':reference_query,'result_rows':len(reference_result),'plan':reference_plan},
        'limits':['Local warm-cache sample, not a production latency guarantee',
            'Ignoring the period index is a controlled baseline, not a schema migration',
            'Small reference tables may correctly use table scans','Timings do not validate source data or LCI semantics']}
    target=ROOT/'evidence/sql-performance.json';target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('server_version','dmf_stored_observations','result_rows','equal_results')},indent=2))
    print(json.dumps({name:r['median_server_ms'] for name,r in report['variants'].items()},indent=2))


if __name__=='__main__': benchmark()
