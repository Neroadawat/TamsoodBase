"""Offline audit of newer layers; stored SQL evidence is not a live SQL check."""
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_layers(root=ROOT):
    checks=[]
    def check(name,passed,detail):checks.append(dict(name='layer_'+name,passed=bool(passed),detail=detail))
    for name,report_path,db_path,table in [
        ('nso','build/nso/report.json','build/nso/nso.sqlite','observation'),
        ('inventory','build/product-inventory/report.json','build/product-inventory/inventory.sqlite','exchange'),
        ('eppo','build/eppo/report.json','build/eppo/eppo.sqlite','observation')]:
        try:
            path=root/report_path;report=json.loads(path.read_text(encoding='utf-8'));rows=report['rows']
            expected={r['observation_id']:r for r in rows}
            check(name+'_identities',bool(rows) and len(expected)==len(rows),len(rows))
            expected_status='SOURCE_REPORTED_PRODUCT_INVENTORY' if name=='inventory' else 'STAGED_SOURCE_VERIFIED'
            check(name+'_status',all(r['status']==expected_status for r in rows),'No acceptance promotion')
            if name=='inventory':
                check(name+'_basis',all(r['reference_amount']=='1000' and r['reference_unit']=='MJ fuel' and r['data_period'] is None and not r['is_full_lci_dataset'] for r in rows),'Reported basis and missing measurement period retained')
                sources={root/'data/raw/mdpi-9415/table4-dom.json':report['source_snapshot_sha256'],root/'data/raw/mdpi-9415/article-visible.txt':report['context_sha256']}
            elif name=='nso':
                sources={root/('data/raw/nso/yearbook-2026/T_'+key+'_2026.csv'):value['sha256'] for key,value in report['source_manifest']['resources'].items()}
                check(name+'_no_promotion',report['accepted_reference']==0 and report['normalized_lci_exchanges']==0 and all(not r['is_normalized_lci_exchange'] for r in rows),'Source statistics only')
            else:
                manifest=json.loads((root/'data/raw/eppo/manifest.json').read_text(encoding='utf-8'))
                sources={root/'data/raw/eppo'/value['filename']:value['sha256'] for value in manifest['resources'].values()}
                check(name+'_unit_scope',all((r['dataset_id']=='11_13' and r['unit']=='BBL/DAY' and r['scope']=='COMPANY_REFINERY_STATISTIC') or (r['dataset_id']=='11_14' and r['unit']=='Million Litres' and r['scope']=='NATIONAL_PRODUCT_STATISTIC') for r in rows),'Rate/company versus quantity/country remain separate')
                check(name+'_no_promotion',report['accepted_reference']==0 and report['normalized_lci_exchanges']==0,'Source statistics only')
            check(name+'_sources',all(digest(p)==h for p,h in sources.items()),'Source bytes match saved hashes')
            hashes=set(sources.values())
            check(name+'_row_provenance',all(r.get('source_sha256',r.get('source_snapshot_sha256')) in hashes for r in rows),'Every row refers to audited source snapshot')
            with closing(sqlite3.connect((root/db_path).resolve().as_uri()+'?mode=ro',uri=True)) as con:
                check(name+'_sqlite_integrity',con.execute('PRAGMA integrity_check').fetchone()[0]=='ok' and not con.execute('PRAGMA foreign_key_check').fetchall(),'Integrity and foreign keys')
                actual={oid:json.loads(payload) for oid,payload in con.execute('SELECT observation_id,payload FROM '+table) if oid in expected}
                check(name+'_sqlite_payload',actual==expected,'All current payloads equal; historical snapshots excluded by identity')
            if name in ('nso','inventory'):
                sql=json.loads((root/'evidence/supplemental-mysql.json').read_text(encoding='utf-8'))
                kind='NSO' if name=='nso' else 'PRODUCT_INVENTORY'
                matches=[d for d in sql['datasets'] if d['kind']==kind]
                check(name+'_mysql_evidence',sql['result']=='passed' and len(matches)==1 and matches[0]['snapshot_id']==digest(path) and matches[0]['records_checked']==len(rows) and matches[0]['full_payload_equal'] and sql['schema_sha256']==digest(root/'sql/mysql/supplemental-schema.sql'),'Stored evidence bound to current report/schema; not a live query')
            else:
                sql=json.loads((root/'evidence/eppo-mysql.json').read_text(encoding='utf-8'))
                check(name+'_mysql_evidence',sql['result']=='passed' and sql['report_sha256']==digest(path) and sql['records_checked']==len(rows) and sql['schema_sha256']==digest(root/'sql/mysql/eppo-schema.sql'),'Stored evidence bound to current report/schema; not a live query')
        except (OSError,ValueError,KeyError,TypeError,sqlite3.Error) as error:
            check(name+'_available',False,str(error))
    return checks


if __name__=='__main__':
    result=audit_layers();print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if all(c['passed'] for c in result) else 1)
