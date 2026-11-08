"""Load the genuine newly acquired DMF snapshot into the isolated owned MySQL lab."""
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.verify_handoff_engines import docker, owned
from src.export_full_mysql import snapshot_id


def main():
    meta = json.loads((ROOT / 'build/handoff/engines.json').read_bytes()); name = meta['mysql_container']
    if not owned(name): raise ValueError('Owned MySQL lab missing')
    expected = json.loads((ROOT / 'build/full-mysql-expected.json').read_bytes())
    manifest = json.loads((ROOT / 'data/raw/dmf' / expected['run_id'] / 'manifest.json').read_bytes())
    if expected['snapshot_ids'] != [snapshot_id(r) for r in manifest['packages']]: raise ValueError('Snapshot identities differ')
    def sql(statement):
        return docker('exec', '-i', name, 'mysql', '-uroot', '--batch', '--skip-column-names', '--default-character-set=utf8mb4', body=statement, timeout=120).stdout.decode('utf-8')
    exists = int(sql("SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='tamsood_research';"))
    if not exists:
        sql((ROOT / 'sql/mysql/full-schema.sql').read_text(encoding='utf-8'))
        sql((ROOT / 'build/full-mysql.sql').read_text(encoding='utf-8'))
    returned = sql('SELECT o.snapshot_id,o.source_line,o.amount,d.status FROM tamsood_research.observation o JOIN tamsood_research.duplicate_disposition d USING(snapshot_id,source_line);')
    actual = {(s, int(line)): (Decimal(amount), status) for s, line, amount, status in (r.split('\t') for r in returned.splitlines())}
    wanted = {(s, line): (Decimal(amount), status) for s, line, amount, status in expected['rows']}
    if actual != wanted: raise ValueError('MySQL observation roundtrip differs')
    run = ROOT / 'build/dmf' / expected['run_id']
    with sqlite3.connect((run / 'candidates.sqlite').resolve().as_uri() + '?mode=ro', uri=True) as con:
        snapshots = {r['package']: snapshot_id(r) for r in manifest['packages']}
        original = {(snapshots[package], line): json.loads(payload) for package, line, payload in con.execute('SELECT package,source_line,raw_json FROM staging')}
    returned = sql('SELECT snapshot_id,source_line,HEX(raw_json) FROM tamsood_research.source_record;')
    restored = {(s, int(line)): json.loads(bytes.fromhex(payload)) for s, line, payload in (r.split('\t') for r in returned.splitlines())}
    if restored != original: raise ValueError('MySQL original raw payload differs')
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'container': name,
              'run_id': expected['run_id'], 'observations_equal': len(actual), 'raw_payloads_equal': len(restored),
              'scope': 'ISOLATED_LOCAL_NEW_SNAPSHOT_NOT_EC2_RESTORE', 'network': 'none', 'published_ports': [],
              'production_changed': False, 'passed': True}
    (ROOT / 'evidence/handoff-dmf-mysql-2026-11-08.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
