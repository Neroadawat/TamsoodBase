"""Restore the normalized candidate into a separate owned local MySQL database."""
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from scripts.audit_normalization import build
from scripts.mysql_workspace import NAME, OWNER, VOLUME, CONFIG
from src.export_full_mysql import exact_decimal, text_sql


def require(condition,message):
    if not condition:raise ValueError(message)


def verify():
    source=ROOT/'build/reusable/reference.sqlite'
    candidate=ROOT/'build/normalization/reference-candidate.sqlite'
    candidate_result=build(source,candidate)
    original_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    schema=(ROOT/'sql/mysql/reusable-schema.sql').read_text(encoding='utf-8')
    start=schema.index('CREATE TABLE IF NOT EXISTS metric (')
    end=schema.index('CREATE TABLE IF NOT EXISTS observation (',start)
    block=schema[start:end]
    for before,after in [
        ('metric_key CHAR(64) PRIMARY KEY, document_id CHAR(64) NOT NULL,','metric_key CHAR(64) PRIMARY KEY,'),
        (' FOREIGN KEY(document_id) REFERENCES document(document_id),\n',''),
        ('FOREIGN KEY(context_id,document_id) REFERENCES context(context_id,document_id)', 'FOREIGN KEY(context_id) REFERENCES context(context_id)'),
        ('INDEX ix_document_metric(document_id,source_metric_id)','INDEX ix_context_metric(context_id,source_metric_id)')]:
        require(block.count(before)==1,'Base schema changed; candidate transformation needs review')
        block=block.replace(before,after)
    schema=schema[:start]+block+schema[end:]
    schema=schema.replace('d.document_id=m.document_id','d.document_id=c.document_id')
    fingerprint=hashlib.sha256((schema+original_hash).encode()).hexdigest()[:12]
    database='tamsood_nf_'+fingerprint
    schema=schema.replace('tamsood_reusable',database)
    folder=candidate.parent
    (folder/'schema-mysql.sql').write_text(schema,encoding='utf-8',newline='\n')
    config=json.loads(CONFIG.read_text(encoding='utf-8'))
    info=json.loads(subprocess.check_output(['docker','inspect',NAME],timeout=20))[0]
    require(config['owner']==OWNER and (info['Config']['Labels'] or {}).get('org.tamsood.workspace')==OWNER and
            info['State']['Running'] and any(m.get('Name')==VOLUME and m['Destination']=='/var/lib/mysql' for m in info['Mounts']),
            'Owned running MySQL workspace required')

    def query(sql,check=True):
        result=subprocess.run(['docker','exec','-i','-e','MYSQL_PWD',NAME,'mysql','-uroot','--batch','--raw',
            '--skip-column-names','--default-character-set=utf8mb4'],input=sql.encode('utf-8'),capture_output=True,
            timeout=120,env=os.environ|{'MYSQL_PWD':config['password']})
        if check and result.returncode:raise RuntimeError(result.stderr.decode(errors='replace').replace(config['password'],'[redacted]'))
        return result

    query(schema)
    with closing(sqlite3.connect(candidate)) as con:
        con.row_factory=sqlite3.Row
        tables=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY rowid")]
        statements=['USE '+database+'; START TRANSACTION;']
        numeric={'report_year','reference_year','pdf_page','extracted_text_line','scale_factor','scaled_amount'}
        for table in tables:
            columns=[r[1] for r in con.execute('PRAGMA table_info('+table+')')]
            for row in con.execute('SELECT * FROM '+table):
                values=[exact_decimal(str(row[c])) if c in numeric else text_sql(row[c]) if row[c] is not None else 'NULL' for c in columns]
                statements.append('INSERT IGNORE INTO '+table+' ('+','.join(columns)+') VALUES ('+','.join(values)+');')
        statements.append('COMMIT;')
        loader='\n'.join(statements)+'\n'
        (folder/'load-mysql.sql').write_text(loader,encoding='utf-8',newline='\n')
        query(loader)
        def compare(view):
            expected=[dict(r) for r in con.execute('SELECT * FROM '+view)]
            fields=list(expected[0])
            require(all(re.fullmatch(r'[a-z_][a-z_0-9]*',f) for f in fields),'Unexpected column')
            pairs=','.join("'"+f+"',CAST("+f+' AS CHAR)' for f in fields)
            output=query('SELECT HEX(CAST(JSON_OBJECT('+pairs+') AS CHAR)) FROM '+database+'.'+view+';').stdout.decode().splitlines()
            actual=[json.loads(bytes.fromhex(line).decode('utf-8')) for line in output]
            def canonical(r):return tuple(sorted((k,None if v is None else Decimal(str(v)) if k in ('scale_factor','scaled_amount') else str(v)) for k,v in r.items()))
            require(Counter(map(canonical,actual))==Counter(map(canonical,expected)),'Candidate MySQL catalog differs: '+view)
            return len(actual)
        all_count=compare('reference_catalog');accepted_count=compare('accepted_reference')
    checks={}
    for label,statement,code in [
        ('missing_context',"UPDATE metric SET context_id=REPEAT('0',64) LIMIT 1",1452),
        ('invalid_kind',"UPDATE metric SET data_kind='INVENTED' LIMIT 1",3819),
        ('negative_amount','UPDATE observation SET scaled_amount=-1 LIMIT 1',3819),
        ('invalid_decision',"UPDATE review SET decision='MTEC_APPROVED' LIMIT 1",3819)]:
        result=query('USE '+database+'; START TRANSACTION; '+statement+'; ROLLBACK;',False)
        require(result.returncode!=0 and ('ERROR '+str(code)).encode() in result.stderr,'Constraint failed: '+label)
        checks[label]='rejected_as_expected'
    metric_document_columns=query("SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='"+database+"' AND table_name='metric' AND column_name='document_id';").stdout.decode().strip()
    require(metric_document_columns=='0','Redundant metric.document_id still exists')
    require(original_hash==hashlib.sha256(source.read_bytes()).hexdigest(),'Original SQLite changed')
    return dict(checked_at=datetime.now(timezone.utc).isoformat(),result='passed',database=database,
        candidate_only=True,production_migrated=False,remote_ec2_changed=False,source_sha256=original_hash,
        source_unchanged=True,reference_catalog_rows=all_count,accepted_reference_rows=accepted_count,
        catalog_all_fields_equal=True,metric_document_id_removed=True,constraint_checks=checks,
        sqlite_lossless_reconstruction=candidate_result['metric_lossless_reconstruction'],
        schema_sha256=hashlib.sha256(schema.encode()).hexdigest(),loader_sha256=hashlib.sha256(loader.encode()).hexdigest(),
        normalization_scope='context/document dependency removed; no whole-schema 5NF claim')


if __name__=='__main__':
    result=verify()
    (ROOT/'evidence/normalization-mysql.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))
