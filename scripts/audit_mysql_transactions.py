"""Real InnoDB transaction lab in an isolated disposable container, never workspace DB.

Synthetic rows demonstrate transaction semantics only; they are not observations.
Uses cached mysql:8.1, no ports/volume/network, and no package installations.
"""
import hashlib
import json
import os
from pathlib import Path
import queue
import secrets
import subprocess
import threading
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def docker(*args, env=None, check=True):
    result = subprocess.run(['docker', *args], capture_output=True, timeout=120, env=env)
    if check and result.returncode:
        raise RuntimeError('Docker lab command failed: '+result.stderr.decode(errors='replace')[:500])
    return result


class Session:
    def __init__(self, name, password):
        self.lines = queue.Queue()
        self.errors = []
        self.process = subprocess.Popen(
            ['docker','exec','-i','-e','MYSQL_PWD',name,'mysql','-uroot',
             '--batch','--raw','--skip-column-names','--unbuffered','--force','lab'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=True,encoding='utf-8',env=os.environ|{'MYSQL_PWD':password})
        def output():
            for line in self.process.stdout:self.lines.put(line.rstrip('\n'))
            self.lines.put(None)
        def errors():
            for line in self.process.stderr:self.errors.append(line.strip())
        threading.Thread(target=output,daemon=True).start()
        threading.Thread(target=errors,daemon=True).start()

    def sql(self, statement):
        marker='done_'+secrets.token_hex(12)
        self.process.stdin.write(statement+';\nSELECT "'+marker+'";\n')
        self.process.stdin.flush()
        rows=[]
        while True:
            line=self.lines.get(timeout=20)
            if line is None:raise RuntimeError('MySQL session closed before marker')
            if line==marker:return rows
            rows.append(line)

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            self.process.wait(timeout=20)


def audit():
    name='tamsood-txn-lab-'+secrets.token_hex(6)
    password=secrets.token_urlsafe(32)
    owner=hashlib.sha256(str(ROOT).lower().encode()).hexdigest()
    docker('image','inspect','mysql:8.1') # do not pull implicitly
    sessions=[];checks={};observed={}
    try:
        docker('run','-d','--name',name,'--label','org.tamsood.transaction-lab='+owner,
               '--network','none','--memory','768m','--pids-limit','256',
               '-e','MYSQL_ROOT_PASSWORD','mysql:8.1',env=os.environ|{'MYSQL_ROOT_PASSWORD':password})
        deadline=time.monotonic()+90
        while True:
            ready=docker('exec','-e','MYSQL_PWD',name,'mysql','-uroot','-e','SELECT 1',
                         env=os.environ|{'MYSQL_PWD':password},check=False)
            if ready.returncode==0:break
            if time.monotonic()>deadline:raise RuntimeError('Lab MySQL readiness timeout')
            time.sleep(1)
        init='CREATE DATABASE lab; USE lab; CREATE TABLE item(id INT PRIMARY KEY, amount DECIMAL(12,3) NOT NULL CHECK(amount>=0)) ENGINE=InnoDB; INSERT INTO item VALUES(1,10),(2,20);'
        docker('exec','-e','MYSQL_PWD',name,'mysql','-uroot','-e',init,env=os.environ|{'MYSQL_PWD':password})
        a=Session(name,password);sessions.append(a)
        b=Session(name,password);sessions.append(b)
        observed['version']=a.sql('SELECT VERSION()')[0]
        observed['default_isolation']=a.sql('SELECT @@transaction_isolation')[0]
        # A statement CHECK failure does not automatically roll back earlier statements.
        a.sql('START TRANSACTION; UPDATE item SET amount=11 WHERE id=1; UPDATE item SET amount=-1 WHERE id=2')
        observed['amount_after_statement_error']=a.sql('SELECT amount FROM item WHERE id=1')[0]
        checks['statement_error_does_not_undo_prior_statement']=observed['amount_after_statement_error']=='11.000'
        a.sql('ROLLBACK')
        checks['explicit_rollback_restores_whole_batch']=a.sql('SELECT amount FROM item ORDER BY id')==['10.000','20.000']
        checks['check_constraint_kept_valid_value']=a.sql('SELECT amount FROM item WHERE id=2')==['20.000']
        b.sql('SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED; START TRANSACTION')
        a.sql('START TRANSACTION; UPDATE item SET amount=12 WHERE id=1')
        checks['read_committed_prevents_dirty_read']=b.sql('SELECT amount FROM item WHERE id=1')==['10.000']
        a.sql('COMMIT')
        checks['read_committed_sees_new_commit_on_second_read']=b.sql('SELECT amount FROM item WHERE id=1')==['12.000']
        b.sql('ROLLBACK; SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ; START TRANSACTION')
        first=b.sql('SELECT amount FROM item WHERE id=1')
        count=b.sql('SELECT COUNT(*) FROM item WHERE id BETWEEN 1 AND 3')
        a.sql('START TRANSACTION; UPDATE item SET amount=13 WHERE id=1; INSERT INTO item VALUES(3,30); COMMIT')
        checks['repeatable_read_consistent_snapshot_value']=b.sql('SELECT amount FROM item WHERE id=1')==first==['12.000']
        checks['repeatable_read_consistent_snapshot_range']=b.sql('SELECT COUNT(*) FROM item WHERE id BETWEEN 1 AND 3')==count==['2']
        b.sql('COMMIT')
        checks['new_transaction_sees_committed_rows']=b.sql('SELECT COUNT(*) FROM item WHERE id BETWEEN 1 AND 3')==['3']
        a.sql('START TRANSACTION; SELECT amount FROM item WHERE id=1 FOR UPDATE')
        b.sql('SET SESSION innodb_lock_wait_timeout=1; START TRANSACTION; UPDATE item SET amount=99 WHERE id=1')
        checks['locked_row_not_overwritten']=a.sql('SELECT amount FROM item WHERE id=1')==['13.000']
        b.sql('ROLLBACK');a.sql('ROLLBACK')
        # Reconnect checks persistence of COMMIT, not OS/power failure durability.
        c=Session(name,password);sessions.append(c)
        checks['commit_survives_new_client_session']=c.sql('SELECT amount FROM item WHERE id=1')==['13.000']
        # Verify the project's actual DDL, with clearly synthetic FK-linked fixtures.
        schema=(ROOT/'sql/mysql/supplemental-schema.sql').read_text(encoding='utf-8')
        docker('exec','-e','MYSQL_PWD',name,'mysql','-uroot','-e',schema,env=os.environ|{'MYSQL_PWD':password})
        a.sql("USE tamsood_supplemental; INSERT INTO dataset_snapshot VALUES(REPEAT('a',64),'PRODUCT_INVENTORY','synthetic-lab-only'); INSERT INTO observation VALUES(REPEAT('a',64),REPEAT('b',64),1,'kg','SOURCE_REPORTED_PRODUCT_INVENTORY',JSON_OBJECT()); INSERT INTO process VALUES(REPEAT('a',64),'LAB',1000,'MJ fuel','Synthetic','Synthetic')")
        a.sql("START TRANSACTION; INSERT INTO inventory_exchange VALUES(REPEAT('a',64),REPEAT('b',64),'LAB','Synthetic','OUTPUT','CO_PRODUCT',NULL,REPEAT('c',64),1,1)")
        checks['actual_schema_accepts_output_coproduct']=a.sql('SELECT COUNT(*) FROM inventory_exchange')==['1']
        a.sql("UPDATE inventory_exchange SET direction='INPUT'")
        checks['actual_schema_rejects_input_coproduct']=a.sql('SELECT direction FROM inventory_exchange')==['OUTPUT']
        a.sql("UPDATE inventory_exchange SET role='INPUT'")
        checks['actual_schema_rejects_output_input_role']=a.sql('SELECT role FROM inventory_exchange')==['CO_PRODUCT']
        a.sql('ROLLBACK')
        checks['actual_schema_fixture_transaction_rolled_back']=a.sql('SELECT COUNT(*) FROM inventory_exchange')==['0']
        for session in sessions:session.close()
        errors=[line for session in sessions for line in session.errors if 'ERROR' in line]
        checks['expected_check_error_observed']=any('3819' in line for line in errors)
        checks['expected_lock_timeout_observed']=any('1205' in line for line in errors)
        unexpected=[line for line in errors if not any(code in line for code in ['3819','1205'])]
        checks['no_unexpected_sql_errors']=not unexpected
        observed['sql_error_codes']=[code for code in ['3819','1205'] if any(code in line for line in errors)]
    finally:
        for session in sessions:
            if session.process.poll() is None:session.close()
        info=docker('inspect',name,check=False)
        if info.returncode==0:
            labels=json.loads(info.stdout)[0]['Config']['Labels'] or {}
            if labels.get('org.tamsood.transaction-lab')!=owner:raise RuntimeError('Lab cleanup ownership mismatch')
            docker('rm','-f','-v',name)
    return {'checked_at':datetime.now(timezone.utc).isoformat(),'engine':'MySQL/InnoDB',
            'scope':'Synthetic isolated lab only; no existing containers/databases or EC2 modified',
            'observed':observed,'checks':checks,'passed':all(checks.values()),
            'temporary_container_removed':True,
            'limitations':['No power-loss/crash/restart durability test','Repeatable-read checks use plain consistent SELECT, not all locking-read semantics','No SERIALIZABLE or READ UNCOMMITTED experiment','No production importer/load benchmark'],
            'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__=='__main__':
    result=audit()
    (ROOT/'evidence/mysql-transaction-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
