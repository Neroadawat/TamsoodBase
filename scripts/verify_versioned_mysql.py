"""Verify MySQL equivalent in a uniquely named disposable schema on the owned runtime.
No API migration, grants, ports, containers, production-table writes or raw upload.
"""
import base64,hashlib,json,subprocess
from scripts.build_versioned_inventory import ROOT,create_store


def literal(value):
    if value is None:return 'NULL'
    if isinstance(value,int):return str(value)
    return 'CONVERT(0x'+str(value).encode('utf8').hex()+' USING utf8mb4)'


REMOTE=r'''
import base64,json,subprocess,uuid,urllib.request,re
payload=json.loads(base64.b64decode(PAYLOAD))
container='tamsoodbase-mysql-runtime'
def call(args,**kwargs):return subprocess.run(args,capture_output=True,timeout=30,**kwargs)
label=call(['docker','inspect','--format','{{index .Config.Labels "org.tamsood.project"}}',container])
if label.returncode or label.stdout.decode().strip()!='TamsoodBase-MySQL-Runtime':raise RuntimeError('Owner check failed')
before=call(['docker','ps','--format','{{.ID}} {{.Names}}']).stdout
def health():
 with urllib.request.urlopen('http://127.0.0.1:8765/readyz',timeout=10) as r:return r.status==200
if not health():raise RuntimeError('Active API not ready before test')
db='ts_verify_'+uuid.uuid4().hex[:16]
owner=uuid.uuid4().hex
def sql(body,expect_error=False,without_db=False,expected_error=1644):
 cmd=['docker','exec','-i',container,'sh','-c','export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"; exec mysql -uroot --batch --raw --skip-column-names --default-character-set=utf8mb4']
 result=call(cmd,input=(('' if without_db else 'USE `'+db+'`;\n')+body).encode())
 if expect_error:
  if result.returncode==0:raise RuntimeError('Invalid SQL unexpectedly accepted')
  found=re.search(r'ERROR (\d+)',result.stderr.decode(errors='replace'))
  if not found or int(found[1])!=expected_error:raise RuntimeError('Negative case failed for an unexpected reason')
 elif result.returncode:raise RuntimeError('MySQL verification SQL failed: '+result.stderr.decode(errors='replace')[:300])
 return result
created=False
result={'scope':'OWNED_MYSQL_TEMPORARY_SCHEMA_NOT_PRODUCTION_MIGRATION','negative_checks':{}}
try:
 sql('CREATE DATABASE `'+db+'` CHARACTER SET utf8mb4 COLLATE utf8mb4_bin; USE `'+db+'`; CREATE TABLE lab_owner(owner CHAR(32) PRIMARY KEY); INSERT INTO lab_owner VALUES(\''+owner+'\');',without_db=True)
 created=True
 sql(payload['ddl'])
 sql(payload['load'])
 result['engine_version']=sql('SELECT VERSION();').stdout.decode().strip()
 actual=[json.loads(bytes.fromhex(line).decode()) for line in sql('SELECT HEX(CAST(original_json AS CHAR CHARACTER SET utf8mb4)) FROM review_export ORDER BY observation_id;').stdout.decode().splitlines()]
 if actual!=payload['expected']:raise RuntimeError('MySQL source payload roundtrip differs')
 typed=[json.loads(bytes.fromhex(line).decode()) for line in sql("SELECT HEX(CAST(JSON_OBJECT('observation_id',observation_id,'process',process_id,'flow',flow_label,'amount',amount,'unit',unit_code,'direction',direction,'role',role,'reference_amount',reference_amount,'reference_unit',reference_unit) AS CHAR CHARACTER SET utf8mb4)) FROM review_export ORDER BY observation_id;").stdout.decode().splitlines()]
 if typed!=payload['typed']:raise RuntimeError('MySQL typed join differs')
 for name,statement in payload['negative'].items():
  sql(statement,expect_error=True);result['negative_checks'][name]=True
 batch=sql(payload['rollback_batch'],expect_error=True,expected_error=1452)
 if batch.stdout.decode().strip()!='59':raise RuntimeError('Rollback test did not reach its first successful insert')
 if sql('SELECT COUNT(*) FROM source_observation;').stdout.decode().strip()!='58':raise RuntimeError('Late batch error left a partial source row')
 result.update(source_rows=58,full_payload_roundtrip=True,typed_join_roundtrip=True,failed_batch_connection_close_rollback=True,
               null_unit_holds=int(sql('SELECT COUNT(*) FROM source_observation WHERE unit_code IS NULL;').stdout),
               sealed_versions=int(sql('SELECT COUNT(*) FROM process_dataset_version WHERE sealed=1;').stdout),production_migrated=False)
finally:
 if created:
  if sql('SELECT owner FROM lab_owner;').stdout.decode().strip()!=owner:raise RuntimeError('Refusing cleanup: ownership marker differs')
  sql('DROP DATABASE `'+db+'`;',without_db=True)
  result['temporary_schema_removed']=True
 result['running_container_ids_unchanged']=before==call(['docker','ps','--format','{{.ID}} {{.Names}}']).stdout
 result['active_api_ready_after']=health()
if not result['running_container_ids_unchanged'] or not result['active_api_ready_after']:raise RuntimeError('Runtime state changed during test; investigate')
print(json.dumps(result))
'''


