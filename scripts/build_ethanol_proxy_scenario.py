import json,hashlib,re
from pathlib import Path
from src.ethanol_proxy_scenario import scenario
ROOT=Path(__file__).resolve().parents[1]
def reviewed_inputs(root=ROOT):
    manifest_path = root / 'evidence/ethanol-reviewed-inputs.json'
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get('approval_scope') != 'INTERNAL_SOURCE_REVIEW':
        raise ValueError('Expected internal source review manifest')
    paths = ('evidence/dede-molasses-balance.json', 'evidence/dede-ethanol-survey-review.json', 'build/transport-sensitivity/report.json')
    inputs = []
    for path in paths:
        data = (root / path).read_bytes()
        if hashlib.sha256(data).hexdigest() != manifest['sha256'].get(path):
            raise ValueError(f'Reviewed input hash mismatch: {path}')
        inputs.append(json.loads(data))
    return manifest, *inputs

def main():
 manifest, mass, energy, transport = reviewed_inputs(ROOT)
 sha = hashlib.sha256((ROOT/'data/raw/dede-bioethanol1/source.pdf').read_bytes()).hexdigest()
 if not mass['sha256'] == energy['sha256'] == sha:
     raise ValueError('DEDE PDF hash mismatch')
 f = next(f for f in transport['factors'] if f['id']=='TGO-CFP-232-April2026')
 if f['activity_unit'] != 'tkm' or hashlib.sha256((ROOT/'data/raw/tgo-cfp-2026-11-03/page.html').read_bytes()).hexdigest() != f['source_sha256']:
     raise ValueError('Invalid freight source or unit')
 basis = re.fullmatch(r'(\d+(?:\.\d+)?)L/day fuel ethanol;\d+(?:\.\d+)?t/day', mass['reference_output'])
 if basis is None:
     raise ValueError('Unsupported production reference output')
 report={'review_date':'2026-11-07','input_review':manifest,'code_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/build_ethanol_proxy_scenario.py','src/ethanol_proxy_scenario.py','src/transport_scenario.py','src/thai_carbon.py']},'scope':'EXPLICIT_THAI_SECONDARY_DATA_SCENARIO','method_support':'evidence/ethanol-proxy-method-support.json','mass_source':{'source_url':mass['source_url'],'sha256':sha,'locator':mass['source_figure']},'energy_source':{'source_url':energy['source_url'],'sha256':sha,'locator':'Table2/PDF11/printed10/molasses'},'factor':f,'scenarios':[scenario('1',energy['observations'],f,distance_km=d,assumption_id='TEAM_PROXY_DEDE_MOLASSES_ENERGY_AND_HYPOTHETICAL_EACH_LEG_'+d+'KM',mass_rows=mass['observations'],production_L_day=basis[1],energy_basis_L_day=energy['reference_output_L_per_day']) for d in ['10','50','100']],'data_quality':{'geography':'Thai survey/Thai reported truck factor;allfactorbackgroundThai notverified','time':'DEDEmeasurementyearunknown;EFversionApril2026;notcurrentThaiaverage','technology':'molassesforeground plus surveyproxy;truck10wheel16tB5/75percentload;notobservedshipment','completeness':'energyquantitiesandtwofreightlegs only;noGHGfullsum','reliability':'sourceverifiedphysicalfigure/survey;scenariochoicesnotindependentmeasurements'},'limitations':['perLethanolnotperkmvehicle','noallocation appliedtoallburdens','steamquantitynotsteamenergy','rangeendpointsnotpairedplants','emptyreturnandfactorboundaryunverified','noCH4/N2O/fossilbiogenicusebridge','noautomaticbaselineorproductionreplacement'],'production_changed':False,'CO2e_total':None}
 out=ROOT/'build/ethanol-proxy-scenario';out.mkdir(parents=True,exist_ok=True);(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'evidence/ethanol-proxy-scenario.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for r in report['scenarios']:print(r['freight'][0]['distance_km'],[(f['leg'],f['screening']['result']) for f in r['freight']])
if __name__=='__main__':main()
