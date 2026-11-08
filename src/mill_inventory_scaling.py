"""Scale one reviewed Thai mill's reported quantities; never an LCIA calculation."""
from decimal import Decimal, InvalidOperation, localcontext
import re


def scale_mill(review, mill, cpo_kg):
    if not isinstance(cpo_kg,str) or not re.fullmatch(r'\d{1,15}(?:\.\d{1,12})?',cpo_kg):
        raise ValueError('CPO kg must be a bounded positive plain decimal string')
    try:
        demand=Decimal(cpo_kg)
    except InvalidOperation:
        raise ValueError('Invalid CPO quantity') from None
    if not demand.is_finite() or demand<=0:
        raise ValueError('CPO quantity must be positive')
    if mill not in [f'Mill {i}' for i in range(1,7)]:
        raise ValueError('Select one reviewed mill; no synthetic mixed plant')
    if review.get('scope')!='ALTERNATIVE_MILL_FOREGROUND_CANDIDATE':
        raise ValueError('Wrong source inventory type')
    rows=[r for r in review['observations'] if r['mill']==mill]
    if len(rows)!=15 or len({r['id'] for r in rows})!=15:
        raise ValueError('Selected mill must retain all 15 unique observations')
    reference=[r for r in rows if r['role']=='REFERENCE_PRODUCT']
    if len(reference)!=1 or reference[0]['flow']!='Crude palm oil' or reference[0]['amount']!='1000':
        raise ValueError('Reference product must be the reported 1000 kg CPO output')
    scaled=[]
    with localcontext() as ctx:
        ctx.prec=100
        factor=demand/Decimal('1000')
        for row in rows:
            if (row['reference_amount']!='1000' or row['reference_unit']!='kg'
                or row['reference_product']!='CPO' or row['source_sha256']!=review['source_sha256']
                or not row.get('source_url') or not row.get('unit')):
                raise ValueError('Source basis/provenance inconsistent')
            amount=Decimal(row['amount'])
            if not amount.is_finite() or amount<0:
                raise ValueError('Source quantity invalid')
            scaled.append({'source':dict(row),'scaled_amount':format(amount*factor,'f'),
                           'scaled_unit':row['unit']})
    return {'mill':mill,'requested_CPO_kg':cpo_kg,'scale_factor':format(factor,'f'),
        'result_type':'SCALED_SOURCE_FOREGROUND_QUANTITIES_NOT_NORMALIZED_LCI',
        'request_class':'USER_SELECTED_ACTIVITY_SCENARIO_NOT_MEASURED_OUTPUT',
        'rows':scaled,'allocation_applied':False,'avoided_product_credit_applied':False,
        'background_provider_applied':False,'CO2e_total':None,'full_lifecycle_inventory':False,
        'rights_status':'NOT_CLEARED','production_changed':False}
