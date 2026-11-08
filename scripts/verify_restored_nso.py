"""Recheck all restored NSO identities and recorded comparison arithmetic, preserving gaps."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from review_nso import totals

ROOT = Path(__file__).resolve().parents[1]


def main():
    rows = json.loads((ROOT / 'build/nso/report.json').read_bytes())['rows']
    by_id = {r['observation_id']: r for r in rows}
    ledger = json.loads((ROOT / 'evidence/nso-review-ledger.json').read_bytes())
    if set(by_id) != {r['observation_id'] for r in ledger['rows']}: raise ValueError('Restored identity mismatch')
    for record in ledger['rows']:
        row = by_id[record['observation_id']]
        for key in ('table_id', 'reference_year', 'label', 'measure', 'unit', 'source_sha256'):
            if row[key] != record[key]: raise ValueError('Restored context differs')
    checked = {}; discrepancies = []
    for name in ('nso-doeb-comparison.json', 'nso-dede-components.json', 'nso-dede-historical.json',
                 'nso-dede-tables.json', 'nso-dede-primary-2024.json', 'nso-dede-revised-comparison.json',
                 'nso-remaining-audit.json'):
        evidence = json.loads((ROOT / 'evidence' / name).read_bytes())
        entries = evidence.get('comparisons', evidence.get('checks', [evidence]))
        for entry in entries:
            if name == 'nso-remaining-audit.json' and entry['status'] != 'EXACT_PUBLICATION_MATCH': continue
            oid = entry['nso_observation_id']; row = by_id[oid]
            if Decimal(row['amount']) != Decimal(entry['nso_value']): raise ValueError('Recorded source value differs')
            external = next((entry[k] for k in ('doeb_thousand_litre', 'dede_revised_value', 'revised_value', 'dede_value') if k in entry), None)
            if external is None: raise ValueError('No external value in ' + name)
            delta = Decimal(row['amount']) - Decimal(external)
            recorded_delta = next((entry[k] for k in ('difference_nso_minus_doeb', 'difference_nso_minus_revised', 'difference') if k in entry), None)
            if recorded_delta is not None and delta != Decimal(recorded_delta): raise ValueError('Comparison arithmetic changed')
            if oid in checked: raise ValueError('Comparison counted twice')
            checked[oid] = name
            if entry.get('within_doeb_display_rounding') is False:
                discrepancies.append({'observation_id': oid, 'label': row['label'], 'year': row['reference_year'],
                                      'nso_value': row['amount'], 'other_value': external, 'difference': str(delta),
                                      'status': 'SOURCE_DIVERGENCE_REVIEW_REQUIRED', 'evidence': name})
    expected_ids = set(json.loads((ROOT / 'evidence/cross-source-coverage.json').read_bytes())['compared_observation_ids'])
    if set(checked) != expected_ids or len(checked) != 169 or len(discrepancies) != 4:
        raise ValueError('Recorded coverage differs')
    arithmetic = totals(rows)
    if not all(c['passed'] for c in arithmetic): raise ValueError('Internal totals fail')
    derived = json.loads((ROOT / 'evidence/nso-remaining-audit.json').read_bytes())['derived_checks']
    for record in derived:
        numerator = Decimal(by_id[record['numerator_id']]['amount'])
        denominator = Decimal(by_id[record['denominator_id']]['amount'])
        if denominator <= 0 or abs(numerator / denominator * 100 - Decimal(by_id[record['nso_observation_id']]['amount'])) > Decimal('0.000000005'):
            raise ValueError('Derived consistency differs')
    remaining = [r for r in ledger['rows'] if r['observation_id'] not in checked]
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'restored_source_identities_verified': len(rows),
              'recorded_comparison_arithmetic_rechecked': len(checked), 'new_external_comparisons': 0,
              'remaining_count': len(remaining), 'remaining_by_reason': dict(Counter(r['cross_source_status'] for r in remaining)),
              'remaining': remaining, 'source_divergences': discrepancies,
              'internal_totals_checked': len(arithmetic), 'derived_percentages_checked': len(derived),
              'scope': 'RESTORED_NSO_AND_PRIOR_EVIDENCE_RECHECK_NOT_NEW_EXTERNAL_VALIDATION',
              'external_raw_files_reacquired': False, 'source_values_changed': False,
              'source_report_sha256': hashlib.sha256((ROOT / 'build/nso/report.json').read_bytes()).hexdigest(), 'passed': True}
    (ROOT / 'evidence/nso-restored-review-2026-11-08.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ('remaining', 'source_divergences')}, ensure_ascii=False))


if __name__ == '__main__': main()
