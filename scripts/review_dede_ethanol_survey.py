"""Review selected complete Table 2 quantity columns; no cross-study inventory merge."""
import json, hashlib, re
from decimal import Decimal, localcontext
from pathlib import Path
from pypdf import PdfReader
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'data/raw/dede-bioethanol1/source.pdf'
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 assert sha=='72052b365f32681579fb24341d1d0d94578708c6b16228a60e1f647294c9e944'
 # Order and units visually checked against PDF11/printed10/Table2.
 rows=[('feedstock','t/day',('350','370'),('540','550')),('water','m3/day',('1200','1500'),('1000','1300')),('yeast','kg/day',('20','80'),('20','80')),('enzyme','kg/day',('20','800'),None),('other_chemicals','kg/day',('1000','5000'),('1000','5000')),('electricity','kWh/day',('25000','47000'),('22000','44000')),('steam','t/day',('300','500'),('200','400')),('ethanol','L/day',('150000','150000'),('150000','150000')),('CO2_product_or_output_not_confirmed_air','t/day',('100','120'),('100','120')),('fusel_oil','L/day',('300','600'),('300','600')),('spent_wash_parent','m3/day',('1400','1600'),('1000','1300')),('wet_sludge_child','t/day',('100','200'),None),('wastewater_child','m3/day',('1200','1400'),('1000','1300'))]
 texts=[PdfReader(p).pages[10].extract_text()]
 with pdfplumber.open(p) as pdf:texts.append(pdf.pages[10].extract_text())
 for t in texts:
  numbers=set(re.findall(r'\d+',t.replace(',','')))
  for _,_,a,b in rows:
   for pair in [a,b]:
    if pair:
     for n in pair:assert n in numbers,n
 out=[]
 with localcontext() as ctx:
  ctx.prec=40
  for name,unit,a,b in rows:
   for route,pair in [('cassava_chips',a),('molasses',b)]:
    out.append({'route':route,'flow':name,'unit':unit,'range':list(pair) if pair else None,'missing_marker':'SOURCE_DASH_NOT_ZERO' if pair is None else None,'per_L_ethanol_range':[str(Decimal(v)/Decimal('150000')) for v in pair] if pair else None,'normalized_unit':unit.removesuffix('/day')+'/L_ethanol','verification':'TWO_PARSER_NUMBERS_PLUS_VISUAL_ROW_UNIT_MAPPING','locator':'Table2/PDF11/printed10/'+route+'/'+name})
 report={'reviewed_at':'2026-11-06','source_url':'https://pei.dede.go.th/dataset/bioethanol1','sha256':sha,'scope':'SURVEY_AND_REFERENCE_RANGES_NOT_SINGLE_MATCHED_PLANT','measurement_year':None,'reference_output_L_per_day':'150000','quantity_cells_reviewed':26,'numeric_range_cells':24,'source_dash_cells':2,'observations':out,'quality_context':{'cassava_spent_wash':{'TS':'5-7%','COD':'40000-60000 mg/L','BOD':'15000-35000 mg/L'},'molasses_spent_wash':{'TS':'15%','COD':'100000-150000 mg/L','BOD':'40000-70000 mg/L'},'wastewater_COD_BOD_unit':'ppm; do not silently substitute mg/L'},'guards':['Ranges are not paired measurements or statistical confidence intervals','Per-litre is source-scale division, not validated linear extrapolation','Parent spent wash and child sludge/wastewater must not be summed','CO2 output is not proven emission to air or fossil carbon','No methane inferred from BOD without treatment/removal/capture/leakage evidence','No allocation, steam energy conversion, or foreign background filling','Not same plant/case as 2008 or SIIT2025'],'rights_status':'NOT_CLEARED','full_lifecycle_lci':False,'CO2e_total':None,'production_changed':False}
 target=ROOT/'evidence/dede-ethanol-survey-review.json';target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('26quantity cells checked:24numericranges/2dash;no full-LCI or totalGHG claim')
if __name__=='__main__':main()
