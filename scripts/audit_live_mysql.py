"""Read-only comparisons against the existing owned local MySQL workspace."""
from contextlib import closing
from collections import Counter
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
from scripts.mysql_workspace import NAME, OWNER, VOLUME, CONFIG
from src.export_full_mysql import snapshot_id


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition,message):
    if not condition:raise ValueError(message)


def audit():
    config=json.loads(CONFIG.read_text(encoding='utf-8'))
    info=json.loads(subprocess.check_output(['docker','inspect',NAME],timeout=20))[0]
    require(config['owner']==OWNER and (info['Config']['Labels'] or {}).get('org.tamsood.workspace')==OWNER,
            'Workspace ownership mismatch')
    require(info['State']['Running'] and any(m.get('Name')==VOLUME and m['Destination']=='/var/lib/mysql' for m in info['Mounts']),
            'Owned MySQL volume is not running')

    def query(statement):
        require(statement.lstrip().upper().startswith('SELECT '),'Audit accepts SELECT only')
        command='START TRANSACTION READ ONLY;\n'+statement+';\nROLLBACK;'
        result=subprocess.run(['docker','exec','-i','-e','MYSQL_PWD',NAME,'mysql','-uroot',
            '--batch','--raw','--skip-column-names','--default-character-set=utf8mb4'],
            input=command.encode(),capture_output=True,timeout=120,env=os.environ|{'MYSQL_PWD':config['password']})
        if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace').replace(config['password'],'[redacted]'))
        return result.stdout.decode('utf-8').splitlines()

    def json_rows(fields,from_clause):
        require(all(re.fullmatch(r'[a-z_][a-z_0-9]*',f) for f in fields),'Unsafe field name')
        pairs=','.join("'"+f+"',CAST("+f+' AS CHAR)' for f in fields)
        return [json.loads(bytes.fromhex(line).decode('utf-8')) for line in query('SELECT HEX(CAST(JSON_OBJECT('+pairs+') AS CHAR)) '+from_clause)]

    def compare(actual,expected,decimal_fields=()):
        def canonical(row):
            return {k:(None if v is None else Decimal(str(v)) if k in decimal_fields else str(v)) for k,v in row.items()}
        require(len(actual)==len(expected),'Live MySQL row count differs')
        require(Counter(tuple(sorted(canonical(r).items())) for r in actual)==
                Counter(tuple(sorted(canonical(r).items())) for r in expected),'Live MySQL typed/raw values differ')

    run=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
    manifest=json.loads((ROOT/'data/raw/dmf'/run/'manifest.json').read_text(encoding='utf-8'))
    sid={e['package']:snapshot_id(e) for e in manifest['packages']}
    require(all(re.fullmatch(r'[0-9a-f]{64}',s) for s in sid.values()),'Invalid snapshot hash')
    hashes=','.join("'"+s+"'" for s in sid.values())
    from_clause='FROM tamsood_research.source_record WHERE snapshot_id IN ('+hashes+')'
    actual=json_rows(['snapshot_id','source_line','raw_json'],from_clause)
    with closing(sqlite3.connect((ROOT/'build/dmf'/run/'candidates.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as con:
        con.row_factory=sqlite3.Row
        expected=[dict(snapshot_id=sid[r['package']],source_line=str(r['source_line']),raw_json=json.loads(r['raw_json'])) for r in con.execute('SELECT * FROM staging')]
        for row in actual:row['raw_json']=json.loads(row['raw_json'])
        # JSON object key order is not part of source field equality.
        require({(r['snapshot_id'],str(r['source_line'])):r['raw_json'] for r in actual}==
                {(r['snapshot_id'],r['source_line']):r['raw_json'] for r in expected},'DMF full raw JSON differs')
        require(len(actual)==len(expected),'DMF raw count differs')
        dmf_raw=len(actual)
        fields=['snapshot_id','source_line','raw_value','amount','production_days','period_start','unit_time_basis','review_status','identity_sha256']
        actual=json_rows(fields,'FROM tamsood_research.observation WHERE snapshot_id IN ('+hashes+')')
        expected=[dict(snapshot_id=sid[r['package']],source_line=r['source_line'],raw_value=r['raw_value'],amount=r['decimal_value'],
            production_days=r['production_days'],period_start=f"{r['year_ce']:04}-{r['month']:02}-01",unit_time_basis='UNCONFIRMED',review_status=r['review_status'],identity_sha256=r['identity_sha256']) for r in con.execute('SELECT * FROM candidate')]
        compare(actual,expected,('amount','production_days'))
        dmf_observations=len(actual)
        actual=json_rows(['snapshot_id','source_line','status','representative_line'],'FROM tamsood_research.duplicate_disposition WHERE snapshot_id IN ('+hashes+')')
        expected=[dict(snapshot_id=sid[r['package']],source_line=r['source_line'],status=r['status'],representative_line=r['representative_line']) for r in con.execute('SELECT * FROM duplicate_disposition')]
        compare(actual,expected)
        actual=json_rows(['snapshot_id','source_line','area','block_label','source_group'],
            'FROM tamsood_research.observation JOIN tamsood_research.production_context USING(context_id) WHERE snapshot_id IN ('+hashes+')')
        expected=[dict(snapshot_id=sid[r['package']],source_line=r['source_line'],area=r['area'],block_label=r['block_label'],source_group=r['source_group']) for r in con.execute('SELECT * FROM candidate')]
        compare(actual,expected)
        actual=json_rows(['snapshot_id','source_line','reasons_json'],'FROM tamsood_research.rejected_record WHERE snapshot_id IN ('+hashes+')')
        expected={(sid[r['package']],str(r['source_line'])):json.loads(r['reasons_json']) for r in con.execute('SELECT * FROM rejected')}
        require({(r['snapshot_id'],r['source_line']):json.loads(r['reasons_json']) for r in actual}==expected and len(actual)==len(expected),'DMF rejected reasons differ')
    mismatch=query('SELECT COUNT(*) FROM tamsood_research.observation o JOIN tamsood_research.production_context c USING(context_id) JOIN tamsood_research.resource_snapshot s USING(snapshot_id) WHERE o.snapshot_id IN ('+hashes+') AND c.package<>s.package')
    require(mismatch==['0'],'DMF context and source package disagree')

    folder=ROOT/'build/reusable'
    release=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))['release_id']
    require(re.fullmatch(r'[0-9a-f]{64}',release),'Invalid release hash')
    with closing(sqlite3.connect((folder/'reference.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as con:
        con.row_factory=sqlite3.Row
        expected=[dict(r) for r in con.execute('SELECT * FROM reference_catalog WHERE release_id=?',(release,))]
    actual=json_rows(list(expected[0]),"FROM tamsood_reusable.reference_catalog WHERE release_id='"+release+"'")
    compare(actual,expected,('scaled_amount','scale_factor'))
    reference_count=len(actual)
    reference_field_count=len(expected[0])

    counts={}
    for folder_name,kind in [('nso','NSO'),('product-inventory','PRODUCT_INVENTORY')]:
        path=ROOT/'build'/folder_name/'report.json';report=json.loads(path.read_text(encoding='utf-8'));snapshot=digest(path)
        actual=json_rows(['observation_id','amount','unit_code','status','payload'],"FROM tamsood_supplemental.observation WHERE snapshot_id='"+snapshot+"'")
        for r in actual:r['payload']=json.loads(r['payload'])
        require({r['observation_id']:r['payload'] for r in actual}=={r['observation_id']:r for r in report['rows']},kind+' full payload differs')
        require(len(actual)==len(report['rows']),kind+' count differs')
        compare([{k:v for k,v in r.items() if k!='payload'} for r in actual],
                [dict(observation_id=r['observation_id'],amount=r['amount'],unit_code=r['unit'],status=r['status']) for r in report['rows']],('amount',))
        counts[kind]=len(actual)
        if kind=='NSO':
            fields=['observation_id','table_id','reference_year','measure','label','source_sha256','source_line','source_column']
            actual=json_rows(fields,"FROM tamsood_supplemental.national_statistic WHERE snapshot_id='"+snapshot+"'")
            compare(actual,[{k:r[k] for k in fields} for r in report['rows']])
        else:
            fields=['observation_id','process_id','flow','direction','role','data_period','source_sha256','source_row','source_column']
            actual=json_rows(fields,"FROM tamsood_supplemental.inventory_exchange WHERE snapshot_id='"+snapshot+"'")
            expected=[dict(observation_id=r['observation_id'],process_id=r['process'],flow=r['flow'],direction=r['direction'],role=r['role'],data_period=r['data_period'],source_sha256=r['source_snapshot_sha256'],source_row=r['source_row'],source_column=r['source_column']) for r in report['rows']]
            compare(actual,expected)
            fields=['process_id','reference_amount','reference_unit','geography','technology_level']
            actual=json_rows(fields,"FROM tamsood_supplemental.process WHERE snapshot_id='"+snapshot+"'")
            expected={r['process']:dict(process_id=r['process'],reference_amount=r['reference_amount'],reference_unit=r['reference_unit'],geography=r['geography'],technology_level=r['technology_level']) for r in report['rows']}
            compare(actual,list(expected.values()),('reference_amount',))
    path=ROOT/'build/eppo/report.json';report=json.loads(path.read_text(encoding='utf-8'))
    snapshots=sorted({r['source_sha256'] for r in report['rows']})
    require(all(re.fullmatch(r'[0-9a-f]{64}',s) for s in snapshots),'Invalid EPPO snapshot')
    fields=['observation_id','snapshot_id','reference_year','month','subject','amount','unit_code','status','source_line','payload']
    actual=json_rows(fields,'FROM tamsood_eppo.observation WHERE snapshot_id IN ('+','.join("'"+s+"'" for s in snapshots)+')')
    for r in actual:r['payload']=json.loads(r['payload'])
    require({r['observation_id']:r['payload'] for r in actual}=={r['observation_id']:r for r in report['rows']},'EPPO payload differs')
    compare([{k:v for k,v in r.items() if k!='payload'} for r in actual],
            [dict(observation_id=r['observation_id'],snapshot_id=r['source_sha256'],reference_year=r['reference_year'],month=r['month'],subject=r['subject'],amount=r['amount'],unit_code=r['unit'],status=r['status'],source_line=r['source_line']) for r in report['rows']],('amount',))
    counts['EPPO']=len(actual)
    return dict(checked_at=datetime.now(timezone.utc).isoformat(),result='passed',mode='SELECT_ONLY_READ_ONLY_TRANSACTIONS',
        container=NAME,dmf_raw_records=dmf_raw,dmf_observations=dmf_observations,dmf_context_package_mismatches=0,
        reference_records=reference_count,reference_catalog_fields_checked=reference_field_count,datasets=counts,
        acceptance_changed=False,schemas_changed=False,remote_ec2_checked=False,
        supplemental_subtype_fields_checked=True,inventory_process_basis_checked=True,dmf_context_and_rejected_reasons_checked=True,
        limitation='Selected current snapshots only; no independent publisher measurement, rights or remote EC2 certification',
        implementation_sha256=digest(Path(__file__)))


if __name__=='__main__':
    result=audit()
    (ROOT/'evidence/live-mysql-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))
