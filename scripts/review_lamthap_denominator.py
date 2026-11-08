"""Record source-text denominator diagnostics; never import or normalize these values."""
import json
from decimal import Decimal, localcontext
from pathlib import Path

URL = 'https://rspo.org/wp-content/uploads/Univanich_Lamthap_Mill_RSPO_audit_report_final_report_22_07.pdf'

def review():
    with localcontext() as ctx:
        ctx.prec = 30
        water_per_ffb = Decimal('310100') / Decimal('196145')
    return {
        'reviewed_at': '2026-11-06',
        'source_url': URL,
        'source_kind': 'RSPO_AUDITOR_PUBLIC_SUMMARY_THAI_FACILITY',
        'assessment_dates': ['2015-01-29', '2015-01-31'],
        'evidence_level': 'WEB_READER_TEXT_ONLY',
        'raw_download': 'HTTP403', 'visual_check': 'WEB_SCREENSHOT_CACHE_MISS',
        'pdf_sha256': None, 'redistribution_status': 'NOT_CLEARED',
        'scope_findings': [
            {'locator': 'PDF5-6 Section1.4', 'finding': 'Production table covers estate/divisions certification supply; independent growers excluded; CPO/PK calculated using extraction ratios. Not whole-mill measured output.'},
            {'locator': 'PDF34 Indicator4.4.4', 'finding': 'Whole-mill2014FFB includes independent smallholders; different denominator coverage and period from2013CDM wastewater.'},
            {'locator': 'PDF29 and34 Indicators4.4.3-4.4.4', 'finding': 'Treated effluent reused/irrigated; zero-discharge narrative is not zero methane/zero water use and BOD threshold is not measured emission load.'}
        ],
        'provisional_water_arithmetic': {
            'locator': 'PDF34 Indicator4.4.4',
            'reported_2014_FFB_t': '196145',
            'reported_approximate_water_m3': '310100',
            'reported_ratio_m3_per_tFFB': '0.63',
            'ratio_from_reported_totals_m3_per_tFFB': str(water_per_ffb),
            'ratio_consistent': False,
            'interpretation': 'Potential source/extraction issue; no reciprocal correction or overwrite. Printed PDF visual verification still missing.'
        },
        'link_to_CDM2013': {'eligible': False, 'blocking_reasons': ['RAW_PDF_UNVERIFIED', '2014_VS_2013', 'CERTIFIED_SUBSET_VS_WHOLE_MILL', 'CALCULATED_VS_MEASURED_CPO', 'WATER_ARITHMETIC_UNRESOLVED']},
        'numeric_rows_imported': 0,
        'normalized_wastewater_per_kgCPO': None,
        'CO2e_total': None,
        'existing_model_changed': False
    }

if __name__ == '__main__':
    result = review()
    Path('evidence/thai-lamthap-denominator-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Denominator rejected:', ', '.join(result['link_to_CDM2013']['blocking_reasons']))
    print('Provisional arithmetic:', result['provisional_water_arithmetic']['ratio_from_reported_totals_m3_per_tFFB'])
