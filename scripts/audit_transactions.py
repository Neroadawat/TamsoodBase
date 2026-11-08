"""Transaction experiments on a disposable copy of the real EPPO schema/data.

Never modifies a project database. This is SQLite evidence, not MySQL evidence.
"""
import hashlib
import json
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(source):
    source = Path(source).resolve()
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    checks = {}
    with tempfile.TemporaryDirectory(prefix='tamsood-transactions-') as directory:
        target = Path(directory) / 'lab.sqlite'
        with closing(sqlite3.connect(source.as_uri()+'?mode=ro', uri=True)) as original:
            with closing(sqlite3.connect(target)) as copy:
                original.backup(copy)
        with closing(sqlite3.connect(target, isolation_level=None)) as writer, closing(sqlite3.connect(target, isolation_level=None, timeout=0.1)) as other:
            writer.execute('PRAGMA foreign_keys=ON')
            writer.execute('PRAGMA journal_mode=DELETE')
            identity, old_month = writer.execute('SELECT observation_id,month FROM observation ORDER BY observation_id LIMIT 1').fetchone()
            # Changing an indexed business-key column may collide with a real row;
            # use a non-key amount instead and retain the original decimal string.
            old_amount = writer.execute('SELECT amount FROM observation WHERE observation_id=?',(identity,)).fetchone()[0]
            changed_amount = '0' if old_amount != '0' else '1'
            try:
                with writer:  # explicit BEGIN is needed with isolation_level=None
                    writer.execute('BEGIN IMMEDIATE')
                    writer.execute('UPDATE observation SET amount=? WHERE observation_id=?',(changed_amount,identity))
                    writer.execute('UPDATE observation SET month=13 WHERE observation_id=?',(identity,))
            except sqlite3.IntegrityError:
                checks['constraint_failure_rolls_back_entire_transaction'] = writer.execute('SELECT amount,month FROM observation WHERE observation_id=?',(identity,)).fetchone() == (old_amount,old_month)
            else:
                checks['constraint_failure_rolls_back_entire_transaction'] = False
            writer.execute('BEGIN IMMEDIATE')
            try:
                writer.execute('UPDATE observation SET amount=? WHERE observation_id=?',(changed_amount,identity))
                checks['other_connection_cannot_read_uncommitted_change'] = other.execute('SELECT amount FROM observation WHERE observation_id=?',(identity,)).fetchone()[0] == old_amount
                try:
                    other.execute('BEGIN IMMEDIATE')
                except sqlite3.OperationalError as error:
                    checks['concurrent_writer_is_blocked'] = error.sqlite_errorcode == sqlite3.SQLITE_BUSY
                else:
                    other.rollback()
                    checks['concurrent_writer_is_blocked'] = False
                writer.commit()
            finally:
                writer.rollback()
            checks['commit_visible_to_other_connection'] = other.execute('SELECT amount FROM observation WHERE observation_id=?',(identity,)).fetchone()[0] == changed_amount
        with closing(sqlite3.connect(target)) as reopened:
            checks['commit_survives_connection_reopen'] = reopened.execute('SELECT amount FROM observation WHERE observation_id=?',(identity,)).fetchone()[0] == changed_amount
    checks['source_database_bytes_unchanged'] = hashlib.sha256(source.read_bytes()).hexdigest() == before
    return {'checked_at':datetime.now(timezone.utc).isoformat(), 'engine':'SQLite',
            'sqlite_version':sqlite3.sqlite_version, 'source_sha256':before,
            'scope':'Disposable copy only; altered lab values are not project observations',
            'checks':checks, 'passed':all(checks.values()),
            'limitations':['No MySQL isolation experiment', 'Reopening is not a simulated power failure',
                           'Single SQLite writer serialization is not production load testing']}


if __name__ == '__main__':
    result = audit(ROOT/'build/eppo/eppo.sqlite')
    (ROOT/'evidence/transaction-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
