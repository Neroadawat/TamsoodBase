"""Export validated pilot rows to deterministic MySQL SQL; never promote acceptance."""
import hashlib
import json
import sqlite3
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def literal(value):
    # Hex strings avoid quoting/SQL-mode ambiguity for externally supplied text.
    return "CONVERT(X'" + str(value).encode('utf-8').hex() + "' USING utf8mb4)"


def export():
    evidence = json.loads((ROOT / 'evidence/dmf_pilot.json').read_text(encoding='utf-8'))
    with sqlite3.connect(ROOT / 'build/pilot.sqlite') as con:
        con.row_factory = sqlite3.Row
        rows = con.execute('SELECT * FROM observation ORDER BY record_id').fetchall()
        batch = dict(con.execute('SELECT * FROM batch').fetchone())
        source = dict(con.execute('SELECT * FROM source').fetchone())
    # Content address includes evidence + exporter + schema, not only CSV.
    batch_id = hashlib.sha256((batch['input_sha256'] + batch['evidence_sha256']
        + hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        + hashlib.sha256((ROOT / 'sql/mysql/schema.sql').read_bytes()).hexdigest()).encode()).hexdigest()
    sql = ['SET NAMES utf8mb4;', 'USE tamsood_pilot;', 'START TRANSACTION;']

    def insert(table, values):
        # No IGNORE: constraint violations must remain visible.
        sql.append(f"INSERT INTO {table} VALUES ({','.join(literal(v) for v in values)});")

    # Shared immutable lookup rows may already exist after a previous import.
    sql.append('INSERT INTO source VALUES (' + ','.join(literal(source[k]) for k in ('source_id','publisher','url','rights_status')) + ') ON DUPLICATE KEY UPDATE source_id=source_id;')
    sql.append('INSERT INTO unit VALUES (' + literal('million_ft3_per_day') + ',' + literal('Million cubic feet per day; source basis retained') + ') ON DUPLICATE KEY UPDATE unit_code=unit_code;')
    # Replacing only this exact content-addressed batch makes reruns idempotent.
    sql.append('DELETE FROM observation WHERE batch_id=' + literal(batch_id) + ';')
    sql.append('DELETE FROM extraction_batch WHERE batch_id=' + literal(batch_id) + ';')
    insert('extraction_batch', [batch_id, source['source_id'], batch['input_sha256'], batch['evidence_sha256'], batch['code_sha256'], evidence['accessed_date'], evidence['method'], evidence['evidence_level']])
    for row in rows:
        value = Decimal(row['value_decimal'])
        if not value.is_finite() or value < 0 or value >= Decimal('1e14') or value != value.quantize(Decimal('0.000001')):
            raise ValueError('Pilot amount cannot be represented exactly in DECIMAL(20,6)')
        context = [source['source_id'], row['area'], row['block'], row['field']]
        context_id = hashlib.sha256(json.dumps(context, ensure_ascii=False).encode()).hexdigest()
        sql.append('INSERT INTO production_context VALUES (' + ','.join(literal(v) for v in [context_id] + context) + ') ON DUPLICATE KEY UPDATE context_id=context_id;')
        insert('observation', [row['record_id'], batch_id, context_id, row['period']+'-01', row['fuel'], row['raw_value'], value, row['unit_code'], row['evidence_locator'], 'PENDING'])
    sql.append('COMMIT;')
    target = ROOT / 'build/mysql-pilot.sql'
    target.write_text('\n'.join(sql)+'\n', encoding='utf-8')
    print(f'Exported {len(rows)} pending records to {target}')
    return target


if __name__ == '__main__':
    export()
