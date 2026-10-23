"""Small staging-to-SQL pilot; no competition acceptance is inferred."""
import csv
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data/staging/dmf_pilot.csv'
EVIDENCE = ROOT / 'evidence/dmf_pilot.json'
REQUIRED = ('record_id', 'period', 'area', 'block', 'field', 'fuel', 'raw_value', 'unit', 'evidence_locator')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(row):
    errors = [f'missing:{key}' for key in REQUIRED if not row.get(key, '').strip()]
    if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', row.get('period', '')):
        errors.append('invalid_period')
    if row.get('area') not in ('onshore', 'offshore'):
        errors.append('invalid_area')
    if row.get('fuel') != 'natural_gas' or row.get('unit') != 'million_ft3_per_day':
        errors.append('unsupported_fuel_unit')
    try:
        value = Decimal(row.get('raw_value', ''))
        if not value.is_finite() or value < 0:
            errors.append('invalid_amount')
    except InvalidOperation:
        errors.append('invalid_amount')
    return errors


def build():
    evidence = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    out = ROOT / 'build'
    out.mkdir(exist_ok=True)
    # Build in memory so a failed run cannot destroy a previous successful DB.
    con = sqlite3.connect(':memory:')
    con.executescript((ROOT / 'sql/schema.sql').read_text(encoding='utf-8'))
    con.execute('INSERT INTO source VALUES (?,?,?,?)', tuple(evidence[k] for k in ('source_id', 'publisher', 'url', 'rights_status')))
    batch = 'pilot-' + digest(INPUT)[:16]
    con.execute('INSERT INTO batch VALUES (?,?,?,?,?,?,?)', (batch, evidence['source_id'], digest(INPUT), digest(EVIDENCE), digest(Path(__file__)), datetime.now(timezone.utc).isoformat(), evidence['method']))
    con.execute('INSERT INTO unit VALUES (?,?)', ('million_ft3_per_day', 'Million cubic feet per day; retain source basis; no conversion'))
    good, bad = [], []
    seen, ids = set(), set()
    with INPUT.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != list(REQUIRED):
            raise ValueError('Unexpected input columns')
        for number, row in enumerate(reader, 2):
            errors = validate(row)
            if row['period'] != evidence['period']:
                errors.append('evidence_period_mismatch')
            key = tuple(row[k] for k in ('period', 'area', 'block', 'field', 'fuel', 'unit'))
            if key in seen or row['record_id'] in ids:
                errors.append('duplicate_in_batch')
            if errors:
                con.execute('INSERT INTO rejected_record VALUES (?,?,?)', (number, json.dumps(row, ensure_ascii=False), json.dumps(errors)))
                bad.append({'row': number, 'record': row, 'reasons': errors})
                continue
            seen.add(key)
            ids.add(row['record_id'])
            con.execute('INSERT INTO observation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (row['record_id'], batch, row['period'], row['area'], row['block'], row['field'], row['fuel'], row['raw_value'], str(Decimal(row['raw_value'])), row['unit'], row['evidence_locator'], 'PASS', 'PENDING'))
            good.append(row)
    assert not con.execute('PRAGMA foreign_key_check').fetchall()
    con.commit()
    with sqlite3.connect(out / 'pilot.sqlite') as target:
        con.backup(target)
    con.close()
    report = {'input_rows': len(good) + len(bad), 'technical_pass': len(good), 'rejected': len(bad),
              'competition_accepted': 0, 'review_pending': len(good), 'input_sha256': digest(INPUT),
              'limitations': ['secondary evidence only', 'rights not reviewed', 'LCI eligibility not confirmed', 'three-row sample, not full monthly coverage']}
    (out / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'rejected.json').write_text(json.dumps(bad, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    build()
