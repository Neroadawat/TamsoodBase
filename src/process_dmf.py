"""Offline processing of exact public DMF snapshots into traceable candidates."""
import calendar
import csv
import hashlib
import io
import json
import sqlite3
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = {
    'production-oil': ('OIL',),
    'production-condensate': ('CONDENSATE', 'CONDENSATE_EQUI_OIL'),
    'production-natural-gas': ('GAS', 'GAS_EQUI_OIL'),
}
BASE = ['YEAR', 'MONTH', 'BLOCK_TYPE', 'BLOCK', 'SOURCE_GROUP']


def sha(body):
    return hashlib.sha256(body).hexdigest()


def validate(row, amount_column):
    errors = []
    try:
        year, month = int(row['YEAR'])-543, int(row['MONTH'])
        last_day = calendar.monthrange(year, month)[1]
        days = Decimal(row['DAYSOFPRODUCE'])
        if not days.is_finite() or days != days.to_integral_value() or not 0 <= days <= last_day:
            errors.append('invalid_days_of_production')
    except (ValueError, TypeError, KeyError, InvalidOperation):
        errors.append('invalid_period_or_days')
    try:
        amount = Decimal(row[amount_column])
        if not amount.is_finite() or amount < 0:
            errors.append('invalid_amount')
    except (KeyError, TypeError, InvalidOperation):
        errors.append('invalid_amount')
    if row.get('BLOCK_TYPE') not in ('บนบก', 'ในทะเล'):
        errors.append('unknown_area')
    if not (row.get('SOURCE_GROUP') or '').strip():
        errors.append('missing_source_group')
    return errors


