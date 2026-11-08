"""Bounded localhost load probe. Never targets production or writes feedback."""
import argparse
import json
import math
import subprocess
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]


def memory(port):
    command = (f'$listener=Get-NetTCPConnection -State Listen -LocalPort {port} | Select-Object -First 1; '
               '$process=Get-Process -Id $listener.OwningProcess; '
               '$process | Select-Object Id,WorkingSet64,PeakWorkingSet64,CPU | ConvertTo-Json -Compress')
    shell = shutil.which('pwsh') or 'C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
    result = subprocess.run([shell,'-NoProfile','-Command',command],capture_output=True,timeout=15)
    return json.loads(result.stdout) if result.returncode == 0 else {'unavailable':True}


def request(port, index):
    if port == 8765:
        path,expected = [('/api/records?product=production-oil&year=2024',200),('/api/nso',200),
            ('/api/export?product=production-oil&year=2024&status=eligible',200),('/api/export',400)][index % 4]
        req = Request(f'http://127.0.0.1:{port}' + path)
    else:
        path = '/ask'; expected = 200
        question = 'E20 N2O cold start เท่าไร' if index % 2 else 'หน่วยหน้าที่ของ FAME คืออะไร'
        req = Request(f'http://127.0.0.1:{port}' + path, data=json.dumps({'question':question}).encode(),
                      headers={'Content-Type':'application/json','Origin':f'http://127.0.0.1:{port}'})
    start = time.perf_counter(); correct = True; size = 0
    try:
        with urlopen(req,timeout=15) as response:
            body = response.read(); status = response.status; size = len(body)
            if port == 8767:
                result = json.loads(body)
                correct = (result['hits'] == []) if index % 2 else result['hits'][0]['id'] == 'fame-functional-unit'
    except HTTPError as error: status = error.code; size = len(error.read())
    except (OSError,ValueError,KeyError,IndexError): status = 0; correct = False
    return {'ms':(time.perf_counter()-start)*1000,'status':status,'passed':status == expected and correct,'bytes':size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label',default='current',choices=('before','after','current','tuned','final',
        'performance-baseline','performance-fixed','performance-confirmation'))
    args = parser.parse_args(); results = []
    for port in (8765,8767):
        for concurrency in (1,4,8):
            before = memory(port); start = time.perf_counter()
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                rows = list(pool.map(lambda index:request(port,index),range(24)))
            elapsed = time.perf_counter()-start; after = memory(port)
            values = sorted(r['ms'] for r in rows)
            results.append({'port':port,'concurrency':concurrency,'requests':len(rows),
                'passed':sum(r['passed'] for r in rows),'status_counts':{str(code):sum(r['status']==code for r in rows) for code in sorted({r['status'] for r in rows})},
                'p50_ms':round(values[math.ceil(len(values)*.5)-1],2),'p95_ms':round(values[math.ceil(len(values)*.95)-1],2),
                'elapsed_seconds':round(elapsed,3),'requests_per_second':round(len(rows)/elapsed,2),
                'server_memory_before':before,'server_memory_after':after})
    report = {'checked_at_utc':datetime.now(timezone.utc).isoformat(),'label':args.label,'results':results,
              'scope':'BOUNDED_LOCALHOST_LOAD_NOT_PRODUCTION_CAPACITY','limits':[
                  '24 requests per concurrency level per service; warm caches and this machine only.',
                  'PeakWorkingSet64 is the server process lifetime peak, not a phase-exclusive allocation measurement.',
                  'RAG prototype processes requests serially; this checks queued requests, not parallel inference.',
                  'No valid human feedback, Gemini request or production request submitted.']}
    path = ROOT/'evidence'/f'local-load-{args.label}-2026-11-08.json'
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    if any(r['passed']!=r['requests'] for r in results): raise SystemExit(1)


if __name__=='__main__':main()
