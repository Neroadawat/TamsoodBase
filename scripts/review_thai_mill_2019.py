"""Review all 90 cells of six Thai mills, preserving plant identities and basis."""
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
FLOWS = ['FFB', 'Kaolin', 'Water', 'Electricity (grid)', 'Electricity (boiler)',
         'Electricity (biogas)', 'Steam', 'Crude palm oil', 'Palm kernel', 'EFB',
         'Fiber', 'Shell', 'Decanter cake', 'Treated POME', 'Electricity']
UNITS = ['kg', 'kg', 'm3', 'kWh', 'kWh', 'kWh', 'kg', 'kg', 'kg', 'kg',
         'kg', 'kg', 'kg', 'm3', 'kWh']
# Column-major transcription checked against the full rendered PDF page11/TableS2.
REVIEWED = [
 '6930 11 1.04 26 105 35 4260 1000 129 1390 0 277 208 3.1 89',
 '6290 15 4.7 10 85 21 2940 1000 342 1109 0 377 241 3.9 681',
 '5950 10 2.8 24 75 34 3640 1000 297 1190 38 383 237 4.3 109',
 '5940 11 4.4 10 91 9 2990 1000 300 1200 0 337 212 4.9 206',
 '6100 10 2.4 13 72 0 2430 1000 352 1350 0 345 305 2.8 106',
 '5650 1.3 0.9 55 80 0 2470 1000 290 1310 0 74 169 2.8 5']


def build():
    raw = ROOT/'data/raw/thai-palm-jsee-2019'
    meta = json.loads((raw/'manifest.json').read_text(encoding='utf8'))
    pdf = raw/'source.pdf'
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != meta['sha256']:
        raise ValueError('Source PDF changed; review required')
    pages = PdfReader(pdf).pages
    text = pages[10].extract_text().split('Table S2.')[1]
    first = [s.strip() for s in text.splitlines()
             if re.fullmatch(r'\d+(?:\.\d+)?', s.strip())]
    with pdfplumber.open(pdf) as doc:
        table = doc.pages[10].extract_tables()[0]
    if table[0] != ['Input/output', 'Units'] + [f'Mill {i}' for i in range(1,7)]:
        raise ValueError('Table headers changed')
    label_lines = table[1][0].splitlines()
    labels = [s for s in label_lines if s not in ('Input','Materials','Energy','Output')]
    if labels != FLOWS or table[1][1].splitlines() != UNITS:
        raise ValueError('Flow labels or units changed')
    columns = [cell.splitlines() for cell in table[1][2:]]
    expected = [s.split() for s in REVIEWED]
    second = [v for col in columns for v in col]
    if columns != expected or first != second or len(first) != 90:
        raise ValueError('All-cell two-extractor/visual transcription mismatch')
    observations = []
    for plant, values in enumerate(columns, 1):
        for index, (flow, unit, value) in enumerate(zip(FLOWS, UNITS, values), 1):
            number = Decimal(value)
            if not number.is_finite() or number < 0:
                raise ValueError('Invalid source amount')
            internal = flow in ('Electricity (boiler)', 'Electricity (biogas)', 'Steam')
            role = ('INTERNAL_ENERGY' if internal else 'TECHNOSPHERE_INPUT') if index <= 7 else (
                'REFERENCE_PRODUCT' if flow == 'Crude palm oil' else
                'TREATED_WASTEWATER_OUTPUT' if flow == 'Treated POME' else 'REPORTED_OUTPUT')
            observations.append({'id':f'TH-MILL2019-{plant}-{index}', 'mill':f'Mill {plant}',
                'flow':flow, 'raw_value':value, 'amount':format(number,'f'), 'unit':unit,
                'direction':'INPUT' if index <= 7 else 'OUTPUT', 'role':role,
                'reference_amount':'1000', 'reference_unit':'kg', 'reference_product':'CPO',
                'publication_year':2019, 'measurement_period':None,
                'geography':'Thailand; six surveyed mills, not national average',
                'pdf_page':11, 'table':'S2', 'source_data_row':index,
                'source_column':plant+2, 'source_url':meta['source_url'],
                'source_sha256':meta['sha256'], 'allocation_status':'NOT_APPLIED_BY_PROJECT',
                'elementary_flow':False, 'model_applied':False, 'rights_status':'NOT_CLEARED'})
    return {'study':'THAI_PALM_BIOREFINERY_2019', 'scope':'ALTERNATIVE_MILL_FOREGROUND_CANDIDATE',
        'observations':observations, 'source_sha256':meta['sha256'],
        'review':{'numeric_cells':90,'two_extractors_all_cells_equal':True,
                 'all_flow_labels_units_equal':True,'visual_page':11,
                 'visual_review':'AI_ASSISTED_SINGLE_REVIEW_NOT_INDEPENDENT_DOUBLE_REVIEW'},
        'FFB_per_CPO_by_mill':{f'Mill {i}':format(Decimal(c[0])/Decimal(c[7]),'f')
                               for i,c in enumerate(columns,1)},
        'compatibility':{'linked_to_2020':False,'averaged_across_plants':False,
            'paper_background_includes_foreign_databases_and_defaults':True,
            'inventory_emissions_not_in_table_S2':True,
            'treated_POME_is_not_untreated_input_or_elementary_emission':True,
            'internal_energy_not_additional_external_provider':True,
            'source_specific_allocation_and_provider_links_pending':True},
        'full_lifecycle_inventory':False, 'production_changed':False}


def main():
    result = build()
    folder = ROOT/'build/thai-mill-2019-review';folder.mkdir(parents=True,exist_ok=True)
    body = json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    path = folder/'review.json';path.write_text(body,encoding='utf8')
    if json.loads(path.read_text(encoding='utf8')) != result:
        raise ValueError('JSON roundtrip changed source fields')
    evidence = {k:v for k,v in result.items() if k!='observations'}
    evidence['all_fields_roundtrip_equal'] = True
    (ROOT/'evidence/thai-mill-2019-review.json').write_text(
        json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result['review']))


if __name__ == '__main__':main()
