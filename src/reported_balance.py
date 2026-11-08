"""Audit visually transcribed source GHG contributions, not elementary gas inventory."""
from decimal import Decimal,localcontext

def reported_balance(components,reported_total):
    if not components:raise ValueError('Components required')
    ids=[r['id'] for r in components]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate component')
    chosen=set(ids)
    if any(chosen.intersection(r.get('ancestor_ids',[])) for r in components):raise ValueError('Parent and child double count')
    with localcontext() as ctx:
        ctx.prec=40
        values=[Decimal(r['value']) for r in components];target=Decimal(reported_total)
        if any(not x.is_finite() for x in values+[target]):raise ValueError('Finite source decimals required')
        total=sum(values,Decimal(0));difference=total-target
        # Each displayed contribution and target rounded to 0.1g.
        allowance=Decimal('0.05')*Decimal(len(values)+1)
    return {'sum_from_displayed_components':str(total),'reported_total':reported_total,'difference':str(difference),'display_rounding_allowance':str(allowance),'within_display_rounding':abs(difference)<=allowance,'reported_value_overwritten':False}
