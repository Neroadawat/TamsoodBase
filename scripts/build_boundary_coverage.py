"""Evidence-scoped coverage, never infer missing exchanges or quantitative completeness."""
import json
from scripts.build_combined_inventory_review import ROOT, build_review


def coverage(upstream, conversion, provider):
    review = build_review(upstream, conversion)
    known_pairs = {('CPO','RBDPO'),('RBDPO','FAME'),('FAME','H-FAME')}
    pairs = {(e['provider_process'],e['consumer_process']) for e in provider['provider_candidates']}
    if pairs != known_pairs or provider['applied_links'] != 0 or provider['allocation_applied']:
        raise ValueError('Provider evidence changed; reassess coverage')
    if any(e['status'] != 'CANDIDATE_NOT_APPLIED' or e['scaling_applied'] for e in provider['provider_candidates']):
        raise ValueError('Provider candidate was applied')
    allrows = upstream['rows']+conversion['rows']
    identities = {r['observation_id']: r for r in allrows}
    for edge in provider['provider_candidates']:
        for field, process, direction in [('provider_observation_id',edge['provider_process'],'OUTPUT'),
                                          ('consumer_observation_id',edge['consumer_process'],'INPUT')]:
            row = identities.get(edge[field])
            if not row or row['process'] != process or row['direction'] != direction or row['flow'] != edge['flow'] or row['unit'] != edge['unit']:
                raise ValueError('Provider locator/context mismatch')
    profiles = []
    for profile in review['profiles']:
        process = profile['process']
        rows = [r for r in allrows if r['process'] == process]
        held = [r['observation_id'] for r in rows if r['unit'] is None]
        incoming = [e for e in provider['provider_candidates'] if e['consumer_process'] == process]
        issues = ['ALLOCATION_APPLICATION_UNRESOLVED','MEASUREMENT_PERIOD_NOT_REPORTED',
                  'BACKGROUND_PROVIDER_COVERAGE_NOT_ESTABLISHED',
                  'ELEMENTARY_FLOW_CLASSIFICATION_NOT_COMPLETED']
        if held: issues.append('SOURCE_UNIT_MISSING')
        if process == 'CPO':
            if any(r['direction']=='INPUT' and r['flow']=='FFB' for r in rows):
                raise ValueError('FFB input now present; reassess missing link')
            issues.append('FFB_INPUT_QUANTITY_NOT_IN_SELECTED_TABLE')
        profiles.append({'process': process, 'observation_ids': [r['observation_id'] for r in rows],
                         'held_observation_ids': held, 'reference_basis': profile['reference_basis'],
                         'incoming_candidate_observation_ids': [e['consumer_observation_id'] for e in incoming],
                         'open_issue_codes': issues,
                         'quality': {'source_extraction': 'REVIEW_EVIDENCE_RECORDED',
                                     'cross_publication': 'NOT_ESTABLISHED_FOR_THIS_INVENTORY',
                                     'independent_measurement': 'NOT_PERFORMED',
                                     'time_representativeness': 'UNKNOWN',
                                     'geography': 'THAILAND_STUDY_CONTEXT_NOT_NATIONAL_AVERAGE',
                                     'technical_model_completeness': 'INCOMPLETE',
                                     'quality_score': None},
                         'model_ready': False})
    return {'scope': 'SELECTED_TABLE_COVERAGE_NOT_STUDY_COMPLETENESS',
            'profiles': profiles, 'observations': 58, 'applied_provider_links': 0,
            'full_lifecycle_inventory': False, 'quantitative_completeness_percent': None,
            'missing_stages_for_whole_lifecycle_claim': ['Verified connections between foreground processes',
                'Background supply of electricity/materials/chemicals',
                'Transport stages within the declared study boundary',
                'Vehicle fuel-use stage', 'Reviewed elementary emissions/resources'],
            'warning': 'Absent from imported model does not mean absent from original study; no missing amount is zero-filled.'}


def main():
    def read(name): return json.loads((ROOT/name).read_text(encoding='utf8'))
    result = coverage(read('build/upstream-inventory/report.json'), read('build/product-inventory/report.json'),
                      read('evidence/upstream-provider-review.json'))
    out = ROOT/'build/combined-inventory-review/boundary-coverage.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
    out.write_text(body, encoding='utf8')
    (ROOT/'evidence/boundary-coverage.json').write_text(body, encoding='utf8')
    print('5 process coverage profiles; 58 locators; 0 applied links; no completeness percentage')


if __name__ == '__main__': main()
