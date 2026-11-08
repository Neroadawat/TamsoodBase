"""Explicit secondary-data foreground scenario; no automatic cross-scope carbon sum."""
from decimal import Decimal,localcontext
from src.thai_carbon import quantity
from src.transport_scenario import freight_scenario

def scenario(litres,energy_rows,factor,*,distance_km,assumption_id,mass_rows,production_L_day,energy_basis_L_day):
    if not assumption_id:raise ValueError('Explicit proxy and route assumption required')
    volume=quantity(litres)
    if volume==0:raise ValueError('Positive ethanol reference output required')
    production_basis = quantity(production_L_day)
    survey_basis = quantity(energy_basis_L_day)
    if not production_basis or not survey_basis:
        raise ValueError('Positive daily production and survey bases required')
    units={'electricity':'kWh/day','steam':'t/day'};selected={}
    with localcontext() as ctx:
        ctx.prec=60
        for flow,unit in units.items():
            matches=[r for r in energy_rows if r.get('route')=='molasses' and r.get('flow')==flow]
            if len(matches)!=1:raise ValueError('Unique molasses energy row required')
            row=matches[0]
            if row.get('unit')!=unit or not row.get('locator') or not row.get('range') or len(row['range'])!=2:raise ValueError('Energy provenance/unit/range missing')
            low,high=map(quantity,row['range'])
            if low>high:raise ValueError('Ordered energy interval required')
            selected[flow]={'amount_range':[format(v/survey_basis*volume,'f') for v in [low,high]],'unit':'kWh' if flow=='electricity' else 't','source_locator':row['locator'],'role':'THAI_SECONDARY_SURVEY_PROXY_NOT_MEASURED_CASE','range_not_probability_distribution':True}
        freight = []
        for leg, flow in [('ethanol_to_blending', 'fuel_ethanol'), ('molasses_to_plant', 'molasses')]:
            matches = [row for row in mass_rows if row.get('flow') == flow]
            if len(matches) != 1:
                raise ValueError(f'Unique reviewed mass observation required for {flow}')
            row = matches[0]
            if row.get('unit') != 't/day' or not row.get('locator') or row.get('role') != 'BOUNDARY_FLOW':
                raise ValueError(f'Invalid mass observation for {flow}')
            mass = volume * quantity(row['amount']) * 1000 / production_basis
            result = freight_scenario(format(mass, 'f'), distance_km, factor, assumption_id=assumption_id)
            freight.append(dict(leg=leg, source_locator=row['locator'], **result))
    return {'reference_output_L_ethanol':litres,'assumption_id':assumption_id,'energy':selected,'freight':freight,'route_distance_status':'HYPOTHETICAL_EACH_LEG_NOT_SOURCE_MEASURED','freight_legs_additive':False,'overlap_and_empty_return_review':'UNRESOLVED_NO_SUM','steam_GHG':None,'electricity_GHG':None,'vehicle_use_GHG':None,'waste_GHG':None,'full_lifecycle_lci':False,'CO2e_total':None,'measured_same_plant':False}
