"""Build only the allowlisted archive and smoke-test an isolated local container."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import tarfile
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def verify():
    package=json.loads((ROOT/'build/deploy/package.json').read_text(encoding='utf-8'))
    manifest=json.loads((ROOT/'build/deploy/manifest.json').read_text(encoding='utf-8'))
    archive=Path(package['archive'])
    if not archive.resolve().is_relative_to((ROOT/'build/deploy').resolve()) or hashlib.sha256(archive.read_bytes()).hexdigest()!=package['archive_sha256']:
        raise ValueError('Deployment archive identity mismatch')
    release=package['release_id'];image='tamsoodbase-api:local-'+release
    name='tamsood-api-check-'+secrets.token_hex(6)
    started=False
    with tempfile.TemporaryDirectory(prefix='tamsood-image-') as tmp:
        folder=Path(tmp)
        with tarfile.open(archive) as tar:
            members=tar.getmembers();expected={r['path']:r for r in manifest['files']}
            if len(members)!=len(expected) or {m.name for m in members}!=set(expected) or any(not m.isfile() for m in members):
                raise ValueError('Archive member allowlist mismatch')
            tar.extractall(folder,filter='data')
        for path,record in expected.items():
            p=folder/path
            if not p.resolve().is_relative_to(folder.resolve()) or hashlib.sha256(p.read_bytes()).hexdigest()!=record['sha256']:
                raise ValueError('Archive member hash mismatch')
        print('Building allowlisted backend image...',flush=True)
        result=subprocess.run(['docker','build','--label','org.tamsood.project=TamsoodBase','-f',str(folder/'deploy/Dockerfile'),'-t',image,str(folder)],capture_output=True,timeout=300)
        (ROOT/'build/deploy/local-image-build.log').write_bytes(result.stdout+result.stderr)
        if result.returncode:raise RuntimeError('Image build failed; see build/deploy/local-image-build.log')
        try:
            subprocess.run(['docker','run','-d','--name',name,'--label','org.tamsood.audit=backend-image',
                '--network','none','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=16m','--cap-drop','ALL',
                '--security-opt','no-new-privileges:true','--memory','384m','--cpus','0.5','--pids-limit','128',image],
                check=True,capture_output=True,timeout=30)
            started=True
            print('Checking Gunicorn routes inside the isolated container...',flush=True)
            probe='''import json,time,urllib.request
deadline=time.monotonic()+40
while True:
 try:
  urllib.request.urlopen('http://127.0.0.1:8000/readyz',timeout=3);break
 except Exception:
  if time.monotonic()>deadline:raise
  time.sleep(.3)
paths=['/','/app.js','/api.js','/config.js','/favicon.svg','/style.css','/healthz','/readyz','/api/summary','/api/source-crosswalk','/api/reports','/api/reference','/api/nso','/api/product-inventory','/api/eppo?dataset=11_13&year=2024&q=SPRC','/api/nso-comparison','/api/records']
checks={};counts={}
for path in paths:
 with urllib.request.urlopen('http://127.0.0.1:8000'+path,timeout=12) as response:
  body=response.read();checks[path]=response.status
  if path in ['/api/reference','/api/nso','/api/product-inventory'] or path.startswith('/api/eppo?'):
   data=json.loads(body);counts[path]=data.get('total',len(data.get('rows',[])))
assert counts['/api/reference']==97 and counts['/api/nso']==273 and counts['/api/product-inventory']==16
assert counts['/api/eppo?dataset=11_13&year=2024&q=SPRC']==12
print(json.dumps(dict(routes=checks,counts=counts)))
'''
            checked=subprocess.run(['docker','exec',name,'python','-c',probe],capture_output=True,timeout=100)
            if checked.returncode:raise RuntimeError('Container route verification failed: '+checked.stderr.decode(errors='replace'))
            checks=json.loads(checked.stdout)
            info=json.loads(subprocess.check_output(['docker','inspect',name],timeout=20))[0]
            if info['Config']['User']!='10001:10001' or not info['HostConfig']['ReadonlyRootfs'] or info['HostConfig']['NetworkMode']!='none' or info['HostConfig']['PortBindings']:
                raise ValueError('Container isolation mismatch')
            result=dict(checked_at=datetime.now(timezone.utc).isoformat(),result='passed',release_id=release,image=image,
                archive_sha256=package['archive_sha256'],archive_allowlist_and_hashes=True,
                runtime=dict(user=info['Config']['User'],read_only=True,network='none',published_ports=[],memory_bytes=info['HostConfig']['Memory']),
                **checks,remote_ec2_changed=False,temporary_container_removed=True)
        finally:
            if started:
                # Only the exact randomly named container created above is removed.
                subprocess.run(['docker','rm','-f',name],check=True,capture_output=True,timeout=30)
    return result


if __name__=='__main__':
    result=verify()
    (ROOT/'evidence/backend-image-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))
