"""Account for current comparison coverage by NSO identity, not publication count."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    nso_path=ROOT/'build/nso/report.json';nso=json.loads(nso_path.read_text(encoding='utf-8'))['rows']
    doeb=json.loads((ROOT/'evidence/nso-doeb-comparison.json').read_text(encoding='utf-8'))
    dede=json.loads((ROOT/'evidence/nso-dede-comparison.json').read_text(encoding='utf-8'))
    ids={r['nso_observation_id'] for r in doeb['comparisons']}
    doeb_source=ROOT/'data/raw/doeb/sales.xls'
    doeb_sha=hashlib.sha256(doeb_source.read_bytes()).hexdigest()
    from decimal import Decimal
    for c in doeb['comparisons']:
        found=[r for r in nso if r['observation_id']==c['nso_observation_id'] and r['table_id']=='13.8' and r['reference_year']==c['year'] and r['label']==c['label'] and r['unit']==c['unit'] and r['amount']==c['nso_value'] and r['source_sha256']==c['nso_sha256']]
        if len(found)!=1 or doeb_sha!=c['doeb_sha256']:raise ValueError('DOEB source or context changed')
        delta=Decimal(c['nso_value'])-Decimal(c['doeb_thousand_litre'])
        if Decimal(c['doeb_stored_million_litre'])*1000!=Decimal(c['doeb_thousand_litre']) or delta!=Decimal(c['difference_nso_minus_doeb']) or (abs(delta)<=Decimal(c['display_tolerance_thousand_litre']))!=c['within_doeb_display_rounding']:raise ValueError('DOEB arithmetic mismatch')
    # Existing DEDE comparison is explicitly one manufacturing total, 2024.
    matches=[r for r in nso if r['observation_id']==dede['nso_observation_id'] and r['table_id']=='13.10' and r['reference_year']==dede['year'] and r['amount']==dede['nso_value'] and r['unit']==dede['unit'] and r['source_sha256']==dede['nso_source_sha256']]
    if len(matches)!=1:raise ValueError('DEDE identity cannot be resolved uniquely')
    ids.add(matches[0]['observation_id'])
    components_path=ROOT/'evidence/nso-dede-components.json'
    component_ids=set()
    if components_path.exists():
        components=json.loads(components_path.read_text(encoding='utf-8'))
        if components['nso_report_sha256']!=hashlib.sha256(nso_path.read_bytes()).hexdigest():raise ValueError('Stale component comparison')
        source=ROOT/'data/raw/dede/revised-2024/energy-balance.xlsx'
        if hashlib.sha256(source.read_bytes()).hexdigest()!=components['revised_source_sha256']:raise ValueError('Revised workbook changed')
        from decimal import Decimal
        for comparison in components['comparisons']:
            found=[r for r in nso if r['observation_id']==comparison['nso_observation_id'] and
                   all(r[key]==comparison[key] for key in ('table_id','reference_year','measure','label','unit')) and
                   r['amount']==comparison['nso_value'] and r['source_sha256']==comparison['nso_source_sha256']]
            if len(found)!=1:raise ValueError('Component context/identity mismatch')
            delta=Decimal(comparison['nso_value'])-Decimal(comparison['dede_revised_value'])
            if delta!=Decimal(comparison['difference_nso_minus_revised']) or (delta==0)!=comparison['exact_displayed_value_match']:
                raise ValueError('Inconsistent component comparison arithmetic')
            component_ids.add(found[0]['observation_id'])
        if len(component_ids)!=len(components['comparisons']):raise ValueError('Duplicate component comparison')
        ids.update(component_ids)
    historical_path=ROOT/'evidence/nso-dede-historical.json';historical_ids=set()
    if historical_path.exists():
        history=json.loads(historical_path.read_text(encoding='utf-8'))
        if history['nso_report_sha256']!=hashlib.sha256(nso_path.read_bytes()).hexdigest():raise ValueError('Stale historical comparison')
        source=ROOT/'data/raw/dede/balance-2023/source.pdf'
        if hashlib.sha256(source.read_bytes()).hexdigest()!=history['source']['sha256']:raise ValueError('Historical PDF changed')
        from decimal import Decimal
        for c in history['comparisons']:
            found=[r for r in nso if r['observation_id']==c['nso_observation_id'] and all(r[k]==c[k] for k in ('table_id','reference_year','measure','label','unit')) and r['amount']==c['nso_value'] and r['source_sha256']==c['nso_source_sha256']]
            if len(found)!=1:raise ValueError('Historical comparison context mismatch')
            delta=Decimal(c['nso_value'])-Decimal(c['dede_value'])
            if delta!=Decimal(c['difference']) or (delta==0)!=c['exact_displayed_value_match']:raise ValueError('Historical arithmetic mismatch')
            historical_ids.add(c['nso_observation_id'])
        if len(historical_ids)!=len(history['comparisons']):raise ValueError('Duplicate historical IDs')
        ids.update(historical_ids)
    extra_ids=set();extra_path=ROOT/'evidence/nso-dede-tables.json'
    if extra_path.exists():
        extra=json.loads(extra_path.read_text(encoding='utf-8'))
        if extra['nso_report_sha256']!=hashlib.sha256(nso_path.read_bytes()).hexdigest():raise ValueError('Stale table comparisons')
        source=ROOT/'data/raw/dede/balance-2023/source.pdf'
        if hashlib.sha256(source.read_bytes()).hexdigest()!=extra['source']['sha256']:raise ValueError('Table comparison PDF changed')
        from decimal import Decimal
        for c in extra['comparisons']:
            found=[r for r in nso if r['observation_id']==c['nso_observation_id'] and all(r[k]==c[k] for k in ('table_id','reference_year','measure','label','unit')) and r['amount']==c['nso_value'] and r['source_sha256']==c['nso_source_sha256']]
            if len(found)!=1:raise ValueError('Table comparison identity mismatch')
            delta=Decimal(c['nso_value'])-Decimal(c['dede_value'])
            if delta!=Decimal(c['difference']) or (delta==0)!=c['exact_displayed_value_match']:raise ValueError('Table comparison arithmetic mismatch')
            extra_ids.add(c['nso_observation_id'])
        if len(extra_ids)!=len(extra['comparisons']) or extra_ids & ids:raise ValueError('Duplicate table comparison IDs')
        ids.update(extra_ids)
    primary_ids=set();primary_path=ROOT/'evidence/nso-dede-primary-2024.json'
    if primary_path.exists():
        primary=json.loads(primary_path.read_text(encoding='utf-8'))
        if primary['nso_report_sha256']!=hashlib.sha256(nso_path.read_bytes()).hexdigest():raise ValueError('Stale primary comparison')
        source=ROOT/'data/raw/dede/revised-2024/energy-balance.xlsx'
        if hashlib.sha256(source.read_bytes()).hexdigest()!=primary['source']['sha256']:raise ValueError('Primary workbook changed')
        for c in primary['comparisons']:
            found=[r for r in nso if r['observation_id']==c['nso_observation_id'] and all(r[k]==c[k] for k in ('table_id','reference_year','measure','label','unit')) and r['amount']==c['nso_value'] and r['source_sha256']==c['nso_source_sha256']]
            if len(found)!=1:raise ValueError('Primary context mismatch')
            delta=Decimal(c['nso_value'])-Decimal(c['dede_value'])
            if delta!=Decimal(c['difference']) or (delta==0)!=c['exact_displayed_value_match'] or (abs(delta)<=Decimal(c['display_tolerance']))!=c['within_display_rounding']:raise ValueError('Primary arithmetic mismatch')
            primary_ids.add(c['nso_observation_id'])
        if len(primary_ids)!=len(primary['comparisons']) or primary_ids & ids:raise ValueError('Duplicate primary IDs')
        ids.update(primary_ids)
    annual_ids=set()
    annual_path=ROOT/'evidence/nso-remaining-audit.json'
    if annual_path.exists():
        annual=json.loads(annual_path.read_text(encoding='utf8'))
        if annual['nso_report_sha256']!=hashlib.sha256(nso_path.read_bytes()).hexdigest():raise ValueError('Stale annual audit')
        if annual['source']['sha256']!=hashlib.sha256((ROOT/'data/raw/dede/balance-2024/source.pdf').read_bytes()).hexdigest():raise ValueError('Annual source changed')
        for c in annual['checks']:
            if c['status']!='EXACT_PUBLICATION_MATCH':continue
            found=[r for r in nso if r['observation_id']==c['nso_observation_id'] and r['reference_year']==2024 and all(r[k]==c[k] for k in ('table_id','label','measure','unit')) and r['amount']==c['nso_value']]
            if len(found)!=1 or Decimal(c['nso_value'])!=Decimal(c['dede_value']):raise ValueError('Annual identity/value mismatch')
            if c['nso_observation_id'] in ids|annual_ids:raise ValueError('Duplicate annual comparison')
            annual_ids.add(c['nso_observation_id'])
        ids.update(annual_ids)
    if not ids<={r['observation_id'] for r in nso}:raise ValueError('Unknown compared NSO identity')
    result=dict(nso_observations=len(nso),compared_unique=len(ids),not_compared=len(nso)-len(ids),
        dede_comparisons=1+len(component_ids)+len(historical_ids)+len(extra_ids)+len(primary_ids)+len(annual_ids),doeb_comparisons=len(doeb['comparisons']),independent_measurements_verified=0,
        nso_report_sha256=hashlib.sha256(nso_path.read_bytes()).hexdigest(),
        note='Comparison of publications from originating agencies; no automatic acceptance or value corrections',
        compared_observation_ids=sorted(ids))
    (ROOT/'evidence/cross-source-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='compared_observation_ids'},indent=2))


if __name__=='__main__':main()
