"""Source-local flow identities and explicit LCIA exclusions; never infer emissions."""
import hashlib
import json
from pathlib import Path
import sqlite3
from src.activity_model_store import audit,identity

ROOT=Path(__file__).resolve().parents[1]
DIMENSIONS={'kg':'mass','g':'mass','mg':'mass','m3':'volume','kWh':'energy','MJ':'energy','MJ fuel':'energy','m2':'area','ha':'area'}


def build():
    evidence=json.loads((ROOT/'evidence/activity-model-store.json').read_text(encoding='utf-8'))
    database=ROOT/evidence['database']
    if hashlib.sha256(database.read_bytes()).hexdigest()!=evidence['database_sha256']:raise ValueError('Model database changed')
    conn=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)
    try:
        audit(conn,require_seal=True)
        sources=[json.loads(r[0]) for r in conn.execute('SELECT payload_json FROM source_observation ORDER BY observation_id')]
    finally:conn.close()
    flows=[]
    for row in sources:
        body={'label':row['flow'],'unit':row['unit'],'scope':'SOURCE_LOCAL_NOT_GLOBAL_ONTOLOGY'}
        flows.append({'observation_id':row.get('observation_id',row.get('id')),'source_flow_id':identity(body),
          'source_label':row['flow'],'unit':row['unit'],'quantity_dimension':DIMENSIONS.get(row['unit'],'UNRESOLVED'),
          'direction':row['direction'],'source_role':row.get('role'),
          'classification':'REPORTED_PROCESS_INPUT' if row['direction']=='INPUT' else 'REPORTED_PROCESS_OUTPUT',
          'elementary_flow':False,'compartment':None,'global_flow_mapping':None,
          'characterization_factor':None,'eligible_for_LCIA':False,
          'reason':'No reviewed elementary-flow compartment/provider/CF mapping; process inputs/outputs are not automatically environmental emissions.',
          'source_sha256':row.get('source_sha256') or row.get('source_snapshot_sha256')})
    return {'scope':'INTERNAL_SOURCE_FLOW_CONTRACT_NOT_ELEMENTARY_INVENTORY','model_release_id':evidence['release_id'],
      'observations':len(flows),'eligible_elementary_observations':0,'CF_method':None,'CF_version':None,'time_horizon':None,
      'CO2e_total':None,'full_lifecycle_inventory':False,'flows':flows,
      'uncertainty':{'measurement_distribution':None,'scenario_variation_is_confidence_interval':False,'display_precision_is_measurement_uncertainty':False},
      'independent_balance':{'performed':False,'reason':'Transfer checks are constructed arithmetic; mass/energy/carbon system closure lacks moisture, composition and emissions.'}}


if __name__=='__main__':
    result=build();folder=ROOT/'build/model-flow-contract';folder.mkdir(exist_ok=True)
    (folder/'contract.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report={k:v for k,v in result.items() if k!='flows'}
    report['contract_sha256']=hashlib.sha256((folder/'contract.json').read_bytes()).hexdigest()
    (ROOT/'evidence/model-flow-contract.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
