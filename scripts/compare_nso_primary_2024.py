"""Exact-context 2024 primary-supply comparisons against retained DEDE balance.

Never infer renewable/other-energy aggregation or change the NSO source values.
"""
from decimal import Decimal
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPECS=[('แอนทราไซต์','E24','E5','แอนทราไซต์'),('บิทูมินัส','G24','G5','บิทูมินัส'),
 ('ถ่านโค้ก','I24','I5','ถ่านโค้ก'),('ถ่านอัดและอื่น ๆ','K24','K5','ถ่านอัดและอื่น ๆ'),
 ('ลิกไนต์','U24','O5','ลิกไนต์'),('น้ำมันดิบ','AI24','AI7','น้ำมันดิบ'),
 ('คอนเดนเสท','AK24','AK7','คอนเดนเสท'),('ก๊าซธรรมชาติ','AG24','AG11','TOTAL NATURAL GAS PRODUCT'),
 ('ก๊าซโซลีนธรรมชาติ','AM24','AM7','ก๊าซโซลีนธรรมชาติ'),('น้ำมันสำเร็จรูป','BO24','BO10','TOTAL PETROLEUM PRODUCTS'),
 ('ไฟฟ้า','BR24','BR9','ELECTRICITY'),('พลังงานเชิงพาณิชย์','BU24','BU9','TOTAL COMMERCIAL ENERGY'),
 ('เชื้อเพลิงชีวภาพ','DB24','DB7','รวมเชื้อเพลิงชีวภาพทั้งหมด'),('รวมยอด','DT24','DT9','GRAND TOTAL')]
def compact(s):return ''.join(str(s).split())
def compare(sheet,rows):
    if '2024' not in str(sheet['DF1'].value) or 'ktoe' not in str(sheet['DW2'].value):raise ValueError('Year/unit changed')
    if compact(sheet['DW24'].value)!='TOTALPRIMARYENERGYSUPPLY':raise ValueError('Supply scope changed')
    if compact(sheet['U7'].value)!='รวม':raise ValueError('Lignite total column changed')
    result=[]
    for label,cell,header,expected in SPECS:
        if compact(sheet[header].value)!=compact(expected):raise ValueError('Fuel header changed: '+header)
        found=[r for r in rows if r['table_id']=='13.5' and r['reference_year']==2024 and r['label']==label and r['unit']=='10^3 ton of oil equivalent']
        if len(found)!=1:raise ValueError('NSO identity/context not unique')
        r=found[0];raw=sheet[cell].value
        if isinstance(raw,bool) or not isinstance(raw,(int,float)):raise ValueError('Missing/non-numeric source cell')
        value=Decimal(str(raw))
        if not value.is_finite():raise ValueError('Non-finite source amount')
        delta=Decimal(r['amount'])-value
        # NSO presents these selected quantities as integers. Compatibility with
        # half an integer step is recorded separately from an exact value match.
        integer_display=Decimal(r['raw_value'])==Decimal(r['raw_value']).to_integral_value()
        tolerance=Decimal('0.5') if integer_display else Decimal('0')
        result.append({**{k:r[k] for k in ('table_id','reference_year','measure','label','unit')},
          'nso_observation_id':r['observation_id'],'nso_source_sha256':r['source_sha256'],'nso_value':r['amount'],
          'dede_value':str(value),'difference':str(delta),'exact_displayed_value_match':delta==0,
          'display_tolerance':str(tolerance),'within_display_rounding':abs(delta)<=tolerance,
          'source_sheet':'ktoe','source_cell':cell,'header_cell':header,'header_value':expected,
          'row_label':'TOTAL PRIMARY ENERGY SUPPLY'})
    return result
def main():
    import openpyxl
    folder=ROOT/'data/raw/dede/revised-2024';path=folder/'energy-balance.xlsx';meta=json.loads((folder/'manifest.json').read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('DEDE snapshot changed')
    nso=ROOT/'build/nso/report.json';rows=json.loads(nso.read_text(encoding='utf-8'))['rows']
    workbook=openpyxl.load_workbook(path,data_only=True,read_only=True)
    try:checks=compare(workbook['ktoe'],rows)
    finally:workbook.close()
    result={'comparisons':checks,'compared_unique':len(checks),'exact_matches':sum(c['exact_displayed_value_match'] for c in checks),
      'within_display_rounding':sum(c['within_display_rounding'] for c in checks),'source':meta,
      'nso_report_sha256':hashlib.sha256(nso.read_bytes()).hexdigest(),'source_values_changed':False,
      'independent_measurements_verified':0,'limitation':'Renewable/other-energy aggregates excluded; rounded compatibility is not exact agreement or independent measurement.'}
    (ROOT/'evidence/nso-dede-primary-2024.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('comparisons','source')},indent=2))
if __name__=='__main__':main()
