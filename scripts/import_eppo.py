"""Rebuild two EPPO source-statistic datasets offline; never infer refinery yields."""
import csv
import hashlib
import io
import json
import re
import sqlite3
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONTHS = {name:i+1 for i,name in enumerate(('January February March April May June July August September October November December').split())}
SPECS = {'11_13':('Company','BBL/DAY','REFINERY_MATERIAL_INTAKE','COMPANY_REFINERY_STATISTIC'),
         '11_14':('Product','Million Litres','PETROLEUM_PRODUCT_PRODUCTION','NATIONAL_PRODUCT_STATISTIC')}


def parse(body, dataset, source):
    subject, unit, activity, scope = SPECS[dataset]
    if hashlib.sha256(body).hexdigest() != source['sha256']:
        raise ValueError('Source snapshot hash mismatch')
    reader = csv.DictReader(io.StringIO(body.decode('utf-8-sig')))
    if reader.fieldnames != ['Year','Month',subject,'Quantity','UNIT']:
        raise ValueError('Unexpected source columns')
    result=[]; identities=set()
    for raw in reader:
        if None in raw or any(v is None for v in raw.values()):
            raise ValueError('Malformed CSV row')
        if not re.fullmatch(r'\d{4}',raw['Year']) or not 1900 <= int(raw['Year']) <= 2100:
            raise ValueError('Invalid Gregorian year')
        if raw['Month'] not in MONTHS or raw['UNIT'] != unit or not raw[subject].strip():
            raise ValueError('Unknown month/unit/subject')
        if not re.fullmatch(r'\d+(?:\.\d+)?',raw['Quantity']):
            raise ValueError('Invalid source amount')
        identity=(int(raw['Year']),MONTHS[raw['Month']],raw[subject])
        if identity in identities:
            raise ValueError('Duplicate source business key')
        identities.add(identity)
        oid=hashlib.sha256(f"{source['sha256']}:{reader.line_num}".encode()).hexdigest()
        result.append(dict(observation_id=oid,dataset_id=dataset,reference_year=identity[0],month=identity[1],
            subject=raw[subject],subject_type=subject,activity=activity,scope=scope,
            amount=str(Decimal(raw['Quantity'])),raw_value=raw['Quantity'],unit=unit,
            geography='Thailand',publisher='Energy Policy and Planning Office',originating_agency=source['originating_agency'],
            status='STAGED_SOURCE_VERIFIED',is_normalized_lci_exchange=False,
            source_url=source['url'],source_sha256=source['sha256'],source_line=reader.line_num,
            source_column='Quantity',source_row=raw,acquired_at=source['acquired_at'],
            license_label=source['license_label'],rights_status='CATALOG_OPEN_DATA_COMMON_LABEL_OBSERVED',
            redistribution_status='SPECIFIC_TERMS_NOT_YET_VERIFIED',
            temporal_basis='Reported BBL/DAY for the named month; no monthly-total conversion' if dataset=='11_13' else 'Monthly quantity reported in Million Litres'))
    if not result:raise ValueError('Empty dataset')
    return result


def main():
    folder=ROOT/'data/raw/eppo';manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    rows=[]
    for dataset in SPECS:
        src=manifest['resources'][dataset]
        rows.extend(parse((folder/src['filename']).read_bytes(),dataset,src))
    out=ROOT/'build/eppo';out.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(out/'eppo.sqlite');con.execute('PRAGMA foreign_keys=ON')
    con.executescript('''CREATE TABLE IF NOT EXISTS source_snapshot(snapshot_id TEXT PRIMARY KEY,dataset_id TEXT NOT NULL,url TEXT NOT NULL,payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS observation(observation_id TEXT PRIMARY KEY,snapshot_id TEXT NOT NULL REFERENCES source_snapshot(snapshot_id),reference_year INTEGER NOT NULL,month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),subject TEXT NOT NULL,amount TEXT NOT NULL,unit TEXT NOT NULL,payload TEXT NOT NULL,UNIQUE(snapshot_id,reference_year,month,subject));''')
    with con:
        for src in manifest['resources'].values():
            con.execute('INSERT OR IGNORE INTO source_snapshot VALUES (?,?,?,?)',(src['sha256'],next(r['dataset_id'] for r in rows if r['source_sha256']==src['sha256']),src['url'],json.dumps(src,ensure_ascii=False)))
        for r in rows:
            values=(r['observation_id'],r['source_sha256'],r['reference_year'],r['month'],r['subject'],r['amount'],r['unit'],json.dumps(r,ensure_ascii=False))
            con.execute('INSERT OR IGNORE INTO observation VALUES (?,?,?,?,?,?,?,?)',values)
    for dataset in SPECS:
        digest=manifest['resources'][dataset]['sha256']
        stored={r[0]:(r[1],r[2],json.loads(r[3])) for r in con.execute('SELECT observation_id,amount,unit,payload FROM observation WHERE snapshot_id=?',(digest,))}
        expected={r['observation_id']:(r['amount'],r['unit'],r) for r in rows if r['dataset_id']==dataset}
        if stored!=expected:raise ValueError('SQLite roundtrip mismatch')
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity failed')
    con.close()
    report=dict(rows=rows,row_count=len(rows),counts_by_dataset=dict(Counter(r['dataset_id'] for r in rows)),
        actual_period=[min((r['reference_year'],r['month']) for r in rows),max((r['reference_year'],r['month']) for r in rows)],
        normalized_lci_exchanges=0,accepted_reference=0,
        limitations=['Company intake and national product totals cannot be joined into plant yield',
            'BBL/DAY and Million Litres are distinct quantity/time bases; no conversion or division applied',
            'Catalog metadata last year 2567 is stale relative to actual CSV through July2026',
            'Reported company labels retained; no automatic historical merger/rebranding mapping',
            'Originating agency DOEB may overlap NSO; republications are not independent measurements',
            '2026 is partial-year; no annualized totals',
            'Open Data Common catalog label observed; specific redistribution terms not verified'])
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    evidence={k:v for k,v in report.items() if k!='rows'}
    evidence.update(source_manifest=manifest,sqlite_roundtrip='passed',duplicate_business_keys=0)
    (ROOT/'evidence/eppo-import.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in evidence.items() if k not in ('source_manifest','limitations')},indent=2))


if __name__=='__main__':main()
