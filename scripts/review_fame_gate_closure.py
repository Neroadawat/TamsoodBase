"""Source-bound decisions for the unfinished Thai FAME study; no burden calculation."""
import hashlib
import json
import unicodedata
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader
import pdfplumber

ROOT=Path(__file__).resolve().parents[1]


def compact(text):
    return ''.join(unicodedata.normalize('NFKC',text).split()).lower()


def checked_passage(path,page,phrase):
    first=PdfReader(path).pages[page-1].extract_text()
    with pdfplumber.open(path) as pdf:
        second=pdf.pages[page-1].extract_text()
    if not all(compact(phrase) in compact(t) for t in (first,second)):
        raise ValueError('Required passage missing from one extractor: '+str(page))
    return {'source_file':str(path.relative_to(ROOT)).replace('\\','/'),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'pdf_page':page,'passage_sha256':hashlib.sha256(phrase.encode()).hexdigest(),
            'verification':'MATCHED_IN_TWO_TEXT_EXTRACTORS_NOT_NEW_VISUAL_REVIEW'}


def build():
    mdpi=ROOT/'data/raw/mdpi-9415/pdf-v3/source.pdf'
    report=ROOT/'data/raw/compete-thailand-report/source.pdf'
    passages={
        'allocation_method':checked_passage(mdpi,4,'The economic allocation procedure was applied to share the environmental burdens if more than one product was produced at any stage.'),
        'fame_allocation':checked_passage(mdpi,7,'burdens being shared 70% for FAME and 30% for crude glycerine'),
        'fuel_mass_prose':checked_passage(mdpi,2,'26.27, 25.51, 22.71 kg of FAME, H-FAME, and BHD'),
        'fuel_mass_table':checked_passage(mdpi,7,'FAME 26.3 kg'),
        'background':checked_passage(mdpi,4,'Most of the databases were selected from ecoinvent 3'),
        'new_report_scope':checked_passage(report,11,'the study was divided into 3 stages: oil palm plantation, palm oil production and transesterification into biodiesel'),
        'new_report_use_exclusion':checked_passage(report,13,'emissions to the air when biodiesel is combusted in diesel engines for transportation which will be considered later')}
    return {'date':'2026-11-05','scope':'SOURCE_BOUND_GATE_DECISIONS_NOT_COMPLETE_LCI',
        'source_evidence':passages,
        'decisions':[
            {'id':'allocation','status':'BLOCKED_TABLE_BASIS_UNKNOWN','method_confirmed':'ECONOMIC',
             'source_reported_factor':{'FAME':'0.70','glycerine':'0.30'},'factor_applied':False,
             'reason':'Method/factors are explicit; gross-versus-already-allocated table status is not established. Do not apply factors twice or transfer them to 2019 mills.',
             'required_evidence':'Calculation workbook or explicit table-specific gross/allocated basis, with co-product and upstream burden treatment.'},
            {'id':'compatibility','status':'NOT_ACCEPTED_FOR_BURDEN_LINKING','activity_scenario_allowed':True,
             'reason':'2019/2020 are publication years, not a proven common measurement period or actual supply chain.',
             'required_evidence':'Per-link product specification, technology, operating period, geography, allocation and representativeness decisions; hypothetical linkage must stay labelled.'},
            {'id':'transport','status':'BLOCKED_PROVIDER_AND_LEGS_MISSING','factor_applied':False,
             'reason':'Estimated 5km FFB leg is not a vehicle/load/return/diesel inventory and may overlap existing diesel inputs.',
             'required_evidence':'All scoped legs, load/empty return convention, compatible Thai vehicle inventory and no-double-count boundary.'},
            {'id':'use','status':'BLOCKED_LITRE_ENERGY_AND_GAS_BASIS','factor_applied':False,
             'reason':'2013 litre-based pickup emissions have no verified compatible density/LHV bridge; CH4/N2O and biogenic/fossil accounting incomplete.',
             'required_evidence':'Matched B100 fuel properties and engine/use inventory; gas identity, compartments, fossil/biogenic carbon and measurement period.'},
            {'id':'waste','status':'BLOCKED_TREATMENT_BOUNDARY','factor_applied':False,
             'reason':'Treated POME cannot be sent to a second raw-POME treatment; methane generation is not measured leakage.',
             'required_evidence':'Raw/treated stream connectivity, treatment already included, actual discharge/leakage/flare and energy-credit boundaries.'},
            {'id':'background','status':'BLOCKED_THAI_PROVIDER_EXCHANGES','factor_applied':False,
             'reason':'Published study uses ecoinvent; its result is not proof of a Thai-only recreated supply chain.',
             'required_evidence':'Compatible Thai electricity/chemicals/fuel process exchanges and usage rights, distinct from aggregate carbon factors.'}],
        'fuel_mass_precision_check':{'prose_kg':'26.27','table_kg':'26.3',
             'table_minus_prose_kg':str(Decimal('26.3')-Decimal('26.27')),
             'interpretation':'CONSISTENT_WITH_ONE_DECIMAL_DISPLAY_ROUNDING_NOT_A_LITRE_CONVERSION',
             'source_value_rewritten':False},
        'new_source_screen':{'source':'COMPETE Thailand report, section3.1, PDF11–13',
             'status':'PRODUCTION_CONTEXT_ONLY_NOT_GAP_CLOSING','rights_status':'NOT_CLEARED',
             'numeric_rows_imported':0,'reason':'Three-stage production scope and explicitly deferred combustion; ranges and mixed basis not copied into 2020 scenarios.'},
        'full_lifecycle_inventory':False,'CO2e_total':None,'new_burden_links_applied':0}


def main():
    result=build()
    path=ROOT/'evidence/fame-gate-closure-review.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'decisions':len(result['decisions']),'source_passages':len(result['source_evidence']),
                      'new_burden_links_applied':0,'CO2e_total':None}))


if __name__=='__main__':main()
