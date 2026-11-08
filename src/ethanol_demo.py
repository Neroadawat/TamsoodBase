"""Study-specific molasses/E10 material basis; never an elementary inventory total."""
from decimal import Decimal, localcontext
from src.thai_carbon import quantity

def molasses_e10_basis(distance_km, *, assumption_id):
    if not isinstance(assumption_id,str) or not assumption_id.strip():
        raise ValueError('Study basis interpretation must have an assumption ID')
    distance=quantity(distance_km)
    if distance<=0:raise ValueError('Travel distance must be positive')
    with localcontext() as ctx:
        ctx.prec=40
        blend=distance/Decimal('13.31')
        ethanol=blend*Decimal('0.10')
        gasoline=blend*Decimal('0.90')
        batch=ethanol/Decimal('10.17')
        def fmt(x):return format(x,'f')
        return {
            'scope':'PARTIAL_STUDY_FOREGROUND_MATERIAL_BASIS',
            'assumption_id':assumption_id,
            'assumptions':['E10 interpreted as0.10ethanol+0.90gasoline volume;no blend-volume contraction adjustment','Study99.5percent ethanol output volume used as its fuel-blending feed;no pureethanol/density correction','Figure1batch linear scaling;not an independently measured supply chain'],
            'distance_km':distance_km,
            'gasoline_equivalent_litres':fmt(distance/Decimal('13.46')),
            'E10_litres':fmt(blend),'ethanol_blending_feed_litres':fmt(ethanol),
            'gasoline_blending_feed_litres':fmt(gasoline),
            'physical_batch_scale_per_tonne_cane':fmt(batch),
            'physical_flows':[
                {'name':name,'amount':fmt(Decimal(value)*batch),'unit':unit,'basis_role':role}
                for name,value,unit,role in [
                    ('cane_stalk','1000','kg','physical_input_before_allocation'),
                    ('molasses','45.2','kg','intermediate_not_additional_final_product'),
                    ('sugar','103.6','kg','co_product'),
                    ('bagasse','247','kg','internal_energy_material_not_avoided_credit'),
                    ('cane_trash','200','kg','residue'),
                    ('stillage','106.8','L','wastewater_not_elementary_discharge')]],
            'economic_allocation':{'sugar':'0.896','molasses':'0.104','applied_to_physical_flows':False,'applies_to':'eligible upstream burdens only;not yet supplied'},
            'mass_balance_closed':False,'elementary_emissions_complete':False,
            'all_background_inputs_thai_verified':False,
            'CO2e_total':None,'full_lifecycle_lci':False,'existing_model_changed':False}
