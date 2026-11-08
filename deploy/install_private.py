"""Install one verified release on EC2 without modifying other services or public routes."""
import argparse
import hashlib
import json
import re
import subprocess
import tarfile
from pathlib import Path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('release');parser.add_argument('sha256');args=parser.parse_args()
    if not re.fullmatch('[0-9a-f]{16}',args.release) or not re.fullmatch('[0-9a-f]{64}',args.sha256):
        raise ValueError('Invalid release/hash')
    base=Path.home()/'tamsoodbase';release=base/'releases'/args.release
    if not release.resolve().is_relative_to(base.resolve()):raise ValueError('Unsafe release path')
    archive=base/('backend-'+args.release+'.tar.gz')
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=args.sha256:raise ValueError('Archive checksum mismatch')
    manifest_body=(release/'deployment-manifest.json').read_bytes()
    if hashlib.sha256(manifest_body).hexdigest()[:16]!=args.release:raise ValueError('Manifest identity mismatch')
    manifest=json.loads(manifest_body)
    with tarfile.open(archive) as tar:
        expected={r['path'] for r in manifest['files']}
        if {m.name for m in tar.getmembers()}!=expected or any(not m.isfile() for m in tar.getmembers()):raise ValueError('Unexpected archive members')
        tar.extractall(release,filter='data')
    for item in manifest['files']:
        path=release/item['path']
        if not path.resolve().is_relative_to(release.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('Deployed file checksum mismatch')
    name='tamsoodbase-api';image='tamsoodbase-api:'+args.release
    existing=subprocess.run(['docker','inspect',name],capture_output=True)
    if existing.returncode==0:
        raise RuntimeError('Container already exists; review its owner and use explicit upgrade/rollback procedure')
    subprocess.run(['docker','build','--label','org.tamsood.project=TamsoodBase','-f',str(release/'deploy/Dockerfile'),'-t',image,str(release)],check=True)
    command=['docker','run','-d','--name',name,'--label','org.tamsood.project=TamsoodBase',
        '--label','org.tamsood.release='+args.release,'--restart','unless-stopped',
        '--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=16m','--cap-drop','ALL',
        '--security-opt','no-new-privileges:true','--memory','384m','--cpus','0.5','--pids-limit','128',
        '--log-opt','max-size=10m','--log-opt','max-file=3','-p','127.0.0.1:8765:8000']
    env=base/'backend.env'
    if env.exists():command+=['--env-file',str(env)]
    command.append(image)
    subprocess.run(command,check=True)
    print(json.dumps(dict(container=name,release=args.release,published_host='127.0.0.1',port=8765,s3='not configured until bucket/role supplied')))


if __name__=='__main__':main()
