"""Check restored local data routes and bounded export; record unavailable layers honestly."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]


def main():
    checks = []
    # Prerequisites declare the expected state; the real HTTP result must still prove it.
    reference_present=all((ROOT/'build/reusable'/name).is_file() for name in ('manifest.json','reference.sqlite'))
    eppo_present=(ROOT/'build/eppo/report.json').is_file()
    routes = [('/',200),('/api/records',200),('/api/nso',200),('/api/product-inventory',200),
              ('/api/model',200),('/api/reference',200 if reference_present else 503),('/api/eppo',200 if eppo_present else 503),
              ('/api/export',400),('/api/export?product=production-oil&year=2024&status=eligible',200)]
    for route, expected in routes:
        try:
            with urlopen('http://127.0.0.1:8765' + route, timeout=20) as response:
                body = response.read(); status = response.status
        except HTTPError as error:
            body = error.read(); status = error.code
        passed = status == expected
        count = None
        if route in ('/api/nso','/api/product-inventory') and status == 200:
            count = len(json.loads(body)['rows']); passed &= count == (273 if route == '/api/nso' else 16)
        if route == '/api/reference' and status == 200:
            count=json.loads(body)['total']
            passed &= count == json.loads((ROOT/'build/reusable/manifest.json').read_bytes())['accepted_reference']
        checks.append({'route':route,'http':status,'expected_http':expected,'expected_behavior_passed':passed,
                       'rows':count,'response_sha256':hashlib.sha256(body).hexdigest()})
    unavailable=[label for route,label in (('/api/reference','corporate reference'),('/api/eppo','EPPO'))
                 if next(c['http'] for c in checks if c['route']==route)!=200]
    report = {'checked_at_utc':datetime.now(timezone.utc).isoformat(), 'checks':checks,
              'passed':all(c['expected_behavior_passed'] for c in checks),
              'fully_available':not unavailable and all(c['expected_behavior_passed'] for c in checks), 'unavailable_layers':unavailable,
              'scope':'LOCAL_HTTP_RESTORED_DATA_NOT_ALL_LAYERS_OR_PRODUCTION'}
    (ROOT / 'evidence/handoff-explorer-2026-11-08.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    if not report['passed']: raise SystemExit(1)


if __name__ == '__main__': main()
