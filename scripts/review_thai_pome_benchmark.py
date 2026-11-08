"""Review measured Thai treatment context and a separate reported WTW benchmark."""
import hashlib
import json
import logging
from decimal import Decimal
from pathlib import Path
import re
from pypdf import PdfReader
import pdfplumber

ROOT=Path(__file__).resolve().parents[1]


def checked_pages(folder, page):
    root=ROOT/'data/raw'/folder
    meta=json.loads((root/'manifest.json').read_text(encoding='utf8'))
    pdf=root/'source.pdf'
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=meta['sha256']:
        raise ValueError('Source hash mismatch')
    logging.getLogger('pypdf').setLevel(logging.ERROR)
    text=PdfReader(pdf).pages[page-1].extract_text()
    with pdfplumber.open(pdf) as other:second=other.pages[page-1].extract_text()
    return meta,[re.sub(r'\s+',' ',s) for s in (text,second)]


def review():
    pome,texts=checked_pages('thai-pome-2011',3)
    matrix=[['14','2.43','70','95','70.03'],['10','5.09','68','95','69.29'],
            ['7','6.50','65','96','66.83'],['6.5','8.70','65','93','66.41']]
    for row in matrix:
        if not all(' '.join(row) in t for t in texts):raise ValueError('Table2 point mismatch')
    # These are generated biogas/output conversion ratios, never fugitive emissions.
    for t in texts:
        if not re.search(r'20\s*m3\s*of\s*gas\s*from\s*1\s*m3',t):
            raise ValueError('Biogas basis mismatch')
        if not re.search(r'2\.5\s*kWh/m3',t):raise ValueError('Generation ratio mismatch')
    benchmark,bt=checked_pages('nstda-wtw-2021',45)
    patterns=[r'WtT of B100FAME\s*=\s*1\.7096',r'TtW of B100\s*=\s*0\.1550',r'WtW of B100FAME\s*=\s*1\.8646']
    for pattern in patterns:
        if not all(re.search(pattern,t) for t in bt):raise ValueError('WTW benchmark mismatch')
    summed=Decimal('1.7096')+Decimal('0.1550')
    if summed!=Decimal('1.8646'):raise ValueError('Reported sum differs')
    return {'treatment':{'site':'Asian Palm Oil Co., Ltd., Krabi, Thailand','publication_year':2011,
      'source_url':pome['url'],'source_sha256':pome['sha256'],'pdf_page':3,'printed_page':135,
      'table':'2','columns':['HRT_days','OLR_kgCOD_per_m3_day','COD_removal_percent','BOD5_removal_percent','CH4_in_biogas_percent'],
      'operating_points':matrix,'biogas_generation':{'amount':'20','unit':'m3 biogas/m3 wastewater'},
      'electricity_per_biogas':{'amount':'2.5','unit':'kWh/m3 biogas'},
      'derived_gross_electricity_per_wastewater':{'amount':'50.0','unit':'kWh/m3 wastewater',
        'derivation':'20 * 2.5','status':'ARITHMETIC_SCREENING_NOT_NET_EXPORT_OR_CREDIT'},
      'fugitive_CH4_emission':None,'CH4_volume_conditions':None,'net_electricity_export_per_m3':None,
      'wastewater_per_FAME_reference_unit':None,'auxiliary_energy_and_reagents_complete':False,
      'foreign_default_baseline_parameters_applied':False,'linked_to_FAME':False,'rights_status':'NOT_CLEARED'},
      'benchmark':{'source_url':benchmark['url'],'source_sha256':benchmark['sha256'],
        'pdf_page':45,'printed_page':37,'footnote':'11','fuel':'B100 FAME',
        'unit':'kgCO2eq/litre','WTT':'1.7096','TTW':'0.1550','WTW':'1.8646',
        'sum_verified':True,'kind':'REPORTED_CHARACTERIZED_RESULT_NOT_ELEMENTARY_LCI',
        'all_inputs_Thai_origin_verified':False,'applied_as_factor':False,'rights_status':'NOT_CLEARED'},
      'validation':{'two_extractors_agree':True,'visual_pages_reviewed':True},
      'production_changed':False,'full_lifecycle_inventory':False}


def main():
    result=review();out=ROOT/'build/thai-pome-benchmark-review';out.mkdir(parents=True,exist_ok=True)
    body=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    (out/'review.json').write_text(body,encoding='utf8')
    (ROOT/'evidence/thai-pome-benchmark-review.json').write_text(body,encoding='utf8')
    print('4 operating points + 2 generation ratios + separate WTW benchmark verified; no fugitive emissions invented')


if __name__=='__main__':main()
