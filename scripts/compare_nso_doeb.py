"""Compare exact-label volume series only; never join diesel reclassifications or LPG mass."""
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    try:import xlrd
    except ImportError:
        sys.path.insert(0,str(ROOT/'.local/xls-deps'));import xlrd
    raw=ROOT/'data/raw/doeb';meta=json.loads((raw/'manifest.json').read_text(encoding='utf-8'))
    digest=hashlib.sha256((raw/'sales.xls').read_bytes()).hexdigest()
    if digest!=meta['sha256']:raise ValueError('DOEB snapshot changed')
    workbook=xlrd.open_workbook(raw/'sales.xls',formatting_info=True);sheet=workbook.sheet_by_name('sale_y')
    if sheet.cell_value(0,0)!='ปีพุทธศักราช' or 'ล้านลิตร' not in sheet.cell_value(0,2):raise ValueError('Header changed')
    nso=json.loads((ROOT/'build/nso/report.json').read_text(encoding='utf-8'))['rows'];checks=[]
    for row in nso:
        if row['table_id']!='13.8' or row['unit']!='Thousand litre' or row['label'] not in ('น้ำมันเบนซิน ออกเทน 91','น้ำมันเตา'):continue
        matches=[i for i in range(1,sheet.nrows) if sheet.cell_value(i,0)==row['reference_year']+543 and sheet.cell_value(i,1).strip()==row['label']]
        if not matches:continue
        if len(matches)!=1:raise ValueError('Ambiguous DOEB match')
        i=matches[0];cell=sheet.cell(i,2);stored=str(cell.value);amount=Decimal(stored)*1000
        fmt=workbook.format_map[workbook.xf_list[cell.xf_index].format_key].format_str
        if fmt!='0.0':raise ValueError('Unexpected display format')
        delta=Decimal(row['amount'])-amount
        checks.append(dict(nso_observation_id=row['observation_id'],label=row['label'],year=row['reference_year'],
            nso_value=row['amount'],doeb_stored_million_litre=stored,doeb_thousand_litre=str(amount),
            unit='Thousand litre',difference_nso_minus_doeb=str(delta),exact_stored_value_match=delta==0,
            within_doeb_display_rounding=abs(delta)<=Decimal('50'),display_tolerance_thousand_litre='50',
            display_format=fmt,doeb_sheet='sale_y',doeb_row=i+1,doeb_column='C',
            nso_url=row['source_url'],nso_sha256=row['source_sha256'],doeb_url=meta['url'],doeb_sha256=digest))
    result=dict(comparisons=checks,count=len(checks),exact_matches=sum(c['exact_stored_value_match'] for c in checks),
                within_display_rounding=sum(c['within_doeb_display_rounding'] for c in checks),
                limitations=['Stored Excel floats retained as text; multiplying1000 only converts million to thousand litres',
                '0.0 Excel formatting implies half-step50thousand-litres tolerance; this is display agreement, not exact source validation',
                'Exact Thai labels only; no automatic diesel reclassification or volume/mass join',
                'NSO republishes DOEB; not independent measurement verification','Unmatched years/series remain unverified'])
    (ROOT/'evidence/nso-doeb-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='comparisons'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
