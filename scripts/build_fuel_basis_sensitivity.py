"""Reproducible Thai fuel-basis sensitivity. No foreground summation or tailpipe substitution."""
from pathlib import Path
from decimal import Decimal,localcontext
import hashlib,json
from src.fuel_basis_scenario import fuel_basis
from src.thai_carbon import screen_activity
ROOT=Path(__file__).resolve().parents[1]
def build():
    props=json.loads((ROOT/'build/thai-b100-properties-2021/report.json').read_text(encoding='utf-8'))
    pdf=ROOT/'data/raw/thai-pnu-b100-2021/source.pdf'
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=props['source_sha256']:raise ValueError('Property source changed')
    values={row['property']:row for row in props['observations']}
    if values['LHV']['source_unit']!='Mj' or values['Density']['source_unit']!='kg/m3':raise ValueError('Unexpected source unit; review before conversion')
    basis=fuel_basis('1000',values['LHV']['amount'],values['Density']['amount'],assumption_id='TEAM_METHOD_2026_11_06_LHV_MJ_KG_INTERPRETATION',lhv_interpreted_mj_per_kg=True)
    factor=json.loads((ROOT/'evidence/thai-carbon-factor-review.json').read_text(encoding='utf-8'))
    if factor['automatically_combined_with_foreground'] is not False or factor['activity_unit']!='kg':raise ValueError('Unsafe factor contract')
    cases=[]
    for name,mass in [('REPORTED_2020_TABLE4_FUEL_MASS','26.3'),('CONDITIONAL_2021_FUEL_PROPERTY_BASIS',basis['mass_kg'])]:
        result=screen_activity(mass,'kg',factor)
        cases.append({'id':name,'activity_mass_kg':mass,'screening':result})
    with localcontext() as ctx:
        ctx.prec=80;a,b=[Decimal(c['screening']['result']) for c in cases]
        difference=b-a;percent=difference/a*100
    report={'scope':'THAI_REPORTED_FACTOR_FUEL_BASIS_SENSITIVITY_NOT_COMPARATIVE_CFP','assumption':basis,'factor_id':factor['id'],'cases':cases,'difference_kgCO2e':str(difference),'difference_percent':str(percent),'interpretation':'Difference arises from alternative fuel-property/basis assumptions; NOT demonstrated carbon saving or measured engine improvement','factor_system_boundary':factor['boundary_status'],'stage_allocation':'NOT_ASSIGNED_NO_BOUNDARY_GUESS','combined_with_foreground':False,'tailpipe_CO2_kg':None,'full_lifecycle_CO2e_total':None,'full_lifecycle_inventory':False,'strict_all_inputs_thai_verified':False,'rights_status':'INTERNAL_REVIEW_NOT_CLEARED_FOR_REDISTRIBUTION','existing_model_changed':False,'source_inputs':{'properties_pdf_sha256':props['source_sha256'],'factor_source_sha256':factor['source_sha256'],'factor_review_file_sha256':hashlib.sha256((ROOT/'evidence/thai-carbon-factor-review.json').read_bytes()).hexdigest()}}
    out=ROOT/'build/fuel-basis-sensitivity';out.mkdir(exist_ok=True);(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
if __name__=='__main__':
    r=build();(ROOT/'evidence/fuel-basis-sensitivity.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'baseline_screen_kgCO2e':r['cases'][0]['screening']['result'],'conditional_screen_kgCO2e':r['cases'][1]['screening']['result'],'difference_percent':r['difference_percent'],'full_total':None}))
