"""Source-reported foreground inventory, preserving the paper's 1000 MJ basis."""
import hashlib
import json
import re
import sqlite3
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
URL='https://www.mdpi.com/2071-1050/12/22/9415'
DOI='10.3390/su12229415'


def extract(evidence,context,digest):
    if 'Life cycle inventory of 1000 MJ fuel.' not in evidence['text']:raise ValueError('Reference basis changed')
    if 'Creative Commons Attribution (CC BY)' not in context:raise ValueError('Licence evidence missing')
    for phrase in ('5 FAME production plants','national pilot plant in Thailand','Finland'):
        if phrase not in context:raise ValueError('Geography evidence missing: '+phrase)
    rows=evidence['rows']
    if [c['text'] for c in rows[0]]!=['Stage','Input/Output','FAME','H-FAME','BHD','Unit']:
        raise ValueError('Column mapping changed')
    direction=None;role=None;stage='Feedstock';result=[];excluded=[]
    for index,cells in enumerate(rows[1:],2):
        if any(c['rowspan']!=1 for c in cells):raise ValueError('Unexpected rowspan')
        if cells[0]['colspan']==2:
            name=cells[0]['text']
            if name in ('Input','Output'):
                direction=name.upper();role='INPUT' if name=='Input' else 'OUTPUT';stage='Feedstock' if name=='Input' else 'Output'
            elif name in ('Product','Co-products'):role='REFERENCE_PRODUCT' if name=='Product' else 'CO_PRODUCT'
            else:stage=name
            continue
        if len(cells)!=6 or any(c['colspan']!=1 for c in cells):raise ValueError('Unexpected data row layout')
        label=cells[1]['text'];unit=cells[5]['text']
        if unit not in ('kg','mg','m3','kWh'):raise ValueError('Unexpected unit')
        for column,product in ((2,'FAME'),(3,'H-FAME'),(4,'BHD')):
            raw=cells[column]['text']
            if not raw:continue  # blank is not zero and not an exchange
            match=re.fullmatch(r'(\d+(?:\.\d+)?)(?:\s+(a))?',raw)
            if not match:raise ValueError('Unexpected numeric/footnote value: '+raw)
            amount=Decimal(match[1]);identifier=hashlib.sha256(f'{digest}:{index}:{column+1}'.encode()).hexdigest()
            record=dict(observation_id=identifier,process=product,flow=label,direction=direction,role=role,
                subprocess=stage,raw_value=raw,amount=str(amount),unit=unit,reference_amount='1000',reference_unit='MJ fuel',
                publication_year=2020,data_period=None,data_period_status='NOT_SPECIFIED_IN_SELECTED_TABLE',
                source_url=URL+'#sustainability-12-09415-t004',doi=DOI,table_id='4',source_row=index,source_column=column+1,
                source_snapshot_sha256=digest,licence='CC BY 4.0',authors='Napapat Permpool; Hafiz Usman Ghani; Shabbir H. Gheewala',
                boundary='Foreground biofuel conversion inventory reported in Table 4; not the entire well-to-wheel system',
                geography='Thailand' if product!='BHD' else 'Finland-derived technology adapted to Thailand context',
                technology_level='Commercial plant study' if product=='FAME' else 'National pilot plant' if product=='H-FAME' else 'Foreign secondary source',
                allocation='Economic allocation discussed in paper: FAME 70% / glycerine 30%; no additional allocation applied here' if product=='FAME' else 'Economic allocation study; no additional allocation applied here',
                annotation='Calculated power for semi-batch reactor' if match[2] else None,
                status='SOURCE_REPORTED_PRODUCT_INVENTORY' if product!='BHD' else 'EXCLUDED_FOREIGN_PRIMARY_TECHNOLOGY',
                is_national_average=False,is_full_lci_dataset=False,is_newly_allocated=False)
            (result if product!='BHD' else excluded).append(record)
    if not result:raise ValueError('No product inventory records')
    return result,excluded


def main():
    raw=ROOT/'data/raw/mdpi-9415';body=(raw/'table4-dom.json').read_bytes()
    context=(raw/'article-visible.txt').read_text(encoding='utf-8')
    digest=hashlib.sha256(body).hexdigest();rows,excluded=extract(json.loads(body),context,digest)
    out=ROOT/'build/product-inventory';out.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(out/'inventory.sqlite')
    con.executescript('''CREATE TABLE IF NOT EXISTS process(process_id TEXT PRIMARY KEY,reference_amount TEXT NOT NULL,reference_unit TEXT NOT NULL,geography TEXT NOT NULL,technology_level TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS exchange(observation_id TEXT PRIMARY KEY,process_id TEXT NOT NULL REFERENCES process(process_id),direction TEXT NOT NULL CHECK(direction IN ('INPUT','OUTPUT')),flow TEXT NOT NULL,amount TEXT NOT NULL,unit TEXT NOT NULL,role TEXT NOT NULL,payload TEXT NOT NULL);''')
    con.execute('PRAGMA foreign_keys=ON')
    with con:
        con.execute('DELETE FROM exchange');con.execute('DELETE FROM process')
        for process in ('FAME','H-FAME'):
            sample=next(r for r in rows if r['process']==process)
            con.execute('INSERT INTO process VALUES (?,?,?,?,?)',(process,'1000','MJ fuel',sample['geography'],sample['technology_level']))
        con.executemany('INSERT INTO exchange VALUES (?,?,?,?,?,?,?,?)',[(r['observation_id'],r['process'],r['direction'],r['flow'],r['amount'],r['unit'],r['role'],json.dumps(r,ensure_ascii=False)) for r in rows])
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Database integrity failed')
    actual={r[0]:json.loads(r[1]) for r in con.execute('SELECT observation_id,payload FROM exchange')};con.close()
    if actual!={r['observation_id']:r for r in rows}:raise ValueError('Database roundtrip failed')
    report=dict(rows=rows,excluded_rows=excluded,source_reported_inventory_count=len(rows),excluded_count=len(excluded),
                checked_at=datetime.now(timezone.utc).isoformat(),doi=DOI,source_url=URL,
                evidence_method='Rendered publisher DOM table and visible article text; not an original HTTP/PDF snapshot',
                source_snapshot_sha256=digest,context_sha256=hashlib.sha256((raw/'article-visible.txt').read_bytes()).hexdigest(),
                limitations=['Publication year is not the measurement year','Do not apply allocation percentages again without confirming table calculation basis',
                'FAME output 26.3 kg is table rounding; do not silently replace with introductory 26.27 kg',
                'Inputs/outputs and co-products are not independent counts of full LCI datasets','Existing corporate reference release stays separate'])
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    evidence={k:v for k,v in report.items() if k not in ('rows','excluded_rows')}
    (ROOT/'evidence/product-inventory.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Source-reported product inventory: {len(rows)}; excluded foreign-source cells: {len(excluded)}')


if __name__=='__main__':main()
