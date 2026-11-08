"""Private consistent MySQL dump; upload via the existing EC2 instance role.

No credentials are printed or stored in the dump. The private seed and retained
SQLite service remain independent rollback paths. Run on the EC2 host.
"""
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import os
import subprocess

def main():
    base=Path.home()/'tamsoodbase';db='tamsoodbase-mysql-runtime'
    info=json.loads(subprocess.check_output(['docker','inspect',db]))[0]
    if info['Config'].get('Labels',{}).get('org.tamsood.project')!='TamsoodBase-MySQL-Runtime':raise RuntimeError('DB ownership mismatch')
    config=json.loads((base/'mysql-runtime/config.json').read_text())
    out=base/'mysql-runtime/backups';out.mkdir(mode=0o700,exist_ok=True)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    path=out/('mysql-'+stamp+'.sql.gz');error=out/('mysql-'+stamp+'.stderr')
    command=['docker','exec','-e','MYSQL_PWD',db,'mysqldump','-uroot','--single-transaction','--no-tablespaces','--set-gtid-purged=OFF','--databases','tamsood_research','tamsood_reusable','tamsood_supplemental','tamsood_eppo','tamsood_api']
    with error.open('wb') as err,path.open('wb') as raw:
        proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=err,env=os.environ|{'MYSQL_PWD':config['root_password']})
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as zipped:
            for chunk in iter(lambda:proc.stdout.read(128*1024),b''):zipped.write(chunk)
        if proc.wait(timeout=300):raise RuntimeError('MySQL dump failed; inspect private stderr')
    os.chmod(path,0o600)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    # API has no root credential; only upload the resulting compressed dump.
    code="""import hashlib,json,sys,tempfile,shutil
from src.s3_storage import client,configuration
with tempfile.TemporaryFile() as f:
 shutil.copyfileobj(sys.stdin.buffer,f);f.seek(0);digest=hashlib.sha256(f.read()).hexdigest();f.seek(0)
 c=configuration();key=c['prefix']+'/backups/mysql/"""+path.name+"""'
 s=client();s.upload_fileobj(f,c['bucket'],key,ExtraArgs={'ServerSideEncryption':'AES256','Metadata':{'sha256':digest}})
 h=s.head_object(Bucket=c['bucket'],Key=key)
 if h.get('Metadata',{}).get('sha256')!=digest or h.get('ServerSideEncryption')!='AES256':raise RuntimeError('S3 backup verification failed')
 print(json.dumps({'bucket':c['bucket'],'key':key,'sha256':digest,'bytes':h['ContentLength'],'encryption':h['ServerSideEncryption']}))
"""
    with path.open('rb') as f:
        result=subprocess.run(['docker','exec','-i','tamsoodbase-api','python','-c',code],stdin=f,capture_output=True,timeout=300)
    if result.returncode:raise RuntimeError('Private S3 backup upload failed')
    uploaded=json.loads(result.stdout)
    if uploaded['sha256']!=digest or uploaded['bytes']!=path.stat().st_size:raise RuntimeError('Backup checksum mismatch')
    record={'passed':True,'type':'CONSISTENT_MYSQL_LOGICAL_DUMP','created_at':stamp,'schemas':5,'s3':uploaded,'restore_tested':False}
    (base/'mysql-runtime/backup-latest.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
