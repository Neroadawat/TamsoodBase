"""Versioned readable source IDs and internal derived-data exports; never alters releases."""
import csv
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DMF={'production-oil':'DMF-CKAN-OIL','production-condensate':'DMF-CKAN-CONDENSATE','production-natural-gas':'DMF-CKAN-GAS'}


def source_id(layer,row):
    if layer=='corporate':
        url=row['source_url']
        if 'investor.sprc.co.th/' in url:return 'SPRC-REPORT-2024'
        if 'investor.thaioilgroup.com/' in url:return 'THAIOIL-REPORT-2024'
        raise ValueError('Unmapped corporate source URL')
    if layer=='nso':return 'NSO-SYB2026-'+row['table_id']
    if layer=='eppo':return 'EPPO-'+row['dataset_id']
    if layer=='inventory':
        if row.get('doi')!='10.3390/su12229415' or row.get('table_id')!='4':raise ValueError('Unmapped inventory source')
        return 'MDPI-SU12229415-T4'
    if layer=='dmf':return DMF[row['package']]
    raise ValueError('Unknown layer')


def build():
    registry=list(csv.DictReader((ROOT/'docs/source-registry.csv').open(encoding='utf-8-sig',newline='')))
    by_id={r['source_id']:r for r in registry}
    if len(by_id)!=len(registry):raise ValueError('Duplicate registry source ID')
    out=ROOT/'build/source-contract';out.mkdir(parents=True,exist_ok=True)
    inputs={};counts=Counter();links={};seen=set()
    target=out/'observations-internal.jsonl'
    with target.open('w',encoding='utf-8',newline='\n') as stream:
        def emit(layer,row,sha,locator,identity):
            sid=source_id(layer,row)
            if sid not in by_id:raise ValueError('Source not registered: '+sid)
            if len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha):raise ValueError('Invalid source hash')
            key=(layer,str(identity))
            if key in seen:raise ValueError('Duplicate observation identity')
            seen.add(key);counts[layer]+=1
            entry=links.setdefault((sid,sha),{'source_id':sid,'source_sha256':sha,'registry_url':by_id[sid]['url'],'registry_rights_status':by_id[sid]['rights_status'],'layers':set(),'observations':0})
            entry['layers'].add(layer);entry['observations']+=1
            stream.write(json.dumps({'source_id':sid,'layer':layer,'observation_key':str(identity),'source_sha256':sha,'locator':locator,'usage_profile':'INTERNAL_REVIEW_ONLY','original':row},ensure_ascii=False)+'\n')
        for layer,path in [('corporate','build/reusable/all-reference.json'),('nso','build/nso/report.json'),('inventory','build/product-inventory/report.json'),('eppo','build/eppo/report.json')]:
            data=(ROOT/path).read_bytes();inputs[path]=hashlib.sha256(data).hexdigest();obj=json.loads(data);rows=obj if isinstance(obj,list) else obj['rows']
            for row in rows:
                sha=row.get('pdf_sha256') or row.get('source_sha256') or row.get('source_snapshot_sha256')
                loc={k:row[k] for k in ['pdf_page','printed_page','extracted_text_line','source_line','source_column','source_row','table_id'] if k in row and k!='source_row'}
                if layer=='inventory':loc['source_row']=row['source_row']
                emit(layer,row,sha,loc,row['observation_id'])
        run=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
        db=ROOT/'build/dmf'/run/'candidates.sqlite';inputs[db.relative_to(ROOT).as_posix()]=hashlib.sha256(db.read_bytes()).hexdigest()
        with sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True) as con:
            con.row_factory=sqlite3.Row
            resources={r['package']:dict(r) for r in con.execute('SELECT * FROM resource')}
            for r in con.execute('SELECT c.*,d.status AS duplicate_status FROM candidate c JOIN duplicate_disposition d USING(package,source_line) ORDER BY package,source_line'):
                row=dict(r);emit('dmf',row,resources[row['package']]['csv_sha256'],{'source_line':row['source_line'],'column':row['amount_column']},row['package']+':'+str(row['source_line']))
    sources=[]
    for key,value in sorted(links.items()):value['layers']=sorted(value['layers']);sources.append(value)
    manifest={'contract_version':'SOURCE_ID_V1','sources':sources,'counts':dict(counts),'inputs':inputs,'export_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'scope':'Additive crosswalk only; existing observation IDs, values, quality decisions and releases unchanged','public_redistribution_cleared':False}
    manifest['contract_id']=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    (out/'crosswalk.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # CSV has trace keys and original JSON: no silent field loss or decimal float conversion.
    with target.open(encoding='utf-8') as stream,(out/'observations-internal.csv').open('w',encoding='utf-8-sig',newline='') as csvfile:
        writer=csv.writer(csvfile);writer.writerow(['source_id','layer','observation_key','source_sha256','locator_json','usage_profile','original_json'])
        for line in stream:
            r=json.loads(line);writer.writerow([r['source_id'],r['layer'],r['observation_key'],r['source_sha256'],json.dumps(r['locator'],ensure_ascii=False),r['usage_profile'],json.dumps(r['original'],ensure_ascii=False)])
    (ROOT/'evidence/source-contract.json').write_text(json.dumps({'passed':True,'contract_id':manifest['contract_id'],'counts':dict(counts),'sources':len(sources),'public_redistribution_cleared':False,'source_ids_registered':True,'duplicate_observation_keys':0,'existing_release_changed':False},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'contract_id':manifest['contract_id'],'counts':dict(counts),'sources':len(sources)}))


if __name__=='__main__':build()
