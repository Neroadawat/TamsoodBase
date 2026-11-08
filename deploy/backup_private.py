"""Upload the active allowlisted runtime snapshot to private S3 and verify restore bytes.

Run on EC2. Does not back up MySQL, keys, environment files, raw CSV/PDF or logs.
No deletions and no automatic recurring schedule are installed.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--release',required=True);args=parser.parse_args()
    base=Path.home()/'tamsoodbase'
    info=json.loads(subprocess.check_output(['docker','inspect','tamsoodbase-api']))[0]
    labels=info['Config'].get('Labels',{})
    if labels.get('org.tamsood.project')!='TamsoodBase' or labels.get('org.tamsood.release')!=args.release:raise RuntimeError('Active service identity mismatch')
    checkpoint=json.loads((base/'active-upgrade.json').read_text())
    if checkpoint['release']!=args.release:raise RuntimeError('Checkpoint mismatch')
    archive=base/('backend-'+args.release+'.tar.gz');body=archive.read_bytes();digest=hashlib.sha256(body).hexdigest()
    if digest!=checkpoint['archive_sha256']:raise ValueError('Archive checksum mismatch')
    manifest=json.loads((base/'releases'/args.release/'deployment-manifest.json').read_text())
    if manifest.get('contains_raw_csv_pdf') is not False:raise ValueError('Unexpected backup scope')
    key='backups/'+args.release+'/'+digest+'.tar.gz'
    code='''import sys,io,json,hashlib,tarfile,boto3
from botocore.exceptions import ClientError
from src.s3_storage import client,configuration,object_key
expected=EXPECTED
manifest=MANIFEST
body=sys.stdin.buffer.read()
if hashlib.sha256(body).hexdigest()!=expected:raise ValueError('Input checksum mismatch')
credentials=boto3.Session().get_credentials()
if not credentials or credentials.method!='iam-role':raise RuntimeError('Instance role required')
s3=client();config=configuration();key=object_key(KEY)
listing=s3.list_objects_v2(Bucket=config['bucket'],Prefix=key,MaxKeys=1)
exists=any(item['Key']==key for item in listing.get('Contents',[]))
if exists:
 head=s3.head_object(Bucket=config['bucket'],Key=key)
 if head.get('Metadata',{}).get('sha256')!=expected:raise ValueError('Existing backup has conflicting checksum')
 action='existing_identical_backup'
else:
 s3.put_object(Bucket=config['bucket'],Key=key,Body=body,ServerSideEncryption='AES256',ContentType='application/gzip',Metadata={'sha256':expected,'scope':'private-derived-runtime-no-credentials'},IfNoneMatch='*')
 action='created'
response=s3.get_object(Bucket=config['bucket'],Key=key);restored=response['Body'].read();response['Body'].close()
if hashlib.sha256(restored).hexdigest()!=expected or response.get('ServerSideEncryption')!='AES256':raise ValueError('Restore bytes/encryption mismatch')
with tarfile.open(fileobj=io.BytesIO(restored),mode='r:gz') as tar:
 files={x['path']:x for x in manifest['files']}
 members=tar.getmembers()
 if len(members)!=len(files) or {m.name for m in members}!=set(files) or any(not m.isfile() for m in members):raise ValueError('Restore member allowlist mismatch')
 for item in members:
  content=tar.extractfile(item).read()
  if hashlib.sha256(content).hexdigest()!=files[item.name]['sha256']:raise ValueError('Restored file checksum mismatch')
print(json.dumps({'result':'passed','action':action,'bucket':config['bucket'],'region':config['region'],'object_key':key,'sha256':expected,'bytes':len(restored),'verified_members':len(files),'encryption':response.get('ServerSideEncryption'),'credential_method':credentials.method,'restore_scope':'Downloaded archive and every member hash verified in memory; no live DB replacement','mysql_backed_up':False,'raw_csv_pdf_or_credentials_included':False,'public_route_changed':False}))
'''
    code=code.replace('EXPECTED',repr(digest)).replace('MANIFEST',repr(manifest)).replace('KEY',repr(key))
    result=subprocess.run(['docker','exec','-i','tamsoodbase-api','python','-c',code],input=body,capture_output=True,timeout=180)
    if result.returncode:raise RuntimeError('Private S3 backup failed: '+result.stderr.decode()[-1500:])
    report=json.loads(result.stdout)
    (base/'backup-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
