"""Check complete retained data through loopback HTTP; never contact production or submit feedback."""
from collections import defaultdict
from contextlib import closing
import csv
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import sqlite3
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8765'
DMF_FIELDS=['package','source_line','year_ce','month','area','block_label','source_group','raw_value','amount_column',
            'metadata_unit','metadata_multiplier','unit_label','unit_time_basis','snapshot_run_id','review_status',
            'duplicate_status','url','csv_sha256','acquired_at']


def csv_value(value):
    if value is None:return ''
    if isinstance(value,str) and value.startswith(('=','+','-','@','\t','\r')):return "'"+value
    return str(value)


def main():
    checks=[]
    def request(path,params=None,expected=200):
        route=path+('?' + urlencode(params) if params else '')
        try:
            with urlopen(BASE+route,timeout=20) as response:
                body=response.read(8_000_001);status=response.status;headers=response.headers
        except HTTPError as error:
            with error:body=error.read(8_000_001);status=error.code;headers=error.headers
        if len(body)>8_000_000 or status!=expected:raise ValueError('Unexpected response: '+route)
        if headers.get('X-Content-Type-Options')!='nosniff':raise ValueError('Missing response content guard')
        checks.append({'route':route,'http':status,'passed':True,'sha256':hashlib.sha256(body).hexdigest()})
        return body

    files=['build/nso/report.json','build/product-inventory/report.json','web/upstream-inventory.json','web/case-study.json',
           'build/reusable/all-reference.json','build/reusable/manifest.json']
    before={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files}
    for endpoint,filename in [('/api/nso',files[0]),('/api/product-inventory',files[1]),
                              ('/upstream-inventory.json',files[2]),('/api/model',files[3])]:
        if json.loads(request(endpoint))!=json.loads((ROOT/filename).read_bytes()):raise ValueError('Complete payload mismatch: '+endpoint)
    references=json.loads((ROOT/files[4]).read_bytes())
    manifest=json.loads((ROOT/files[5]).read_bytes())
    for decision in ('ACCEPTED_REFERENCE','all','HOLD_CONTEXT'):
        expected=[r for r in references if decision=='all' or r['decision']==decision]
        actual=[]
        for page in range(1,(len(expected)+29)//30+2):
            result=json.loads(request('/api/reference',{'decision':decision,'page':page}))
            if result['total']!=len(expected) or result['manifest']['release_id']!=manifest['release_id']:raise ValueError('Wrong reference release/count')
            actual.extend(result['rows'])
        if actual!=expected:raise ValueError('Reference pagination changed rows/order')
    publisher_names={'THAIOIL':'Thai Oil Public Company Limited','SPRC':'Star Petroleum Refining Public Company Limited'}
    for publisher in publisher_names:
        for year in (2021,2022,2023,2024):
            for kind in ('ORGANIZATION_INPUT','ORGANIZATION_OUTPUT','REPORTED_INTENSITY','CONTEXT_METRIC'):
                params={'decision':'all','publisher':publisher,'year':year,'data_kind':kind}
                expected=[r for r in references if r['publisher']==publisher_names[publisher] and r['reference_year']==year and r['data_kind']==kind]
                result=json.loads(request('/api/reference',params))
                if result['total']!=len(expected) or result['rows']!=expected:raise ValueError('Reference filter mismatch')
    for params in ({'decision':'all'},{},{'decision':'HOLD_CONTEXT'},{'publisher':'SPRC','year':'2024'},{'year':'1900'}):
        expected=[r for r in references if (params.get('decision')=='all' or r['decision']==params.get('decision','ACCEPTED_REFERENCE'))
                  and (not params.get('publisher') or r['publisher']==publisher_names[params['publisher']])
                  and (not params.get('year') or r['reference_year']==int(params['year']))]
        data=json.loads(request('/api/reference.json',params))
        if data['rows']!=expected:raise ValueError('Complete reference JSON export differs')
        reader=csv.DictReader(io.StringIO(request('/api/reference.csv',params).decode('utf-8-sig')))
        actual=list(reader)
        if reader.fieldnames!=data['fields'] or actual!=[{k:csv_value(row[k]) for k in data['fields']} for row in expected]:
            raise ValueError('Complete reference CSV values/schema/order differ')
    for query in ('%','_','\\',"' OR 1=1 --"):
        expected=[r for r in references if r['decision']=='ACCEPTED_REFERENCE' and (query in r['label'] or query in r['source_metric_id'])]
        result=json.loads(request('/api/reference',{'q':query}))
        if result['total']!=len(expected) or result['rows']!=expected[:30]:raise ValueError('Search is not literal')
    for params in ({'page':0},{'page':-1},{'page':'bad'},{'year':'2024 OR 1=1'},
                   {'publisher':'unknown'},{'decision':'MTEC_APPROVED'},{'data_kind':'INVENTED'},{'q':'x'*161}):
        request('/api/reference',params,400)
    source_reports=json.loads(request('/api/reports'))['sources']
    for report,folder in zip(source_reports,('report-pilot','sprc-report')):
        original=json.loads((ROOT/'build'/folder/'report.json').read_bytes())
        if {k:v for k,v in report.items() if k!='display_name'}!={k:v for k,v in original.items() if k!='display_name'}:
            raise ValueError('Report source/provenance differs')
    if len(source_reports)!=2:raise ValueError('Missing Corporate source report')

    run=json.loads((ROOT/'data/raw/dmf/latest.json').read_bytes())['run_id']
    database=ROOT/'build/dmf'/run/'candidates.sqlite'
    database_hash=hashlib.sha256(database.read_bytes()).hexdigest()
    groups=defaultdict(list)
    with closing(sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)) as con:
        con.row_factory=sqlite3.Row
        metadata={p:json.loads((ROOT/'data/raw/dmf'/run/(p+'.metadata.json')).read_bytes())['result'] for p in ('production-oil','production-condensate','production-natural-gas')}
        selected='c.package,c.source_line,c.year_ce,c.month,c.area,c.block_label,c.source_group,c.raw_value,c.amount_column,c.review_status,d.status AS duplicate_status,r.metadata_unit,r.url,r.csv_sha256,r.acquired_at'
        cursor=con.execute('SELECT '+selected+' FROM candidate c JOIN duplicate_disposition d USING(package,source_line) '
                           'JOIN resource r USING(package) ORDER BY c.package,c.year_ce DESC,c.month DESC,c.source_line')
        for record in cursor:
            row=dict(record);multiplier=metadata[row['package']].get('unit_of_multiplier','')
            row.update(metadata_multiplier=multiplier,unit_label=(multiplier or '')+(row['metadata_unit'] or ''),
                       unit_time_basis='UNCONFIRMED',snapshot_run_id=run)
            groups[(row['package'],row['year_ce'])].append(row)
        total=con.execute('SELECT COUNT(*) FROM candidate').fetchone()[0]
    checked_rows=0
    for (package,year),rows in groups.items():
        body=request('/api/export',{'product':package,'year':year,'status':'all'})
        reader=csv.DictReader(io.StringIO(body.decode('utf-8-sig')))
        if reader.fieldnames!=DMF_FIELDS or list(reader)!=[{k:csv_value(row[k]) for k in DMF_FIELDS} for row in rows]:
            raise ValueError('DMF source-to-CSV mismatch')
        checked_rows+=len(rows)
    if checked_rows!=total:raise ValueError('Not all candidate records were checked')
    request('/api/export',expected=400)
    if hashlib.sha256(database.read_bytes()).hexdigest()!=database_hash:raise ValueError('Read-only check changed source DB')
    if any(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest for name,digest in before.items()):
        raise ValueError('Source artifacts changed during HTTP validation')
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'LOOPBACK_ALL_RESTORED_FIELDS_NOT_PRODUCTION_CAPACITY',
            'requests_checked':len(checks),'checks':checks,'corporate_rows':len(references),
            'dmf_rows':checked_rows,'dmf_partitions':len(groups),'nso_rows':273,'foreground_rows':16,'upstream_rows':42,
            'source_hashes_unchanged':before,'feedback_submitted':False,'gemini_called':False,'production_changed':False,'passed':True}
    folder=ROOT/'build/handoff';folder.mkdir(parents=True,exist_ok=True)
    (folder/'end-to-end-data-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('checks','source_hashes_unchanged')},indent=2))


if __name__=='__main__':main()
