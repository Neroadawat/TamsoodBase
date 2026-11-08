"""Produce separate review projections from the sealed source; no runtime migration."""
import json,sqlite3,hashlib
from pathlib import Path
from collections import Counter
from src.decimal_projection import sql_decimal
ROOT=Path(__file__).resolve().parents[1]
def build():
    release=json.loads((ROOT/'evidence/activity-model-store.json').read_text(encoding='utf-8'))
    path=ROOT/release['database'];before=hashlib.sha256(path.read_bytes()).hexdigest()
    if before!=release['database_sha256']:raise ValueError('Sealed input mismatch')
    c=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
    rows=[]
    for oid,amount,unit in c.execute('SELECT observation_id,amount,unit FROM source_observation ORDER BY observation_id'):
        rows.append({'kind':'source','key':oid,'raw_text':amount,'unit':unit,'numeric':sql_decimal(amount) if unit else None,'status':'ELIGIBLE' if unit and sql_decimal(amount) is not None else 'EXCLUDED_UNIT_OR_PRECISION'})
    for run,oid,amount,unit in c.execute('SELECT r.run_id,r.observation_id,r.scaled_amount,s.unit FROM result_exchange r JOIN source_observation s USING(observation_id) ORDER BY run_id,observation_id'):
        numeric=sql_decimal(amount) if amount is not None and unit else None
        rows.append({'kind':'result','key':run+':'+oid,'raw_text':amount,'unit':unit,'numeric':numeric,'status':'ELIGIBLE' if numeric is not None else 'EXCLUDED_UNIT_OR_PRECISION'})
    c.close();assert before==hashlib.sha256(path.read_bytes()).hexdigest()
    out=ROOT/'build/decimal-projection';out.mkdir(parents=True,exist_ok=True)
    (out/'projection.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # All values enter through SQL quoted strings. Numeric coercion occurs only after exact fit checks above.
    def quote(value):return 'NULL' if value is None else "'"+value.replace("'","''")+"'"
    sql='CREATE TABLE numeric_review (kind VARCHAR(8) NOT NULL, identity_key VARCHAR(260) NOT NULL, raw_text TEXT, unit_code VARCHAR(128), amount DECIMAL(65,30), status VARCHAR(40) NOT NULL, PRIMARY KEY(kind,identity_key), CHECK((status=\'ELIGIBLE\' AND amount IS NOT NULL AND unit_code IS NOT NULL) OR (status=\'EXCLUDED_UNIT_OR_PRECISION\' AND amount IS NULL)));\n'
    sql+='\n'.join('INSERT INTO numeric_review VALUES('+','.join(quote(row[k]) for k in ['kind','key','raw_text','unit','numeric','status'])+');' for row in rows)
    (out/'projection.sql').write_text(sql+'\n',encoding='utf-8')
    report={'scope':'LOCAL_NUMERIC_QUERY_PROJECTION_NOT_PRODUCTION','model_release_id':release['release_id'],'rows':len(rows),'status_counts':dict(Counter(row['status'] for row in rows)),'sql_decimal':'DECIMAL(65,30)','rounding_applied':False,'source_database_unchanged':True,'production_changed':False}
    (ROOT/'evidence/decimal-projection.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build()))
