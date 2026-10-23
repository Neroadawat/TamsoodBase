"""Import downloaded official NSO CSVs, retaining table/row/column evidence."""
import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sqlite3
from collections import Counter
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='https://www.nso.go.th/public/e-book/Statistical-Yearbook/SYB-2026_webPage/'
TABLES=('13.5','13.6','13.7','13.8','13.10')


def unit_for(table,row):
    if table=='13.5':return '10^3 ton of oil equivalent'
    if table=='13.6':return 'Million litre'
    if table=='13.7':
        if row[0].startswith('ปริมาณ'):return 'Million litre'
        if row[0].startswith('มูลค่า'):return 'Million Baht'
        raise ValueError('Unknown import measure')
    if table=='13.8':return 'Thousand kilogram' if '(1)' in row[0] else 'Thousand litre'
    if table=='13.10':
        if row[0]=='จำนวน':return '10^3 ton of oil equivalent'
        if row[0]=='ร้อยละ':return 'percent'
        raise ValueError('Unknown manufacturing measure')
    raise ValueError('Unsupported table')


def parse(body,table,source_url):
    text=body.decode('utf-8-sig')
    if table=='13.8' and 'Quantities in thousand kilogram' not in text:
        raise ValueError('Mass footnote missing')
    reader=csv.reader(io.StringIO(text,newline=''))
    indexed=[]
    for row in reader:indexed.append((reader.line_num,row))
    candidates=[(line,row) for line,row in indexed if any(re.fullmatch(r'25\d{2} \(20\d{2}\)',cell.strip()) for cell in row)]
    if len(candidates)!=1:raise ValueError('Expected one year header')
    header_line,header=candidates[0]
    years=[(column,int(cell.split('(')[1][:4])) for column,cell in enumerate(header) if re.fullmatch(r'25\d{2} \(20\d{2}\)',cell.strip())]
    if not years:raise ValueError('No data years')
    if any(int(header[column].split()[0])-543!=year for column,year in years):
        raise ValueError('Buddhist and Gregorian years disagree')
    if len({year for _,year in years})!=len(years):raise ValueError('Duplicate year columns')
    source=[row[0].strip() for _,row in indexed if row and row[0].strip().startswith('Source:')]
    if len(source)!=1:raise ValueError('Source agency not unique')
    footer=[row[0] for line,row in indexed if line>header_line and row and not any(column<len(row) and re.fullmatch(r'-?\d+(?:\.\d+)?',row[column].strip()) for column,_ in years) and row[0].strip()]
    rows=[];digest=hashlib.sha256(body).hexdigest()
    ended=False
    for line,row in indexed:
        if line<=header_line:continue
        if not any(cell.strip() for cell in row):
            ended=True
            continue
        if ended:continue
        if len(row)!=len(header):raise ValueError('Column count changed')
        label=row[0] if table=='13.8' else row[1] or row[0]
        group='Sales' if table=='13.8' else row[0]
        unit=unit_for(table,row)
        for column,year in years:
            raw=row[column].strip()
            if not re.fullmatch(r'-?\d+(?:\.\d+)?',raw):raise ValueError('Missing or nonnumeric cell: '+str((table,line,column)))
            amount=Decimal(raw)
            if amount<0 and table!='13.5':raise ValueError('Unexpected negative')
            identity=hashlib.sha256(json.dumps([digest,line,column+1],separators=(',',':')).encode()).hexdigest()
            rows.append(dict(observation_id=identity,table_id=table,publication_year=2026,reference_year=year,
                publisher='National Statistical Office of Thailand',originating_agency=source[0].removeprefix('Source:').strip(),
                label=label,measure=group,raw_value=raw,amount=str(amount),unit=unit,geography='Thailand',
                data_kind='NATIONAL_ENERGY_STATISTIC',status='STAGED_SOURCE_VERIFIED',is_normalized_lci_exchange=False,
                source_url=source_url,source_sha256=digest,source_line=line,source_column=column+1,
                source_header=header[column],source_row=row,notes=footer,rights_status='PUBLIC_DOWNLOAD_REUSE_SCOPE_UNCONFIRMED'))
    if not rows:raise ValueError('No observations parsed')
    if len({(r['measure'],r['label'],r['reference_year']) for r in rows})!=len(rows):raise ValueError('Duplicate metric identity')
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--download-dir',type=Path);args=parser.parse_args()
    raw=ROOT/'data/raw/nso/yearbook-2026';raw.mkdir(parents=True,exist_ok=True)
    manifest_path=raw/'manifest.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {'acquisition_method':'Official website download links via browser; direct HTTP returned 418','resources':{}}
    all_rows=[]
    for table in TABLES:
        name=f'T_{table}_2026.csv';target=raw/name;url=BASE+f'File_SYB/2026/13/{name}'
        if args.download_dir:
            body=(args.download_dir/name).read_bytes();parse(body,table,url)
            if target.exists() and target.read_bytes()!=body:raise ValueError('Snapshot exists with different bytes; create a new version')
            if not target.exists():shutil.copyfile(args.download_dir/name,target)
            manifest['resources'].setdefault(table,dict(url=url,sha256=hashlib.sha256(body).hexdigest(),acquired_at=datetime.now(timezone.utc).isoformat()))
        body=target.read_bytes()
        if hashlib.sha256(body).hexdigest()!=manifest['resources'][table]['sha256']:raise ValueError('Snapshot hash mismatch')
        all_rows.extend(parse(body,table,url))
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    out=ROOT/'build/nso';out.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(out/'nso.sqlite')
    con.execute('CREATE TABLE IF NOT EXISTS observation (observation_id TEXT PRIMARY KEY,table_id TEXT NOT NULL,reference_year INTEGER NOT NULL,measure TEXT NOT NULL,label TEXT NOT NULL,amount TEXT NOT NULL,unit TEXT NOT NULL,payload TEXT NOT NULL,UNIQUE(table_id,measure,label,reference_year))')
    with con:
        con.execute('DELETE FROM observation')
        con.executemany('INSERT INTO observation VALUES (?,?,?,?,?,?,?,?)',[(r['observation_id'],r['table_id'],r['reference_year'],r['measure'],r['label'],r['amount'],r['unit'],json.dumps(r,ensure_ascii=False)) for r in all_rows])
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity failed')
    stored=con.execute('SELECT payload FROM observation ORDER BY observation_id').fetchall();con.close()
    if sorted(all_rows,key=lambda r:r['observation_id'])!=[json.loads(r[0]) for r in stored]:raise ValueError('Database roundtrip mismatch')
    report=dict(title='NSO Yearbook 2026: selected energy tables',rows=all_rows,row_count=len(all_rows),
                counts_by_table=dict(Counter(r['table_id'] for r in all_rows)),source_manifest=manifest,
                accepted_reference=0,normalized_lci_exchanges=0,scope='National annual statistics; not plant/product inventory',
                warnings=['NSO republishes DEDE/DOEB data; do not count republication as independent measurements',
                          'Table13.5 net supply may be negative; keep sign and stock-change definition',
                          'Table13.8 footnote(1) uses mass, overriding general volume header',
                          'Table13.7 monetary values and Table13.10 percentages are context, not material flows',
                          'Tables/years may overlap other datasets; no summation across tables'])
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','source_manifest')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
