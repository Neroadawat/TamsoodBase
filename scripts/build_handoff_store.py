"""Build a separate content-addressed review store from available real records."""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ('web/upstream-inventory.json', 'build/product-inventory/report.json',
          'build/nso/report.json', 'docs/rag/public-evidence.json')
SCHEMA = '''PRAGMA foreign_keys=ON;
CREATE TABLE source(snapshot TEXT PRIMARY KEY);
CREATE TABLE process(process_key TEXT PRIMARY KEY,snapshot TEXT NOT NULL REFERENCES source,name TEXT NOT NULL);
CREATE TABLE observation(id TEXT PRIMARY KEY,layer TEXT NOT NULL,snapshot TEXT NOT NULL REFERENCES source,
 process_key TEXT REFERENCES process,amount TEXT NOT NULL,unit TEXT,status TEXT NOT NULL,
 public INTEGER NOT NULL CHECK(public IN (0,1)),payload TEXT NOT NULL);
CREATE TABLE card_observation(card_id TEXT NOT NULL,observation_id TEXT NOT NULL REFERENCES observation,
 PRIMARY KEY(card_id,observation_id));
CREATE INDEX ix_card ON card_observation(card_id);
'''


def canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def verify_existing_release(prior, expected):
    """Do not bless changed lineage or process metadata when reusing a release."""
    for table, order in (('source', 'snapshot'), ('process', 'process_key'),
                         ('observation', 'id'), ('card_observation', 'card_id,observation_id')):
        if (list(prior.execute('PRAGMA table_info('+table+')')) != list(expected.execute('PRAGMA table_info('+table+')'))
                or list(prior.execute('SELECT * FROM '+table+' ORDER BY '+order))
                != list(expected.execute('SELECT * FROM '+table+' ORDER BY '+order))):
            raise ValueError('Existing immutable release differs: '+table)
    if prior.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or prior.execute('PRAGMA foreign_key_check').fetchall():
        raise ValueError('Existing immutable release integrity failed')


def main():
    inputs = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in INPUTS}
    inputs['builder_code'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    release = hashlib.sha256(canonical(inputs).encode()).hexdigest()
    directory = ROOT / 'build/handoff/releases' / release
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'review.sqlite'
    all_rows = []
    for layer, filename in zip(('upstream', 'foreground', 'nso'), INPUTS[:3]):
        all_rows.extend((layer, r) for r in json.loads((ROOT / filename).read_bytes())['rows'])
    con = sqlite3.connect(':memory:'); con.executescript(SCHEMA)
    expected = {}
    for layer, row in all_rows:
        oid = row['observation_id']
        if oid in expected: raise ValueError('Duplicate source identity')
        expected[oid] = row
        sha = row.get('source_snapshot_sha256') or row['source_sha256']
        con.execute('INSERT OR IGNORE INTO source VALUES(?)', (sha,))
        key = None
        if layer != 'nso':
            key = hashlib.sha256(canonical([sha, row['process']]).encode()).hexdigest()
            con.execute('INSERT OR IGNORE INTO process VALUES(?,?,?)', (key, sha, row['process']))
        public = layer != 'nso' and row.get('licence', '') == 'CC BY 4.0'
        # Upstream public projection carries the verified licence at the snapshot level.
        if layer == 'upstream': public = json.loads((ROOT / INPUTS[0]).read_bytes())['licence'] == 'CC BY 4.0'
        con.execute('INSERT INTO observation VALUES(?,?,?,?,?,?,?,?,?)',
                    (oid, layer, sha, key, row['amount'], row['unit'], row['status'], int(public), canonical(row)))
        cards = []
        if layer == 'foreground':
            cards = ['fame-functional-unit', 'fame-measurement-period']
            if row['process'] == 'FAME': cards.append('fame-allocation-caution')
        elif layer == 'upstream':
            cards = ['palm-upstream-basis']
            if row['flow'] == 'Land seeding': cards.append('palm-land-unit-hold')
            if row['process'] == 'CPO': cards.append('palm-cpo-provider-gap')
        for card in cards:
            con.execute('INSERT INTO card_observation VALUES(?,?)', (card, oid))
    con.commit()
    actual = {oid: json.loads(payload) for oid, payload in con.execute('SELECT id,payload FROM observation')}
    if actual != expected or con.execute('PRAGMA foreign_key_check').fetchall():
        raise ValueError('Review store roundtrip failed')
    if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': raise ValueError('Integrity failure')
    if path.exists():
        with sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True) as prior:
            verify_existing_release(prior, con)
    else:
        with sqlite3.connect(path) as dest: con.backup(dest)
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'release': release,
              'database': path.relative_to(ROOT).as_posix(), 'input_sha256': inputs,
              'corpus_sha256': inputs['docs/rag/public-evidence.json'],
              'database_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'counts': {name: con.execute('SELECT COUNT(*) FROM ' + name).fetchone()[0]
                         for name in ('source', 'process', 'observation', 'card_observation')},
              'by_layer': dict(con.execute('SELECT layer,COUNT(*) FROM observation GROUP BY layer')),
              'public_inventory_observations': con.execute('SELECT COUNT(*) FROM observation WHERE public=1').fetchone()[0],
              'full_payload_roundtrip': len(actual), 'integrity_check': True,
              'scope': 'LOCAL_REVIEW_RESTORATION_NOT_PRODUCTION_OR_FULL_LCI', 'production_changed': False}
    con.close()
    pointer = ROOT / 'build/handoff/current.json'; temporary = pointer.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8'); temporary.replace(pointer)
    (ROOT / 'evidence/handoff-store-2026-11-08.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
