"""Optional private S3 artifact storage, using the AWS default credential chain."""
import os
from pathlib import PurePosixPath


def configuration():
    return dict(bucket=os.environ.get('TAMSOOD_S3_BUCKET','').strip(),
                prefix=os.environ.get('TAMSOOD_S3_PREFIX','tamsoodbase').strip('/'),
                region=os.environ.get('AWS_REGION','ap-southeast-2'))


def object_key(name):
    path=PurePosixPath(name)
    if not name or name.startswith('/') or '\\' in name or '..' in path.parts or str(path)!=name:
        raise ValueError('Invalid artifact key')
    prefix=configuration()['prefix']
    if not prefix or '..' in PurePosixPath(prefix).parts or '\\' in prefix:raise ValueError('Invalid artifact prefix')
    return prefix+'/'+name


def client():
    config=configuration()
    if not config['bucket']:raise RuntimeError('S3 bucket not configured')
    import boto3
    return boto3.client('s3',region_name=config['region'])


def upload_artifact(path,name):
    # Caller must explicitly select a rights-reviewed internal artifact. No API upload route.
    key=object_key(name);config=configuration()
    client().upload_file(str(path),config['bucket'],key,ExtraArgs={'ServerSideEncryption':'AES256'})
    return key
