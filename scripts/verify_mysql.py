"""Run isolated MySQL integration checks; removes only its own disposable container."""
import json
import os
import secrets
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify():
    # The user's machine already has the course's mysql:8.1 image.
    name = 'tamsood-check-' + secrets.token_hex(5)
    password = secrets.token_urlsafe(24)
    env = os.environ | {'MYSQL_ROOT_PASSWORD': password}

    def docker(*args, input=None, check=True):
        result = subprocess.run(['docker', *args], input=input, capture_output=True,
                                env=env, check=False, timeout=60)
        if check and result.returncode:
            raise RuntimeError(result.stderr.decode('utf-8', errors='replace').replace(password, '[redacted]'))
        return result

    def query(sql, check=True):
        return docker('exec','-i','-e','MYSQL_PWD='+password,name,
                      'mysql','-uroot','--default-character-set=utf8mb4','--batch','--skip-column-names',
                      input=sql.encode('utf-8'), check=check)

    started = False
    try:
        docker('run','--pull=never','--detach','--name',name,'--network','none',
               '-e','MYSQL_ROOT_PASSWORD','mysql:8.1')
        started = True
        deadline = time.monotonic()+90
        while query('SELECT 1;', check=False).returncode:
            if time.monotonic()>deadline:
                raise RuntimeError('Disposable MySQL did not become ready')
            time.sleep(2)
        schema = (ROOT / 'sql/mysql/schema.sql').read_text(encoding='utf-8')
        data = (ROOT / 'build/mysql-pilot.sql').read_text(encoding='utf-8')
        query(schema)
        query(data)
        query(data)
        result = query('USE tamsood_pilot; SELECT COUNT(*), SUM(amount), COUNT(DISTINCT context_id) FROM observation;').stdout.decode().strip()
        if result != '3\t662.650000\t3':
            raise AssertionError(result)
        # SUM above verifies fixture round-trip only; these three fields are not national coverage.
        tests = {
            'negative_amount': "UPDATE observation SET amount=-1 WHERE record_id='DMF-001'",
            'missing_source_fk': "INSERT INTO production_context VALUES(REPEAT('f',64),'missing','onshore','X','X')",
            'promotion_blocked': "UPDATE observation SET review_status='ACCEPTED' WHERE record_id='DMF-001'",
            'duplicate': 'INSERT INTO observation SELECT * FROM observation LIMIT 1',
        }
        expected = {'negative_amount': b'3819', 'missing_source_fk': b'1452', 'promotion_blocked': b'3819', 'duplicate': b'1062'}
        for key, sql in tests.items():
            failure = query('USE tamsood_pilot; '+sql+';', check=False)
            if failure.returncode == 0 or expected[key] not in failure.stderr:
                raise AssertionError(key + ': unexpected constraint result')
        output = query((ROOT / 'sql/mysql/queries.sql').read_text(encoding='utf-8')).stdout.decode('utf-8')
        report = {'mysql_version': query('SELECT VERSION();').stdout.decode().strip(),
                  'rows_after_two_imports': 3, 'exact_decimal_roundtrip': True,
                  'constraint_checks': list(tests), 'competition_accepted': 0}
        (ROOT / 'build/mysql-verification.json').write_text(json.dumps(report,indent=2), encoding='utf-8')
        (ROOT / 'build/mysql-query-results.tsv').write_text(output, encoding='utf-8')
        print(json.dumps(report,indent=2))
    finally:
        if started:
            docker('rm','--force',name)


if __name__ == '__main__':
    verify()
