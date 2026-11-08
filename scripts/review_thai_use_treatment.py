"""Source-local 2013 Thai use emissions and qualitative treatment scenarios.

Never merge into the 2020 FAME route or publish copyrighted source content.
"""
import hashlib
import json
import re
from pathlib import Path
from decimal import Decimal
from pypdf import PdfReader
import pdfplumber

ROOT=Path(__file__).resolve().parents[1]


def normalize(text):
    # pdfplumber puts the two subscript glyphs on the following line.
    # Reattach only this exact visually reviewed sentence, never infer gas IDs.
    text=text.replace('2.78 kg CO , 7.5 g CO, 29 g NO and 1.3 g Particulate Matter (PM)\n2 x',
                      '2.78 kg CO2, 7.5 g CO, 29 g NOx and 1.3 g Particulate Matter (PM)')
    return re.sub(r'\s+',' ',text).replace('ﬁ','fi').replace('ﬂ','fl')


def review():
    folder=ROOT/'data/raw/thai-palm-chapter-2013'
    meta=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
    pdf=folder/'source.pdf'
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=meta['sha256']:
        raise ValueError('Source PDF changed')
    reader=PdfReader(pdf)
    with pdfplumber.open(pdf) as other:
        texts=[normalize(reader.pages[47].extract_text()),normalize(other.pages[47].extract_text())]
        treatment=[normalize(reader.pages[46].extract_text()),normalize(other.pages[46].extract_text())]
    specs=[('CO2','2.78','kg',r'2\.78\s*kg\s*CO\s*2'),
           ('CO','7.5','g',r'7\.5\s*g\s*CO\b'),
           ('NOx','29','g',r'29\s*g\s*NO\s*x'),
           ('PM_UNSPECIFIED','1.3','g',r'1\.3\s*g\s*Particulate Matter')]
    rows=[]
    for gas,amount,unit,pattern in specs:
        if not all(re.search(pattern,t) for t in texts):
            raise ValueError('Source mismatch: '+gas)
        rows.append({'id':'TH2013-USE-'+gas,'source_flow':gas,'amount':amount,'unit':unit,
          'amount_kg':str(Decimal(amount)/(1000 if unit=='g' else 1)),
          'reference_amount':'1','reference_unit':'litre biodiesel','direction':'OUTPUT',
          'compartment':'air','subcompartment':None,'global_flow_id':None,
          'geography':'Thailand study context','vehicle':'pickup / LDDV',
          'evidence_class':'SECONDARY_REPORTED_THAI_TEST','measurement_reference':'Pleanjai 2008, not yet inspected directly',
          'measurement_year':None,'publication_year':2013,'pdf_page':48,'printed_page':36,
          'section':'2.3.5','source_url':meta['canonical_url'],'source_sha256':meta['sha256'],
          'rights_status':'NOT_CLEARED','model_link_status':'UNLINKED_ALTERNATIVE_2013',
          'full_lifecycle_inventory':False})
    required=['Base case','Scenario 1','Scenario 2','Scenario 3','Open ponds','Biogas recovery','Co-composting with POME']
    if not all(all(p.replace(' ','') in t.replace(' ','') for p in required) for t in treatment):
        raise ValueError('Treatment scenario labels differ')
    scenarios=[{'id':'BASE','EFB':'dumped in plantation','POME':'open ponds with CH4 leakage'},
      {'id':'S1','EFB':'dumped in plantation','POME':'biogas recovery'},
      {'id':'S2','EFB':'co-composting with POME','POME':'open ponds'},
      {'id':'S3','EFB':'co-composting with POME','POME':'biogas recovery'}]
    for phrase in ('Scenario1EFBisdumpedintheplantationBiogasrecovery',
                   'Scenario2Co-compostingwithPOMEOpenponds',
                   'Scenario3Co-compostingwithPOMEBiogasrecovery'):
        if not all(phrase in t.replace(' ','') for t in treatment):
            raise ValueError('Treatment scenario relationship mismatch')
    if not all(re.search(r'0\.15\s*kg\s*CO',t) for t in texts):
        raise ValueError('Fossil subset amount mismatch')
    return {'study':'THAI_PALM_BIODIESEL_2013_ALTERNATIVE','use_observations':rows,
      'treatment_scenarios':scenarios,'treatment_locator':{'table':'2.1','pdf_page':47,'printed_page':35},
      'reported_fossil_CO2_subset':{'amount':'0.15','unit':'kg CO2/litre biodiesel',
        'add_to_total_CO2':False,'meaning':'Reported fossil subset estimate; not an additional emission flow'},
      'review':{'two_extractors_agree':True,'visual_pages_previously_reviewed':[47,48],
        'treatment_quantities_available':False,'CH4_N2O_use_inventory_available':False,
        'PM_size_fraction_known':False,'fuel_LHV_density_compatible_with_2020_verified':False,
        'source_all_inputs_thai_verified':False,'source_representativeness':'historical secondary Thai case, not current national average'},
      'source_sha256':meta['sha256'],'full_lifecycle_inventory':False,
      'merged_into_2020':False,'production_changed':False,'rights_status':'NOT_CLEARED'}


def main():
    result=review();out=ROOT/'build/thai-use-treatment-review';out.mkdir(parents=True,exist_ok=True)
    (out/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    evidence={k:v for k,v in result.items() if k!='use_observations'}
    evidence['use_observations_reviewed']=len(result['use_observations'])
    (ROOT/'evidence/thai-use-treatment-review.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('4 use observations and 4 qualitative treatment scenarios reviewed; not linked/published')


if __name__=='__main__':main()
