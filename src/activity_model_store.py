"""Append-only local model release with exact-decimal replay and source FKs."""
import hashlib
import json
import sqlite3
from decimal import Decimal, localcontext


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def identity(value):return hashlib.sha256(canonical(value).encode('utf8')).hexdigest()


def decimal_text(value):
    value=Decimal(value)
    if not value.is_finite():raise ValueError('Nonfinite quantity')
    text=format(value,'f')
    return text.rstrip('0').rstrip('.') if '.' in text else text


def validate_case(case):
    rows=case['rows']
    if len(rows)!=55 or case['full_lifecycle_inventory'] or case['CO2e_total'] is not None:
        raise ValueError('Expected partial 55-row activity scenario')
    if case['allocation']['status']!='UNRESOLVED_NOT_APPLIED':raise ValueError('Unreviewed allocation')
    ids=[]
    with localcontext() as context:
        context.prec=100
        for row in rows:
            source=row['source'];ids.append(source.get('observation_id',source.get('id')))
            factor=Decimal(row['scale_factor']);amount=Decimal(source['amount'])
            if not factor.is_finite() or factor<=0 or not amount.is_finite() or amount<0:
                raise ValueError('Invalid activity or source amount')
            if row['scale_factor']!=case['component_scale_factors'][row['component']]:
                raise ValueError('Component activity mismatch')
            held=not source.get('unit') or str(source.get('status','')).startswith('HOLD')
            if held:
                if row['scaled_amount'] is not None or row['status']!='HOLD_SOURCE_UNIT':raise ValueError('Hold changed')
            elif row['status']!='SCENARIO_ACTIVITY_SCALED' or Decimal(row['scaled_amount'])!=amount*factor:
                raise ValueError('Scaled quantity differs from source and activity')
    if len(set(ids))!=55 or None in ids:raise ValueError('Duplicate/missing source identity')
    expected={('FFB','CPO'),('CPO','RBDPO'),('RBDPO','FAME')}
    edges=case['physical_transfer_candidates']
    if len(edges)!=3 or {(e['provider'],e['consumer']) for e in edges}!=expected:
        raise ValueError('Missing, duplicate or unexpected provider link')
    indexed={r['source'].get('observation_id',r['source'].get('id')):r for r in rows}
    with localcontext() as context:
        context.prec=100
        for edge in edges:
            output=indexed.get(edge['provider_output_id']);input_row=indexed.get(edge['consumer_input_id'])
            if not output or not input_row or output['component']!=edge['provider'] or input_row['component']!=edge['consumer']:
                raise ValueError('Provider endpoint membership mismatch')
            if output['source']['direction']!='OUTPUT' or input_row['source']['direction']!='INPUT' or any(r['source'].get('unit')!='kg' or r['scaled_amount'] is None for r in (output,input_row)):
                raise ValueError('Provider direction/unit mismatch')
            supplied=Decimal(output['source']['amount'])*Decimal(output['scale_factor'])
            consumed=Decimal(input_row['source']['amount'])*Decimal(input_row['scale_factor'])
            if edge['burden_link_applied'] or supplied!=consumed or supplied!=Decimal(edge['supplied_kg']) or consumed!=Decimal(edge['consumed_kg']):
                raise ValueError('Provider quantity differs from endpoint activity')


def initialize(conn,schema):
    conn.executescript(schema)
    tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    for table in tables:
        for action in ('UPDATE','DELETE'):
            conn.execute(f"CREATE TRIGGER immutable_{table}_{action.lower()} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'Immutable model release'); END")
        if table!='release_seal':
            conn.execute(f"CREATE TRIGGER sealed_{table}_insert BEFORE INSERT ON {table} WHEN EXISTS(SELECT 1 FROM release_seal) BEGIN SELECT RAISE(ABORT,'Sealed model release'); END")
    conn.commit()


