"""Build FAME-only stage register from the preserved full source payloads."""
import hashlib
import json
from pathlib import Path
from src.lifecycle_model import GATES, validate_lifecycle

ROOT = Path(__file__).resolve().parents[1]


def build(review):
    selected = [m['source'] for m in review['mappings'] if m['process'] != 'H-FAME']
    def stage(code, processes, reason, issues):
        rows = [r for r in selected if r['process'] in processes]
        return {'id': code, 'status': 'PARTIAL' if rows else 'MISSING',
                'reason': reason, 'observation_ids': [r['observation_id'] for r in rows],
                'evidence': sorted({r['source_url'] for r in rows}), 'open_issues': issues}
    result = {'route': 'FAME', 'candidate_only': True,
      'functional_unit': {'amount': '1000', 'unit': 'MJ fuel', 'service': 'fuel use'},
      'study_doi': '10.3390/su12229415',
      'stages': [
        stage('RAW_MATERIAL', ['FFB'], 'Cultivation observations retained on their own 1000 kg basis', ['missing_unit', 'background_emissions']),
        stage('MANUFACTURING', ['CPO','RBDPO','FAME'], 'Source unit-process observations, not yet linked/scaled', ['FFB_input', 'allocation_basis', 'provider_links']),
        stage('DISTRIBUTION', [], 'Study includes transport but quantitative compatible transport inventory not imported', ['distance', 'payload', 'empty_return', 'transport_provider']),
        stage('USE', [], 'Study specifies pickup-truck use; full quantitative use inventory not available here', ['compatible_tailpipe_inventory', 'biogenic_fossil_split']),
        stage('END_OF_LIFE', [], 'Relevance and treatment scope must be documented; no zero-waste assumption', ['waste_routes', 'treatment_boundary', 'avoid_combustion_double_count'])],
      'parameters': [{'id': key, 'value': None, 'unit': unit, 'status':'MISSING'} for key,unit in
        [('FFB_per_CPO','kg/kg'),('FFB_transport_distance','km'),('CPO_transport_distance','km'),
         ('RBDPO_transport_distance','km'),('fuel_distribution_distance','km'),('use_emission_inventory',None),('waste_treatment_inventory',None)]],
      'gates': {g:'UNRESOLVED' for g in GATES}, 'full_lifecycle_inventory':False,
      'source_measured_complete':False, 'source_observations':selected,
      'source_values_changed':False, 'production_changed':False}
    result['readiness'] = validate_lifecycle(result)
    return result


def main():
    source=ROOT/'build/combined-inventory-review/review.json'
    result=build(json.loads(source.read_text(encoding='utf8')))
    result['input_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    out=ROOT/'build/lifecycle-candidate';out.mkdir(parents=True,exist_ok=True)
    (out/'fame.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    evidence={k:v for k,v in result.items() if k!='source_observations'}
    evidence['source_observation_count']=len(result['source_observations'])
    (ROOT/'evidence/lifecycle-candidate.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'observations':len(result['source_observations']),**result['readiness']}))


if __name__=='__main__':main()
