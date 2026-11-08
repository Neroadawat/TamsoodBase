"""Check the new model in an owner-marked temporary MySQL schema; never migrate API."""
import base64
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
from scripts.verify_versioned_mysql import literal

ROOT=Path(__file__).resolve().parents[1]


def ddl():
    text=(ROOT/'sql/activity-model-review.sql').read_text(encoding='utf-8')
    text=text.replace('PRAGMA foreign_keys=ON;','')
    text=re.sub(r'CREATE TRIGGER dataset_process_membership.*?END;', '',text,flags=re.S)
    primary={'release_manifest':'release_id','source_observation':'observation_id','process_dataset_version':'version_id','product_system_version':'model_id','scenario_case':'scenario_id','dataset_exchange':'version_id,observation_id'}
    text=re.sub(r'REFERENCES (\w+)(?![\w(])',lambda m:'REFERENCES '+m[1]+'('+primary[m[1]]+')',text)
    text=re.sub(r'(\w+_json) TEXT',r'\1 JSON',text).replace(' TEXT',' VARCHAR(128)')
    text=text.replace("CHECK(json_type(payload_json,'$.amount') IS 'text')","CHECK(JSON_CONTAINS_PATH(payload_json,'one','$.amount')=1 AND JSON_TYPE(JSON_EXTRACT(payload_json,'$.amount'))='STRING')")
    text=text.replace("CHECK(json_extract(payload_json,'$.amount')=amount)","CHECK(JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.amount'))=amount)")
    text=text.replace("CHECK(json_type(payload_json,'$.unit') IS NOT NULL)","CHECK(JSON_CONTAINS_PATH(payload_json,'one','$.unit')=1)")
    text=text.replace("CHECK(json_extract(payload_json,'$.unit') IS unit)","CHECK((CASE WHEN JSON_TYPE(JSON_EXTRACT(payload_json,'$.unit'))='NULL' THEN NULL ELSE JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.unit')) END) <=> unit)")
    def inline(match):
        name,body=match[1],match[2];constraints=[]
        def convert(m):
            constraints.append('FOREIGN KEY('+m[1]+') REFERENCES '+m[3]+'('+m[4]+')')
            return m[1]+m[2]
        body=re.sub(r'(\w+)( VARCHAR\(128\)(?: NOT NULL| PRIMARY KEY)*) REFERENCES (\w+)\(([^)]+)\)',convert,body)
        return 'CREATE TABLE '+name+'('+body+(','+','.join(constraints) if constraints else '')+') ENGINE=InnoDB;'
    text=re.sub(r'CREATE TABLE (\w+)\((.*?)\);',inline,text,flags=re.S)
    tables=re.findall(r'CREATE TABLE (\w+)\(',text)
    triggers=["CREATE TRIGGER dataset_process_membership BEFORE INSERT ON dataset_exchange FOR EACH ROW BEGIN IF NOT ((SELECT COALESCE(JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.process')),JSON_UNQUOTE(JSON_EXTRACT(payload_json,'$.reference_product'))) FROM source_observation WHERE observation_id=NEW.observation_id) <=> (SELECT process_name FROM process_dataset_version WHERE version_id=NEW.version_id)) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Source process membership mismatch'; END IF; END"]
    for table in tables:
        for action in ('UPDATE','DELETE'):
            triggers.append('CREATE TRIGGER immutable_'+table+'_'+action.lower()+' BEFORE '+action+' ON '+table+" FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Immutable model release'")
        if table!='release_seal':triggers.append('CREATE TRIGGER sealed_'+table+'_insert BEFORE INSERT ON '+table+" FOR EACH ROW BEGIN IF EXISTS(SELECT 1 FROM release_seal) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sealed model release'; END IF; END")
    return text+'\nDELIMITER $$\n'+'$$\n'.join(triggers)+'$$\nDELIMITER ;\n',tables


