"""Traceable process profiles and source-local flow mapping; no allocation/model calculation."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.inventory_scope import study_scope

def map_flows(rows,registry):
    if registry['source_doi']!='10.3390/su12229415':raise ValueError('Unsupported source registry')
    entries=registry['flows'];lookup={f['source_label']:f for f in entries}
    if len(lookup)!=len(entries) or len({f['flow_id'] for f in entries})!=len(entries):raise ValueError('Duplicate flow identity/label')
    mapped=[]
    for row in rows:
        flow=lookup.get(row['flow'])
        if row['doi']!=registry['source_doi'] or not flow or flow['source_unit']!=row['unit']:raise ValueError('Flow/unit/source not reviewed')
        if flow['compartment'] is not None:raise ValueError('Cannot infer environmental compartment from process utility table')
        mapped.append({'observation_id':row['observation_id'],'flow_id':flow['flow_id'],'classification':flow['classification'],'quantity_dimension':flow['quantity_dimension'],'source_label':row['flow'],'source_unit':row['unit'],'source_row':row['source_row'],'source_column':row['source_column'],'mapping_status':'SOURCE_LOCAL_EXACT_NOT_GLOBAL_ONTOLOGY','provider_status':'NOT_LINKED','source_value_changed':False})
    return mapped

def main():
    path=ROOT/'build/product-inventory/report.json';body=path.read_bytes();report=json.loads(body)
    registry_path=ROOT/'docs/inventory-flow-registry.json';registry=json.loads(registry_path.read_text(encoding='utf8'))
    context=(ROOT/'data/raw/mdpi-9415/article-visible.txt').read_text(encoding='utf8')
    raw=ROOT/'data/raw/mdpi-9415/table4-dom.json'
    if hashlib.sha256(raw.read_bytes()).hexdigest()!=report['source_snapshot_sha256']:raise ValueError('Source changed')
    scope=study_scope(report['rows'],context);mapped=map_flows(report['rows'],registry)
    profiles=[]
    for process in scope['processes']:
        rows=[r for r in report['rows'] if r['process']==process['process']]
        profiles.append(process|{'study_functional_unit':scope['study_functional_unit'],'readiness':{
            'source_locator_present':all(r['source_row']>0 and r['source_column']>0 for r in rows),
            'reference_basis_consistent':True,'reference_product_identified':True,
            'source_local_flow_mapping_complete':True,'measurement_period_known':all(r['data_period'] is not None for r in rows),
            'provider_links_complete':False,'allocation_application_resolved':False,
            'elementary_flow_coverage_reviewed':False,'independent_expert_reviewed':False,
            'model_ready':False,'status':'SOURCE_REPORTED_FOREGROUND_REVIEWED_NOT_MODEL_READY'}})
    # Same-name product is a candidate, not permission to link or scale allocated datasets.
    upstream=[r for r in report['rows'] if r['process']=='FAME' and r['role']=='REFERENCE_PRODUCT']
    downstream=[r for r in report['rows'] if r['process']=='H-FAME' and r['direction']=='INPUT' and r['flow']=='FAME']
    candidates=[]
    if len(upstream)==len(downstream)==1 and upstream[0]['unit']==downstream[0]['unit']:
        candidates.append({'consumer_observation_id':downstream[0]['observation_id'],'provider_observation_id':upstream[0]['observation_id'],'status':'CANDIDATE_NOT_APPLIED','evidence':'Same article, product label FAME and mass unit kg','blocked_by':['Allocation application not resolved','Measurement period unspecified','Compatibility of source process models not reviewed'],'scaling_applied':False})
    result={'version':1,'inventory_sha256':hashlib.sha256(body).hexdigest(),'registry_sha256':hashlib.sha256(registry_path.read_bytes()).hexdigest(),'source_snapshot_sha256':report['source_snapshot_sha256'],'profiles':profiles,'mapped_exchanges':mapped,'provider_candidates':candidates,'counts':{'source_exchanges':len(report['rows']),'mapped_exchanges':len(mapped),'source_local_flows':len({m['flow_id'] for m in mapped}),'provider_candidates':len(candidates),'applied_provider_links':0,'model_ready_processes':0},'source_values_changed':False,'production_migrated':False,'scope':'Local review artifact, not a new set of accepted LCI observations or a whole-lifecycle model'}
    out=ROOT/'build/inventory-model-review';out.mkdir(parents=True,exist_ok=True)
    (out/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (ROOT/'evidence/inventory-model-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result['counts'],indent=2))
if __name__=='__main__':main()
