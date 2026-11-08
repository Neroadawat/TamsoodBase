"""Account for every NSO observation without turning missing comparisons into passes."""
from collections import Counter
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    report=ROOT/'build/nso/report.json';rows=json.loads(report.read_text(encoding='utf-8'))['rows']
    coverage=json.loads((ROOT/'evidence/cross-source-coverage.json').read_text())
    if coverage['nso_report_sha256']!=hashlib.sha256(report.read_bytes()).hexdigest():raise ValueError('Stale coverage')
    prior=json.loads((ROOT/'evidence/source-cell-audit.json').read_text());ledger=ROOT/'build/source-cell-audit/ledger.jsonl'
    if hashlib.sha256(ledger.read_bytes()).hexdigest()!=prior['ledger_sha256']:raise ValueError('Original source audit ledger changed')
    verified={r['observation_key']:r for r in map(json.loads,ledger.read_text(encoding='utf-8').splitlines()) if r['layer']=='nso' and r['matched']}
    checks={}
    for filename in ('nso-doeb-comparison.json','nso-dede-components.json','nso-dede-historical.json','nso-dede-tables.json','nso-dede-primary-2024.json'):
        evidence=json.loads((ROOT/'evidence'/filename).read_text(encoding='utf-8'))
        for c in evidence['comparisons']:
            oid=c['nso_observation_id']
            if oid in checks:raise ValueError('Comparison counted twice')
            if 'within_doeb_display_rounding' in c:
                state='DISPLAY_ROUNDING_AGREEMENT' if c['within_doeb_display_rounding'] else 'SOURCE_DIVERGENCE_REVIEW_REQUIRED'
            elif c['exact_displayed_value_match']:state='EXACT_PUBLICATION_MATCH'
            elif c.get('within_display_rounding'):state='DISPLAY_ROUNDING_AGREEMENT'
            else:state='SOURCE_DIVERGENCE_REVIEW_REQUIRED'
            checks[oid]=(state,filename)
    original=json.loads((ROOT/'evidence/nso-dede-revised-comparison.json').read_text())
    checks[original['nso_observation_id']]=('EXACT_PUBLICATION_MATCH' if original['exact_displayed_value_match'] else 'SOURCE_DIVERGENCE_REVIEW_REQUIRED','nso-dede-revised-comparison.json')
    annual=json.loads((ROOT/'evidence/nso-remaining-audit.json').read_text(encoding='utf8'))
    held={}
    for c in annual['checks']:
        if c['status']=='EXACT_PUBLICATION_MATCH':checks[c['nso_observation_id']]=('EXACT_PUBLICATION_MATCH','nso-remaining-audit.json')
        else:held[c['nso_observation_id']]=c['status']
    derived={c['nso_observation_id']:c for c in annual['derived_checks']}
    result=[]
    for r in rows:
        oid=r['observation_id']
        if oid not in verified or verified[oid]['source_sha256']!=r['source_sha256']:raise ValueError('Prior direct source verification missing')
        if oid in checks:state,evidence=checks[oid]
        else:
            evidence=None
            if oid in held:state=held[oid];evidence='nso-remaining-audit.json'
            elif r['table_id']=='13.10' and r['measure']=='ร้อยละ':state='NO_DIRECT_EXTERNAL_PERCENT_CELL'
            elif r['table_id']=='13.8' and r['reference_year']==2025:state='DOEB_SNAPSHOT_ENDS_2024'
            elif r['table_id']=='13.8' and r['unit']=='Thousand kilogram':state='EXTERNAL_SHEET_VOLUME_NOT_MASS'
            elif r['table_id']=='13.8':state='FUEL_CLASSIFICATION_MAPPING_NOT_APPROVED'
            elif r['table_id']=='13.5' and r['label'] in ('พลังงานหมุนเวียน','พลังงานอื่น ๆ'):state='AGGREGATION_SCOPE_DIFFERS'
            else:state='EXTERNAL_2024_TABLE_NOT_YET_EXTRACTED'
        result.append({**{k:r[k] for k in ('observation_id','table_id','reference_year','label','measure','unit','source_url','source_sha256')},'original_source_cell_verified':True,'cross_source_status':state,'comparison_evidence':evidence,'derived_consistency_verified':derived.get(oid,{}).get('within_8_decimal_rounding')})
    if set(checks)!=set(coverage['compared_observation_ids']):raise ValueError('Coverage differs from row ledger')
    payload={'reviewed_observations':len(result),'original_source_cell_verified':len(result),'cross_source_compared':len(checks),'cross_source_not_compared':len(result)-len(checks),'status_counts':dict(Counter(r['cross_source_status'] for r in result)),'rows':result,'source_values_changed':False,'scope':'All273 accounted for; comparison gaps explicitly remain open, not passed; original source checks refer to retained snapshot audit'}
    (ROOT/'evidence/nso-review-ledger.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
