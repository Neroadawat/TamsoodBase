"""Verify current supplemental DDL/data in a fresh, owned temporary MySQL volume."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import mysql_workspace
import load_supplemental_mysql


def main():
    name='tamsood-supplement-check-'+secrets.token_hex(6);volume=name+'-data';owner='TamsoodBase-Isolated-Supplement';password=secrets.token_urlsafe(32)
    def docker(*args,check=True):
        r=subprocess.run(['docker',*args],capture_output=True,timeout=120,env=os.environ|{'MYSQL_ROOT_PASSWORD':password})
        if check and r.returncode:raise RuntimeError(r.stderr.decode(errors='replace').replace(password,'[redacted]'))
        return r
    docker('image','inspect','mysql:8.1')
    try:
        docker('volume','create','--label','org.tamsood.verify='+owner,volume)
        docker('run','-d','--name',name,'--label','org.tamsood.workspace='+owner,'--network','none','--memory','768m','-v',volume+':/var/lib/mysql','-e','MYSQL_ROOT_PASSWORD','mysql:8.1')
        with tempfile.TemporaryDirectory(prefix='tamsood-verify-') as folder:
            config=Path(folder)/'config.json';config.write_text(json.dumps({'owner':owner,'password':password}),encoding='utf-8')
            with patch.multiple(mysql_workspace,NAME=name,OWNER=owner,VOLUME=volume,CONFIG=config):load_supplemental_mysql.main()
        p=ROOT/'evidence/supplemental-mysql.json';e=json.loads(p.read_text());e.update(verification_scope='Fresh isolated temporary MySQL database; existing workspace not migrated',persistent_workspace_migrated=False);p.write_text(json.dumps(e,indent=2)+'\n',encoding='utf-8')
    finally:
        info=docker('inspect',name,check=False)
        if info.returncode==0:
            if json.loads(info.stdout)[0]['Config']['Labels'].get('org.tamsood.workspace')!=owner:raise RuntimeError('Container ownership mismatch')
            docker('rm','-f','-v',name)
        info=docker('volume','inspect',volume,check=False)
        if info.returncode==0:
            if json.loads(info.stdout)[0]['Labels'].get('org.tamsood.verify')!=owner:raise RuntimeError('Volume ownership mismatch')
            docker('volume','rm',volume)


if __name__=='__main__':main()
