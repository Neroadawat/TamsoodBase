"""Source-specific SPRC extraction with rounding checks and unresolved context issues."""
import hashlib
import json
import re
import sqlite3
from decimal import Decimal
from pathlib import Path
from src.export_full_mysql import text_sql,exact_decimal

ROOT=Path(__file__).resolve().parents[1]
NUMBER=r'(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?'


def table_row(text,label,unit,count=4):
    matches=[]
    for line_number,line in enumerate(text.splitlines(),1):
        clean=re.sub(r'^\s*(?:\d{3}-\d?\s+)?','',line).strip()
        match=re.fullmatch(re.escape(label)+r'\s+'+re.escape(unit)+r'\s+('+NUMBER+r'(?:\s+'+NUMBER+r'){'+str(count-1)+'})',clean)
        if match: matches.append((line_number,match[1].split()))
    if len(matches)!=1: raise ValueError('Missing/ambiguous SPRC row: '+label)
    return matches[0]


def rounding_radius(raw,factor='1'):
    """Half a displayed last digit. Assumption used to flag, not correct data."""
    decimals=len(raw.split('.')[1]) if '.' in raw else 0
    return Decimal('0.5')*(Decimal(10)**(-decimals))*Decimal(factor)


def rounding_overlap(left,left_factor,right,right_factor):
    a=Decimal(left.replace(',',''))*Decimal(left_factor)
    b=Decimal(right.replace(',',''))*Decimal(right_factor)
    return abs(a-b)<=rounding_radius(left,left_factor)+rounding_radius(right,right_factor)


