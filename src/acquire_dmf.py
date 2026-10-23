"""Acquire public DMF CKAN metadata and CSVs, retaining exact response bytes."""
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ('production-oil', 'production-condensate', 'production-natural-gas')


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'TamsoodBase academic source review/0.1'})
    with urllib.request.urlopen(request, timeout=40) as response:
        headers = {k: response.headers[k] for k in ('Content-Type', 'Content-Length', 'ETag', 'Last-Modified') if k in response.headers}
        return response.read(), headers, response.url


def acquire():
    run = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target = ROOT / 'data/raw/dmf' / run
    target.mkdir(parents=True, exist_ok=False)
    manifest = {'run_id': run, 'acquired_at': datetime.now(timezone.utc).isoformat(), 'packages': []}
    # Partial runs remain on disk with exact bytes; latest.json updates only on completion.
    for name in PACKAGES:
        metadata_url = 'https://catalog.dmf.go.th/api/3/action/package_show?id=' + name
        body, headers, final_url = fetch(metadata_url)
        (target / (name + '.metadata.json')).write_bytes(body)
        response = json.loads(body)
        if not response.get('success'):
            raise ValueError('CKAN metadata request failed: ' + name)
        package = response['result']
        resources = [r for r in package['resources'] if r.get('format', '').upper() == 'CSV']
        if len(resources) != 1:
            raise ValueError('Expected exactly one CSV resource: ' + name)
        resource = resources[0]
        time.sleep(1)
        csv_bytes, csv_headers, csv_url = fetch(resource['url'])
        (target / (name + '.csv')).write_bytes(csv_bytes)
        entry = {'package': name, 'package_id': package['id'], 'resource_id': resource['id'],
                 'metadata_url': metadata_url, 'metadata_final_url': final_url,
                 'metadata_sha256': hashlib.sha256(body).hexdigest(),
                 'metadata_headers': headers, 'csv_url': csv_url, 'csv_headers': csv_headers,
                 'csv_sha256': hashlib.sha256(csv_bytes).hexdigest(), 'csv_bytes': len(csv_bytes),
                 'license_id': package.get('license_id'), 'license_url': package.get('license_url'),
                 'resource_unit': resource.get('resource_unit_of_measure'),
                 'resource_last_modified': resource.get('last_modified')}
        manifest['packages'].append(entry)
        (target / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        print(name, len(csv_bytes), 'bytes')
        time.sleep(1)
    manifest['complete'] = True
    (target / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / 'data/raw/dmf/latest.json').write_text(json.dumps({'run_id': run}), encoding='utf-8')
    print('Saved original responses:', target)


if __name__ == '__main__':
    acquire()
