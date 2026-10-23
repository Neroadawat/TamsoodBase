"""Build the typed, versioned team reference-data release from verified PDF observations."""
import csv
import hashlib
import json
import sqlite3
from collections import Counter
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
from src.export_full_mysql import exact_decimal,text_sql
from src.trace_report import trace

ROOT=Path(__file__).resolve().parents[1]
PROFILE='LOCAL_RESEARCH_REFERENCE'
TABLES={
 'publisher':['publisher_id','name'],
 'document':['document_id','publisher_id','title','report_year','source_url','accessed_at','rights_status'],
 'unit':['unit_code','dimension'],
 'context':['context_id','document_id','source_scope','description','geography_status'],
 'metric':['metric_key','document_id','source_metric_id','label','context_id','unit_code','data_kind','aggregation_role'],
 'observation':['observation_id','metric_key','reference_year','raw_value','raw_unit_label','scale_factor','scaled_amount','pdf_page','printed_page','extracted_text_line'],
 'quality_issue':['issue_id','document_id','source_issue_id','reason'],
 'issue_observation':['issue_id','observation_id'],
 'review':['observation_id','decision','policy_version','review_actor','trace_verification'],
 'data_release':['release_id','policy_version','usage_profile','created_at'],
 'release_observation':['release_id','observation_id']}
KEYS={'publisher':['publisher_id'],'document':['document_id'],'unit':['unit_code'],
 'context':['context_id'],'metric':['metric_key'],'observation':['observation_id'],
 'quality_issue':['issue_id'],'issue_observation':['issue_id','observation_id'],
 'review':['observation_id','policy_version'],'data_release':['release_id'],
 'release_observation':['release_id','observation_id']}
CONSTRAINTS={
 'document':['FOREIGN KEY(publisher_id) REFERENCES publisher'],
 'context':['FOREIGN KEY(document_id) REFERENCES document','UNIQUE(context_id,document_id)'],
 'metric':['FOREIGN KEY(document_id) REFERENCES document','FOREIGN KEY(context_id,document_id) REFERENCES context(context_id,document_id)',
           'FOREIGN KEY(unit_code) REFERENCES unit','UNIQUE(document_id,source_metric_id,metric_key)'],
 'observation':['FOREIGN KEY(metric_key) REFERENCES metric','UNIQUE(metric_key,reference_year)'],
 'quality_issue':['FOREIGN KEY(document_id) REFERENCES document'],
 'issue_observation':['FOREIGN KEY(issue_id) REFERENCES quality_issue','FOREIGN KEY(observation_id) REFERENCES observation'],
 'review':['FOREIGN KEY(observation_id) REFERENCES observation'],
 'release_observation':['FOREIGN KEY(release_id) REFERENCES data_release','FOREIGN KEY(observation_id) REFERENCES observation']}
DIMENSIONS={'GJ':'ENERGY','MWh':'ENERGY','t':'MASS','GJ/BOE':'ENERGY_PER_OIL_EQUIVALENT',
 'GJ/t throughput':'ENERGY_PER_FEEDSTOCK_MASS','m3':'VOLUME','m3/year':'VOLUME_PER_YEAR'}


