"""Compare actual WSGI responses across SQLite and isolated MySQL processes.

Write a private baseline with --baseline FILE; compare with --compare FILE.
This performs no data mutations and never prints database credentials.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from src.wsgi import application

PATHS = ['/readyz','/api/summary','/api/source-crosswalk','/api/reports',
 '/api/report-pilot','/api/nso','/api/product-inventory','/api/nso-comparison',
 '/api/records','/api/records?status=all&page=2',
 '/api/records?q=%25','/api/records?q=_','/api/records?q=!',
 '/api/record?package=production-oil&line=2',
 '/api/reference','/api/reference?page=2','/api/reference?decision=all',
 '/api/reference.json?decision=all','/api/reference.csv?decision=all',
 '/api/reference?decision=HOLD_CONTEXT','/api/reference?q=%25',
 '/api/eppo','/api/eppo?dataset=11_13&year=&page=2',
 '/api/eppo?dataset=11_14&year=','/api/eppo?dataset=11_13&year=2024&q=SPRC',
 '/api/eppo?dataset=invalid','/api/reference?year=bad']

def responses():
    result={}
    for path in PATHS:
        u=urlsplit(path); status=[]
        body=b''.join(application({'REQUEST_METHOD':'GET','PATH_INFO':u.path,'QUERY_STRING':u.query},lambda s,h:status.append(s)))
        try: body=json.dumps(json.loads(body),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
        except (ValueError,UnicodeError): pass
        result[path]={'status':status[0],'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}
    return result

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--baseline');g.add_argument('--compare');a=p.parse_args()
    actual=responses()
    if a.baseline:Path(a.baseline).write_text(json.dumps(actual,indent=2)+'\n');return
    expected=json.loads(Path(a.compare).read_text())
    differences=[{'path':k,'expected':v,'actual':actual.get(k)} for k,v in expected.items() if actual.get(k)!=v]
    print(json.dumps({'passed':not differences,'routes':len(actual),'differences':differences},indent=2))
    if differences:raise SystemExit(1)

if __name__=='__main__':main()
