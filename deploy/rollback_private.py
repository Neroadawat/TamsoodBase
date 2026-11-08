"""Review or apply rollback of only TamsoodBase; default is read-only dry run."""
import argparse
import json
import os
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path


def info(name):return json.loads(subprocess.check_output(['docker','inspect',name]))[0]


def main():
    p=argparse.ArgumentParser();p.add_argument('--current',required=True);p.add_argument('--previous',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    if not all(re.fullmatch('[0-9a-f]{16}',v) for v in [a.current,a.previous]):raise ValueError('Invalid release IDs')
    base=Path.home()/'tamsoodbase';name='tamsoodbase-api';rollback='tamsoodbase-rollback-'+a.previous;retired='tamsoodbase-retired-'+a.current
    current=info(name);old=info(rollback)
    for item,release in [(current,a.current),(old,a.previous)]:
        labels=item['Config'].get('Labels',{})
        if labels.get('org.tamsood.project')!='TamsoodBase' or labels.get('org.tamsood.release')!=release:raise RuntimeError('Container identity mismatch')
        if any(b['HostIp']!='127.0.0.1' for values in item['HostConfig']['PortBindings'].values() for b in values):raise RuntimeError('Unexpected public binding')
    if old['State']['Running']:raise RuntimeError('Rollback container already running')
    checkpoint=base/('backend.env.before-'+a.current)
    if not checkpoint.is_file() or checkpoint.is_symlink():raise RuntimeError('Environment checkpoint missing/unsafe')
    if retired in subprocess.check_output(['docker','ps','-a','--format','{{.Names}}']).decode().splitlines():raise RuntimeError('Retired name already used')
    plan={'result':'rollback_preflight_passed','apply':a.apply,'current':a.current,'previous':a.previous,'preserved_new_container':retired,'s3_configuration':'Restores previous runtime environment; S3 settings may revert','public_route_changed':False}
    if a.apply:
        saved_env=base/('backend.env.retired-'+a.current)
        if saved_env.exists():raise RuntimeError('Retired environment checkpoint already exists')
        shutil.copyfile(base/'backend.env',saved_env);os.chmod(saved_env,0o600)
        subprocess.run(['docker','stop','--time','25',name],check=True)
        subprocess.run(['docker','rename',name,retired],check=True)
        try:
            shutil.copyfile(checkpoint,base/'backend.env');os.chmod(base/'backend.env',0o600)
            subprocess.run(['docker','rename',rollback,name],check=True)
            subprocess.run(['docker','start',name],check=True)
            import time
            for attempt in range(30):
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8765/readyz',timeout=3) as r:
                        if r.status==200:break
                except Exception:
                    if attempt==29:raise
                    time.sleep(1)
            plan['result']='rollback_applied'
        except Exception:
            # Preserve both versions and restore the just-retired known-good service.
            probe=subprocess.run(['docker','inspect',name],capture_output=True)
            if probe.returncode==0:
                labels=info(name)['Config'].get('Labels',{})
                if labels.get('org.tamsood.project')!='TamsoodBase' or labels.get('org.tamsood.release')!=a.previous:raise RuntimeError('Unexpected container during recovery')
                subprocess.run(['docker','stop',name],check=True);subprocess.run(['docker','rename',name,rollback],check=True)
            shutil.copyfile(saved_env,base/'backend.env');os.chmod(base/'backend.env',0o600)
            subprocess.run(['docker','rename',retired,name],check=True);subprocess.run(['docker','start',name],check=True)
            raise
        (base/'rollback-result.json').write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps(plan,indent=2))


if __name__=='__main__':main()