def main():
    def read(name):return json.loads((ROOT/name).read_text(encoding='utf8'))
    up=read('build/upstream-inventory/report.json');base=read('build/product-inventory/report.json')
    con,versions=create_store(up,base)
    try:
        lines=['START TRANSACTION;']
        for table in ('source_observation','process_dataset_version','dataset_exchange','numeric_parse_audit'):
            for row in con.execute('SELECT * FROM '+table):
                values=list(row)
                if table=='process_dataset_version':values[-1]=0
                lines.append('INSERT INTO '+table+' VALUES('+','.join(literal(v) for v in values)+');')
        lines.append('UPDATE process_dataset_version SET sealed=1; COMMIT;')
    finally:con.close()
    rows=sorted(up['rows']+base['rows'],key=lambda r:r['observation_id'])
    typed=[{k:r[k] for k in ('observation_id','process','flow','amount','unit','direction','role','reference_amount','reference_unit')} for r in rows]
    draft='0'*64
    invalid_process="START TRANSACTION; INSERT INTO process_dataset_version SELECT '"+draft+"',process_id,contract_version,reference_amount,reference_unit,reference_observation_id,0,'UNRESOLVED',0 FROM process_dataset_version WHERE process_id='CPO'; INSERT INTO dataset_exchange SELECT '"+draft+"',observation_id FROM source_observation WHERE process_id='FFB' LIMIT 1; COMMIT;"
    negative={'source_update':"UPDATE source_observation SET amount='0';",'source_delete':'DELETE FROM source_observation;',
        'sealed_version_change':"UPDATE process_dataset_version SET reference_unit='kg';",
        'membership_delete':'DELETE FROM dataset_exchange;','parse_update':'UPDATE numeric_parse_audit SET allocation_applied=1;',
        'process_mismatch':invalid_process}
    negative['typed_payload_mismatch']="INSERT INTO source_observation SELECT 'TEST_ONLY_MISMATCH',process_id,source_hash,flow_label,'999',unit_code,direction,role,source_status,JSON_SET(original_json,'$.observation_id','TEST_ONLY_MISMATCH') FROM source_observation LIMIT 1;"
    negative['reference_product_mismatch']="INSERT INTO process_dataset_version SELECT '"+draft+"',process_id,contract_version,reference_amount,reference_unit,(SELECT observation_id FROM source_observation WHERE process_id='FFB' AND role='REFERENCE_PRODUCT'),0,'UNRESOLVED',0 FROM process_dataset_version WHERE process_id='CPO';"
    rollback="START TRANSACTION; INSERT INTO source_observation SELECT 'TEST_ONLY_ROLLBACK',process_id,source_hash,flow_label,amount,unit_code,direction,role,source_status,JSON_SET(original_json,'$.observation_id','TEST_ONLY_ROLLBACK') FROM source_observation LIMIT 1; SELECT COUNT(*) FROM source_observation; INSERT INTO dataset_exchange VALUES('missing-version','missing-observation'); COMMIT;"
    ddl=(ROOT/'sql/mysql/versioned-review.sql').read_text(encoding='utf8')
    payload={'ddl':ddl,'load':'\n'.join(lines),'expected':rows,'typed':typed,'negative':negative,'rollback_batch':rollback}
    encoded=base64.b64encode(json.dumps(payload,ensure_ascii=False).encode()).decode()
    script=REMOTE.replace('PAYLOAD',repr(encoded),1)
    run=subprocess.run(['C:/Program Files/Git/usr/bin/ssh.exe','-i',str(ROOT/'.local/ec2-deploy.pem'),'-o','BatchMode=yes','-o','ConnectTimeout=8','ubuntu@54.206.67.32','python3 -'],input=script.encode(),capture_output=True,timeout=150)
    if run.returncode:raise RuntimeError(run.stderr.decode(errors='replace')[-1500:])
    result=json.loads(run.stdout)
    result['schema_sha256']=hashlib.sha256(ddl.encode()).hexdigest()
    (ROOT/'evidence/versioned-mysql.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
