"""Check the running local-only evidence demo without Gemini or Cloud."""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:8767'


def request(body=None, origin=BASE, content_type='application/json', path='/ask'):
    headers = {'Origin': origin, 'Content-Type': content_type}
    req = Request(BASE + path, data=body, headers=headers)
    try:
        with urlopen(req, timeout=20) as response:
            return response.status, response.read().decode('utf-8')
    except HTTPError as error:
        return error.code, error.read().decode('utf-8')


def main():
    checks = []
    cards = json.loads((ROOT / 'docs/rag/public-evidence.json').read_text(encoding='utf-8'))
    status, page = request(path='/')
    checks.append({'case': 'page_with_scope_notice', 'status': status,
                   'passed': status == 200 and f'การ์ดหลักฐาน {len(cards)} ใบ' in page})
    cases = [
        ('positive', {'question': 'ตอนเครื่องยังเย็น รถที่เติมแก๊สโซฮอล์ E10 วิ่งได้กี่กิโลเมตรต่อลิตร'}, 200, BASE, 'application/json'),
        ('unrelated', {'question': 'ขอสูตรทำข้าวผัดไข่'}, 200, BASE, 'application/json'),
        ('unsupported_fuel', {'question': 'E20 cold start กินน้ำมันเท่าไร'}, 200, BASE, 'application/json'),
        ('unsupported_species', {'question': 'E10 N₂O ตอนเครื่องเย็นเท่าไร'}, 200, BASE, 'application/json'),
        ('unsupported_stage', {'question': 'E10 hot start CO2 เท่าไร'}, 200, BASE, 'application/json'),
        ('mixed_language', {'question': 'งาน Songkitti รายงานการกินน้ำมันช่วง cold start ไว้อย่างไร'}, 200, BASE, 'application/json'),
        ('new_basis', {'question': 'หน่วยหน้าที่ของ FAME คืออะไร'}, 200, BASE, 'application/json'),
        ('new_hold', {'question': 'ทำไม Land seeding ถึงถูกพักการใช้'}, 200, BASE, 'application/json'),
        ('new_allocation', {'question': 'สัดส่วนจัดสรร FAME กับกลีเซอรีนเป็นเท่าไร'}, 200, BASE, 'application/json'),
        ('missing_physical_quantity', {'question': 'FAME ใช้เมทานอลกี่กิโลกรัมต่อตัน'}, 200, BASE, 'application/json'),
        ('blank', {'question': '  '}, 400, BASE, 'application/json'),
        ('wrong_type', {'question': 123}, 400, BASE, 'application/json'),
        ('missing_field', {}, 400, BASE, 'application/json'),
        ('oversized_question', {'question': 'ก' * 501}, 400, BASE, 'application/json'),
        ('cross_origin', {'question': 'E10'}, 403, 'https://example.org', 'application/json'),
        ('wrong_content_type', {'question': 'E10'}, 400, BASE, 'text/plain'),
    ]
    for name, payload, expected, origin, content_type in cases:
        status, body = request(json.dumps(payload).encode(), origin, content_type)
        passed = status == expected
        result = None
        if status == 200:
            result = json.loads(body)
            passed &= result['summary'] is None
            passed &= all(any(all(hit[k] == c[k] for k in c) for c in cards) for hit in result['hits'])
            expected_card = {'positive':'e10-cold-start', 'mixed_language':'e10-cold-start',
                             'new_basis':'fame-functional-unit', 'new_hold':'palm-land-unit-hold',
                             'new_allocation':'fame-allocation-caution'}.get(name)
            passed &= (bool(result['hits']) and result['hits'][0]['id'] == expected_card) if expected_card else result['hits'] == []
        checks.append({'case': name, 'status': status, 'passed': passed, 'result': result})
    status, _ = request(b'{')
    checks.append({'case': 'malformed_json', 'status': status, 'passed': status == 400})
    status, _ = request(b'x' * 8193)
    checks.append({'case': 'oversized_body', 'status': status, 'passed': status == 400})
    result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'LOCAL_HTTP_NOT_BROWSER_VISUAL_OR_LLM',
              'passed': all(c['passed'] for c in checks), 'checks': checks}
    (ROOT / 'evidence/rag-expanded-http-2026-11-08.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
