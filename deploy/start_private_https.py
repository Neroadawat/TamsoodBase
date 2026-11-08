"""Start an authenticated temporary test URL without changing Caddy or SGs.

Requires explicit user selection of a temporary HTTPS preview. Credentials stay
in the private host folder. Only this project's new containers are managed.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import time
import urllib.error
import urllib.request

OWNER='TamsoodBase-HTTPS-Test'
TUNNEL_IMAGE='cloudflare/cloudflared@sha256:1b1d34d0a9c0bfca9de72db8460d328db3f19edd2b96169114e3e893a97bbe53'

def docker(*args):return subprocess.check_output(['docker',*args],stderr=subprocess.STDOUT).decode()
def others():
    return {r['Names']:(r['ID'],r['State']) for r in [json.loads(line) for line in docker('ps','-a','--format','{{json .}}').splitlines()] if not r['Names'].startswith('tamsoodbase-')}
def probe(url,authorization=None):
    req=urllib.request.Request(url,headers={'Authorization':authorization} if authorization else {})
    try:
        with urllib.request.urlopen(req,timeout=30) as response:return response.status,response.read()
    except urllib.error.HTTPError as e:return e.code,e.read()

def main():
    base=Path.home()/'tamsoodbase';folder=base/'https-test';folder.mkdir(mode=0o700,exist_ok=True)
    old=others();active=json.loads(docker('inspect','tamsoodbase-api'))[0]
    if active['Config'].get('Labels',{}).get('org.tamsood.project')!='TamsoodBase':raise RuntimeError('API owner mismatch')
    if any(v['HostIp']!='127.0.0.1' for values in active['HostConfig']['PortBindings'].values() for v in values):raise RuntimeError('API is not private')
    if probe('http://127.0.0.1:8765/readyz')[0]!=200:raise RuntimeError('API not ready')
    names=['tamsoodbase-https-gateway','tamsoodbase-https-tunnel']
    existing=docker('ps','-a','--format','{{.Names}}').splitlines()
    if any(name in existing for name in names):raise RuntimeError('HTTPS test containers already exist; inspect before replacing')
    if (folder/'credentials.json').exists():raise RuntimeError('Existing HTTPS credentials; inspect before replacing')
    password=secrets.token_urlsafe(24);username='tamsood-team';salt=secrets.token_bytes(16)
    credentials={'username':username,'password':password}
    config={'username':username,'salt':salt.hex(),'iterations':600000,'password_hash':hashlib.pbkdf2_hmac('sha256',password.encode(),salt,600000).hex()}
    (folder/'credentials.json').write_text(json.dumps(credentials));os.chmod(folder/'credentials.json',0o600)
    (folder/'access.json').write_text(json.dumps(config));os.chmod(folder/'access.json',0o444)
    script=base/'mysql-runtime/private_gateway.py';os.chmod(script,0o444)
    auth='Basic '+base64.b64encode((username+':'+password).encode()).decode()
    created=[]
    try:
        docker('run','-d','--name',names[0],'--label','org.tamsood.project='+OWNER,'--network','host','--restart','unless-stopped',
          '--read-only','--cap-drop','ALL','--security-opt','no-new-privileges:true','--memory','96m','--cpus','0.25','--pids-limit','48',
          '--log-opt','max-size=5m','--log-opt','max-file=2','--mount','type=bind,source='+str(script)+',target=/gateway.py,readonly',
          '--mount','type=bind,source='+str(folder/'access.json')+',target=/config/access.json,readonly',
          '--entrypoint','python',active['Config']['Image'],'/gateway.py');created.append(names[0])
        deadline=time.monotonic()+30
        while True:
            try:
                if probe('http://127.0.0.1:18766/healthz')[0]==401:break
            except OSError:pass
            if time.monotonic()>deadline:raise RuntimeError('Gateway did not start')
            time.sleep(1)
        if probe('http://127.0.0.1:18766/readyz',auth)[0]!=200:raise RuntimeError('Authenticated gateway not ready')
        docker('image','inspect',TUNNEL_IMAGE)
        docker('run','-d','--name',names[1],'--label','org.tamsood.project='+OWNER,'--network','host','--restart','unless-stopped',
          '--read-only','--cap-drop','ALL','--security-opt','no-new-privileges:true','--memory','96m','--cpus','0.25','--pids-limit','48',
          '--log-opt','max-size=5m','--log-opt','max-file=2',TUNNEL_IMAGE,'tunnel','--no-autoupdate','--protocol','http2','--url','http://127.0.0.1:18766');created.append(names[1])
        deadline=time.monotonic()+90;url=None
        while time.monotonic()<deadline:
            logs=subprocess.run(['docker','logs',names[1]],capture_output=True)
            match=re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', (logs.stdout+logs.stderr).decode(errors='replace'))
            if match:url=match.group();break
            time.sleep(2)
        if not url:raise RuntimeError('No temporary HTTPS URL issued')
        checks={};deadline=time.monotonic()+90
        while True:
            try:
                code,_=probe(url+'/healthz')
                if code==401:break
            except OSError:pass
            if time.monotonic()>deadline:raise RuntimeError('HTTPS gateway unreachable')
            time.sleep(3)
        for path in ('/','/healthz','/api/reference.csv','/api/records'):
            code,_=probe(url+path)
            if code!=401:raise RuntimeError('Unauthenticated route exposed')
            checks[path]={'unauthenticated':code}
        for path in ('/','/readyz','/api/reference','/api/nso','/api/product-inventory'):
            code,body=probe(url+path,auth)
            if code!=200:raise RuntimeError('Authenticated HTTPS route failed')
            checks.setdefault(path,{})['authenticated']=code
            if path=='/api/reference' and json.loads(body)['total']!=97:raise RuntimeError('Unexpected reference data')
        if probe(url+'/healthz','Basic '+base64.b64encode(b'tamsood-team:wrong').decode())[0]!=401:raise RuntimeError('Incorrect password accepted')
        if others()!=old:raise RuntimeError('Unrelated service state changed')
        result={'passed':True,'url':url,'kind':'TEMPORARY_AUTHENTICATED_HTTPS_TEST','checks':checks,
          'incorrect_password_status':401,'tls_certificate_verified':True,'security_group_changed':False,'caddy_changed':False,
          'unrelated_containers_unchanged':True,'origin':'127.0.0.1:18766','database_public':False,'production_frontend_published':False,
          'limitation':'Quick Tunnel URL may change on restart; testing only, no uptime guarantee'}
        (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    except Exception:
        for name in reversed(created):
            info=json.loads(docker('inspect',name))[0]
            if info['Config'].get('Labels',{}).get('org.tamsood.project')==OWNER:docker('rm','-f',name)
        raise

if __name__=='__main__':main()
