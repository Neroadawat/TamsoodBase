"""Typed candidate from visually reviewed scanned Thai GSP tables, not OCR."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def build():
    raw=ROOT/'data/raw/thai-gas-gsp-2007'
    meta=json.loads((raw/'manifest.json').read_text(encoding='utf8'))
    for name,digest in meta['file_sha256'].items():
        if hashlib.sha256((raw/(name+'.pdf')).read_bytes()).hexdigest()!=digest:
            raise ValueError('Chapter source hash changed')
    transcription=raw/'transcription.json'
    if hashlib.sha256(transcription.read_bytes()).hexdigest()!=meta['transcription_sha256']:
        raise ValueError('Reviewed transcription changed; visual review required')
    source=json.loads(transcription.read_text(encoding='utf8'))
    rows=source['rows']
    if len(rows)!=42 or len({r['id'] for r in rows})!=42:
        raise ValueError('Expected 42 unique table cells')
    result=[]
    for row in rows:
        item=dict(row);value=row['raw_value']
        if value=='-':
            amount=None;status='HOLD_DASH_NOT_ZERO'
        else:
            amount=Decimal(value)
            if not amount.is_finite() or amount<0:raise ValueError('Invalid source amount')
            amount=format(amount,'f');status='VISUALLY_TRANSCRIBED_SOURCE_CANDIDATE'
        item.update(amount=amount,status=status,reference_amount='1',reference_unit='kg product',
          reference_product_status='SOURCE_EACH_PRODUCT_MASS_ALLOCATION_NOT_A_SELECTED_SINGLE_FUEL',
          allocation='MASS_BASED_APPLIED_IN_SOURCE_DO_NOT_REAPPLY',
          geography='Map Ta Phut, Rayong, Thailand',publication_year=2007,measurement_period=None,
          boundary='GATE_TO_GATE_GAS_SEPARATION',source_url=meta['canonical_url'],doi=meta['doi'],
          source_sha256=meta['file_sha256']['ch4'],global_flow_id=None,
          model_applied=False,full_lifecycle_inventory=False,rights_status='NOT_CLEARED')
        result.append(item)
    co2=[r for r in result if r['flow']=='CO2']
    if any(r['unit']!='mg' or r['compartment']!='air' for r in co2):
        raise ValueError('CO2 unit/compartment mismatch')
    return {'domain':'Petroleum, Natural Gas & Fuels','scope':'SCANNED_GSP_GATE_TO_GATE_REVIEW',
       'observations':result,'source_hashes':meta['file_sha256'],
       'transcription_sha256':meta['transcription_sha256'],
       'review_method':'MANUAL_VISUAL_NOT_OCR_OR_INDEPENDENT_DOUBLE_REVIEW',
       'source_issues':source['notes'],
       'comparison':{'GSP3_CO2_detailed_mg':'62600','GSP3_CO2_summary_mg':'63000',
          'summary_match':'DISPLAY_PRECISION_DIFFERENCE_RETAINED',
          'GSP1_capacity_ch3':'390','GSP1_capacity_ch4':'350','capacity_unit':'MMSCFD',
          'capacity_status':'UNRESOLVED_SOURCE_CONFLICT'},
       'missing_for_full_lifecycle':['extraction','transmission','distribution','fuel_use',
         'complete_waste_treatment','provider_origin','single_reference_product_mapping'],
       'counts':{'source_cells':42,'numeric_cells':41,'held_dashes':1},
       'production_changed':False,'full_lifecycle_inventory':False}


def main():
    result=build();out=ROOT/'build/thai-gsp-review';out.mkdir(parents=True,exist_ok=True)
    body=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    (out/'review.json').write_text(body,encoding='utf8')
    restored=json.loads((out/'review.json').read_text(encoding='utf8'))
    if restored!=result:raise ValueError('Roundtrip changed source payloads')
    evidence={k:v for k,v in result.items() if k!='observations'}
    evidence['roundtrip_all_fields_equal']=True
    (ROOT/'evidence/thai-gsp-review.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
