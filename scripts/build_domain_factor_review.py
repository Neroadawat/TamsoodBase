"""Retained TGO factors relevant to Petroleum, Natural Gas & Fuels.

Reference factors remain separate from elementary inventories and applied models.
"""
import hashlib
import json
from pathlib import Path
from decimal import Decimal
from scripts.screen_thai_carbon import FactorRows

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={28:('kg','1.0017'),29:('kg','1.1254'),30:('kg','1.1142'),
31:('kg','1.1083'),32:('kg','1.1366'),33:('kg','0.7238'),34:('m3','0.5534'),
35:('kg','0.9458'),36:('kg','0.2941'),37:('kg','0.4304'),38:('kg','0.4006'),
39:('kg','0.325'),40:('kg','0.3708'),41:('kg','0.3503'),42:('kg','0.2374'),307:('kg','1.0372')}


def build():
    raw=ROOT/'data/raw/tgo-cfp-2026-11-03'
    meta=json.loads((raw/'manifest.json').read_text(encoding='utf8'))
    body=(raw/'page.html').read_bytes()
    if hashlib.sha256(body).hexdigest()!=meta['sha256']:raise ValueError('Source changed')
    parser=FactorRows();parser.feed(body.decode('utf8'));selected={}
    for row in parser.rows:
        cells=row[-7:]
        if len(cells)!=7 or not cells[0].rstrip('.').isdigit():continue
        number=int(cells[0].rstrip('.'))
        if number not in EXPECTED:continue
        if number in selected:raise ValueError('Duplicate factor identity')
        if tuple(cells[3:5])!=EXPECTED[number]:raise ValueError('Unreviewed amount or unit')
        if not cells[5].startswith('Thai National LCI Database') or cells[6]!='Update_April2026':
            raise ValueError('Source/version changed')
        if not Decimal(cells[4]).is_finite():raise ValueError('Invalid factor')
        if 'IPCC 2013 GWP 100a V1.03' not in cells[2]:raise ValueError('Unreviewed method')
        imported=number in (33,34,35)
        selected[number]={'id':f'TGO-CFP-{number}-April2026','row_number':number,
          'source_cells':cells,'name':cells[1],'description':cells[2],
          'activity_unit':cells[3],'value':cells[4],'result_unit':'kgCO2e',
          'scope_class':'CHARACTERIZED_PRODUCT_FACTOR_NOT_ELEMENTARY_LCI',
          'source_url':meta['url'],'source_sha256':meta['sha256'],
          'source_snapshot_date':'2026-11-03','review_date':'2026-11-04',
          'process_family':'GAS_SEPARATION' if number<=32 else 'FUEL_SUPPLY_MIX' if imported else 'BIOFUEL' if number==307 else 'REFINING',
          'reported_geography':'Thai National LCI dataset',
          'explicit_imported_mix':imported,'strict_all_inputs_thai_verified':False,
          'admission_status':'HOLD_EXPLICIT_IMPORTED_MIX' if imported else 'REFERENCE_ONLY_BACKGROUND_ORIGIN_UNRESOLVED',
          'role':'PRODUCT_SUPPLY','direct_emission_factor':False,
          'model_applied':False,'boundary_verified_for_combination':False,
          'rights_status':'NOT_CLEARED_FOR_REDISTRIBUTION'}
    if set(selected)!=set(EXPECTED):raise ValueError('Required domain factor missing')
    return {'domain':'Petroleum, Natural Gas & Fuels','factors':list(selected.values()),
       'full_lifecycle_inventory':False,'production_changed':False,
       'limitation':'Thai reported product factors; underlying supply origin/boundary not fully audited. No imported mix admitted under strict Thai-only policy.'}


def main():
    result=build();out=ROOT/'build/domain-factor-review';out.mkdir(parents=True,exist_ok=True)
    (out/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    evidence={'domain':result['domain'],'source_factor_rows':len(result['factors']),
      'explicit_imported_mix_holds':[r['row_number'] for r in result['factors'] if r['explicit_imported_mix']],
      'source_sha256':result['factors'][0]['source_sha256'],
      'all_source_cells_retained':True,'model_applied':False,'production_changed':False,'full_lifecycle_inventory':False}
    (ROOT/'evidence/domain-factor-review.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf8')
    print(json.dumps(evidence))


if __name__=='__main__':main()
