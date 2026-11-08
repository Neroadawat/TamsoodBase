"""Lossless review index across Tables 1-4, never a linked LCI model."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_review(upstream, conversion):
    rows = upstream['rows'] + conversion['rows']
    if len(rows) != 58 or len({r['observation_id'] for r in rows}) != 58:
        raise ValueError('Expected 58 distinct source observations')
    flows, mappings = {}, []
    for row in rows:
        if row['doi'] != '10.3390/su12229415' or row['licence'] != 'CC BY 4.0':
            raise ValueError('Unreviewed source or licence')
        if not Decimal(row['amount']).is_finite() or Decimal(row['amount']) < 0:
            raise ValueError('Invalid source quantity')
        if row['is_full_lci_dataset'] or row.get('allocation_applied_by_this_project', False) or row.get('is_newly_allocated', False):
            raise ValueError('Unexpected model transformation')
        source_hash = row.get('source_sha256') or row.get('source_snapshot_sha256')
        if not source_hash or not row.get('source_url'):
            raise ValueError('Missing provenance')
        # Equality means only identical source label/unit, never equivalence of providers.
        key = (row['doi'], row['flow'], row['unit'])
        flow_id = hashlib.sha256(json.dumps(key, ensure_ascii=False).encode()).hexdigest()
        flows.setdefault(flow_id, {'flow_id': flow_id, 'source_label': row['flow'],
                                  'source_unit': row['unit'], 'compartment': None,
                                  'global_flow_id': None, 'semantic_equivalence_reviewed': False})
        if row['unit'] is None and row['status'] != 'HOLD_MISSING_UNIT':
            raise ValueError('Missing unit must stay held')
        mappings.append({'observation_id': row['observation_id'], 'flow_id': flow_id,
                         'process': row['process'], 'role': row['role'],
                         'mapping_status': 'HOLD_MISSING_UNIT' if row['unit'] is None else 'SOURCE_LABEL_UNIT_EXACT_ONLY',
                         'source': dict(row)})
    profiles = []
    for process in ('FFB', 'CPO', 'RBDPO', 'FAME', 'H-FAME'):
        selected = [r for r in rows if r['process'] == process]
        bases = {(r['reference_amount'], r['reference_unit']) for r in selected}
        products = [r for r in selected if r['role'] == 'REFERENCE_PRODUCT' and r['direction'] == 'OUTPUT']
        if len(bases) != 1 or len(products) != 1:
            raise ValueError('Inconsistent process basis/reference product')
        profiles.append({'process': process, 'source_rows': len(selected),
                         'reference_basis': list(next(iter(bases))),
                         'reference_product_observation_id': products[0]['observation_id'],
                         'held_rows': sum(r['unit'] is None for r in selected),
                         'model_ready': False, 'allocation_application_resolved': False,
                         'measurement_period_known': all(r['data_period'] is not None for r in selected)})
    return {'scope': 'COMBINED_SOURCE_REVIEW_NOT_LINKED_LCI', 'counts': {
        'observations': 58, 'processes': 5, 'source_local_label_unit_keys': len(flows),
        'missing_unit_holds': 1, 'applied_provider_links': 0},
        'flows': list(flows.values()), 'mappings': mappings, 'profiles': profiles,
        'full_lifecycle_inventory': False, 'source_values_changed': False,
        'production_migrated': False}


def main():
    paths = [ROOT/'build/upstream-inventory/report.json', ROOT/'build/product-inventory/report.json']
    reports = [json.loads(p.read_text(encoding='utf8')) for p in paths]
    result = build_review(*reports)
    result['input_sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    out = ROOT/'build/combined-inventory-review'
    out.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
    (out/'review.json').write_text(text, encoding='utf8')
    # Verify every original field after serialization, including nulls and decimal strings.
    restored = json.loads((out/'review.json').read_text(encoding='utf8'))
    if [m['source'] for m in restored['mappings']] != reports[0]['rows']+reports[1]['rows']:
        raise ValueError('Source roundtrip failed')
    evidence = {'counts': result['counts'], 'input_sha256': result['input_sha256'],
                'all_58_source_payloads_roundtrip_equal': True,
                'profiles': result['profiles'], 'scope': result['scope'],
                'production_migrated': False, 'full_lifecycle_inventory': False}
    (ROOT/'evidence/combined-inventory-review.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps(evidence['counts']))


if __name__ == '__main__':
    main()
