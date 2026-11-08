"""Hypothetical Thai truck freight screening; never a reconstructed route inventory."""
from decimal import Decimal,localcontext
from src.thai_carbon import quantity,screen_activity

def freight_scenario(mass_kg,distance_km,factor,*,assumption_id):
    if not assumption_id:raise ValueError('Hypothetical route assumption required')
    if factor.get('activity_unit')!='tkm':raise ValueError('A km factor cannot be used as a tkm factor')
    with localcontext() as ctx:
        ctx.prec=210;tkm=quantity(mass_kg)/Decimal(1000)*quantity(distance_km)
    result=screen_activity(format(tkm,'f'),'tkm',factor)
    return {'scope':'HYPOTHETICAL_FREIGHT_FACTOR_SCREENING','assumption_id':assumption_id,'mass_kg':mass_kg,'distance_km':distance_km,'tkm':format(tkm,'f'),'loading_policy':'Already represented in selected EF; do not divide by loading a second time','screening':result,'empty_return_added':False,'return_convention_verified':False,'full_transport_inventory':False,'combined_with_biodiesel_factor':False,'existing_model_changed':False}
