"""Compare one manufacturing total with an explicitly revised DEDE publication."""
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def manufacturing_total(sheet):
    if '2024' not in str(sheet['DF1'].value) or 'ktoe' not in str(sheet['DW2'].value):
        raise ValueError('Year/unit changed')
    if str(sheet['A52'].value).strip()!='อุตสาหกรรมการผลิต' or str(sheet['DW52'].value).strip()!='MANUFACTURING':
        raise ValueError('Manufacturing row changed')
    if str(sheet['DT9'].value).strip()!='GRAND TOTAL':
        raise ValueError('Grand-total column changed')
    value=sheet['DT52'].value
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        raise ValueError('Numeric cached total required')
    amount=Decimal(str(value))
    if not amount.is_finite() or amount<0:raise ValueError('Invalid manufacturing total')
    return amount


def main():
    import openpyxl
    folder=ROOT/'data/raw/dede/revised-2024';path=folder/'energy-balance.xlsx'
    meta=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=meta['sha256']:raise ValueError('Revised source snapshot changed')
    workbook=openpyxl.load_workbook(path,data_only=True,read_only=True)
    try:value=manufacturing_total(workbook['ktoe'])
    finally:workbook.close()
    original=json.loads((ROOT/'evidence/nso-dede-comparison.json').read_text(encoding='utf-8'))
    rows=json.loads((ROOT/'build/nso/report.json').read_text(encoding='utf-8'))['rows']
    matches=[r for r in rows if r['observation_id']==original['nso_observation_id'] and r['source_sha256']==original['nso_source_sha256']]
    if len(matches)!=1:raise ValueError('NSO evidence identity changed')
    row=matches[0];delta=Decimal(row['amount'])-value
    result=dict(nso_observation_id=row['observation_id'],year=2024,nso_value=row['amount'],dede_revised_value=str(value),
        difference_nso_minus_revised=str(delta),exact_displayed_value_match=delta==0,unit=row['unit'],
        status='MATCH_REVISED_PUBLICATION' if delta==0 else 'REVISED_PUBLICATION_DIFFERS',
        revised_source_url=meta['url'],revised_source_sha256=digest,catalog_url=meta['catalog_url'],catalog_label=meta['catalog_label'],
        revised_sheet='ktoe',revised_cell='DT52',row_label='MANUFACTURING',column_label='GRAND TOTAL',
        previous_preliminary_value=original['dede_preliminary_value'],previous_difference=original['difference_nso_minus_dede'],
        source_values_changed=False,independent_measurements_verified=0,
        interpretation='NSO matches the displayed total in the separately published revised energy balance. Earlier preliminary report remains different; specific calculation changes are not established.',
        rights_status=meta['rights_status'])
    (ROOT/'evidence/nso-dede-revised-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
