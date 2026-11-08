"""Read-only approved card-to-observation lookup; no generated SQL or Cypher."""
import hashlib
import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LineageUnavailable(RuntimeError):
    """Local evidence state failed verification; not a malformed client request."""


class Lineage:
    def __init__(self):
        self.manifest = json.loads((ROOT / 'build/handoff/current.json').read_bytes())
        self.path = (ROOT / self.manifest['database']).resolve()
        if not self.path.is_relative_to((ROOT / 'build/handoff/releases').resolve()):
            raise LineageUnavailable('Invalid lineage location')
        if hashlib.sha256(self.path.read_bytes()).hexdigest() != self.manifest['database_sha256']:
            raise LineageUnavailable('Lineage database changed')
        if hashlib.sha256((ROOT / 'docs/rag/public-evidence.json').read_bytes()).hexdigest() != self.manifest['corpus_sha256']:
            raise LineageUnavailable('Lineage corpus changed; rebuild the review store')

    @contextmanager
    def connect(self):
        if hashlib.sha256(self.path.read_bytes()).hexdigest() != self.manifest['database_sha256']:
            raise LineageUnavailable('Lineage database changed')
        con = sqlite3.connect(self.path.as_uri() + '?mode=ro', uri=True)
        try: yield con
        finally: con.close()

    def observation(self, oid):
        if not isinstance(oid, str) or not re.fullmatch('[a-f0-9]{64}', oid): raise ValueError('Invalid observation ID')
        with self.connect() as con:
            row = con.execute('SELECT payload FROM observation WHERE id=? AND public=1', (oid,)).fetchone()
        if row is None: raise LookupError('No approved public observation')
        return json.loads(row[0])

    def card(self, card_id):
        with self.connect() as con:
            records = con.execute('SELECT o.id,o.payload FROM card_observation c JOIN observation o ON o.id=c.observation_id WHERE c.card_id=? AND o.public=1 ORDER BY o.id', (card_id,)).fetchall()
        return {'release': self.manifest['release'], 'count': len(records),
                'relation': 'SUPPORTING_SOURCE_ROWS_NOT_A_CALCULATED_TOTAL',
                'observations': [{'observation_id': oid, 'process': r['process'], 'flow': r['flow'],
                                  'amount': r['amount'], 'unit': r['unit'], 'status': r['status'],
                                  'evidence_url': '/evidence?id=' + oid}
                                 for oid, payload in records[:3] for r in [json.loads(payload)]]}
