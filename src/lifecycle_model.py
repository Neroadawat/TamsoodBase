"""Evidence-gated lifecycle candidate. Missing activity is never zero activity."""
from decimal import Decimal, InvalidOperation
import hashlib
import json

STAGES = ('RAW_MATERIAL', 'MANUFACTURING', 'DISTRIBUTION', 'USE', 'END_OF_LIFE')
GATES = ('allocation_basis', 'reference_flow_scaling', 'provider_compatibility',
         'background_coverage', 'elementary_flow_mapping', 'no_double_counting')
REQUIRED_PARAMETERS = ('FFB_per_CPO', 'FFB_transport_distance',
                       'CPO_transport_distance', 'RBDPO_transport_distance',
                       'fuel_distribution_distance', 'use_emission_inventory',
                       'waste_treatment_inventory')


def validate_lifecycle(model):
    if model.get('route') != 'FAME':
        raise ValueError('Only the selected FAME route is reviewed')
    fu = model.get('functional_unit', {})
    if fu != {'amount': '1000', 'unit': 'MJ fuel', 'service': 'fuel use'}:
        raise ValueError('Study FU must remain explicit')
    stages = model.get('stages', [])
    if len(stages) != 5 or {s['id'] for s in stages} != set(STAGES):
        raise ValueError('Five unique stage decisions required')
    all_ids = []
    source_rows=model.get('source_observations', [])
    source_ids=[r['observation_id'] for r in source_rows]
    if len(source_ids)!=len(set(source_ids)):
        raise ValueError('Duplicate source observations')
    for stage in stages:
        status = stage.get('status')
        if status not in ('MISSING', 'PARTIAL', 'COMPLETE', 'EXCLUDED_WITH_REASON'):
            raise ValueError('Invalid coverage status')
        if not stage.get('reason'):
            raise ValueError('Coverage reason required')
        ids = stage.get('observation_ids', [])
        if any(oid not in source_ids for oid in ids):
            raise ValueError('Stage references an unknown source observation')
        if status in ('MISSING','EXCLUDED_WITH_REASON') and ids:
            raise ValueError('Missing/excluded stage cannot own included observations')
        if status in ('COMPLETE', 'PARTIAL') and not ids:
            raise ValueError('Coverage requires actual observations')
        if status == 'COMPLETE' and (stage.get('open_issues') or not stage.get('evidence')):
            raise ValueError('Complete stage has unresolved evidence')
        if status == 'EXCLUDED_WITH_REASON' and not stage.get('exclusion_evidence'):
            raise ValueError('Exclusion requires explicit scope evidence')
        all_ids.extend(ids)
    if len(all_ids) != len(set(all_ids)):
        raise ValueError('Observation counted in multiple stages')
    if set(all_ids)!=set(source_ids):
        raise ValueError('Every included observation must belong to a stage')
    # Assumptions remain visible and cannot silently become source measurements.
    parameters = model.get('parameters', [])
    parameter_ids = [p.get('id') for p in parameters]
    if len(parameter_ids) != len(set(parameter_ids)):
        raise ValueError('Duplicate lifecycle parameter')
    for parameter in parameters:
        value = parameter.get('value')
        if value is None:
            if parameter.get('status') != 'MISSING':
                raise ValueError('Missing value needs missing status')
            continue
        try:
            number = Decimal(value) if isinstance(value, str) else Decimal('NaN')
        except InvalidOperation:
            raise ValueError('Invalid parameter') from None
        if not number.is_finite() or number < 0 or not parameter.get('unit'):
            raise ValueError('Invalid parameter quantity/unit')
        if parameter.get('status') not in ('SOURCE_VERIFIED', 'SCENARIO_ASSUMPTION'):
            raise ValueError('Parameter evidence class required')
        if not parameter.get('evidence'):
            raise ValueError('Parameter source or assumption justification required')
    unresolved = [g for g in GATES if model.get('gates', {}).get(g) != 'VERIFIED']
    complete = all(s['status'] in ('COMPLETE', 'EXCLUDED_WITH_REASON') for s in stages)
    missing = any(p.get('value') is None for p in model.get('parameters', []))
    assumptions = any(p.get('status') == 'SCENARIO_ASSUMPTION' for p in model.get('parameters', []))
    # Coverage labels cannot erase unresolved rows or remove required decisions.
    # These are readiness blockers, not permission to repair source quantities.
    blockers = []
    for key in REQUIRED_PARAMETERS:
        if key not in parameter_ids:
            blockers.append({'kind': 'REQUIRED_PARAMETER_ABSENT', 'id': key})
    for row in source_rows:
        oid = row['observation_id']
        if not row.get('unit'):
            blockers.append({'kind': 'SOURCE_UNIT_MISSING', 'id': oid})
        if str(row.get('status', '')).startswith(('HOLD', 'REJECT')):
            blockers.append({'kind': 'SOURCE_UNRESOLVED', 'id': oid})
        digest = row.get('source_sha256') or row.get('source_snapshot_sha256')
        if (not row.get('source_url') or not isinstance(digest, str)
                or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest)):
            blockers.append({'kind': 'SOURCE_PROVENANCE_MISSING', 'id': oid})
    for gate in GATES:
        if model.get('gates', {}).get(gate) == 'VERIFIED' and not model.get('gate_evidence', {}).get(gate):
            blockers.append({'kind': 'GATE_EVIDENCE_MISSING', 'id': gate})
        if model.get('gates', {}).get(gate) == 'VERIFIED':
            reference=model.get('gate_evidence',{}).get(gate)
            registry=model.get('decision_registry',{})
            decision=registry.get(reference) if isinstance(reference,str) else None
            valid=False
            if isinstance(decision,dict):
                body={k:v for k,v in decision.items() if k!='decision_id'}
                digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
                valid=(reference==digest==decision.get('decision_id') and decision.get('gate')==gate
                       and bool(model.get('model_version_id')) and decision.get('model_version_id')==model['model_version_id']
                       and decision.get('state')=='ACCEPTED' and bool(decision.get('reviewer_role'))
                       and bool(decision.get('source_locator')) and decision.get('source_sha256') in
                       {r.get('source_sha256') or r.get('source_snapshot_sha256') for r in source_rows})
            if not valid:blockers.append({'kind':'GATE_DECISION_UNRESOLVED','id':gate})
    ready = complete and not unresolved and not missing and bool(all_ids) and not blockers
    if model.get('full_lifecycle_inventory') and not ready:
        raise ValueError('Full lifecycle claim rejected: unresolved model gates')
    if model.get('source_measured_complete') and (assumptions or not ready):
        raise ValueError('Measurement completeness requires a ready model without assumptions')
    return {'model_ready': ready, 'unresolved_gates': unresolved,
            'readiness_scope':'STRUCTURAL_EVIDENCE_BINDING_NOT_INDEPENDENT_SCIENTIFIC_REVIEW',
            'independent_scientific_review_performed':False,
            'readiness_blockers': blockers,
            'scenario_assumptions_present': assumptions,
            'missing_stages': [s['id'] for s in stages if s['status'] == 'MISSING']}
