"""Traceable partial GHG calculations; completeness is never inferred from arithmetic."""
import re
from decimal import Decimal, localcontext
from src.thai_carbon import quantity

def provenance(source):
    if not source.get('source_url') or not source.get('locator') or not re.fullmatch(r'[0-9a-f]{64}',source.get('source_sha256','')):
        raise ValueError('Source URL, SHA256 and locator required')

def characterize(amount, unit, gas_id, factors, *, basis_id, coverage_id, source):
    provenance(source);provenance(factors)
    if unit!='kg':raise ValueError('Gas mass must be explicit kg; CO2e cannot be characterized again')
    if not basis_id or not coverage_id:raise ValueError('Basis and nonoverlap coverage identity required')
    if not factors.get('method_id') or factors.get('horizon_years')!=100:raise ValueError('Explicit GWP100 method required')
    if gas_id not in factors.get('gases',{}):raise ValueError('Gas/origin not in selected method; no default GWP')
    coefficient=quantity(factors['gases'][gas_id]);mass=quantity(amount)
    with localcontext() as ctx:
        ctx.prec=210;result=mass*coefficient
    return {'amount_kgCO2e':format(result,'f'),'gas_mass_kg':amount,'gas_id':gas_id,
            'GWP100':format(coefficient,'f'),'method_id':factors['method_id'],
            'basis_id':basis_id,'coverage_ids':[coverage_id],
            'source':dict(source),'factor_source':{k:factors[k] for k in ['source_url','source_sha256','locator']},
            'full_lifecycle_result':False,'CO2e_total':None}

def partial_sum(results):
    if not results:raise ValueError('At least one characterized result required')
    method=results[0]['method_id'];basis=results[0]['basis_id'];seen=set();total=Decimal(0)
    with localcontext() as ctx:
        ctx.prec=210
        for r in results:
            if r.get('method_id')!=method or r.get('basis_id')!=basis:raise ValueError('Mixed GWP methods or functional bases')
            ids=r.get('coverage_ids',[])
            if not ids or len(set(ids))!=len(ids) or seen.intersection(ids):raise ValueError('Duplicate/overlapping coverage')
            provenance(r.get('source',{}))
            seen.update(ids);total+=quantity(r['amount_kgCO2e'])
    return {'partial_kgCO2e':format(total,'f'),'method_id':method,'basis_id':basis,'coverage_ids':sorted(seen),'coverage_note':'Caller must review physical scope overlap;different IDs alone do not prove independence','full_lifecycle_result':False,'CO2e_total':None}