def process(run_id=None):
    if run_id is None:
        run_id = json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
    if Path(run_id).name != run_id or run_id in ('.', '..'):
        raise ValueError('Invalid run ID')
    raw = ROOT/'data/raw/dmf'/run_id
    manifest = json.loads((raw/'manifest.json').read_text(encoding='utf-8'))
    if not manifest.get('complete'):
        raise ValueError('Incomplete acquisition')
    out = ROOT/'build/dmf'/run_id
    out.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(':memory:')
    con.executescript('''
    PRAGMA foreign_keys=ON;
    CREATE TABLE resource(package TEXT PRIMARY KEY, url TEXT NOT NULL, csv_sha256 TEXT NOT NULL,
        metadata_sha256 TEXT NOT NULL, license_label TEXT, metadata_unit TEXT, acquired_at TEXT NOT NULL);
    CREATE TABLE staging(package TEXT NOT NULL REFERENCES resource, source_line INTEGER NOT NULL,
        raw_json TEXT NOT NULL, PRIMARY KEY(package,source_line));
    CREATE TABLE candidate(package TEXT NOT NULL, source_line INTEGER NOT NULL,
        year_ce INTEGER NOT NULL, month INTEGER NOT NULL, area TEXT NOT NULL,
        block_label TEXT, source_group TEXT NOT NULL, amount_column TEXT NOT NULL,
        raw_value TEXT NOT NULL, decimal_value TEXT NOT NULL, production_days TEXT NOT NULL,
        identity_sha256 TEXT NOT NULL, duplicate_of_line INTEGER,
        review_status TEXT NOT NULL CHECK(review_status='PENDING'),
        PRIMARY KEY(package,source_line), FOREIGN KEY(package,source_line) REFERENCES staging);
    CREATE TABLE rejected(package TEXT NOT NULL,source_line INTEGER NOT NULL,reasons_json TEXT NOT NULL,
        PRIMARY KEY(package,source_line), FOREIGN KEY(package,source_line) REFERENCES staging);
    CREATE VIEW traceable_candidate AS SELECT c.*,r.url,r.csv_sha256,r.metadata_unit,r.license_label,
        r.acquired_at,s.raw_json FROM candidate c JOIN resource r USING(package)
        JOIN staging s USING(package,source_line);
    ''')
    summary = {'run_id':run_id, 'packages':[], 'competition_accepted':0,
               'review_gates':['unit_time_basis', 'license_terms', 'numerical_external_review', 'LCI_eligibility', 'duplicate_resolution']}
    for entry in manifest['packages']:
        name = entry['package']
        columns = COLUMNS[name]
        body = (raw/(name+'.csv')).read_bytes()
        meta_body = (raw/(name+'.metadata.json')).read_bytes()
        if sha(body) != entry['csv_sha256'] or sha(meta_body) != entry['metadata_sha256']:
            raise ValueError('Snapshot checksum mismatch: '+name)
        metadata = json.loads(meta_body)['result']
        con.execute('INSERT INTO resource VALUES(?,?,?,?,?,?,?)', (name,entry['csv_url'],sha(body),sha(meta_body),
                    metadata.get('license_id'),entry.get('resource_unit'),manifest['acquired_at']))
        # CSV supplied in Thai Windows encoding. Strict decoding; never replace bad bytes.
        reader = csv.DictReader(io.StringIO(body.decode('cp874'), newline=''))
        expected = BASE + list(columns) + ['DAYSOFPRODUCE']
        if reader.fieldnames != expected:
            raise ValueError('Source schema changed: '+name)
        counts = Counter(); periods = []; seen = {}; first_values = {}; flags = Counter(); unique = set()
        for row in reader:
            line = reader.line_num
            counts['raw_rows'] += 1
            con.execute('INSERT INTO staging VALUES(?,?,?)',(name,line,json.dumps(row,ensure_ascii=False)))
            errors = validate(row,columns[0])
            if None in row or any(v is None for v in row.values()):
                errors.append('malformed_csv_row')
            if errors:
                counts['rejected'] += 1
                flags.update(errors)
                con.execute('INSERT INTO rejected VALUES(?,?,?)',(name,line,json.dumps(errors)))
                continue
            year, month = int(row['YEAR'])-543, int(row['MONTH'])
            identity = json.dumps([name,year,month,row['BLOCK_TYPE'],row['BLOCK'],row['SOURCE_GROUP']],ensure_ascii=False)
            key = sha(identity.encode())
            duplicate = seen.get(key)
            if duplicate is not None:
                flags['duplicate_identity'] += 1
                if Decimal(row[columns[0]]) != first_values[key]:
                    flags['duplicate_conflicting_amount'] += 1
            else:
                seen[key] = line
                first_values[key] = Decimal(row[columns[0]])
            unique.add(key)
            if not row['BLOCK'].strip(): flags['missing_block_label'] += 1
            value = Decimal(row[columns[0]])
            if value == 0: flags['zero_amount'] += 1
            periods.append(f'{year:04}-{month:02}')
            con.execute('INSERT INTO candidate VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (name,line,year,month,row['BLOCK_TYPE'],row['BLOCK'] or None,row['SOURCE_GROUP'],columns[0],
                 row[columns[0]],str(value),row['DAYSOFPRODUCE'],key,duplicate,'PENDING'))
            counts['structural_pass'] += 1
        summary['packages'].append({'package':name,'title':metadata['title'], **counts,
            'unique_candidate_identities':len(unique),'period_min':min(periods) if periods else None,
            'period_max':max(periods) if periods else None,'flags':dict(flags),
            'metadata_last_year_be':metadata.get('last_year_of_data'),
            'metadata_unit':metadata.get('unit_of_measure'),'metadata_multiplier':metadata.get('unit_of_multiplier'),
            'ckan_isopen':metadata.get('isopen'), 'license_label':metadata.get('license_id'),
            'excluded_equivalent_columns':list(columns[1:])})
    assert not con.execute('PRAGMA foreign_key_check').fetchall()
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    con.commit()
    with sqlite3.connect(out/'candidates.sqlite') as target: con.backup(target)
    with (out/'candidates.csv').open('w',encoding='utf-8-sig',newline='') as f:
        cursor = con.execute('SELECT package,source_line,year_ce,month,area,block_label,source_group,amount_column,raw_value,decimal_value,production_days,duplicate_of_line,review_status,url,csv_sha256 FROM traceable_candidate ORDER BY package,source_line')
        writer=csv.writer(f);writer.writerow([d[0] for d in cursor.description]);writer.writerows(cursor)
    with (out/'duplicate-review.csv').open('w',encoding='utf-8-sig',newline='') as f:
        cursor=con.execute('''SELECT a.package,a.source_line,a.duplicate_of_line,a.year_ce,a.month,
            a.source_group,a.raw_value AS later_value,b.raw_value AS first_value,
            a.identity_sha256 FROM candidate a JOIN candidate b
            ON a.package=b.package AND a.duplicate_of_line=b.source_line
            ORDER BY a.package,a.source_line''')
        writer=csv.writer(f);writer.writerow([d[0] for d in cursor.description]);writer.writerows(cursor)
    with (out/'rejected.csv').open('w',encoding='utf-8-sig',newline='') as f:
        cursor=con.execute('SELECT * FROM rejected JOIN staging USING(package,source_line)')
        writer=csv.writer(f);writer.writerow([d[0] for d in cursor.description]);writer.writerows(cursor)
    con.close()
    summary['raw_rows'] = sum(p.get('raw_rows',0) for p in summary['packages'])
    summary['structural_pass'] = sum(p.get('structural_pass',0) for p in summary['packages'])
    summary['rejected'] = sum(p.get('rejected',0) for p in summary['packages'])
    (out/'quality-report.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return summary


if __name__ == '__main__':
    process()
