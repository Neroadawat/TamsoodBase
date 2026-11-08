"""Fetch one official PDF and retain original bytes locally; no reuse grant implied."""
import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
URL='https://investor.thaioilgroup.com/storage/download/sustainability/2024/top-sustainability2024-en.pdf'
MAX_PDF_BYTES=32*1024*1024


def acquire(source='thaioil',expected_sha256=None):
    if expected_sha256 is not None and not re.fullmatch('[a-fA-F0-9]{64}',expected_sha256):
        raise ValueError('Expected SHA256 must contain 64 hexadecimal characters')
    urls={'thaioil':URL,'sprc':'https://investor.sprc.co.th/storage/downloads/sustainability-reports/20250307-sprc-sd2024-en.pdf'}
    url=urls[source]
    folder=ROOT/'data/raw'/source/'2024';folder.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(url,timeout=60) as response:
        body=response.read(MAX_PDF_BYTES+1);final=response.url
        headers={key:response.headers.get(key) for key in ('Content-Type','Last-Modified','ETag')}
    if len(body)>MAX_PDF_BYTES: raise ValueError('PDF exceeds the bounded download size')
    if not body.startswith(b'%PDF-'): raise ValueError('Source did not return PDF')
    digest=hashlib.sha256(body).hexdigest();pdf=folder/'sustainability-report.pdf'
    if expected_sha256 is not None and digest!=expected_sha256.lower():
        raise ValueError('PDF does not match the recorded source; no snapshot written')
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
    parser.add_argument('--recorded',action='store_true',help='Require the exact PDF hash from the previous source review')
    args=parser.parse_args()
    evidence={'thaioil':'thaioil-pilot-review-2026-10-22.json','sprc':'sprc-review-2026-10-22.json'}
    expected=json.loads((ROOT/'evidence'/evidence[args.source]).read_bytes())['pdf_sha256'] if args.recorded else None
    acquire(args.source,expected)
