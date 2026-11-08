"""Verified private EC2 upgrade with staging, ownership checks and rollback.

Run on the EC2 host after copying the allowlisted archive and manifest.
Never changes another project's containers, routing, IAM or public access.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import tarfile
import time
import urllib.request
from pathlib import Path, PurePosixPath

OWNER='TamsoodBase'


def docker(*args):
    return subprocess.check_output(['docker',*args],stderr=subprocess.STDOUT).decode()


def inspect(name):return json.loads(docker('inspect',name))[0]


def owned(name):
    info=inspect(name)
    if info['Config'].get('Labels',{}).get('org.tamsood.project')!=OWNER:raise RuntimeError('Container owner mismatch: '+name)
    return info


def unrelated():
    result={}
    for line in docker('ps','-a','--format','{{json .}}').splitlines():
        row=json.loads(line)
        if not row['Names'].startswith('tamsoodbase-'):result[row['Names']]={'id':row['ID'],'state':row['State']}
    return result


def run_container(name,image,port,env,release):
    settings=dict(line.split('=',1) for line in Path(env).read_text().splitlines() if '=' in line)
    network=None
    if settings.get('TAMSOOD_DATA_BACKEND')=='mysql':
        host=settings.get('TAMSOOD_MYSQL_HOST','')
        if host!='tamsoodbase-mysql-runtime':raise RuntimeError('Unexpected MySQL runtime')
        network=host+'-private'
        n=json.loads(docker('network','inspect',network))[0]
        db=inspect(host)
        if not n.get('Internal') or n.get('Labels',{}).get('org.tamsood.project')!='TamsoodBase-MySQL-Runtime':raise RuntimeError('Unowned or public DB network')
        if db['Config'].get('Labels',{}).get('org.tamsood.project')!='TamsoodBase-MySQL-Runtime' or db['HostConfig']['PortBindings']:raise RuntimeError('Unowned or exposed DB')
    docker('run','-d','--name',name,'--label','org.tamsood.project='+OWNER,
           '--label','org.tamsood.release='+release,'--restart','unless-stopped',
           '--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=16m','--cap-drop','ALL',
           '--security-opt','no-new-privileges:true','--memory','384m','--cpus','0.5','--pids-limit','128',
           '--log-opt','max-size=10m','--log-opt','max-file=3','-p',f'127.0.0.1:{port}:8000',
           '--env-file',str(env),image)
    if network:
        try:docker('network','connect',network,name)
        except Exception:
            owned(name);docker('rm','-f',name)
            raise


ROUTES=['/','/app.js','/api.js','/config.js','/favicon.svg','/style.css','/healthz','/readyz',
        '/api/summary','/api/source-crosswalk','/api/reports','/api/reference','/api/nso','/api/product-inventory',
        '/api/eppo?dataset=11_13&year=2024&q=SPRC','/api/nso-comparison','/api/records']


def verify(port,name):
    deadline=time.monotonic()+60
    while True:
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/readyz',timeout=4) as r:
                if r.status==200:break
        except Exception:
            if time.monotonic()>deadline:raise RuntimeError('Readiness timeout')
            time.sleep(1)
    checks={}
    for path in ROUTES:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}'+path,timeout=20) as response:
            body=response.read();checks[path]=response.status
            if path=='/api/reference' and json.loads(body)['total']!=97:raise RuntimeError('Reference count mismatch')
            if path=='/api/nso' and json.loads(body)['row_count']!=273:raise RuntimeError('NSO count mismatch')
            if path=='/api/product-inventory' and len(json.loads(body)['rows'])!=16:raise RuntimeError('Inventory count mismatch')
            if path=='/api/source-crosswalk' and len(json.loads(body)['sources'])!=13:raise RuntimeError('Source contract mismatch')
            if path.startswith('/api/eppo?') and json.loads(body)['total']!=12:raise RuntimeError('EPPO count mismatch')
    info=owned(name)
    if info['Config']['User']!='10001:10001' or not info['HostConfig']['ReadonlyRootfs']:raise RuntimeError('Runtime hardening mismatch')
    if any(b['HostIp']!='127.0.0.1' for values in info['HostConfig']['PortBindings'].values() for b in values):raise RuntimeError('Unexpected public binding')
    return checks


def main():
    p=argparse.ArgumentParser();p.add_argument('release');p.add_argument('sha256');p.add_argument('--expected-old',required=True);p.add_argument('--mysql',action='store_true');args=p.parse_args()
    if not re.fullmatch('[0-9a-f]{16}',args.release) or not re.fullmatch('[0-9a-f]{64}',args.sha256):raise ValueError('Invalid release identity')
    base=Path.home()/'tamsoodbase';release=base/'releases'/args.release
    old=owned('tamsoodbase-api')
    if old['Config']['Labels'].get('org.tamsood.release')!=args.expected_old:raise RuntimeError('Active release changed; stop for review')
    if not old['State']['Running']:raise RuntimeError('Old service not running')
    other_before=unrelated()
    if shutil.disk_usage(base).free<1024**3:raise RuntimeError('Insufficient disk space')
    with socket.socket() as s:s.bind(('127.0.0.1',18765))
    rollback='tamsoodbase-rollback-'+args.expected_old
    candidate='tamsoodbase-stage-'+args.release
    names=docker('ps','-a','--format','{{.Names}}').splitlines()
    if candidate in names or rollback in names:raise RuntimeError('Staging/rollback name already exists; no changes made')
    archive=base/('backend-'+args.release+'.tar.gz');manifest_body=(release/'deployment-manifest.json').read_bytes()
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=args.sha256 or hashlib.sha256(manifest_body).hexdigest()[:16]!=args.release:raise ValueError('Package hash mismatch')
    manifest=json.loads(manifest_body);expected={x['path'] for x in manifest['files']}
    for name in expected:
        path=PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:raise ValueError('Unsafe package path')
    with tarfile.open(archive) as tar:
        members=tar.getmembers()
        if len(members)!=len(expected) or {m.name for m in members}!=expected or any(not m.isfile() for m in members):raise ValueError('Unexpected package members')
        tar.extractall(release,filter='data')
    for item in manifest['files']:
        if hashlib.sha256((release/item['path']).read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Extracted file hash mismatch')
    env=base/'backend.env';pending=base/('backend.env.pending-'+args.release);backup=base/('backend.env.before-'+args.release)
    if backup.exists() or pending.exists():raise RuntimeError('Environment checkpoint already exists')
    previous=env.read_bytes() if env.exists() else b''
    updates={'TAMSOOD_S3_BUCKET':'tamsoodbase-team-fuel-2026-a7k9','TAMSOOD_S3_PREFIX':'tamsoodbase','AWS_REGION':'ap-southeast-2'}
    if args.mysql:
        config=base/'mysql-runtime/backend.mysql.env'
        if config.stat().st_mode & 0o077:raise RuntimeError('MySQL env permissions too broad')
        updates.update(dict(line.split('=',1) for line in config.read_text().splitlines() if '=' in line))
        if updates.get('TAMSOOD_DATA_BACKEND')!='mysql':raise RuntimeError('MySQL mode missing')
    lines=[line for line in previous.decode().splitlines() if line.split('=',1)[0] not in updates]
    if not any(line.startswith('TAMSOOD_ALLOWED_ORIGINS=') for line in lines):lines.append('TAMSOOD_ALLOWED_ORIGINS=')
    pending.write_text('\n'.join(lines+[k+'='+v for k,v in updates.items()])+'\n');os.chmod(pending,0o600)
    image='tamsoodbase-api:'+args.release
    build=subprocess.run(['docker','build','--label','org.tamsood.project='+OWNER,'-f',str(release/'deploy/Dockerfile'),'-t',image,str(release)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (release/'image-build.log').write_bytes(build.stdout)
    if build.returncode:raise RuntimeError('Image build failed; see private image-build.log')
    stage_created=False;renamed=False;final_created=False;old_stopped=False
    try:
        run_container(candidate,image,18765,pending,args.release);stage_created=True
        stage_checks=verify(18765,candidate)
        mysql_parity=None
        if args.mysql:
            baseline=(base/'mysql-runtime/api-baseline.json').read_text()
            check=(base/'mysql-runtime/check_mysql_api_parity.py').read_text()
            code="from pathlib import Path\nPath('/tmp/mysql-baseline.json').write_text("+repr(baseline)+")\n"+check
            probe=subprocess.run(['docker','exec','-i','-e','PYTHONPATH=/app',candidate,'python','-','--compare','/tmp/mysql-baseline.json'],input=code.encode(),capture_output=True)
            if probe.returncode:raise RuntimeError('MySQL API parity failed: '+probe.stdout.decode()[:2000]+probe.stderr.decode()[:1000])
            mysql_parity=json.loads(probe.stdout)
        s3_code="""import json,boto3;from src.s3_storage import configuration,client
