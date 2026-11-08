"""Retrieve the selected private S3 backup via EC2 IAM, verify bytes/hash."""
import hashlib
import json
from pathlib import Path
import os
import subprocess

def main():
    base=Path.home()/'tamsoodbase/mysql-runtime'
    record=json.loads((base/'backup-latest.json').read_text());item=record['s3']
    if item['bucket']!='tamsoodbase-team-fuel-2026-a7k9' or not item['key'].startswith('tamsoodbase/backups/mysql/'):
        raise RuntimeError('Unexpected backup scope')
    code="""import sys
from src.s3_storage import client
r=client().get_object(Bucket=sys.argv[1],Key=sys.argv[2])
try:
 for chunk in iter(lambda:r['Body'].read(131072),b''):sys.stdout.buffer.write(chunk)
finally:r['Body'].close()
"""
    path=base/'restore-download.sql.gz'
    with path.open('wb') as f:
        result=subprocess.run(['docker','exec','tamsoodbase-api','python','-c',code,item['bucket'],item['key']],stdout=f,stderr=subprocess.PIPE,timeout=180)
    os.chmod(path,0o600)
    if result.returncode:raise RuntimeError('S3 retrieval failed')
    if path.stat().st_size!=item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
        raise RuntimeError('Downloaded backup does not match manifest')
    print(json.dumps({'passed':True,'source':'S3_GET_OBJECT','sha256':item['sha256'],'bytes':item['bytes']}))

if __name__=='__main__':main()
