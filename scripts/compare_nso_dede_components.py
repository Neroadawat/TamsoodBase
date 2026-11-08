"""Compare five fuel subtotals using the already retained revised DEDE workbook."""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
if __package__:
    from .compare_nso_dede_revised import manufacturing_total
else:
    from compare_nso_dede_revised import manufacturing_total

ROOT=Path(__file__).resolve().parents[1]
SPECS=[('ถ่านหิน','W52','W9','TOTAL COAL & ITS PRODUCTS'),
       ('น้ำมันสำเร็จรูป','BO52','BO5','รวมน้ำมันสำเร็จรูปทั้งหมด'),
       ('ก๊าซธรรมชาติ','AG52','AG7','รวมก๊าซธรรมชาติทั้งหมด'),
       ('ไฟฟ้า','BR52','BR9','ELECTRICITY'),
       ('พลังงานหมุนเวียน','DC52','DC9','TOTAL RENEWABLE ENERGY')]
UNIT='10^3 ton of oil equivalent'


def compact(value):return ''.join(str(value).split())


def compare(sheet,rows):
    grand_total=manufacturing_total(sheet)
    comparisons=[];values=[]
    for label,cell,header_cell,header in SPECS:
        if compact(sheet[header_cell].value)!=compact(header):
            raise ValueError('Fuel header changed: '+header_cell)
        matches=[r for r in rows if r['table_id']=='13.10' and r['reference_year']==2024 and r['measure']=='จำนวน' and r['label']==label and r['unit']==UNIT]
        if len(matches)!=1:raise ValueError('NSO fuel/year/unit not unique: '+label)
        row=matches[0];cached=sheet[cell].value
        if isinstance(cached,bool) or not isinstance(cached,(int,float)):
            raise ValueError('Numeric cached subtotal required: '+cell)
        value=Decimal(str(cached))
        if not value.is_finite() or value<0:raise ValueError('Invalid fuel subtotal: '+cell)
        delta=Decimal(row['amount'])-value
        comparisons.append(dict(nso_observation_id=row['observation_id'],nso_source_sha256=row['source_sha256'],
            nso_source_line=row['source_line'],nso_source_column=row['source_column'],table_id='13.10',reference_year=2024,
            measure='จำนวน',label=label,unit=UNIT,nso_value=row['amount'],dede_revised_value=str(value),
            difference_nso_minus_revised=str(delta),exact_displayed_value_match=delta==0,
            revised_sheet='ktoe',revised_cell=cell,header_cell=header_cell,column_label=header,row_label='MANUFACTURING',
            status='MATCH_REVISED_PUBLICATION' if delta==0 else 'REVISED_PUBLICATION_DIFFERS'))
        values.append(value)
    if sum(values)!=grand_total:raise ValueError('Selected fuel subtotals do not reconcile to manufacturing total')
    return comparisons


def main():
    import openpyxl
    folder=ROOT/'data/raw/dede/revised-2024';path=folder/'energy-balance.xlsx'
    meta=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    if sha!=meta['sha256']:raise ValueError('Revised workbook hash mismatch')
    nso=ROOT/'build/nso/report.json';rows=json.loads(nso.read_text(encoding='utf-8'))['rows']
    workbook=openpyxl.load_workbook(path,data_only=True,read_only=True)
    try:comparisons=compare(workbook['ktoe'],rows)
    finally:workbook.close()
    result=dict(checked_at=datetime.now(timezone.utc).isoformat(),comparisons= comparisons,
        compared_unique=len(comparisons),exact_displayed_matches=sum(c['exact_displayed_value_match'] for c in comparisons),
        nso_report_sha256=hashlib.sha256(nso.read_bytes()).hexdigest(),revised_source_url=meta['url'],
        revised_source_sha256=sha,rights_status=meta['rights_status'],source_values_changed=False,
        source_observations_added=0,independent_measurements_verified=0,
        limitation='Five 2024 manufacturing quantity subtotals only; percentages and other years are not counted. NSO republishes DEDE; matching publications do not establish independent measurements.')
    (ROOT/'evidence/nso-dede-components.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='comparisons'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
