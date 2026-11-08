"""Locate potential provider edges; never apply allocation or calculate lifecycle totals."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    up_path=ROOT/'build/upstream-inventory/report.json';base_path=ROOT/'build/product-inventory/report.json'
    upstream=json.loads(up_path.read_text(encoding='utf8'));base=json.loads(base_path.read_text(encoding='utf8'))
    allrows=upstream['rows']+base['rows'];edges=[]
    for supplier,consumer,flow in [('CPO','RBDPO','CPO'),('RBDPO','FAME','RBDPO'),('FAME','H-FAME','FAME')]:
        product=[r for r in allrows if r['process']==supplier and r['role']=='REFERENCE_PRODUCT' and r['flow']==flow]
        inputs=[r for r in allrows if r['process']==consumer and r['direction']=='INPUT' and r['flow']==flow]
        if len(product)!=1 or len(inputs)!=1:raise ValueError('Ambiguous candidate provider')
        p,c=product[0],inputs[0]
        if p['unit']!=c['unit'] or p['doi']!=c['doi']:raise ValueError('Candidate source/unit incompatible')
        edges.append({'provider_process':supplier,'consumer_process':consumer,'provider_observation_id':p['observation_id'],'consumer_observation_id':c['observation_id'],'flow':flow,'provider_output':p['amount'],'consumer_input':c['amount'],'unit':p['unit'],'doi':p['doi'],'status':'CANDIDATE_NOT_APPLIED','hold_reasons':['Allocation application unresolved','Measurement periods unavailable','Link compatibility needs domain review'],'scaling_applied':False})
    if any(r['process']=='CPO' and r['direction']=='INPUT' and r['flow']=='FFB' for r in allrows):raise ValueError('Missing-feedstock assessment needs revision')
    result={'source_report_sha256':{'upstream':hashlib.sha256(up_path.read_bytes()).hexdigest(),'conversion':hashlib.sha256(base_path.read_bytes()).hexdigest()},'provider_candidates':edges,'missing_links':[{'provider_process':'FFB','consumer_process':'CPO','reason':'No FFB input amount in Table2; do not infer from output totals'}],'applied_links':0,'allocation_applied':False,'full_lifecycle_inventory':False,'production_updated':False}
    (ROOT/'evidence/upstream-provider-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('3 provider candidates; 1 missing feedstock link; 0 applied links')
if __name__=='__main__':main()
