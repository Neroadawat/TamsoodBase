"""Fetch one official PDF and retain original bytes locally; no reuse grant implied."""
import argparse
import hashlib
import json
import urllib.request
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
URL='https://investor.thaioilgroup.com/storage/download/sustainability/2024/top-sustainability2024-en.pdf'


def acquire(source='thaioil'):
    urls={'thaioil':URL,'sprc':'https://investor.sprc.co.th/storage/downloads/sustainability-reports/20250307-sprc-sd2024-en.pdf'}
    url=urls[source]
    folder=ROOT/'data/raw'/source/'2024';folder.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(url,timeout=60) as response:
        body=response.read();final=response.url
        headers={key:response.headers.get(key) for key in ('Content-Type','Last-Modified','ETag')}
    if not body.startswith(b'%PDF-'): raise ValueError('Source did not return PDF')
    digest=hashlib.sha256(body).hexdigest();pdf=folder/'sustainability-report.pdf'
    if pdf.exists() and hashlib.sha256(pdf.read_bytes()).hexdigest()!=digest:
        raise ValueError('PDF changed; preserve the old snapshot and review a new version before replacing')
    if not pdf.exists():
        pdf.write_bytes(body)
        (folder/'manifest.json').write_text(json.dumps({'source_url':url,'final_url':final,
            'accessed_at':datetime.now(timezone.utc).isoformat(),'sha256':digest,'bytes':len(body),
            'headers':headers,'rights_status':'public_readable_reuse_not_confirmed','redistribute_raw':False},indent=2),encoding='utf-8')
    print('Original PDF verified: '+digest)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',choices=['thaioil','sprc'],default='thaioil')
    acquire(parser.parse_args().source)
