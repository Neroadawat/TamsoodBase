"""Explicit mixed-vintage Thai physical-activity scenario, NOT allocated LCI."""
import hashlib
import json
from decimal import Decimal, localcontext
from pathlib import Path
from scripts.review_thai_mill_2019 import build as review_mills
from pypdf import PdfReader
import pdfplumber

ROOT=Path(__file__).resolve().parents[1]


def unique(rows,flow,direction):
    matches=[r for r in rows if r['flow']==flow and r['direction']==direction]
    if len(matches)!=1 or matches[0]['unit']!='kg':
        raise ValueError('Unique mass transfer required: '+flow)
    amount=Decimal(matches[0]['amount'])
    if not amount.is_finite() or amount<=0:
        raise ValueError('Positive transfer required')
    return matches[0]


def review_ffb_distance():
    path=ROOT/'data/raw/thai-palm-jsee-2019/source.pdf'
    phrase='distance between oil palm plantations and mills was estimated to be about 5 km.'
    first=' '.join(PdfReader(path).pages[2].extract_text().split())
    with pdfplumber.open(path) as pdf:
        page=pdf.pages[2]
        second=' '.join(page.crop((300,600,page.width,page.height)).extract_text().split())
    if phrase not in first or phrase not in second:
        raise ValueError('Estimated FFB distance source text changed')
    return {'reported_distance_km':'5','evidence_class':'SOURCE_REPORTED_ESTIMATE',
        'source_url':'https://www.jseejournal.com/media/219/attachment/Life%20cycle%20assessment%20pp.%2065-73.pdf',
        'pdf_page':3,'printed_page':67,'section':'2.2.2',
        'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'distance_return_convention':'NOT_EXPLICIT_IN_SELECTED_PASSAGE',
        'visual_review':'tmp/pdfs/thai-palm2019-page3.png'}


def build(combined,mills,mill='Mill 1',ffb_distance=None):
    if mill not in [f'Mill {i}' for i in range(1,7)]:raise ValueError('Unknown mill')
    rows=[m['source'] for m in combined['mappings']]
    components={p:[r for r in rows if r['process']==p] for p in ['FFB','RBDPO','FAME']}
    components['CPO']=[dict(r)
                        for r in mills['observations'] if r['mill']==mill]
    if [len(components[p]) for p in ['FFB','CPO','RBDPO','FAME']] != [19,15,11,10]:
        raise ValueError('Unexpected component membership')
    bases={'FFB':('1000','kg'),'CPO':('1000','kg'),
           'RBDPO':('1000','kg'),'FAME':('1000','MJ fuel')}
    for process,items in components.items():
        if any((r['reference_amount'],r['reference_unit'])!=bases[process] for r in items):
            raise ValueError('Reference basis changed')
    # Same product labels identify potential transfers, not proven quality/provider equivalence.
    fame_rbd=unique(components['FAME'],'RBDPO','INPUT')
    rbd_output=unique(components['RBDPO'],'RBDPO','OUTPUT')
    rbd_cpo=unique(components['RBDPO'],'CPO','INPUT')
    cpo_output=unique(components['CPO'],'Crude palm oil','OUTPUT')
    cpo_ffb=unique(components['CPO'],'FFB','INPUT')
    ffb_output=unique(components['FFB'],'FFB','OUTPUT')
    with localcontext() as ctx:
        ctx.prec=100
        factors={'FAME':Decimal(1)}
        factors['RBDPO']=Decimal(fame_rbd['amount'])/Decimal(rbd_output['amount'])
        demand_cpo=Decimal(rbd_cpo['amount'])*factors['RBDPO']
        factors['CPO']=demand_cpo/Decimal(cpo_output['amount'])
        demand_ffb=Decimal(cpo_ffb['amount'])*factors['CPO']
        factors['FFB']=demand_ffb/Decimal(ffb_output['amount'])
        scaled=[]
        for process,items in components.items():
            for row in items:
                held=not row.get('unit') or str(row.get('status','')).startswith('HOLD')
                value=Decimal(row['amount'])
                if not value.is_finite() or value<0:raise ValueError('Invalid source quantity')
                scaled.append({'source':dict(row),'component':process,
                    'scale_factor':format(factors[process],'f'),
                    'scaled_amount':None if held else format(value*factors[process],'f'),
                    'status':'HOLD_SOURCE_UNIT' if held else 'SCENARIO_ACTIVITY_SCALED'})
        edges=[]
        for provider,consumer,output,input_row in [
            ('FFB','CPO',ffb_output,cpo_ffb),('CPO','RBDPO',cpo_output,rbd_cpo),
            ('RBDPO','FAME',rbd_output,fame_rbd)]:
            supplied=Decimal(output['amount'])*factors[provider]
            consumed=Decimal(input_row['amount'])*factors[consumer]
            if supplied!=consumed:raise ValueError('Physical transfer imbalance')
            edges.append({'provider':provider,'consumer':consumer,
                'provider_output_id':output.get('observation_id',output.get('id')),
                'consumer_input_id':input_row.get('observation_id',input_row.get('id')),
                'supplied_kg':format(supplied,'f'),'consumed_kg':format(consumed,'f'),
                'balance_equal':True,'compatibility':'PRODUCT_LABEL_AND_MASS_ONLY_SCENARIO',
                'burden_link_applied':False})
    transport=[{'id':leg,'distance_km':None,'loaded_tkm':None,'empty_return':None,
                'provider':None,'status':'MISSING'} for leg in
        ['FFB_TO_MILL','CPO_TO_REFINERY','RBDPO_TO_FAME','FAME_TO_USER']]
    if ffb_distance:
        if ffb_distance['source_sha256']!=mills['source_sha256'] or ffb_distance['reported_distance_km']!='5':
            raise ValueError('Unreviewed transport distance')
        transport[0].update(distance_km='5',loaded_tkm=format(demand_ffb*Decimal('0.005'),'f'),
            status='SCENARIO_LOADED_LEG_ACTIVITY_ONLY',source=dict(ffb_distance),
            assumption='Apply reported between-site estimate once to the loaded leg; return/loading/fuel/provider remain unresolved.',
            emissions_applied=False)
    return {'scenario_id':'THAI_FAME_ACTIVITY_'+mill.replace(' ','').upper(),
        'result_type':'GROSS_PHYSICAL_ACTIVITY_SCENARIO_NOT_ALLOCATED_ENVIRONMENTAL_LCI',
        'selection':{'mill':mill,'reason':('Stable first source-column baseline.' if mill=='Mill 1' else 'Alternative source-column scenario, not baseline.')+' All six plants retained; not selected for lowest burden or national representativeness.',
                     'national_average':False},
        'demand_basis':{'amount':'1000','unit':'MJ fuel','source_doi':'10.3390/su12229415'},
        'physical_demand_kg':{'RBDPO':fame_rbd['amount'],'CPO':format(demand_cpo,'f'),
                             'FFB':format(demand_ffb,'f')},
        'component_scale_factors':{k:format(v,'f') for k,v in factors.items()},
        'rows':scaled,'physical_transfer_candidates':edges,
        'transport_legs':transport,
        'allocation':{'status':'UNRESOLVED_NOT_APPLIED','CPO2020_reported_factor':'0.92',
            'FAME2020_reported_factor':'0.70','CPO2019_method':'SCENARIO_SYSTEM_EXPANSION_IN_SOURCE',
            'reason':'Do not transfer 2020 CPO allocation to a different mill or apply economic factors twice.'},
        'open_gates':['mixed_vintage_provider_quality_and_period_compatibility',
            'source_tables_pre_or_post_allocation','missing_cultivation_unit',
            'transport_and_distribution','compatible_use_inventory','waste_treatment_emissions',
            'Thai_background_exchanges_and_rights','elementary_flow_mapping'],
        'treatment_note':'Treated POME retained as output; not reinterpreted as raw POME or gas leakage.',
        'CO2e_total':None,'full_lifecycle_inventory':False,'production_changed':False}


