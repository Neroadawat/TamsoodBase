"""Conservative, source-specific PDF table extraction; not a normalized LCI dataset.

Run with a Python environment containing pypdf. Raw PDFs are kept local.
"""
import hashlib
import json
import re
import sqlite3
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPECS=[
 ('throughput','Refinery throughput (1)','Metric Ton','t','1','CONTEXT','REFINERY_FEEDSTOCK'),
 ('energy_total','Total energy consumption  (2)','Million GJ','GJ','1000000','INPUT','TOP_TPX_TLB_LABIX_TOPSPP'),
 ('fuel_total','Total fuel consumption  (2)','Million GJ','GJ','1000000','INPUT','TOP_TPX_TLB_LABIX_TOPSPP'),
 ('natural_gas','Natural gas','Million GJ','GJ','1000000','INPUT','TOP_TPX_TLB_LABIX_TOPSPP'),
 ('fuel_oil','Fuel oil','Million GJ','GJ','1000000','INPUT','TOP_TPX_TLB_LABIX_TOPSPP'),
 ('fuel_gas','Fuel gas','Million GJ','GJ','1000000','INPUT','TOP_TPX_TLB_LABIX_TOPSPP'),
 ('coke','Coke','Million GJ','GJ','1000000','INPUT','TOP_TPX_TLB_LABIX_TOPSPP'),
 ('diesel','Diesel','Million GJ','GJ','1000000','INPUT','TOP_TPX_TLB_LABIX_TOPSPP'),
 ('electricity_consumption','Electricity consumption','Megawatt-Hour','MWh','1','INPUT','TOP_TPX_TLB_LABIX_TOPSPP'),
 ('electricity_purchased','Electricity purchased from external source','Megawatt-Hour','MWh','1','INPUT','TOP_TPX_TLB_LABIX_TOPSPP'),
 ('electricity_sold','Electricity sold (4)','Megawatt-Hour','MWh','1','OUTPUT','TOP_TPX_TLB_LABIX_TOPSPP'),
 ('energy_intensity','Refinery energy intensity','GJ/ BOE (12)','GJ/BOE','1','CONTEXT','REPORTED_INTENSITY_BOUNDARY_REVIEW'),
]


def extract_values(text,label,unit):
    # Matching the whole left side prevents fuel oil being confused with fuel gas.
    matches=[]
    for number,line in enumerate(text.splitlines(),1):
        clean=re.sub(r'^\s*•\s*','',line).strip()
        if not clean.startswith(label): continue
        tail=clean[len(label):].strip()
        if not tail.startswith(unit): continue
        numeric=tail[len(unit):].strip().split()
        if len(numeric)!=4 or any(not re.fullmatch(r'(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?',v) for v in numeric):
            raise ValueError('Ambiguous or censored table row: '+label)
        matches.append((number,numeric))
    if len(matches)!=1: raise ValueError('Expected one unambiguous table row: '+label)
    return matches[0]


def build():
    from pypdf import PdfReader
    folder=ROOT/'data/raw/thaioil/2024'
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    pdf=folder/'sustainability-report.pdf';body=pdf.read_bytes()
    digest=hashlib.sha256(body).hexdigest()
    if digest!=manifest['sha256']: raise ValueError('PDF checksum mismatch')
    reader=PdfReader(pdf)
    text=reader.pages[59].extract_text(extraction_mode='layout')
    notes=reader.pages[61].extract_text()
    if 'TOP, TPX, TLB, LABIX, and TOPSPP' not in notes: raise ValueError('Expected boundary footnote missing')
    if not re.search(r'2021\s+2022\s+2023\s+2024',text): raise ValueError('Year columns changed')
    rows=[]
    for code,label,unit,canonical,factor,direction,boundary in SPECS:
        line,values=extract_values(text,label,unit)
        for year,raw in zip(range(2021,2025),values):
            value=Decimal(raw.replace(',',''));normalized=value*Decimal(factor)
            rows.append({'metric_id':code,'source_label':label,'year':year,'raw_value':raw,
                'value':str(value),'source_unit':unit,'normalized_value':str(normalized),
                'normalized_unit':canonical,'scale_factor':factor,'direction':direction,
                'boundary':boundary,'quantity_basis':'ANNUAL_REPORTED_METRIC',
                'reference_product_amount':None,'allocation_method':None,
                'country_relevance':'THAILAND_RELATED_COMPANY_REPORT_SCOPE_REVIEW',
                'source_url':manifest['source_url'],'pdf_sha256':digest,'pdf_page':60,'printed_page':'63',
                'footnotes_pdf_page':62,'footnotes_printed_page':'65','extracted_text_line':line,
                'accessed_at':manifest['accessed_at'],'validation_status':'PENDING_DOMAIN_AND_RIGHTS_REVIEW',
                'competition_accepted':False})
    out=ROOT/'build/report-pilot';out.mkdir(parents=True,exist_ok=True)
    (out/'page60-layout.txt').write_text(text,encoding='utf-8')
    con=sqlite3.connect(out/'reports.sqlite')
    con.executescript('DROP TABLE IF EXISTS report_metric; CREATE TABLE report_metric(pdf_sha256 TEXT NOT NULL,metric_id TEXT NOT NULL,year INTEGER NOT NULL,value TEXT NOT NULL,payload_json TEXT NOT NULL,PRIMARY KEY(pdf_sha256,metric_id,year));')
    con.executemany('INSERT INTO report_metric VALUES(?,?,?,?,?)',[(digest,r['metric_id'],r['year'],r['value'],json.dumps(r,ensure_ascii=False)) for r in rows]);con.commit()
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok';con.close()
    report={'source':'THAIOIL_2024_REPORT','source_url':manifest['source_url'],'pdf_sha256':digest,
        'extraction_method':'pypdf layout + strict source-specific four-column matching',
        'extractor_version':1,'pypdf_version':__import__('pypdf').__version__,
        'metric_count':len(SPECS),'row_count':len(rows),'competition_accepted':0,
        'visual_review':'Selected rows on PDF page 60 / printed 63 compared with rendered page',
        'limits':['Selected indicators only; not a complete inventory',
            'Energy boundary includes five companies; do not divide by refinery-only throughput',
            'Totals and components overlap; do not sum energy, fuel and electricity totals',
            'Power-of-ten scaling only; no product allocation or normalization',
            'Reuse rights and competition eligibility not confirmed'], 'rows':rows}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    # Portable SQL uses exact decimals and UTF-8 hex, never interpolated literals.
    from src.export_full_mysql import text_sql,exact_decimal
    sql="SET NAMES utf8mb4; USE tamsood_research;\nCREATE TABLE IF NOT EXISTS report_metric (pdf_sha256 CHAR(64) NOT NULL,metric_id VARCHAR(80) NOT NULL,reference_year SMALLINT NOT NULL,amount DECIMAL(30,12) NOT NULL,payload_json JSON NOT NULL,PRIMARY KEY(pdf_sha256,metric_id,reference_year),CHECK(amount>=0));\nSTART TRANSACTION;\n"
    sql+='DELETE FROM report_metric WHERE pdf_sha256='+text_sql(digest)+';\n'
    for r in rows:
        sql+='INSERT INTO report_metric VALUES('+','.join([text_sql(digest),text_sql(r['metric_id']),str(r['year']),exact_decimal(r['value']),text_sql(json.dumps(r,ensure_ascii=False))])+');\n'
    sql+='COMMIT;\n'
    (out/'load-mysql.sql').write_text(sql,encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False,indent=2))


if __name__=='__main__': build()
