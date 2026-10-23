"""Load the full dataset into an owned, persistent local MySQL workspace."""
import argparse
import hashlib
import json
import os
import secrets
import subprocess
import sys
import time
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NAME='tamsoodbase-mysql'
VOLUME='tamsoodbase-mysql-data'
OWNER=hashlib.sha256(str(ROOT).lower().encode()).hexdigest()
CONFIG=ROOT/'.local/mysql-workspace.json'


def workspace(action='load',reports=False,reusable=False,check_reference=False):
    def docker(*args,input=None,env=None,check=True):
        result=subprocess.run(['docker',*args],input=input,capture_output=True,env=env,timeout=180)
        if check and result.returncode:
            message=result.stderr.decode('utf-8',errors='replace')
            if CONFIG.exists(): message=message.replace(json.loads(CONFIG.read_text())['password'],'[redacted]')
            raise RuntimeError(message)
        return result
    existing=docker('container','inspect',NAME,check=False)
    if existing.returncode==0:
        info=json.loads(existing.stdout)[0]
        if (info['Config']['Labels'] or {}).get('org.tamsood.workspace')!=OWNER:
            raise RuntimeError('Container name belongs to another workspace; no changes made')
        if not any(m.get('Name')==VOLUME and m['Destination']=='/var/lib/mysql' for m in info['Mounts']):
            raise RuntimeError('Unexpected database volume; no changes made')
        if not CONFIG.exists(): raise RuntimeError('Local credentials missing; existing database left untouched')
    if action=='stop':
        if existing.returncode==0: docker('stop',NAME)
        print('Managed MySQL workspace stopped');return
    if action=='status' and (existing.returncode or not info['State']['Running']):
        print(json.dumps({'container':NAME,'running':False,'database_checked':False}));return
    if not CONFIG.exists():
        if docker('volume','inspect',VOLUME,check=False).returncode==0:
            raise RuntimeError('Volume already exists without known credentials; no changes made')
        CONFIG.parent.mkdir(exist_ok=True)
        CONFIG.write_text(json.dumps({'container':NAME,'volume':VOLUME,'owner':OWNER,'password':secrets.token_urlsafe(32)}),encoding='utf-8')
    config=json.loads(CONFIG.read_text())
    if config['owner']!=OWNER: raise RuntimeError('Credential owner mismatch')
    password=config['password']
    if existing.returncode:
        docker('run','--pull=never','--detach','--name',NAME,'--label','org.tamsood.workspace='+OWNER,
               '--network','none','--mount','type=volume,source='+VOLUME+',target=/var/lib/mysql',
               '-e','MYSQL_ROOT_PASSWORD','mysql:8.1',env=os.environ|{'MYSQL_ROOT_PASSWORD':password})
    elif not info['State']['Running']: docker('start',NAME)

    def query(body,check=True):
        return docker('exec','-i','-e','MYSQL_PWD='+password,NAME,'mysql','-h127.0.0.1','--protocol=TCP','-uroot',
            '--default-character-set=utf8mb4','--batch','--skip-column-names',input=body,check=check)

    deadline=time.monotonic()+100
    while query(b'SELECT 1;',False).returncode:
        if time.monotonic()>deadline: raise RuntimeError('MySQL workspace readiness timed out')
        time.sleep(2)
    if action in ('load','load-reference'):
        if action=='load':
            for path in ('sql/mysql/full-schema.sql','build/full-mysql.sql'):
                query((ROOT/path).read_bytes())
        if reports:
            for folder_name in ('report-pilot','sprc-report'):
                folder=ROOT/'build'/folder_name
                if not (folder/'report.json').exists(): continue
                report=json.loads((folder/'report.json').read_text(encoding='utf-8'))
                query((folder/'load-mysql.sql').read_bytes())
                digest=report['pdf_sha256']
                if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest): raise ValueError('Invalid report hash')
                result=query(('SELECT metric_id,reference_year,amount,HEX(CAST(payload_json AS CHAR)) FROM tamsood_research.report_metric WHERE pdf_sha256=\''+digest+'\';').encode()).stdout.decode()
                data=[line.split('\t') for line in result.splitlines()]
                actual={(parts[0],int(parts[1])):Decimal(parts[2]) for parts in data}
                expected={(r['metric_id'],r['year']):Decimal(r['value']) for r in report['rows']}
                if actual!=expected: raise RuntimeError('Report MySQL numeric verification failed')
                actual_payloads={(p[0],int(p[1])):json.loads(bytes.fromhex(p[3]).decode('utf-8')) for p in data}
                if actual_payloads!={(r['metric_id'],r['year']):r for r in report['rows']}: raise RuntimeError('Report metadata verification failed')
                (folder/'mysql-verification.json').write_text(json.dumps({'pdf_sha256':digest,'report_json_sha256':hashlib.sha256((folder/'report.json').read_bytes()).hexdigest(),'numeric_values_checked':len(actual),'metadata_records_checked':len(data),'result':'passed','competition_accepted':0},indent=2),encoding='utf-8')
        if reusable or action=='load-reference':
            folder=ROOT/'build/reusable';manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
            sql=(folder/'load-mysql.sql').read_bytes()
            if hashlib.sha256(sql).hexdigest()!=manifest['files']['load-mysql.sql']: raise RuntimeError('Reusable SQL hash mismatch')
            query(sql)
            release=manifest['release_id']
            if len(release)!=64 or any(c not in '0123456789abcdef' for c in release): raise ValueError('Invalid release ID')
            body="SELECT observation_id,scaled_amount,unit_code,decision,data_kind,aggregation_role,pdf_sha256,pdf_page,raw_value,policy_version FROM tamsood_reusable.reference_catalog WHERE release_id='"+release+"';"
            lines=[line.split('\t') for line in query(body.encode()).stdout.decode().splitlines()]
            rows=json.loads((folder/'all-reference.json').read_text(encoding='utf-8'))
            actual={p[0]:(Decimal(p[1]),p[2],p[3],p[4],p[5],p[6],int(p[7]),p[8],p[9]) for p in lines}
            expected={r['observation_id']:(Decimal(r['scaled_amount']),r['unit_code'],r['decision'],r['data_kind'],r['aggregation_role'],r['pdf_sha256'],r['pdf_page'],r['raw_value'],r['policy_version']) for r in rows}
            if actual!=expected: raise RuntimeError('Reusable relational roundtrip failed')
            verification={'release_id':release,'records_checked':len(rows),'result':'passed','fields_checked':['scaled_amount','unit_code','decision','data_kind','aggregation_role','pdf_sha256','pdf_page','raw_value','policy_version'],'export_manifest_sha256':hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest()}
            if check_reference:
                oid=rows[0]['observation_id']
                mid=query(("SELECT metric_key FROM tamsood_reusable.observation WHERE observation_id='"+oid+"';").encode()).stdout.decode().strip()
                cases={
                  'negative_amount':("UPDATE observation SET scaled_amount=-1 WHERE observation_id='"+oid+"'",3819),
                  'unknown_kind':("UPDATE metric SET data_kind='INVENTED' WHERE metric_key='"+mid+"'",3819),
                  'missing_context':("UPDATE metric SET context_id='"+'0'*64+"' WHERE metric_key='"+mid+"'",1452),
                  'unknown_decision':("UPDATE review SET decision='MTEC_APPROVED' WHERE observation_id='"+oid+"'",3819),
                  'duplicate_identity':("INSERT INTO observation SELECT * FROM observation WHERE observation_id='"+oid+"'",1062),
                  'missing_observation':("UPDATE review SET observation_id='"+'0'*64+"' WHERE observation_id='"+oid+"'",1452)}
                verified={}
                for name,(statement,code) in cases.items():
                    # Success executes ROLLBACK; error closes the connection and rolls back.
                    result=query(('USE tamsood_reusable; START TRANSACTION; '+statement+'; ROLLBACK;').encode(),False)
                    if result.returncode==0 or ('ERROR '+str(code)).encode() not in result.stderr: raise RuntimeError('Reference constraint failed: '+name)
                    verified[name]={'result':'rejected_as_expected','mysql_error':code}
                verification['constraint_checks']=verified
            (folder/'mysql-verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
            print(json.dumps({'reusable_records_verified':len(rows),'team_accepted_reference':manifest['accepted_reference'],'held_context':manifest['held_context']},indent=2))
            if action=='load-reference': return
    output=query(b'USE tamsood_research; SELECT (SELECT COUNT(*) FROM source_record),(SELECT COUNT(*) FROM observation),(SELECT COUNT(*) FROM rejected_record),(SELECT COUNT(*) FROM deduplicated_pending);').stdout.decode().strip()
    fields=output.split('\t')
    report={'container':NAME,'volume':VOLUME,'network':'none','published_ports':[],
            'raw_rows':int(fields[0]),'observations':int(fields[1]),'rejected':int(fields[2]),'deduplicated_pending':int(fields[3]),
            'storage':'persistent_named_volume','competition_accepted':0}
    (ROOT/'build/mysql-workspace-status.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['load','load-reference','status','stop'],nargs='?',default='load')
    parser.add_argument('--reports',action='store_true',help='Also import and verify the separately built PDF report pilot')
    parser.add_argument('--reusable',action='store_true',help='Also import and verify the typed team reference-data release')
    parser.add_argument('--check-reference',action='store_true',help='Test reusable constraints in rolled-back transactions')
    args=parser.parse_args();workspace(args.action,args.reports,args.reusable,args.check_reference)