def main():
    path=ROOT/'build/combined-inventory-review/review.json'
    combined=json.loads(path.read_text(encoding='utf8'));mills=review_mills()
    digests={hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in (
        'data/raw/mdpi-9415/pdf-v3/source.pdf','data/raw/mdpi-9415/table4-dom.json')}
    for mapping in combined['mappings']:
        row=mapping['source']
        if (row.get('source_sha256') or row.get('source_snapshot_sha256')) not in digests:
            raise ValueError('2020 source snapshot hash not retained')
    distance=review_ffb_distance()
    cases=[build(combined,mills,f'Mill {i}',distance) for i in range(1,7)]
    folder=ROOT/'build/thai-fame-activity-chain';folder.mkdir(parents=True,exist_ok=True)
    result={'baseline':cases[0],'alternatives':cases[1:],
            'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'mill_pdf_sha256':mills['source_sha256']}
    out=folder/'scenarios.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if json.loads(out.read_text(encoding='utf8'))!=result:raise ValueError('Roundtrip mismatch')
    evidence={'scenario_count':6,'source_rows_per_scenario':55,'all_fields_roundtrip_equal':True,
        'baseline_physical_demand_kg':cases[0]['physical_demand_kg'],
        'all_three_physical_transfer_balances_equal':all(e['balance_equal'] for c in cases for e in c['physical_transfer_candidates']),
        'all_scenarios_CO2e_null':all(c['CO2e_total'] is None for c in cases),
        'reviewed_FFB_distance':distance,
        'baseline_loaded_leg_tkm':cases[0]['transport_legs'][0]['loaded_tkm'],
        'input_sha256':result['input_sha256'],'mill_pdf_sha256':result['mill_pdf_sha256'],
        'scenario_artifact_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
        'full_lifecycle_inventory':False,'production_changed':False}
    (ROOT/'evidence/thai-fame-activity-chain.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf8')
    print(json.dumps(evidence))


if __name__=='__main__':main()