REMOTE=r'''
import base64,json,subprocess,uuid,urllib.request,re
p=json.loads(base64.b64decode(PAYLOAD));container='tamsoodbase-mysql-runtime'
def run(args,**kw):return subprocess.run(args,capture_output=True,timeout=50,**kw)
owner=run(['docker','inspect','--format','{{index .Config.Labels "org.tamsood.project"}}',container])
if owner.returncode or owner.stdout.decode().strip()!='TamsoodBase-MySQL-Runtime':raise RuntimeError('Container owner mismatch')
def ready():
 with urllib.request.urlopen('http://127.0.0.1:8765/readyz',timeout=15) as r:return r.status==200
if not ready():raise RuntimeError('API not ready before isolated verification')
db='ts_activity_'+uuid.uuid4().hex[:16];marker=uuid.uuid4().hex
def sql(body,negative=False,root=False,expected_error=1644):
 cmd=['docker','exec','-i',container,'sh','-c','export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"; exec mysql -uroot --batch --raw --skip-column-names --default-character-set=utf8mb4']
 r=run(cmd,input=(('' if root else 'USE `'+db+'`;\n')+body).encode())
 if negative:
  if not r.returncode:raise RuntimeError('Negative SQL was accepted')
  found=re.search(r'ERROR (\d+)',r.stderr.decode(errors='replace'))
  if not found or int(found[1])!=expected_error:raise RuntimeError('Negative SQL failed for an unexpected reason')
 elif r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[:450])
 return r
created=False
try:
 sql('CREATE DATABASE `'+db+'` CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;USE `'+db+'`;CREATE TABLE lab_owner(marker CHAR(32) PRIMARY KEY);INSERT INTO lab_owner VALUES(\''+marker+'\');',root=True);created=True
 sql(p['ddl']);sql(p['load'])
 actual=[json.loads(bytes.fromhex(line).decode()) for line in sql('SELECT HEX(CAST(payload_json AS CHAR CHARACTER SET utf8mb4)) FROM source_observation ORDER BY observation_id;').stdout.decode().splitlines()]
 if actual!=p['expected_sources']:raise RuntimeError('Source payload roundtrip mismatch')
 results=[line.split('\t') for line in sql("SELECT run_id,observation_id,COALESCE(scaled_amount,'<NULL>'),status FROM result_exchange ORDER BY run_id,observation_id;").stdout.decode().splitlines()]
 if results!=p['expected_results']:raise RuntimeError('All result cells roundtrip mismatch')
 checks={}
 for name,body in p['negative_before_seal'].items():sql(body,negative=True,expected_error=3819 if name=='missing_json_amount' else 1644);checks[name]=True
 sql('INSERT INTO release_seal VALUES(\''+p['release_id']+'\');')
 for name,body in p['negative_after_seal'].items():sql(body,negative=True);checks[name]=True
 result={'scope':'OWNED_TEMPORARY_MYSQL_SCHEMA_NOT_API_MIGRATION','engine_version':sql('SELECT VERSION();').stdout.decode().strip(),'source_payloads_checked':len(actual),'result_rows_all_cells_checked':len(results),'negative_checks':checks,'production_API_ready_after':ready(),'production_tables_changed':False}
 if not result['production_API_ready_after']:raise RuntimeError('API readiness changed')
finally:
 if created:
  if sql('SELECT marker FROM lab_owner;').stdout.decode().strip()!=marker:raise RuntimeError('Cleanup owner mismatch')
  sql('DROP DATABASE `'+db+'`;',root=True)
print(json.dumps(result))
'''


def main():
    schema,tables=ddl();(ROOT/'sql/mysql/activity-model-review.sql').write_text('-- Isolated candidate; not a production migration.\n'+schema,encoding='utf-8')
    evidence=json.loads((ROOT/'evidence/activity-model-store.json').read_text(encoding='utf-8'))
    path=ROOT/evidence['database']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=evidence['database_sha256']:raise ValueError('Changed source store')
    conn=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
    try:
        lines=['START TRANSACTION;']
        for table in tables:
            if table=='release_seal':continue
            for row in conn.execute('SELECT * FROM '+table):lines.append('INSERT INTO '+table+' VALUES('+','.join(map(literal,row))+');')
        lines.append('COMMIT;')
        sources=[json.loads(r[0]) for r in conn.execute('SELECT payload_json FROM source_observation ORDER BY observation_id')]
        results=[list(r) for r in conn.execute("SELECT run_id,observation_id,COALESCE(scaled_amount,'<NULL>'),status FROM result_exchange ORDER BY run_id,observation_id")]
    finally:conn.close()
    payload={'ddl':schema,'load':'\n'.join(lines),'release_id':evidence['release_id'],'expected_sources':sources,'expected_results':results,
      'negative_before_seal':{'missing_json_amount':"INSERT INTO source_observation VALUES('invalid','12','kg',JSON_OBJECT('unit','kg'));",'process_mismatch':"INSERT INTO dataset_exchange SELECT v.version_id,s.observation_id FROM process_dataset_version v CROSS JOIN source_observation s WHERE v.process_name='CPO' AND JSON_UNQUOTE(JSON_EXTRACT(s.payload_json,'$.process'))='FAME' LIMIT 1;"},
      'negative_after_seal':{'immutable_source':"UPDATE source_observation SET amount='999';",'immutable_result':'DELETE FROM result_exchange;','late_insert':"INSERT INTO required_decision SELECT scenario_id,'late','OPEN' FROM scenario_case LIMIT 1;"}}
    script=REMOTE.replace('PAYLOAD',repr(base64.b64encode(json.dumps(payload,ensure_ascii=False).encode()).decode()),1)
    run=subprocess.run(['C:/Program Files/Git/usr/bin/ssh.exe','-i',str(ROOT/'.local/ec2-deploy.pem'),'-o','BatchMode=yes','-o','ConnectTimeout=8','ubuntu@54.206.67.32','python3 -'],input=script.encode(),capture_output=True,timeout=180)
    if run.returncode:raise RuntimeError(run.stderr.decode(errors='replace')[-1800:])
    report=json.loads(run.stdout);report.update(model_release_id=evidence['release_id'],schema_sha256=hashlib.sha256(schema.encode()).hexdigest(),passed=True)
    (ROOT/'evidence/activity-model-mysql.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
