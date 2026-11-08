"""Verify production URL anonymously; private credential read is leak check only."""
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request
from scripts.check_mysql_api_parity import PATHS

def main():
    root=Path(__file__).resolve().parents[1];origin='https://tamsoodbase.vercel.app'
    credentials=json.loads((root/'.local/https-test-credentials.json').read_text())
    def get(path,authorized=False):
        request=urllib.request.Request(origin+path)
        try:response=urllib.request.urlopen(request,timeout=40)
        except urllib.error.HTTPError as error:response=error
        with response:return response.status,response.headers,response.read()
    checks={};baseline=json.loads((root/'.local/mysql-api-baseline.json').read_text())
    for path in PATHS:
        code,headers,body=get(path,True)
        try:body=json.dumps(json.loads(body),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
        except (ValueError,UnicodeError):pass
        expected=baseline[path]
        if code!=int(expected['status'].split()[0]) or hashlib.sha256(body).hexdigest()!=expected['sha256']:
            raise RuntimeError('Production API differs: '+path+' status '+str(code))
        checks[path]=code
    unauth={}
    for path in ('/api/reference','/api/reference.csv','/api/login','/api/export'):
        code,_,_=get(path)
        if code!=200:raise RuntimeError('Anonymous route requires login or failed: '+path)
        unauth[path]=code
    for path in ('/','/api.js','/app.js','/config.js'):
        code,_,body=get(path)
        if code!=200:raise RuntimeError('Frontend asset unavailable')
        if credentials['password'].encode() in body:raise RuntimeError('Credential exposed in asset')
    code,_,body=get('/config.js')
    if b'"apiBaseUrl":""' not in body or b'loginUrl' in body:raise RuntimeError('Wrong same-origin config')
    result={'passed':True,'production_url':origin,'api_parity_routes':checks,'unauthenticated':unauth,
      'static_assets_contain_password':False,'transport':'ANONYMOUS_FRONTEND_SERVER_AUTHENTICATED_UPSTREAM',
      'backend_origin_temporary':True,'vercel_frontend_url_stable':True,'git_push_performed':False,
      'limitation':'Anyone with Vercel URL can read data per user instruction; data rights statuses remain unchanged. Backend Quick Tunnel may change; update TAMSOOD_BACKEND_ORIGIN and redeploy.'}
    (root/'evidence/vercel-deployment.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
