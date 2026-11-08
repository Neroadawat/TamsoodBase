"""Exercise local search -> source row -> actual graph, without submitting human feedback."""
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:8767'


def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=25) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error: return error.code, None


def post(path, payload):
    request = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
        headers={'Content-Type':'application/json', 'Origin':BASE})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error: return error.code, None


def main():
    checks = []
    for question, expected in [('ทำไม Land seeding ถึงถูกพักการใช้', 'palm-land-unit-hold'),
                               ('หน่วยหน้าที่ของ FAME คืออะไร', 'fame-functional-unit')]:
        status, result = post('/ask', {'question':question})
        passed = status == 200 and result['hits'][0]['id'] == expected and result['summary'] is None
        hit = result['hits'][0]; lineage = hit['lineage']
        passed &= lineage['count'] > 0 and bool(lineage['observations'])
        row = lineage['observations'][0]; oid = row['observation_id']
        observed_status, observation = get('/evidence?id=' + oid)
        graph_status, graph = get('/graph?id=' + oid)
        passed &= observed_status == graph_status == 200
        passed &= observation['observation_id'] == oid and observation['amount'] == row['amount']
        passed &= graph['rows'][0]['observation_id'] == oid and graph['rows'][0]['amount'] == row['amount']
        passed &= graph['rows'][0]['unit'] == row['unit']
        if expected == 'palm-land-unit-hold':
            passed &= observation['unit'] is None and observation['status'] == 'HOLD_MISSING_UNIT'
        checks.append({'case':expected,'passed':passed,'observation_id':oid,'lineage_count':lineage['count']})
        with urllib.request.urlopen(BASE + '/evidence/view?id=' + oid, timeout=10) as response:
            page = response.read().decode('utf-8')
            readable = response.status == 200 and 'text/html' in response.headers['Content-Type']
            readable &= observation['amount'] in page and 'ช่วงปีที่วัด' in page
            if observation['unit'] is None: readable &= 'พักการใช้' in page
        checks.append({'case':'readable_source_view','passed':readable})
        status, _ = post('/review', {'search_id':result['search_id'],'verdict':'invented'})
        checks.append({'case':'invalid_review_rejected','passed':status == 400})
    nso = json.loads((ROOT / 'build/nso/report.json').read_bytes())['rows'][0]['observation_id']
    for path, expected in [('/evidence?id=' + nso,404), ('/evidence?id=' + '0'*64,404),
                           ('/evidence?id=not-an-id',400), ('/graph?id=invalid',400),
                           ('/evidence/view?id=' + nso,404), ('/evidence/view?id=invalid',400),
                           ('/evidence?id=' + '0'*64 + '&id=' + '1'*64,400)]:
        status, _ = get(path); checks.append({'case':path.split('?')[0] + ':' + str(expected),'passed':status == expected})
    status, _ = post('/review', {'search_id':'invented','verdict':'sufficient'})
    checks.append({'case':'unissued_review_rejected','passed':status == 400})
    report = {'checked_at_utc':datetime.now(timezone.utc).isoformat(),'passed':all(c['passed'] for c in checks),
              'checks':checks,'human_feedback_submitted':False,'llm_called':False,
              'scope':'LOCAL_HTTP_REAL_SQLITE_AND_NEO4J_NOT_PRODUCTION'}
    (ROOT / 'evidence/handoff-integration-2026-11-08.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if not report['passed']: raise SystemExit(1)


if __name__ == '__main__': main()
