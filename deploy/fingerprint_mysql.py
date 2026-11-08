"""Canonical logical row fingerprint, streamed without printing row data/secrets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

SCHEMAS=['tamsood_research','tamsood_reusable','tamsood_supplemental','tamsood_eppo','tamsood_api']
def main():
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    config=json.loads((a.base/'config.json').read_text())
    if config.get('owner')!='TamsoodBase-MySQL-Runtime' or config.get('name')!=a.name:raise RuntimeError('Config owner mismatch')
    info=json.loads(subprocess.check_output(['docker','inspect',a.name]))[0]
    if info['Config'].get('Labels',{}).get('org.tamsood.project')!='TamsoodBase-MySQL-Runtime':raise RuntimeError('Container owner mismatch')
    command=['docker','exec','-e','MYSQL_PWD',a.name,'mysqldump','-uroot','--single-transaction','--no-create-info','--no-create-db','--skip-triggers','--compact','--skip-comments','--skip-add-locks','--skip-disable-keys','--skip-set-charset','--skip-tz-utc','--skip-extended-insert','--order-by-primary','--no-tablespaces','--set-gtid-purged=OFF','--databases',*SCHEMAS]
    proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=os.environ|{'MYSQL_PWD':config['root_password']})
    digest=hashlib.sha256();size=0
    for chunk in iter(lambda:proc.stdout.read(131072),b''):digest.update(chunk);size+=len(chunk)
    error=proc.stderr.read();code=proc.wait(timeout=240)
    if code:raise RuntimeError('Logical fingerprint failed')
    result={'schemas':SCHEMAS,'ordered_logical_rows_sha256':digest.hexdigest(),'bytes':size,'method':'mysqldump canonical data-only, PK order, one INSERT per row'}
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
