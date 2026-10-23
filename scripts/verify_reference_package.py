"""Verify the data product outside the repo, with an optional isolated MySQL restore."""
import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import uuid
import zipfile
from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path

if __package__:
    from .mysql_workspace import ROOT,CONFIG,NAME,OWNER
else:
    from mysql_workspace import ROOT,CONFIG,NAME,OWNER


def verify(mysql=False):
    folder=ROOT/'build/reusable';package=folder/'reference-data-local.zip'
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest()}
    with tempfile.TemporaryDirectory(prefix='reference-check-',dir=ROOT/'build') as directory:
        target=Path(directory)
        with zipfile.ZipFile(package) as archive:
            manifest=json.loads(archive.read('package-manifest.json'))
            if set(archive.namelist())!=set(manifest['files'])|{'package-manifest.json'}: raise ValueError('Unexpected archive member')
            for name in archive.namelist():
                if '/' in name or '\\' in name or Path(name).name!=name: raise ValueError('Unsafe archive path')
                body=archive.read(name)
                if name in manifest['files'] and hashlib.sha256(body).hexdigest()!=manifest['files'][name]: raise ValueError('Hash mismatch')
                (target/name).write_bytes(body)
        rows=json.loads((target/'accepted-reference.json').read_text(encoding='utf-8'))
        release=manifest['release_id']
        con=sqlite3.connect((target/'reference.sqlite').as_uri()+'?mode=ro',uri=True)
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or con.execute('PRAGMA foreign_key_check').fetchall(): raise ValueError('SQLite restore integrity failed')
        if con.execute('SELECT COUNT(*) FROM accepted_reference WHERE release_id=?',(release,)).fetchone()[0]!=manifest['accepted_reference']: raise ValueError('Accepted count mismatch')
        count=con.execute('SELECT COUNT(*) FROM reference_catalog WHERE release_id=?',(release,)).fetchone()[0];con.close()
        result=subprocess.run([sys.executable,'-I',str(target/'use_reference.py'),str(target/'accepted-reference.json'),'--year','2024'],cwd=target,capture_output=True,text=True,encoding='utf-8')
        if result.returncode: raise RuntimeError('Standalone SDK failed: '+result.stderr)
        expected=[r for r in rows if r['source_metric_id']=='natural_gas' and r['reference_year']==2024]
        if result.stdout.count(' | 2024 | ')!=len(expected) or any(str(Decimal(r['scaled_amount'])) not in result.stdout for r in expected): raise ValueError('Standalone SDK values mismatch')
        report.update(release_id=release,files_checked=len(manifest['files']),sqlite_records=count,
            accepted_reference=len(rows),sdk_isolated_python='passed',sdk_extra_packages_required=False,
            verification_scope='Package extraction, SQLite read and standalone standard-library client; not a fresh OS install')
        if mysql:
            config=json.loads(CONFIG.read_text());password=config['password']
            info=json.loads(subprocess.run(['docker','inspect',NAME],capture_output=True,check=True).stdout)[0]
            if (info['Config']['Labels'] or {}).get('org.tamsood.workspace')!=OWNER or config['owner']!=OWNER: raise RuntimeError('Workspace ownership mismatch')
            def query(sql):
                command=['docker','exec','-i','-e','MYSQL_PWD='+password,NAME,'mysql','-h127.0.0.1','--protocol=TCP','-uroot','--default-character-set=utf8mb4','--batch','--raw','--skip-column-names']
                result=subprocess.run(command,input=sql.encode(),capture_output=True,timeout=90)
                if result.returncode: raise RuntimeError(result.stderr.decode(errors='replace').replace(password,'[redacted]'))
                return result.stdout.decode().strip()
            name='tamsood_verify_'+uuid.uuid4().hex[:12]
            if not re.fullmatch('tamsood_verify_[0-9a-f]{12}',name): raise ValueError('Invalid temporary DB name')
            sql=(target/'load-mysql.sql').read_text(encoding='utf-8')
            if sql.count('CREATE DATABASE IF NOT EXISTS tamsood_reusable ')!=1 or sql.count('USE tamsood_reusable;')!=1: raise ValueError('Unexpected SQL restore directives')
            sql=sql.replace('CREATE DATABASE IF NOT EXISTS tamsood_reusable ','CREATE DATABASE IF NOT EXISTS '+name+' ').replace('USE tamsood_reusable;','USE '+name+';')
            # Only a database successfully created by this run is ever removed.
            query('CREATE DATABASE '+name+' CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;')
            try:
                for _ in range(2): query(sql)
                if not re.fullmatch('[0-9a-f]{64}',release): raise ValueError('Invalid release')
                restored=query("SELECT observation_id,scaled_amount,unit_code,pdf_sha256,pdf_page,decision FROM "+name+".accepted_reference WHERE release_id='"+release+"';")
                actual={p[0]:(Decimal(p[1]),p[2],p[3],int(p[4]),p[5]) for p in (line.split('\t') for line in restored.splitlines())}
                expected={r['observation_id']:(Decimal(r['scaled_amount']),r['unit_code'],r['pdf_sha256'],r['pdf_page'],r['decision']) for r in rows}
                if actual!=expected: raise ValueError('Clean MySQL restore does not match exported records')
                total=int(query("SELECT COUNT(*) FROM "+name+".reference_catalog WHERE release_id='"+release+"';"))
                if total!=count: raise ValueError('Restore source count mismatch')
                report['mysql_clean_restore']={'result':'passed','imports':2,'accepted_records_checked':len(actual),'all_records':total,'temporary_database_removed':True}
            finally: query('DROP DATABASE '+name+';')
    report['result']='passed'
    (ROOT/'evidence/reference-package-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mysql',action='store_true');verify(parser.parse_args().mysql)
