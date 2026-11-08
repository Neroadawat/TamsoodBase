"""Read-only WSGI boundary for Gunicorn; reuse existing reviewed route dispatch."""
import json
import os
import sqlite3
from contextlib import closing
from http import HTTPStatus
from urllib.parse import urlsplit
from . import explorer


class CapturedHandler(explorer.Handler):
    def __init__(self,path):
        self.path=path
        self.result=None

    def respond(self,body,kind='application/json; charset=utf-8',status=200,headers=None):
        if not isinstance(body,bytes):body=json.dumps(body,ensure_ascii=False).encode('utf-8')
        self.result=(status,kind,headers or {},body)


def readiness():
    """Check usable current data, not just the existence of manifest files."""
    try:
        if explorer.mysql_store.enabled():return explorer.mysql_store.ready()
        root=explorer.ROOT
        run=json.loads((root/'data/raw/dmf/latest.json').read_text(encoding='utf-8'))['run_id']
        if not isinstance(run,str) or not run or '/' in run or '\\' in run or run in ('.','..'):
            return False
        with closing(sqlite3.connect((root/'build/dmf'/run/'candidates.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as con:
            if not con.execute('SELECT 1 FROM deduplicated_candidates LIMIT 1').fetchone():return False
        for name in ('review-report.json','quality-report.json'):
            json.loads((root/'build/dmf'/run/name).read_text(encoding='utf-8'))
        manifest=json.loads((root/'build/reusable/manifest.json').read_text(encoding='utf-8'))
        with closing(sqlite3.connect((root/'build/reusable/reference.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as con:
            count=con.execute('SELECT COUNT(*) FROM accepted_reference WHERE release_id=?',(manifest['release_id'],)).fetchone()[0]
            if count!=manifest['accepted_reference'] or count==0:return False
        for folder in ('nso','product-inventory','eppo'):
            report=json.loads((root/'build'/folder/'report.json').read_text(encoding='utf-8'))
            if not report['rows']:return False
        return True
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,sqlite3.Error):
        return False


def application(environ,start_response):
    method=environ.get('REQUEST_METHOD','GET')
    path=environ.get('PATH_INFO','/')
    query=environ.get('QUERY_STRING','')
    origin=environ.get('HTTP_ORIGIN','')
    allowed={s.strip() for s in os.environ.get('TAMSOOD_ALLOWED_ORIGINS','').split(',') if s.strip()}
    common=[('X-Content-Type-Options','nosniff'),('Referrer-Policy','no-referrer'),('Cache-Control','no-store')]
    if origin and origin in allowed:
        common.extend([('Access-Control-Allow-Origin',origin),('Vary','Origin'),('Access-Control-Allow-Methods','GET, HEAD, OPTIONS')])
    if method not in ('GET','HEAD','OPTIONS'):
        status,kind,headers,body=405,'application/json',{'Allow':'GET, HEAD, OPTIONS'},b'{"error":"Read-only API"}'
    elif len(path)+len(query)>8192:
        status,kind,headers,body=414,'application/json',{},b'{"error":"Request URL too long"}'
    elif method=='OPTIONS':
        status,kind,headers,body=204,'text/plain',{},b''
    elif path=='/healthz':
        status,kind,headers,body=200,'application/json',{},b'{"status":"ok","service":"tamsoodbase-api"}'
    elif path=='/readyz':
        ready=readiness()
        status,kind,headers,body=(200 if ready else 503),'application/json',{},json.dumps({'ready':ready}).encode()
    else:
        handler=CapturedHandler(path+('?' + query if query else ''))
        handler.do_GET()
        status,kind,headers,body=handler.result
    response_headers=common+[('Content-Type',kind),('Content-Length',str(len(body)))]+list(headers.items())
    start_response(str(status)+' '+HTTPStatus(status).phrase,response_headers)
    return [b'' if method=='HEAD' else body]
