"""Explicitly conditional fuel-property sensitivity, never an LCI/CO2 total."""
from decimal import Decimal,localcontext

def fuel_basis(energy_mj,lhv,density_kg_m3,*,assumption_id=None,lhv_interpreted_mj_per_kg=False):
    if not assumption_id or not lhv_interpreted_mj_per_kg:raise ValueError('Explicit scenario assumption required for incomplete source LHV unit')
    values=[Decimal(str(x)) for x in (energy_mj,lhv,density_kg_m3)]
    if any(not x.is_finite() or x<=0 for x in values):raise ValueError('Positive finite quantities required')
    with localcontext() as ctx:
        ctx.prec=40;energy,heat,density=values;mass=energy/heat;litres=mass/(density/Decimal(1000))
        return {'scope':'CONDITIONAL_FUEL_PROPERTY_SCENARIO_NOT_MODEL_FUEL_REPLACEMENT','assumption_id':assumption_id,'energy_MJ':str(energy),'mass_kg':str(mass),'volume_litres':str(litres),'density_kg_per_litre':str(density/1000),'LHV_interpretation':'MJ/kg assumed; original header Mj preserved','CO2e_total':None,'emission_factor_eligible':False,'existing_model_changed':False}