def persist(conn,artifact,manifest):
    cases=[artifact['baseline']]+artifact['alternatives']
    for case in cases:validate_case(case)
    release=identity(manifest);model=identity({'release':release,'system':'THAI_FAME_ACTIVITY'})
    # A single transaction covers source, links, decisions and all calculation results.
    with conn:
        conn.execute('INSERT INTO release_manifest VALUES(?,?)',(release,canonical(manifest)))
        conn.execute('INSERT INTO product_system_version VALUES(?,?,?,?,?)',
            (model,release,'1000','MJ fuel','ACTIVITY_SCENARIO_NOT_FULL_LCI'))
        seen={};versions={}
        for case in cases:
            for row in case['rows']:
                source=row['source'];oid=source.get('observation_id',source.get('id'));body=canonical(source)
                if oid in seen:
                    if seen[oid]!=body:raise ValueError('Source identity has conflicting payload')
                else:
                    conn.execute('INSERT INTO source_observation VALUES(?,?,?,?)',(oid,source['amount'],source['unit'],body));seen[oid]=body
        for case in cases:
            scenario=identity({'release':release,'case':case})
            meta={k:v for k,v in case.items() if k not in ('rows','physical_transfer_candidates')}
            conn.execute('INSERT INTO scenario_case VALUES(?,?,?,?)',(scenario,model,case['scenario_id'],canonical(meta)))
            for process,factor in case['component_scale_factors'].items():
                rows=sorted((r['source'] for r in case['rows'] if r['component']==process),key=canonical)
                vid=identity({'process':process,'sources':rows})
                if vid not in versions:
                    conn.execute('INSERT INTO process_dataset_version VALUES(?,?,?)',(vid,process,len(rows)))
                    for source in rows:
                        oid=source.get('observation_id',source.get('id'))
                        conn.execute('INSERT INTO dataset_exchange VALUES(?,?)',(vid,oid))
                    versions[vid]=True
                conn.execute('INSERT INTO process_instance VALUES(?,?,?,?)',(scenario,process,vid,factor))
            instance=dict(conn.execute('SELECT process_name,version_id FROM process_instance WHERE scenario_id=?',(scenario,)))
            for edge in case['physical_transfer_candidates']:
                conn.execute('INSERT INTO provider_link_candidate VALUES(?,?,?,?,?,?,?,?,?,?)',
                    (scenario,edge['provider'],edge['consumer'],instance[edge['provider']],edge['provider_output_id'],
                     instance[edge['consumer']],edge['consumer_input_id'],decimal_text(edge['supplied_kg']),
                     decimal_text(edge['consumed_kg']),'UNREVIEWED_BURDEN_LINK_NOT_APPLIED'))
            conn.execute('INSERT INTO allocation_decision VALUES(?,?,?)',(scenario,'UNRESOLVED_NOT_APPLIED',canonical(case['allocation'])))
            for leg in case['transport_legs']:
                conn.execute('INSERT INTO scenario_assumption VALUES(?,?,?)',(scenario,leg['id'],canonical(leg)))
            for decision in case['open_gates']:
                conn.execute('INSERT INTO required_decision VALUES(?,?,?)',(scenario,decision,'OPEN'))
            input_hash=identity(case);run_manifest={'release_id':release,'input_sha256':input_hash,
                'implementation_sha256':manifest['implementation_sha256'],'scenario_id':scenario,
                'runtime':manifest['runtime'],'result_type':case['result_type']}
            run=identity(run_manifest)
            conn.execute('INSERT INTO calculation_run VALUES(?,?,?,?,?)',(run,scenario,input_hash,manifest['implementation_sha256'],canonical(run_manifest)))
            for row in case['rows']:
                oid=row['source'].get('observation_id',row['source'].get('id'))
                conn.execute('INSERT INTO result_exchange VALUES(?,?,?,?,?,?,?)',
                    (run,scenario,row['component'],instance[row['component']],oid,row['scaled_amount'],row['status']))
    return release


