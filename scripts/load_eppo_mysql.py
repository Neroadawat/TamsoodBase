"""Load EPPO snapshots into an owned MySQL database and verify every record."""
import hashlib
import json
import os
import subprocess
from decimal import Decimal
from pathlib import Path
from load_supplemental_mysql import literal, decimal_value
from mysql_workspace import NAME, OWNER, VOLUME, CONFIG

ROOT=Path(__file__).resolve().parents[1]


def main():
    config=json.loads(CONFIG.read_text(encoding='utf-8'))
    info=json.loads(subprocess.check_output(['docker','inspect',NAME]))[0]
    if config['owner']!=OWNER or (info['Config']['Labels'] or {}).get('org.tamsood.workspace')!=OWNER or not any(m.get('Name')==VOLUME and m['Destination']=='/var/lib/mysql' for m in info['Mounts']):
        raise RuntimeError('Workspace ownership mismatch')
    def query(sql,check=True):
        result=subprocess.run(['docker','exec','-i','-e','MYSQL_PWD',NAME,'mysql','-uroot','--batch','--skip-column-names','--default-character-set=utf8mb4'],input=sql.encode(),capture_output=True,timeout=180,env=os.environ|{'MYSQL_PWD':config['password']})
        if check and result.returncode:raise RuntimeError(result.stderr.decode(errors='replace').replace(config['password'],'[redacted]'))
        return result
    schema=(ROOT/'sql/mysql/eppo-schema.sql').read_text(encoding='utf-8');query(schema)
    body=(ROOT/'build/eppo/report.json').read_bytes();rows=json.loads(body)['rows']
    manifest=json.loads((ROOT/'data/raw/eppo/manifest.json').read_text(encoding='utf-8'))
    statements=['USE tamsood_eppo; START TRANSACTION;']
    for key,src in manifest['resources'].items():
        statements.append('INSERT IGNORE INTO source_snapshot VALUES ('+','.join(map(literal,[src['sha256'],key,src['url'],json.dumps(src,ensure_ascii=False)]))+');')
    for r in rows:
        values=[literal(r['observation_id']),literal(r['source_sha256']),str(r['reference_year']),str(r['month']),literal(r['subject']),decimal_value(r['amount']),literal(r['unit']),literal(r['status']),str(r['source_line']),literal(json.dumps(r,ensure_ascii=False))]
        statements.append('INSERT IGNORE INTO observation VALUES ('+','.join(values)+');')
    statements.append('COMMIT;');query('\n'.join(statements))
    total=0
    for src in manifest['resources'].values():
        output=query('USE tamsood_eppo; SELECT observation_id,reference_year,month,HEX(subject),amount,HEX(unit_code),status,source_line,HEX(CAST(payload AS CHAR)) FROM observation WHERE snapshot_id='+literal(src['sha256'])+';').stdout.decode()
        actual={}
        for line in output.splitlines():
            p=line.split('\t');actual[p[0]]=(int(p[1]),int(p[2]),bytes.fromhex(p[3]).decode(),Decimal(p[4]),bytes.fromhex(p[5]).decode(),p[6],int(p[7]),json.loads(bytes.fromhex(p[8]).decode()))
        expected={r['observation_id']:(r['reference_year'],r['month'],r['subject'],Decimal(r['amount']),r['unit'],r['status'],r['source_line'],r) for r in rows if r['source_sha256']==src['sha256']}
        if actual!=expected:raise RuntimeError('EPPO MySQL roundtrip mismatch')
        total+=len(actual)
    checks={}
    for name,statement,code in [
        ('invalid_month','UPDATE observation SET month=13 LIMIT 1',3819),
        ('unknown_snapshot',"UPDATE observation SET snapshot_id=REPEAT('0',64) LIMIT 1",1452),
        ('negative_quantity','UPDATE observation SET amount=-1 LIMIT 1',3819)]:
        result=query('USE tamsood_eppo; START TRANSACTION; '+statement+'; ROLLBACK;',False)
        if not result.returncode or ('ERROR '+str(code)).encode() not in result.stderr:raise RuntimeError('Constraint failed: '+name)
        checks[name]='rejected_as_expected'
    evidence=dict(result='passed',database='tamsood_eppo',records_checked=total,report_sha256=hashlib.sha256(body).hexdigest(),schema_sha256=hashlib.sha256(schema.encode()).hexdigest(),constraint_checks=checks,acceptance_changed=False)
    (ROOT/'evidence/eppo-mysql.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8');print(json.dumps(evidence,indent=2))


if __name__=='__main__':main()