def identity(*parts):
    return hashlib.sha256(json.dumps(parts,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def classification(row):
    code=row['metric_id']
    if code in ('energy_intensity','fuel_intensity'): return 'REPORTED_INTENSITY','INTENSITY'
    if row['direction']=='CONTEXT': return 'CONTEXT_METRIC','CONTEXT'
    kind='ORGANIZATION_INPUT' if row['direction']=='INPUT' else 'ORGANIZATION_OUTPUT'
    role='TOTAL' if code in ('energy_total','fuel_total','water_withdrawn_appendix','water_used_narrative') else 'COMPONENT' if code in ('natural_gas','fuel_oil','fuel_gas','coke','diesel','lpg','fresh_water_appendix') else 'MEASURE'
    return kind,role


def build():
    policy=(ROOT/'docs/team-data-policy.md').read_bytes();policy_hash=hashlib.sha256(policy).hexdigest()
    sources=[]
    for folder,publisher,title in [('report-pilot','THAIOIL','Thai Oil Public Company Limited'),('sprc-report','SPRC','Star Petroleum Refining Public Company Limited')]:
        body=(ROOT/'build'/folder/'report.json').read_bytes()
        sources.append((json.loads(body),publisher,title,hashlib.sha256(body).hexdigest()))
    schema_hash=hashlib.sha256((ROOT/'sql/mysql/reusable-schema.sql').read_bytes()).hexdigest()
    implementations={name:hashlib.sha256((ROOT/'src'/name).read_bytes()).hexdigest()
                     for name in ('build_reusable.py','trace_report.py','report_pilot.py','sprc_report.py')}
    release_id=identity(policy_hash,schema_hash,implementations,[s[3] for s in sources])
    # Include evidence/mapping revision in the review fingerprint, preserving old decisions.
    policy_version='TEAM_REFERENCE_V1-'+release_id[:12]
    tables={table:[] for table in TABLES};seen={table:set() for table in TABLES};records=[]
    def add(table,values):
        key=tuple(values[TABLES[table].index(k)] for k in KEYS[table])
        if key not in seen[table]: tables[table].append(values);seen[table].add(key)
    created_at=datetime.now(timezone.utc).isoformat()
    previous=ROOT/'build/reusable/manifest.json'
    if previous.exists():
        old=json.loads(previous.read_text(encoding='utf-8'))
        if old['release_id']==release_id: created_at=old['created_at']
    add('data_release',[release_id,policy_version,PROFILE,created_at])
    trace_count=0
    for report,publisher,title,report_hash in sources:
        doc=report['pdf_sha256'];add('publisher',[publisher,title])
        add('document',[doc,publisher,'Sustainability report 2024',2024,report['source_url'],report['rows'][0]['accessed_at'],'PUBLIC_REPORT_REUSE_NOT_CONFIRMED'])
        held={(metric,issue['year']) for issue in report.get('issues',[]) for metric in issue['metrics']}
        obs_ids={}
        for row in report['rows']:
            # Re-read original bytes and year column for EVERY selected row, not a spot-check.
            result=trace(report['source'],row['metric_id'],row['year'])
            if result['verification']!='PDF_HASH_AND_REEXTRACTED_COLUMN_MATCH': raise ValueError('Trace failed')
            trace_count+=1
            unit=row['normalized_unit']
            if unit not in DIMENSIONS: raise ValueError('Unmapped dimensional meaning: '+unit)
            exact_decimal(row['normalized_value']);exact_decimal(row['scale_factor'])
            if Decimal(row['raw_value'].replace(',',''))*Decimal(row['scale_factor'])!=Decimal(row['normalized_value']):
                raise ValueError('Unit scaling mismatch')
            kind,role=classification(row)
            boundary=row.get('boundary_note') or ('Refinery feedstock only' if row['boundary']=='REFINERY_FEEDSTOCK' else 'Reported intensity; scope requires reading source documentation' if kind=='REPORTED_INTENSITY' else 'Energy reporting covers TOP, TPX, TLB, LABIX and TOPSPP')
            context_key=identity(doc,row['boundary'],boundary)
            # Mapping content participates in metric identity so revised mapping preserves old releases.
            label=row.get('metric_label_th') or row['source_label']
            metric_key=identity(doc,row['metric_id'],context_key,unit,kind,role,label)
            obs=identity(metric_key,row['year'],row['raw_value'],row['source_unit'],row['scale_factor'],row['pdf_page'],row['extracted_text_line'])
            obs_ids[(row['metric_id'],row['year'])]=obs
            add('unit',[unit,DIMENSIONS[unit]])
            add('context',[context_key,doc,row['boundary'],boundary,row['country_relevance']])
            add('metric',[metric_key,doc,row['metric_id'],label,context_key,unit,kind,role])
            add('observation',[obs,metric_key,row['year'],row['raw_value'],row['source_unit'],row['scale_factor'],row['normalized_value'],row['pdf_page'],row['printed_page'],row['extracted_text_line']])
            decision='HOLD_CONTEXT' if (row['metric_id'],row['year']) in held else 'ACCEPTED_REFERENCE'
            add('review',[obs,decision,policy_version,'AUTOMATED_TEAM_POLICY_V1',result['verification']])
            add('release_observation',[release_id,obs])
        for issue in report.get('issues',[]):
            issue_id=identity(doc,issue['issue_id'],issue['explanation'])
            add('quality_issue',[issue_id,doc,issue['issue_id'],issue['explanation']])
            for metric in issue['metrics']: add('issue_observation',[issue_id,obs_ids[(metric,issue['year'])]])
    out=ROOT/'build/reusable';out.mkdir(parents=True,exist_ok=True)
    temporary=out/'reference.sqlite.tmp'
    if temporary.exists(): raise RuntimeError('Previous temporary build remains; inspect before retrying')
    con=sqlite3.connect(temporary);con.execute('PRAGMA foreign_keys=ON')
    for table,columns in TABLES.items():
        fields=[name+(' INTEGER' if name in ('reference_year','report_year','pdf_page','extracted_text_line') else ' TEXT')+' NOT NULL' for name in columns]
        fields+=['PRIMARY KEY('+','.join(KEYS[table])+')',*CONSTRAINTS.get(table,[])]
        con.execute('CREATE TABLE '+table+' ('+','.join(fields)+')')
        con.executemany('INSERT INTO '+table+' VALUES('+','.join('?' for _ in columns)+')',tables[table])
    con.commit()
    views=(ROOT/'sql/mysql/reusable-schema.sql').read_text(encoding='utf-8').split('CREATE OR REPLACE VIEW reference_catalog AS',1)[1]
    con.executescript('CREATE VIEW reference_catalog AS'+views.replace('CREATE OR REPLACE VIEW','CREATE VIEW'))
    if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or con.execute('PRAGMA foreign_key_check').fetchall(): raise ValueError('Relational integrity failed')
    con.row_factory=sqlite3.Row
    records=[dict(row) for row in con.execute('SELECT * FROM reference_catalog WHERE release_id=? ORDER BY reference_year DESC,publisher,source_metric_id',(release_id,))]
    for row in records:
        row.update(redistribution_status='NOT_CLEARED',is_normalized_lci_exchange=False,
                   reference_product_amount=None,allocation_method=None)
    con.close();temporary.replace(out/'reference.sqlite')
    sql=(ROOT/'sql/mysql/reusable-schema.sql').read_text(encoding='utf-8')+'\nSTART TRANSACTION;\n'
    for table,columns in TABLES.items():
        for values in tables[table]:
            encoded=[exact_decimal(str(value)) if name in ('scaled_amount','scale_factor') else str(value) if isinstance(value,int) else text_sql(value) for name,value in zip(columns,values)]
            key=KEYS[table][0]
            sql+='INSERT INTO '+table+' ('+','.join(columns)+') VALUES ('+','.join(encoded)+') ON DUPLICATE KEY UPDATE '+key+'='+key+';\n'
    (out/'load-mysql.sql').write_text(sql+'COMMIT;\n',encoding='utf-8')
    accepted=[r for r in records if r['decision']=='ACCEPTED_REFERENCE']
    for filename,rows in [('accepted-reference.json',accepted),('all-reference.json',records)]:
        (out/filename).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    with (out/'accepted-reference.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(accepted)
    manifest={'release_id':release_id,'created_at':created_at,'policy_version':policy_version,'policy_sha256':policy_hash,
        'schema_sha256':schema_hash,'implementation_sha256':implementations,
        'usage_profile':PROFILE,'source_observations':len(records),'accepted_reference':len(accepted),
        'held_context':len(records)-len(accepted),'normalized_lci_exchanges':0,
        'reextracted_pdf_records':trace_count,'data_kinds':dict(Counter(r['data_kind'] for r in accepted)),
        'redistribution_status':'NOT_CLEARED','source_document_hashes':[s[0]['pdf_sha256'] for s in sources],
        'files':{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ('accepted-reference.json','all-reference.json','accepted-reference.csv','reference.sqlite','load-mysql.sql')},
        'limitations':['Team acceptance is for local reference-data use, not third-party approval',
            'Annual organizational data are not product-normalized LCI exchanges',
            'Totals and components overlap; do not sum every row',
            'Source rights and redistribution permissions are not granted by this export']}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))


if __name__=='__main__': build()