def audit(conn,artifact=None,manifest=None,require_seal=False):
    if conn.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Broken model FK')
    expected_counts={'release_manifest':1,'product_system_version':1,'scenario_case':6,'calculation_run':6,
                     'result_exchange':330,'provider_link_candidate':18,'source_observation':130,
                     'process_dataset_version':9,'process_instance':24,'allocation_decision':6,
                     'required_decision':48,'scenario_assumption':24}
    counts={table:conn.execute('SELECT count(*) FROM '+table).fetchone()[0] for table in expected_counts}
    if counts!=expected_counts:raise ValueError('Incomplete or unexpected model release')
    for vid,n in conn.execute('SELECT version_id,source_count FROM process_dataset_version'):
        if conn.execute('SELECT count(*) FROM dataset_exchange WHERE version_id=?',(vid,)).fetchone()[0]!=n:
            raise ValueError('Dataset source count mismatch')
    stored_manifest=json.loads(conn.execute('SELECT payload_json FROM release_manifest').fetchone()[0])
    release=identity(stored_manifest)
    if conn.execute('SELECT release_id FROM release_manifest').fetchone()[0]!=release:raise ValueError('Manifest identity mismatch')
    if manifest is not None and canonical(stored_manifest)!=canonical(manifest):raise ValueError('Implementation manifest mismatch')
    if require_seal and conn.execute('SELECT release_id FROM release_seal').fetchall()!=[(release,)]:raise ValueError('Release not sealed')
    expected={c['scenario_id']:c for c in [artifact['baseline']]+artifact['alternatives']} if artifact else None
    for sid,key,metadata in conn.execute('SELECT scenario_id,scenario_key,metadata_json FROM scenario_case'):
        case=json.loads(metadata)
        case['rows']=[{'source':json.loads(body),'component':process,'scale_factor':factor,'scaled_amount':scaled,'status':status}
          for body,process,factor,scaled,status in conn.execute('''SELECT s.payload_json,r.process_name,p.activity_factor,r.scaled_amount,r.status
          FROM result_exchange r JOIN source_observation s USING(observation_id)
          JOIN process_instance p ON p.scenario_id=r.scenario_id AND p.process_name=r.process_name WHERE r.scenario_id=?''',(sid,))]
        case['physical_transfer_candidates']=[dict(provider=p,consumer=c,provider_output_id=po,consumer_input_id=ci,
          supplied_kg=s,consumed_kg=q,burden_link_applied=False) for p,c,po,ci,s,q in conn.execute('''SELECT provider,consumer,provider_exchange,consumer_exchange,supplied_kg,consumed_kg FROM provider_link_candidate WHERE scenario_id=?''',(sid,))]
        validate_case(case)
        if expected is not None:
            original=expected.get(key)
            if original is None or sid!=identity({'release':release,'case':original}):raise ValueError('Unexpected scenario identity')
            if sorted(map(canonical,case['rows']))!=sorted(map(canonical,original['rows'])):raise ValueError('Scenario source/result mismatch')
        runs=conn.execute('SELECT run_id,input_sha256,implementation_sha256,manifest_json FROM calculation_run WHERE scenario_id=?',(sid,)).fetchall()
        if len(runs)!=1:raise ValueError('Scenario run missing or duplicated')
        run,input_hash,implementation,body=runs[0];run_manifest=json.loads(body)
        if run!=identity(run_manifest) or implementation!=stored_manifest['implementation_sha256'] or run_manifest['release_id']!=release or run_manifest['scenario_id']!=sid or run_manifest['input_sha256']!=input_hash:
            raise ValueError('Run manifest mismatch')
        if expected is not None and input_hash!=identity(expected[key]):raise ValueError('Run input hash mismatch')
    rows=conn.execute('''SELECT s.payload_json,p.activity_factor,r.scaled_amount,r.status
      FROM result_exchange r JOIN source_observation s USING(observation_id)
      JOIN process_instance p ON p.scenario_id=r.scenario_id AND p.process_name=r.process_name''').fetchall()
    with localcontext() as context:
        context.prec=100
        for body,factor,scaled,status in rows:
            source=json.loads(body)
            if status=='HOLD_SOURCE_UNIT':
                if scaled is not None or source.get('unit'):raise ValueError('Invalid held result')
            elif Decimal(scaled)!=Decimal(source['amount'])*Decimal(factor):raise ValueError('Replay mismatch')
    return {'result_rows_replayed':len(rows),'source_observations':conn.execute('SELECT count(*) FROM source_observation').fetchone()[0],
        'dataset_versions':conn.execute('SELECT count(*) FROM process_dataset_version').fetchone()[0],
        'calculation_runs':conn.execute('SELECT count(*) FROM calculation_run').fetchone()[0],
        'candidate_links':conn.execute('SELECT count(*) FROM provider_link_candidate').fetchone()[0],
        'held_results':conn.execute("SELECT count(*) FROM result_exchange WHERE status='HOLD_SOURCE_UNIT'").fetchone()[0],
        'foreign_keys_ok':True,'full_lifecycle_inventory':False,'production_changed':False}