def build():
    from pypdf import PdfReader
    folder=ROOT/'data/raw/sprc/2024';pdf=folder/'sustainability-report.pdf'
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest!=manifest['sha256']: raise ValueError('Original SPRC PDF hash mismatch')
    reader=PdfReader(pdf);pages={n:reader.pages[n-1].extract_text(extraction_mode='layout') for n in (5,49,119,121)}
    if 'Caltex' not in pages[5] or '2024' not in pages[5]: raise ValueError('Reporting scope changed')
    specs=[
      ('energy_total','พลังงานใช้รวม',121,'organization (fuel consumption +','GJ','GJ','1','INPUT',4),
      ('fuel_total','เชื้อเพลิงใช้รวม',121,'Total fuel consumption (non-renewable)','GJ','GJ','1','INPUT',4),
      ('natural_gas','ก๊าซธรรมชาติ',121,'Natural Gas','GJ','GJ','1','INPUT',4),
      ('lpg','ก๊าซปิโตรเลียมเหลว',121,'LPG','GJ','GJ','1','INPUT',4),
      ('fuel_gas','ก๊าซเชื้อเพลิง',121,'Fuel Gas','GJ','GJ','1','INPUT',4),
      ('coke','โค้ก',121,'Coke','GJ','GJ','1','INPUT',4),
      ('electricity_purchased','ไฟฟ้าซื้อจากภายนอก',121,'Electricity purchased','GJ','GJ','1','INPUT',4),
      ('fuel_intensity','ความเข้มเชื้อเพลิงตามรายงาน',121,'Fuel intensity ratio','GJ/ ton','GJ/t throughput','1','CONTEXT',4),
      ('water_withdrawn_appendix','น้ำถอนจากแหล่ง · ภาคผนวก',119,'Total water withdrawn by sources','Million m3','m3','1000000','INPUT',4),
      ('fresh_water_appendix','น้ำจืด · ภาคผนวก',119,'Fresh water','Million m3','m3','1000000','INPUT',4),
      ('water_consumption_appendix','น้ำใช้สุทธิ · ภาคผนวก',119,'Water consumption','Million m3','m3','1000000','CONTEXT',4),
      ('water_used_narrative','น้ำใช้ · ตารางเนื้อหา',49,'Total amount of water used','','m3/year','1','INPUT',3),
      ('external_raw_water_narrative','น้ำดิบภายนอก · ตารางเนื้อหา',49,'Total amount of raw water from','','m3/year','1','INPUT',3),
      ('wastewater_narrative','น้ำเสียเกิดขึ้น · ตารางเนื้อหา',49,'Total amount of wastewater produced','','m3/year','1','OUTPUT',3),
    ]
    rows=[]
    for code,title,page,label,match_unit,canonical,factor,direction,count in specs:
        # The narrative water table carries its unit in the header, not each row.
        if not match_unit:
            if 'Cubic meter per year' not in pages[page]: raise ValueError('Water unit header missing')
            # Supply the already-verified header unit for the same strict row parser.
            lines=[]
            for line in pages[page].splitlines():
                if line.strip().startswith(label): line=line.replace(label,label+' m3/year',1)
                lines.append(line)
            line_number,values=table_row('\n'.join(lines),label,'m3/year',count)
            source_unit='m3/year'
        else:
            line_number,values=table_row(pages[page],label,match_unit,count);source_unit=match_unit
        for year,raw in zip(range(2025-count,2025),values):
            value=Decimal(raw.replace(',',''))
            rows.append({'metric_id':code,'metric_label_th':title,'source_label':label,'year':year,
              'raw_value':raw,'value':str(value),'source_unit':source_unit,
              'normalized_value':str(value*Decimal(factor)),'normalized_unit':canonical,'scale_factor':factor,
              'direction':direction,'boundary':'SPRC_REPORTED_OPERATIONS_SCOPE_REVIEW',
              'boundary_note':'Report scope includes operations, distribution and fuels marketing; refinery-only scope not assumed',
              'quantity_basis':'REPORTED_INTENSITY' if code=='fuel_intensity' else 'ANNUAL_REPORTED_METRIC',
              'reference_product_amount':None,'allocation_method':None,
              'country_relevance':'THAILAND_RELATED_REPORT_SCOPE_REVIEW',
              'source_url':manifest['source_url'],'pdf_sha256':digest,'pdf_page':page,'printed_page':str(page-1),
              'footnotes_pdf_page':5,'footnotes_printed_page':'4','extracted_text_line':line_number,
              'accessed_at':manifest['accessed_at'],'validation_status':'PENDING_DOMAIN_AND_RIGHTS_REVIEW',
              'competition_accepted':False})
    lookup={(r['metric_id'],r['year']):r for r in rows};issues=[];checks=[]
    for year in range(2021,2025):
        for total,parts in [('energy_total',['fuel_total','electricity_purchased']),('fuel_total',['natural_gas','lpg','fuel_gas','coke'])]:
            selected=[lookup[(key,year)] for key in [total,*parts]]
            residual=Decimal(selected[0]['value'])-sum(Decimal(r['value']) for r in selected[1:])
            tolerance=sum(rounding_radius(r['raw_value']) for r in selected)
            checks.append({'year':year,'total_metric':total,'component_metrics':parts,'residual_GJ':str(residual),
                'rounding_tolerance_GJ':str(tolerance),'result':'WITHIN_DISPLAY_ROUNDING' if abs(residual)<=tolerance else 'REVIEW',
                'source_values_corrected':False})
    for year in range(2022,2025):
        for left,right in [('water_used_narrative','water_withdrawn_appendix'),('external_raw_water_narrative','fresh_water_appendix')]:
            a,b=lookup[(left,year)],lookup[(right,year)]
            if not rounding_overlap(a['raw_value'],a['scale_factor'],b['raw_value'],b['scale_factor']):
                issues.append({'issue_id':f'WATER-{left}-{year}','year':year,'metrics':[left,right],
                    'left_m3':a['normalized_value'],'right_m3':b['normalized_value'],
                    'left_unit':a['normalized_unit'],'right_unit':b['normalized_unit'],
                    'comparison_basis':'NUMERIC_ANNUAL_TABLE_VALUES_ONLY_NOT_EQUIVALENCE',
                    'source_pages':[a['pdf_page'],b['pdf_page']],'status':'HOLD_CONTEXT_OR_REVISION_DIFFERENCE',
                    'explanation':'Different labels may represent different contexts; displayed rounding alone does not reconcile values',
                    'automatic_merge_allowed':False,'preferred_source':None})
    out=ROOT/'build/sprc-report';out.mkdir(parents=True,exist_ok=True)
    for page,text in pages.items(): (out/f'page{page}-layout.txt').write_text(text,encoding='utf-8')
    con=sqlite3.connect(out/'reports.sqlite');con.executescript('DROP TABLE IF EXISTS report_metric; CREATE TABLE report_metric(pdf_sha256 TEXT,metric_id TEXT,year INTEGER,value TEXT,payload_json TEXT,PRIMARY KEY(pdf_sha256,metric_id,year));')
    con.executemany('INSERT INTO report_metric VALUES(?,?,?,?,?)',[(digest,r['metric_id'],r['year'],r['value'],json.dumps(r,ensure_ascii=False)) for r in rows]);con.commit();con.close()
    report={'source':'SPRC_2024_REPORT','display_name':'SPRC · รายงาน 2024','source_url':manifest['source_url'],
        'pdf_sha256':digest,'row_count':len(rows),'metric_count':len(specs),'competition_accepted':0,
        'issues':issues,'arithmetic_checks':checks,'rows':rows,
        'limits':['Company-report boundary includes marketing and distribution; do not assume refinery-only scope',
            'Water labels differ between tables; unresolved differences preserved',
            'Totals/components overlap; no summation across all metrics','Public access does not establish redistribution rights'],
        'extraction_method':'pypdf layout and source-specific exact row matching','pypdf_version':__import__('pypdf').__version__}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    sql="SET NAMES utf8mb4; USE tamsood_research;\nCREATE TABLE IF NOT EXISTS report_metric (pdf_sha256 CHAR(64) NOT NULL,metric_id VARCHAR(80) NOT NULL,reference_year SMALLINT NOT NULL,amount DECIMAL(30,12) NOT NULL,payload_json JSON NOT NULL,PRIMARY KEY(pdf_sha256,metric_id,reference_year),CHECK(amount>=0));\nSTART TRANSACTION;\n"
    sql+='DELETE FROM report_metric WHERE pdf_sha256='+text_sql(digest)+';\n'
    for r in rows: sql+='INSERT INTO report_metric VALUES('+','.join([text_sql(digest),text_sql(r['metric_id']),str(r['year']),exact_decimal(r['value']),text_sql(json.dumps(r,ensure_ascii=False))])+');\n'
    (out/'load-mysql.sql').write_text(sql+'COMMIT;\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','arithmetic_checks')},ensure_ascii=False,indent=2))


if __name__=='__main__': build()
