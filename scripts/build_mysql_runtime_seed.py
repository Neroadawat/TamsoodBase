"""Build private, source-bound MySQL seed with typed schemas and exact API text.

No credentials, no external publishing. Load only into an empty owned database.
"""
import hashlib
import json
import sqlite3
from pathlib import Path
from scripts.load_supplemental_mysql import literal,decimal_value
from src.export_full_mysql import snapshot_id

ROOT=Path(__file__).resolve().parents[1]


def build():
    out=ROOT/'build/mysql-runtime';out.mkdir(parents=True,exist_ok=True)
    run=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
    manifest=json.loads((ROOT/'data/raw/dmf'/run/'manifest.json').read_text(encoding='utf-8'))
    snapshots={r['package']:snapshot_id(r) for r in manifest['packages']}
    paths=['sql/mysql/full-schema.sql','build/full-mysql.sql','build/reusable/load-mysql.sql','sql/mysql/supplemental-schema.sql','sql/mysql/eppo-schema.sql','sql/mysql/api-schema.sql',
      'build/reusable/manifest.json','build/reusable/all-reference.json','build/nso/report.json','build/product-inventory/report.json','build/eppo/report.json','build/source-contract/crosswalk.json']
    paths.extend(['build/dmf/'+run+'/candidates.sqlite','build/dmf/'+run+'/review-report.json','build/dmf/'+run+'/quality-report.json','data/raw/dmf/'+run+'/manifest.json','data/raw/eppo/manifest.json','evidence/nso-dede-comparison.json','evidence/nso-dede-revised-comparison.json','build/report-pilot/report.json','build/sprc-report/report.json'])
    paths.extend('data/raw/dmf/'+run+'/'+p+'.metadata.json' for p in snapshots)
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    release=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
    target=out/'seed.sql'
    with target.open('w',encoding='utf-8',newline='\n') as f:
        def sql(s):f.write(s+'\n')
        for path in paths[:6]:sql((ROOT/path).read_text(encoding='utf-8'))
        sql('START TRANSACTION;')
        for dataset,kind in [('nso','NSO'),('product-inventory','PRODUCT_INVENTORY')]:
            path=ROOT/'build'/dataset/'report.json';body=path.read_bytes();report=json.loads(body);sid=hashlib.sha256(body).hexdigest()
            sql('USE tamsood_supplemental;')
            sql('INSERT INTO dataset_snapshot VALUES('+','.join(map(literal,[sid,kind,'build/'+dataset+'/report.json']))+');')
            for r in report['rows']:
                sql('INSERT INTO observation VALUES('+','.join([literal(sid),literal(r['observation_id']),decimal_value(r['amount']),literal(r['unit']),literal(r['status']),literal(json.dumps(r,ensure_ascii=False))])+');')
                if kind=='NSO':values=[sid,r['observation_id'],r['table_id'],r['reference_year'],r['measure'],r['label'],r['source_sha256'],r['source_line'],r['source_column']];table='national_statistic'
                else:
                    sql('INSERT IGNORE INTO process VALUES('+','.join(map(literal,[sid,r['process'],r['reference_amount'],r['reference_unit'],r['geography'],r['technology_level']]))+');')
                    values=[sid,r['observation_id'],r['process'],r['flow'],r['direction'],r['role'],r['data_period'],r['source_snapshot_sha256'],r['source_row'],r['source_column']];table='inventory_exchange'
                sql('INSERT INTO '+table+' VALUES('+','.join(map(literal,values))+');')
        eppo=json.loads((ROOT/'build/eppo/report.json').read_text(encoding='utf-8'));raw=json.loads((ROOT/'data/raw/eppo/manifest.json').read_text(encoding='utf-8'))
        sql('USE tamsood_eppo;')
        for key,r in raw['resources'].items():sql('INSERT INTO source_snapshot VALUES('+','.join(map(literal,[r['sha256'],key,r['url'],json.dumps(r,ensure_ascii=False)]))+');')
        for r in eppo['rows']:
            values=[literal(r['observation_id']),literal(r['source_sha256']),str(r['reference_year']),str(r['month']),literal(r['subject']),decimal_value(r['amount']),literal(r['unit']),literal(r['status']),str(r['source_line']),literal(json.dumps(r,ensure_ascii=False))]
            sql('INSERT INTO observation VALUES('+','.join(values)+');')
        sql('USE tamsood_api;')
        artifacts={'runtime_info':{'dataset_release':release,'run_id':run,'dmf_snapshots':snapshots,'counts':{'dmf':34899,'reference':101,'nso':273,'inventory':16,'eppo':5934}}}
        for package,sid in snapshots.items():sql('INSERT INTO current_dmf VALUES('+','.join(map(literal,[package,sid]))+');')
        db=ROOT/'build/dmf'/run/'candidates.sqlite'
        with sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True) as con:
            con.row_factory=sqlite3.Row
            for r in con.execute('SELECT * FROM staging'):
                sql('INSERT INTO raw_representation VALUES('+','.join(map(literal,[snapshots[r['package']],r['source_line'],r['raw_json']]))+');')
            for r in con.execute('SELECT * FROM candidate'):
                sql('INSERT INTO candidate_representation VALUES('+','.join(map(literal,[snapshots[r['package']],r['source_line'],r['decimal_value'],r['production_days'],r['duplicate_of_line']]))+');')
        for name,path in [('review','build/dmf/'+run+'/review-report.json'),('quality','build/dmf/'+run+'/quality-report.json'),('reference_manifest','build/reusable/manifest.json'),('source_crosswalk','build/source-contract/crosswalk.json'),('nso_comparison','evidence/nso-dede-comparison.json'),('nso_revised','evidence/nso-dede-revised-comparison.json'),('thaioil_report','build/report-pilot/report.json'),('sprc_report','build/sprc-report/report.json')]:
            artifacts[name]=json.loads((ROOT/path).read_text(encoding='utf-8'))
        artifacts['dmf_metadata']={p:json.loads((ROOT/'data/raw/dmf'/run/(p+'.metadata.json')).read_text(encoding='utf-8'))['result'] for p in snapshots}
        reference=json.loads((ROOT/'build/reusable/all-reference.json').read_text(encoding='utf-8'));artifacts['reference_fields']=list(reference[0])
        for r in reference:sql('INSERT INTO reference_representation VALUES('+','.join(map(literal,[r['observation_id'],json.dumps(r,ensure_ascii=False)]))+');')
        for dataset in ['nso','product-inventory','eppo']:
            path=ROOT/'build'/dataset/'report.json';report=json.loads(path.read_text(encoding='utf-8'));rows=report.pop('rows');report['mysql_snapshot_id']=hashlib.sha256(path.read_bytes()).hexdigest();artifacts[dataset]=report
            for ordinal,r in enumerate(rows):sql('INSERT INTO row_order VALUES('+','.join(map(literal,[dataset,r['observation_id'],ordinal]))+');')
        for name,value in artifacts.items():sql('INSERT INTO artifact VALUES('+','.join(map(literal,[name,json.dumps(value,ensure_ascii=False)]))+');')
        sql('COMMIT;')
    result={'dataset_release':release,'seed_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,'inputs':hashes,'scope':'PRIVATE_MYSQL_SEED; normalized typed data + original presentation text; no credentials; load into EMPTY owned schemas only'}
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='inputs'},indent=2))


if __name__=='__main__':build()