c=configuration();credentials=boto3.Session().get_credentials()
if not credentials or credentials.method!='iam-role':raise RuntimeError('Expected instance role')
if c!={'bucket':'tamsoodbase-team-fuel-2026-a7k9','prefix':'tamsoodbase','region':'ap-southeast-2'}:raise RuntimeError('Persistent S3 config mismatch')
s=client();s.list_objects_v2(Bucket=c['bucket'],Prefix='tamsoodbase/health/',MaxKeys=1)
r=s.get_object(Bucket=c['bucket'],Key='tamsoodbase/health/backend-check-4fdd27f70faa4eff9ca0a34658deb938.txt');body=r['Body'].read();r['Body'].close()
if len(body)!=79 or r.get('ServerSideEncryption')!='AES256':raise RuntimeError('S3 marker mismatch')
print(json.dumps({'credential_method':credentials.method,'configuration':c,'marker_bytes':len(body),'encryption':r.get('ServerSideEncryption')}))"""
        stage_s3=json.loads(docker('exec',candidate,'python','-c',s3_code))
        if unrelated()!=other_before:raise RuntimeError('Unrelated service state changed; no switch')
        backup.write_bytes(previous);os.chmod(backup,0o600)
        shutil.copyfile(pending,env);os.chmod(env,0o600)
        docker('stop','--time','25','tamsoodbase-api');old_stopped=True
        docker('rename','tamsoodbase-api',rollback);renamed=True
        run_container('tamsoodbase-api',image,8765,env,args.release);final_created=True
        final_checks=verify(8765,'tamsoodbase-api')
        final_s3=json.loads(docker('exec','tamsoodbase-api','python','-c',s3_code))
        if unrelated()!=other_before:raise RuntimeError('Unrelated service state changed')
        result={'result':'passed','release':args.release,'previous_release':args.expected_old,'image':image,
                'archive_sha256':args.sha256,'staging_routes':stage_checks,'active_routes':final_checks,
                's3':final_s3,'rollback_container':rollback,'rollback_environment':str(backup),
                'bind':'127.0.0.1:8765','unrelated_containers_unchanged':True,
                'public_route_changed':False,'iam_changed':False}
        result['data_backend']='mysql' if args.mysql else 'existing'
        result['mysql_parity']=mysql_parity
        (base/'active-upgrade.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
    except Exception:
        if final_created:
            owned('tamsoodbase-api');docker('rm','-f','tamsoodbase-api')
        if renamed:
            owned(rollback);docker('rename',rollback,'tamsoodbase-api');docker('start','tamsoodbase-api')
        elif old_stopped:
            owned('tamsoodbase-api');docker('start','tamsoodbase-api')
        if backup.exists():env.write_bytes(previous);os.chmod(env,0o600)
        raise
    finally:
        if stage_created:
            owned(candidate);docker('rm','-f',candidate)


if __name__=='__main__':main()
