"""Local voluntary search feedback, bound to actual issued results."""
import json
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReviewInbox:
    def __init__(self, corpus_hash, path=None):
        self.corpus_hash = corpus_hash
        self.path = path or ROOT / '.local/rag-feedback.jsonl'
        self.pending = {}

    def issue(self, question, hits):
        self.pending = {k: v for k, v in self.pending.items() if time.monotonic() - v['started'] < 3600}
        if len(self.pending) >= 128: self.pending.pop(next(iter(self.pending)))
        token = secrets.token_urlsafe(24)
        self.pending[token] = {'started': time.monotonic(), 'question': question,
                               'card_ids': [h['id'] for h in hits]}
        return token

    def record(self, token, verdict, note=''):
        if not isinstance(token, str) or token not in self.pending: raise ValueError('Search expired or unknown')
        if verdict not in ('sufficient', 'insufficient', 'uncertain'): raise ValueError('Invalid verdict')
        if not isinstance(note, str) or len(note) > 1000: raise ValueError('Invalid note')
        item = self.pending[token]
        if time.monotonic() - item['started'] > 3600: raise ValueError('Search expired')
        record = {'recorded_at_utc': datetime.now(timezone.utc).isoformat(), 'corpus_sha256': self.corpus_hash,
                  'question': item['question'], 'card_ids': item['card_ids'], 'verdict': verdict,
                  'note': note.strip(), 'reviewer_identity': 'NOT_COLLECTED',
                  'independent_human_review_verified': False}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')
        del self.pending[token]
        return {'saved': True}
