"""Compare a trusted pre-change Explorer source with current code on the same local data.

The --baseline file is Python source and is executed: use only the team's saved source.
No acquisition, production request, data mutation or persistent cache is used.
"""
import argparse
import cProfile
import hashlib
import json
import math
import pstats
import statistics
import sys
import time
import types
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src import explorer
from audit_local_query_plans import fingerprint


def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()


def invoke(module,kind):
    params={'product':'production-oil','year':'2024'}
    if kind=='records':return module.records(params)
    if kind=='export_filtered':return module.csv_export(module.records(params,export=True))
    try:module.records({},export=True)
    except ValueError as error:return str(error)
    raise ValueError('Broad export unexpectedly allowed')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',required=True,type=Path)
    args=parser.parse_args()
    if explorer.mysql_store.enabled():raise ValueError('Local SQLite comparison only')
    source=args.baseline.read_bytes()
    before=types.ModuleType('src.explorer_baseline')
    before.__package__='src';before.__file__=str(ROOT/'src/explorer.py')
    exec(compile(source,str(args.baseline),'exec'),before.__dict__)
    run,con=explorer.database()
    try:
        initial_hash=fingerprint(con)
        contexts=con.execute('SELECT DISTINCT package,year_ce FROM candidate ORDER BY package,year_ce').fetchall()
        expected_rows=con.execute('SELECT COUNT(*) FROM candidate').fetchone()[0]
    finally:con.close()
    digest=hashlib.sha256();csv_digest=hashlib.sha256();total=0
    for package,year in contexts:
        params={'product':package,'year':str(year),'status':'all'}
        old=before.records(params,export=True);new=explorer.records(params,export=True)
        if old!=new:raise ValueError('API rows or their order changed')
        old_csv=before.csv_export(old);new_csv=explorer.csv_export(new)
        if old_csv!=new_csv:raise ValueError('CSV bytes changed')
        digest.update(encoded([package,year,new]));csv_digest.update(new_csv);total+=len(new)
    if total!=expected_rows:raise ValueError('All-record parity did not cover the full candidate table')
    pages=[]
    for params in ({},{'page':'2'},{'product':'production-natural-gas','year':'2026'},
                   {'status':'HOLD_CONFLICT'},{'status':'EXCLUDE_EXACT_COPY'},
                   {'q':"' OR 1=1 --"},{'q':'%_!'}):
        if before.records(params)!=explorer.records(params):raise ValueError('Page parity changed')
        pages.append(params)
    results=[]
    for label,module in [('before',before),('after',explorer)]:
        for kind in ('records','export_filtered','export_broad_rejected'):
            profile=cProfile.Profile();profile.enable()
            for _ in range(8):invoke(module,kind)
            profile.disable()
            entries=[]
            # pstats keeps function timing without serializing raw records or paths.
            for (filename,line,function),(primitive,calls,own,cumulative,callers) in pstats.Stats(profile).stats.items():
                entries.append({'file':Path(filename).name,'line':line,'function':function,
                                'calls':calls,'own_ms':round(own*1000,3),'cumulative_ms':round(cumulative*1000,3)})
            timings=[]
            for concurrency in (1,8):
                def timed(_):
                    start=time.perf_counter();invoke(module,kind)
                    return (time.perf_counter()-start)*1000
                with ThreadPoolExecutor(max_workers=concurrency) as pool:
                    values=sorted(pool.map(timed,range(24)))
                timings.append({'concurrency':concurrency,'requests':24,
                                'p50_ms':round(statistics.median(values),3),
                                'p95_ms':round(values[math.ceil(len(values)*.95)-1],3)})
            results.append({'version':label,'operation':kind,'profile_repetitions':8,
                            'top_cumulative':sorted(entries,key=lambda e:-e['cumulative_ms'])[:8],'timings':timings})
    _,con=explorer.database()
    try:
        if fingerprint(con)!=initial_hash:raise ValueError('Source data changed during comparison')
    finally:con.close()
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'SAME_MACHINE_LOCAL_FUNCTION_COMPARISON_NOT_PRODUCTION_CAPACITY',
            'baseline_code_sha256':hashlib.sha256(source).hexdigest(),
            'current_code_sha256':hashlib.sha256((ROOT/'src/explorer.py').read_bytes()).hexdigest(),
            'run_id':run,'data_sha256_before_and_after':initial_hash,
            'all_candidate_rows_compared':total,'export_partitions_compared':len(contexts),
            'api_projection_sha256':digest.hexdigest(),'csv_projection_sha256':csv_digest.hexdigest(),
            'page_cases_compared':pages,'results':results,'passed':True,
            'limits':['Same process/machine and warm local data; before is measured first, not a randomized trial.',
                      'All-record parity covers API/CSV projection, not independent scientific validation.',
                      'Read the separate HTTP load evidence before claiming end-to-end improvements.']}
    (ROOT/'evidence/explorer-performance-fix-2026-11-08.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False))
    for result in results:print(result['version'],result['operation'],result['timings'])


if __name__=='__main__':main()
