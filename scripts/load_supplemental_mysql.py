"""Load versioned NSO statistics and research inventory without changing acceptance."""
import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def literal(value):
    if value is None:
        return 'NULL'
    return "CONVERT(X'" + str(value).encode('utf-8').hex() + "' USING utf8mb4)"


def decimal_value(value):
    number = Decimal(value)
    if not number.is_finite() or abs(number) >= Decimal('1e18') or number != number.quantize(Decimal('0.000000000001')):
        raise ValueError('Amount cannot be stored exactly in DECIMAL(30,12)')
    return format(number, 'f')


def main():
    from mysql_workspace import NAME, OWNER, VOLUME, CONFIG
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    if config['owner'] != OWNER:
        raise RuntimeError('Credential owner mismatch')
    info = json.loads(subprocess.check_output(['docker', 'inspect', NAME]))[0]
    if (info['Config']['Labels'] or {}).get('org.tamsood.workspace') != OWNER or not any(
        m.get('Name') == VOLUME and m['Destination'] == '/var/lib/mysql' for m in info['Mounts']
    ):
        raise RuntimeError('Workspace ownership mismatch')
    if not info['State']['Running']:
        subprocess.run(['docker', 'start', NAME], check=True, capture_output=True, timeout=60)

    def query(sql, check=True):
        result = subprocess.run(['docker', 'exec', '-i', '-e', 'MYSQL_PWD', NAME, 'mysql',
            '-uroot', '--default-character-set=utf8mb4', '--batch', '--skip-column-names'],
            input=sql.encode('utf-8'), capture_output=True, timeout=120,
            env=os.environ | {'MYSQL_PWD': config['password']})
        if check and result.returncode:
            raise RuntimeError(result.stderr.decode('utf-8', errors='replace').replace(config['password'], '[redacted]'))
        return result

    deadline = time.monotonic() + 60
    while query('SELECT 1;', False).returncode:
        if time.monotonic() >= deadline:
            raise RuntimeError('MySQL readiness timed out')
        time.sleep(2)
    schema = (ROOT/'sql/mysql/supplemental-schema.sql').read_text(encoding='utf-8')
    query(schema)
    results = []
    for kind, path in [('NSO', 'build/nso/report.json'), ('PRODUCT_INVENTORY', 'build/product-inventory/report.json')]:
        body = (ROOT/path).read_bytes()
        snapshot = hashlib.sha256(body).hexdigest()
        rows = json.loads(body)['rows']
        if not rows or len({r['observation_id'] for r in rows}) != len(rows):
            raise ValueError('Empty or duplicate observations')
        statements = ['USE tamsood_supplemental;', 'START TRANSACTION;',
            'INSERT IGNORE INTO dataset_snapshot VALUES (' + ','.join(map(literal, [snapshot, kind, path])) + ');']
        for r in rows:
            oid = r['observation_id']
            amount = decimal_value(r['amount'])
            payload = json.dumps(r, ensure_ascii=False, sort_keys=True)
            statements.append('INSERT IGNORE INTO observation VALUES (' + ','.join([
                literal(snapshot), literal(oid), amount, literal(r['unit']), literal(r['status']), literal(payload)]) + ');')
            if kind == 'NSO':
                values = [snapshot, oid, r['table_id'], r['reference_year'], r['measure'], r['label'], r['source_sha256'], r['source_line'], r['source_column']]
                statements.append('INSERT IGNORE INTO national_statistic VALUES (' + ','.join(map(literal, values)) + ');')
            else:
                process = [snapshot, r['process'], decimal_value(r['reference_amount']), r['reference_unit'], r['geography'], r['technology_level']]
                statements.append('INSERT IGNORE INTO process VALUES (' + ','.join(map(literal, process)) + ');')
                values = [snapshot, oid, r['process'], r['flow'], r['direction'], r['role'], r['data_period'], r['source_snapshot_sha256'], r['source_row'], r['source_column']]
                statements.append('INSERT IGNORE INTO inventory_exchange VALUES (' + ','.join(map(literal, values)) + ');')
        statements.append('COMMIT;')
        query('\n'.join(statements))
        stored = query('USE tamsood_supplemental; SELECT observation_id,amount,unit_code,status,HEX(CAST(payload AS CHAR)) FROM observation WHERE snapshot_id=' + literal(snapshot) + ';').stdout.decode('utf-8')
        actual = {}
        for line in stored.splitlines():
            oid, amount, unit, status, payload = line.split('\t')
            actual[oid] = (Decimal(amount), unit, status, json.loads(bytes.fromhex(payload).decode('utf-8')))
        expected = {r['observation_id']: (Decimal(r['amount']), r['unit'], r['status'], r) for r in rows}
        if actual != expected:
            raise RuntimeError('Supplemental roundtrip mismatch: ' + kind)
        child = 'national_statistic' if kind == 'NSO' else 'inventory_exchange'
        count = int(query('USE tamsood_supplemental; SELECT COUNT(*) FROM ' + child + ' WHERE snapshot_id=' + literal(snapshot)).stdout)
        if count != len(rows):
            raise RuntimeError('Subtype count mismatch')
        fields = (['table_id','reference_year','measure','label','source_sha256','source_line','source_column']
            if kind == 'NSO' else ['process_id','flow','direction','role','data_period','source_sha256','source_row','source_column'])
        expression = 'JSON_OBJECT(' + ','.join(literal(f)+','+f for f in fields) + ')'
        typed = query('USE tamsood_supplemental; SELECT observation_id,HEX(CAST('+expression+' AS CHAR)) FROM '+child+' WHERE snapshot_id='+literal(snapshot)).stdout.decode()
        actual_typed = {line.split('\t')[0]:json.loads(bytes.fromhex(line.split('\t')[1]).decode()) for line in typed.splitlines()}
        expected_typed = {}
        for r in rows:
            mapped = r | ({'process_id':r['process'],'source_sha256':r['source_snapshot_sha256']} if kind != 'NSO' else {})
            expected_typed[r['observation_id']] = {f:mapped[f] for f in fields}
        if actual_typed != expected_typed:
            raise RuntimeError('Typed subtype roundtrip mismatch')
        if kind != 'NSO':
            stored_process = query('USE tamsood_supplemental; SELECT process_id,reference_amount,HEX(reference_unit),HEX(geography),HEX(technology_level) FROM process WHERE snapshot_id='+literal(snapshot)).stdout.decode()
            actual_process = {p[0]:(Decimal(p[1]),*[bytes.fromhex(v).decode() for v in p[2:]]) for p in (line.split('\t') for line in stored_process.splitlines())}
            expected_process = {r['process']:(Decimal(r['reference_amount']),r['reference_unit'],r['geography'],r['technology_level']) for r in rows}
            if actual_process != expected_process:
                raise RuntimeError('Process reference basis mismatch')
        results.append(dict(kind=kind, snapshot_id=snapshot, records_checked=len(rows), subtype_records=count, full_payload_equal=True))
    # Invalid references and inventory directions must fail inside rollback-only transactions.
    checks = {}
    for label, statement, code in [
        ('orphan_observation', "INSERT INTO observation VALUES (REPEAT('0',64),REPEAT('0',64),1,'kg','STAGED_SOURCE_VERIFIED',JSON_OBJECT())", 1452),
        ('invalid_direction', "UPDATE inventory_exchange SET direction='SIDEWAYS' LIMIT 1", 3819)]:
        result = query('USE tamsood_supplemental; START TRANSACTION; ' + statement + '; ROLLBACK;', False)
        if result.returncode == 0 or ('ERROR ' + str(code)).encode() not in result.stderr:
            raise RuntimeError('Constraint check failed: ' + label)
        checks[label] = 'rejected_as_expected'
    evidence = dict(checked_at=datetime.now(timezone.utc).isoformat(), database='tamsood_supplemental',
        result='passed', datasets=results, constraint_checks=checks, acceptance_changed=False,
        schema_sha256=hashlib.sha256(schema.encode('utf-8')).hexdigest(),
        limitations=['Website still reads SQLite/JSON', 'Snapshots are versioned; counts must filter snapshot_id',
                     'Loading into MySQL does not establish full LCI eligibility or redistribution rights'])
    (ROOT/'evidence/supplemental-mysql.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
