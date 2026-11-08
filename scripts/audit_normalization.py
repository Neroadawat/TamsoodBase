"""Build a non-destructive normalization candidate; never migrate the live API DB."""
import hashlib
from contextlib import closing
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def build(source, target):
    source, target = Path(source), Path(target)
    if source.resolve() == target.resolve():
        raise ValueError('Candidate must not overwrite source')
    target.parent.mkdir(parents=True, exist_ok=True)
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    with closing(sqlite3.connect(f'{source.resolve().as_uri()}?mode=ro', uri=True)) as old:
        old.row_factory = sqlite3.Row
        if old.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or old.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Source database integrity failed')
        conflicts = old.execute('SELECT COUNT(*) FROM metric m JOIN context c USING(context_id) WHERE m.document_id<>c.document_id').fetchone()[0]
        if conflicts:
            raise ValueError('Existing context/document inconsistency: migration refused')
        # A fresh in-memory DB avoids partially replacing an earlier candidate on failure.
        with closing(sqlite3.connect(':memory:')) as new:
            new.execute('PRAGMA foreign_keys=ON')
            objects = old.execute("SELECT type,name,sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY rowid").fetchall()
            for obj in objects:
                if obj['type'] != 'table':
                    continue
                ddl = obj['sql']
                if obj['name'] == 'metric':
                    ddl = '''CREATE TABLE metric (
                        metric_key TEXT PRIMARY KEY NOT NULL,
                        source_metric_id TEXT NOT NULL,label TEXT NOT NULL,
                        context_id TEXT NOT NULL REFERENCES context(context_id),
                        unit_code TEXT NOT NULL REFERENCES unit(unit_code),
                        data_kind TEXT NOT NULL,aggregation_role TEXT NOT NULL)'''
                new.execute(ddl)
            # Existing builder table order is dependency order; insert with deferred checks.
            new.execute('PRAGMA defer_foreign_keys=ON')
            for obj in objects:
                if obj['type'] != 'table':
                    continue
                name = obj['name']
                columns = [r[1] for r in new.execute(f'PRAGMA table_info("{name}")')]
                fields = ','.join('"'+c+'"' for c in columns)
                rows = old.execute(f'SELECT {fields} FROM "{name}"').fetchall()
                new.executemany(f'INSERT INTO "{name}" ({fields}) VALUES ({",".join("?" for _ in columns)})', [tuple(r) for r in rows])
            for obj in objects:
                if obj['type'] in ('view', 'index', 'trigger'):
                    ddl = obj['sql'].replace('d.document_id=m.document_id', 'd.document_id=c.document_id')
                    new.execute(ddl)
            new.commit()
            if new.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Candidate foreign keys failed')
            columns = [r[1] for r in old.execute('PRAGMA table_info(metric)')]
            fields = ','.join('c.document_id' if c == 'document_id' else 'm.'+c for c in columns)
            reconstructed = sorted(new.execute(f'SELECT {fields} FROM metric m JOIN context c USING(context_id)').fetchall())
            if reconstructed != sorted(tuple(r) for r in old.execute('SELECT * FROM metric')):
                raise ValueError('Metric reconstruction changed source values')
            counts = {}
            for view in ('reference_catalog', 'accepted_reference'):
                before = sorted(tuple(r) for r in old.execute(f'SELECT * FROM {view}'))
                after = sorted(new.execute(f'SELECT * FROM {view}').fetchall())
                if before != after:
                    raise ValueError(view + ' changed')
                counts[view] = len(after)
            with closing(sqlite3.connect(target)) as output:
                new.backup(output)
    if hashlib.sha256(source.read_bytes()).hexdigest() != original_hash:
        raise ValueError('Source database changed during audit')
    return {'source_sha256': original_hash, 'source_unchanged': True,
            'candidate': str(target.relative_to(ROOT)) if target.is_relative_to(ROOT) else str(target),
            'context_document_conflicts': conflicts, 'metric_lossless_reconstruction': True,
            'catalog_all_columns_equal': True, 'foreign_key_check': 'PASS',
            'counts': counts, 'scope': 'metric decomposition only; no whole-schema 5NF certification',
            'production_migrated': False}


if __name__ == '__main__':
    result = build(ROOT/'build/reusable/reference.sqlite', ROOT/'build/normalization/reference-candidate.sqlite')
    evidence = ROOT/'evidence/normalization-audit.json'
    evidence.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
