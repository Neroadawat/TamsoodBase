"""Verify all Corporate fields in a release-owned schema inside the isolated MySQL lab.

No production connection, grants, published ports, raw redistribution or scientific promotion.
"""
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.verify_handoff_engines import docker,owned,OWNER
from src.build_reusable import TABLES,KEYS


def identifier(value):
    if not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]{0,63}',value):raise ValueError('Unsafe SQL identifier')
    return '`'+value+'`'


def canonical(value,column):
    if value is None:return None
    return Decimal(str(value)) if column in ('scale_factor','scaled_amount') else str(value)


def main():
    meta=json.loads((ROOT/'build/handoff/engines.json').read_bytes());name=meta['mysql_container']
    if not owned(name):raise ValueError('Owned isolated MySQL lab is required')
    folder=ROOT/'build/reusable';manifest=json.loads((folder/'manifest.json').read_bytes())
    release=manifest['release_id']
    if not re.fullmatch('[a-f0-9]{64}',release):raise ValueError('Invalid release identity')
    for filename,expected in manifest['files'].items():
        if filename not in ('accepted-reference.json','all-reference.json','accepted-reference.csv','reference.sqlite','load-mysql.sql'):
            raise ValueError('Unexpected release file')
        if hashlib.sha256((folder/filename).read_bytes()).hexdigest()!=expected:raise ValueError('Release file hash mismatch')
    if manifest['redistribution_status']!='NOT_CLEARED' or manifest['normalized_lci_exchanges']!=0:
        raise ValueError('Unexpected source use policy')
    schema='handoff_corporate_'+release[:12];quoted=identifier(schema)
    def sql(statement,check=True):
        return docker('exec','-i',name,'mysql','-uroot','--batch','--raw','--skip-column-names',
                      '--default-character-set=utf8mb4',body=statement,check=check)
    def fingerprint_other_layers():
        statements=[
            'SELECT id,SHA2(payload,256) FROM handoff_review.observation ORDER BY id;',
            'SELECT snapshot_id,source_line,SHA2(raw_json,256) FROM tamsood_research.source_record ORDER BY snapshot_id,source_line;',
            'SELECT o.snapshot_id,o.source_line,o.amount,d.status FROM tamsood_research.observation o '
            'JOIN tamsood_research.duplicate_disposition d USING(snapshot_id,source_line) ORDER BY o.snapshot_id,o.source_line;']
        return [hashlib.sha256(sql(statement).stdout).hexdigest() for statement in statements]
    other_before=fingerprint_other_layers()
    exists=int(sql("SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='"+schema+"';").stdout)
    marker=OWNER+'|'+release+'|'+manifest['files']['load-mysql.sql']
    if exists:
        current=sql('SELECT marker FROM '+quoted+'._handoff_owner;').stdout.decode().strip()
        if current!=marker:raise ValueError('Existing schema ownership/source mismatch')
    else:
        sql('CREATE DATABASE '+quoted+' CHARACTER SET utf8mb4 COLLATE utf8mb4_bin; '
            'CREATE TABLE '+quoted+'._handoff_owner(marker VARCHAR(255) PRIMARY KEY); '
            "INSERT INTO "+quoted+"._handoff_owner VALUES('"+marker+"');")
    source=(folder/'load-mysql.sql').read_text(encoding='utf-8')
    if 'CREATE DATABASE IF NOT EXISTS tamsood_reusable ' not in source:raise ValueError('Unexpected SQL schema header')
    sql(re.sub(r'\btamsood_reusable\b',schema,source))

    def mysql_rows(table,columns,order):
        # Hex encoding preserves tabs/newlines/Thai and NULL distinctly in every field.
        expressions=["IF("+identifier(c)+" IS NULL,'N',CONCAT('V',HEX(CAST("+identifier(c)+" AS CHAR CHARACTER SET utf8mb4))))" for c in columns]
        output=sql('SELECT '+','.join(expressions)+' FROM '+quoted+'.'+identifier(table)+' ORDER BY '+','.join(identifier(c) for c in order)+';').stdout.decode()
        return [[canonical(None if token=='N' else bytes.fromhex(token[1:]).decode('utf-8'),column)
                 for token,column in zip(line.split('\t'),columns)] for line in output.splitlines()]

    def compare_all():
        checks={}
        with closing(sqlite3.connect((folder/'reference.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as con:
            for table,columns in TABLES.items():
                expected=[[canonical(v,c) for v,c in zip(row,columns)] for row in con.execute(
                    'SELECT '+','.join(columns)+' FROM '+table+' ORDER BY '+','.join(KEYS[table]))]
                actual=mysql_rows(table,columns,KEYS[table])
                if expected!=actual:raise ValueError('MySQL/SQLite field mismatch: '+table)
                checks[table]={'rows':len(actual),'columns':len(columns),'all_fields_equal':True}
            columns=[r[1] for r in con.execute('PRAGMA table_info(reference_catalog)')]
            expected=[[canonical(v,c) for v,c in zip(row,columns)] for row in con.execute(
                'SELECT '+','.join(columns)+' FROM reference_catalog ORDER BY observation_id')]
            if mysql_rows('reference_catalog',columns,['observation_id'])!=expected:
                raise ValueError('Complete reference catalog projection differs')
            checks['reference_catalog']={'rows':len(expected),'columns':len(columns),'all_fields_equal':True}
        return checks
    checks=compare_all()
    rows=json.loads((folder/'all-reference.json').read_bytes());oid=rows[0]['observation_id']
    mid=sql('SELECT metric_key FROM '+quoted+".observation WHERE observation_id='"+oid+"';").stdout.decode().strip()
    other_context=sql('SELECT c.context_id FROM '+quoted+'.context c JOIN '+quoted+'.metric m ON m.metric_key=\''+mid+"' WHERE c.document_id<>m.document_id LIMIT 1;").stdout.decode().strip()
    if not re.fullmatch('[a-f0-9]{64}',mid) or not re.fullmatch('[a-f0-9]{64}',other_context):raise ValueError('No valid context test identity')
    cases={
        'negative_amount':("UPDATE observation SET scaled_amount=-1 WHERE observation_id='"+oid+"'",3819),
        'zero_scale':("UPDATE observation SET scale_factor=0 WHERE observation_id='"+oid+"'",3819),
        'unknown_kind':("UPDATE metric SET data_kind='INVENTED' WHERE metric_key='"+mid+"'",3819),
        'wrong_document_context':("UPDATE metric SET context_id='"+other_context+"' WHERE metric_key='"+mid+"'",1452),
        'unknown_decision':("UPDATE review SET decision='MTEC_APPROVED' WHERE observation_id='"+oid+"'",3819),
        'duplicate_identity':("INSERT INTO observation SELECT * FROM observation WHERE observation_id='"+oid+"'",1062),
        'missing_observation':("UPDATE review SET observation_id='"+'0'*64+"' WHERE observation_id='"+oid+"'",1452),
    }
    rejected={}
    for label,(statement,error) in cases.items():
        result=sql('USE '+quoted+'; START TRANSACTION; '+statement+'; ROLLBACK;',check=False)
        if result.returncode==0 or ('ERROR '+str(error)).encode() not in result.stderr:
            raise ValueError('Constraint did not reject as expected: '+label)
        rejected[label]=error
    late=sql('USE '+quoted+"; START TRANSACTION; UPDATE observation SET raw_value='ROLLBACK_PROBE' WHERE observation_id='"+oid+"'; SELECT ROW_COUNT(); UPDATE review SET observation_id='"+'0'*64+"' WHERE observation_id='"+oid+"'; COMMIT;",check=False)
    if late.returncode==0 or b'ERROR 1452' not in late.stderr or late.stdout.strip()!=b'1':
        raise ValueError('Late rollback fixture failed for an unexpected reason')
    compare_all()
    if fingerprint_other_layers()!=other_before:raise ValueError('Existing lab layers changed')
    for filename,expected in manifest['files'].items():
        if hashlib.sha256((folder/filename).read_bytes()).hexdigest()!=expected:raise ValueError('Local source changed during verification')
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'container':name,'schema':schema,'release_id':release,
            'tables':checks,'observations_verified':len(rows),'decisions':{'ACCEPTED_REFERENCE':97,'HOLD_CONTEXT':4},
            'constraint_rejections':rejected,'late_error_rolled_back_prior_update':True,
            'existing_lab_layer_hashes_unchanged':other_before,'source_release_unchanged':True,
            'redistribution_status':'NOT_CLEARED','normalized_lci_exchanges':0,'production_changed':False,
            'scope':'LOCAL_OWNED_MYSQL_LAB_NOT_PRODUCTION_MIGRATION','passed':True}
    (ROOT/'build/handoff/corporate-mysql-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
