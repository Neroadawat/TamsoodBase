"""Provision only an owned private MySQL runtime. Never touches other projects.

Run on local Docker first, then EC2. Secrets stay in base/config.json (0600).
Existing non-empty uncheckpointed databases are not dropped or overwritten.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import time

OWNER='TamsoodBase-MySQL-Runtime'


def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--name',default='tamsoodbase-mysql-runtime');a=p.parse_args()
    if not re.fullmatch(r'tamsoodbase-mysql-[a-z0-9-]+',a.name):raise ValueError('Unsafe container name')
    base=a.base.resolve();base.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((base/'manifest.json').read_text());seed=base/'seed.sql.gz'
    configfile=base/'config.json';network=a.name+'-private';volume=a.name+'-data'
    if configfile.exists():
        config=json.loads(configfile.read_text())
        if config.get('owner')!=OWNER or config.get('name')!=a.name:raise RuntimeError('Config ownership mismatch')
    else:
        config={'owner':OWNER,'name':a.name,'root_password':secrets.token_urlsafe(32),'reader_password':secrets.token_urlsafe(32)}
        configfile.write_text(json.dumps(config));os.chmod(configfile,0o600)
    def docker(*args,check=True,input=None):
        r=subprocess.run(['docker',*args],input=input,capture_output=True,timeout=120,
                         env=os.environ|{'MYSQL_PWD':config['root_password'],'MYSQL_ROOT_PASSWORD':config['root_password']})
        if check and r.returncode:raise RuntimeError('MySQL operation failed: '+r.stderr.decode(errors='replace').replace(config['root_password'],'[redacted]').replace(config['reader_password'],'[redacted]')[:900])
        return r
    def query(sql,check=True):
        return docker('exec','-i','-e','MYSQL_PWD',a.name,'mysql','-uroot','--batch','--raw','--skip-column-names','--default-character-set=utf8mb4',check=check,input=sql.encode())
    # A known cached official image is required; image acquisition is a separate step.
    docker('image','inspect','mysql:8.4')
    info=docker('network','inspect',network,check=False)
    if info.returncode:
        docker('network','create','--internal','--label','org.tamsood.project='+OWNER,network)
    else:
        n=json.loads(info.stdout)[0]
        if not n['Internal'] or (n.get('Labels') or {}).get('org.tamsood.project')!=OWNER:raise RuntimeError('Network ownership/isolation mismatch')
    info=docker('volume','inspect',volume,check=False)
    if info.returncode:docker('volume','create','--label','org.tamsood.project='+OWNER,volume)
    elif (json.loads(info.stdout)[0].get('Labels') or {}).get('org.tamsood.project')!=OWNER:raise RuntimeError('Volume ownership mismatch')
    info=docker('inspect',a.name,check=False)
    if info.returncode:
        docker('run','-d','--name',a.name,'--label','org.tamsood.project='+OWNER,'--restart','unless-stopped',
               '--network',network,'--memory','512m','--memory-swap','768m','--cpus','0.5','--pids-limit','256',
               '--log-opt','max-size=10m','--log-opt','max-file=3','--mount','type=volume,source='+volume+',target=/var/lib/mysql',
               '-e','MYSQL_ROOT_PASSWORD','mysql:8.4','--innodb-buffer-pool-size=67108864','--performance-schema=OFF',
               '--max-connections=25','--temptable-max-ram=16777216','--innodb-log-buffer-size=8388608','--innodb-redo-log-capacity=67108864','--mysqlx=0')
    else:
        n=json.loads(info.stdout)[0]
        if (n['Config']['Labels'] or {}).get('org.tamsood.project')!=OWNER or n['HostConfig']['PortBindings'] or not any(m.get('Name')==volume for m in n['Mounts']):raise RuntimeError('Container ownership/storage/isolation mismatch')
        if not n['State']['Running']:docker('start',a.name)
    deadline=time.monotonic()+150
    while query('SELECT 1;',False).returncode:
        if time.monotonic()>deadline:raise RuntimeError('Owned MySQL did not become ready')
        time.sleep(2)
    databases=query("SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name IN ('tamsood_research','tamsood_reusable','tamsood_supplemental','tamsood_eppo','tamsood_api');").stdout.strip()
    if databases==b'0':
        digest=hashlib.sha256()
        with gzip.open(seed,'rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
        if digest.hexdigest()!=manifest['seed_sha256']:raise ValueError('Seed hash mismatch')
        # Stream rather than duplicating a 100+ MB seed in memory on the small EC2.
        with gzip.open(seed,'rb') as source,(base/'import.log').open('wb') as log:
            proc=subprocess.Popen(['docker','exec','-i','-e','MYSQL_PWD',a.name,'mysql','-uroot','--max-allowed-packet=64M','--default-character-set=utf8mb4'],stdin=subprocess.PIPE,stdout=log,stderr=log,env=os.environ|{'MYSQL_PWD':config['root_password']})
            try:shutil.copyfileobj(source,proc.stdin,1024*128);proc.stdin.close();code=proc.wait(timeout=420)
            except Exception:proc.kill();raise
            if code:raise RuntimeError('Seed import stopped; inspect private import.log. No automatic DROP/reload performed')
    release=query("SELECT JSON_UNQUOTE(JSON_EXTRACT(payload,'$.dataset_release')) FROM tamsood_api.artifact WHERE name='runtime_info';").stdout.decode().strip()
    if release!=manifest['dataset_release']:raise RuntimeError('Database dataset release differs; no overwrite')
    counts={}
    for key,sql,expected in [('dmf','tamsood_research.observation',34899),('raw','tamsood_research.source_record',34905),('reference','tamsood_reusable.reference_catalog',101),('supplemental','tamsood_supplemental.observation',289),('eppo','tamsood_eppo.observation',5934)]:
        n=int(query('SELECT COUNT(*) FROM '+sql+';').stdout)
        if n!=expected:raise RuntimeError('Seed count mismatch: '+key)
        counts[key]=n
    password=config['reader_password'] # generated URL-safe, still validate before SQL literal
    if not re.fullmatch('[A-Za-z0-9_-]+',password):raise RuntimeError('Unexpected generated credential format')
    query("CREATE USER IF NOT EXISTS 'tamsood_reader'@'%' IDENTIFIED BY '"+password+"';")
    for db in ['tamsood_api','tamsood_research','tamsood_reusable','tamsood_supplemental','tamsood_eppo']:query('GRANT SELECT ON '+db+".* TO 'tamsood_reader'@'%';")
    env='\n'.join(['TAMSOOD_DATA_BACKEND=mysql','TAMSOOD_MYSQL_HOST='+a.name,'TAMSOOD_MYSQL_PORT=3306','TAMSOOD_MYSQL_USER=tamsood_reader','TAMSOOD_MYSQL_PASSWORD='+password,'TAMSOOD_DATASET_RELEASE='+release])+'\n'
    (base/'backend.mysql.env').write_text(env);os.chmod(base/'backend.mysql.env',0o600)
    info=json.loads(docker('inspect',a.name).stdout)[0]
    if info['HostConfig']['PortBindings']:raise RuntimeError('Database port published unexpectedly')
    result={'passed':True,'container':a.name,'network':network,'internal_network':True,'volume':volume,'persistent':True,'ports_published':False,'dataset_release':release,'seed_sha256':manifest['seed_sha256'],'counts':counts,'reader_grants':'SELECT only on five TamsoodBase schemas','memory_limit_bytes':info['HostConfig']['Memory'],'production_api_switched':False}
    (base/'prepared.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
