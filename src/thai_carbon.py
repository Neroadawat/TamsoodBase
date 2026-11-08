"""Scoped screening arithmetic, not a complete LCI or certified CFP result."""
from decimal import Decimal, InvalidOperation, localcontext


def quantity(value):
    if not isinstance(value, str):
        raise ValueError('Use decimal strings')
    if len(value)>100 or 'e' in value.lower():
        raise ValueError('Use bounded plain decimal notation')
    try:
        number = Decimal(value)
    except InvalidOperation:
        raise ValueError('Invalid number') from None
    if not number.is_finite() or number < 0:
        raise ValueError('Nonnegative finite quantity required')
    return number


def screen_activity(amount, unit, factor):
    if factor.get('geography') != 'TH' or factor.get('provenance_class') != 'THAI_NATIONAL_LCI_REPORTED':
        raise ValueError('Thai activity-factor evidence required; Thai publisher alone is insufficient')
    if unit != factor.get('activity_unit'):
        raise ValueError('Unit mismatch: no implicit litre/kg/MJ conversion')
    if factor.get('result_unit') != 'kgCO2e' or not factor.get('method') or not factor.get('version'):
        raise ValueError('Characterized factor method/version required')
    if not factor.get('source_url') or not factor.get('source_sha256') or not factor.get('locator'):
        raise ValueError('Factor provenance missing')
    activity, coefficient = quantity(amount), quantity(factor['value'])
    with localcontext() as ctx:
        ctx.prec=210
        result = activity * coefficient
    return {'activity_amount':amount, 'activity_unit':unit, 'factor_id':factor['id'],
            'factor_value':factor['value'], 'factor_version':factor['version'],
            'method':factor['method'], 'result':format(result,'f'), 'result_unit':'kgCO2e',
            'result_type':'SCOPED_FACTOR_SCREENING', 'full_lifecycle_result':False,
            'direct_CO2_kg':None, 'source_url':factor['source_url'],
            'source_sha256':factor['source_sha256'], 'source_locator':factor['locator'],
            'thai_representative_factor_reported':True,
            'strict_all_inputs_thai_verified':factor.get('underlying_all_inputs_thai_audited') is True,
            'limitation':'Characterized factor result only; boundary and overlap review required before summation. Not a full LCI, direct CO2 measurement or certified CFP.'}
