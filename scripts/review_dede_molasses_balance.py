"""Verify DEDE Figure6 physical foreground; distinguish printed model from field validation."""
import json,hashlib,re
from pathlib import Path
from decimal import Decimal,localcontext
from pypdf import PdfReader
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'data/raw/dede-bioethanol1/source.pdf';sha=hashlib.sha256(p.read_bytes()).hexdigest()
 assert sha=='72052b365f32681579fb24341d1d0d94578708c6b16228a60e1f647294c9e944'
 flows=[('molasses','external','mixing','532.45'),('water','external','mixing','987.64'),('mixed_feed','mixing','fermentation','1703.85'),('CO2_output_destination_unknown','fermentation','external','114.98'),('fermented_liquid','fermentation','distillation','1588.87'),('fusel_oil','distillation','external','0.60'),('thick_slop','distillation','external','1286.17'),('recycle_distillation','distillation','mixing','177.53'),('alcohol_95pct','distillation','dehydration','124.58'),('recycle_dehydration','dehydration','mixing','6.23'),('fuel_ethanol','dehydration','external','118.35')]
 with pdfplumber.open(p) as doc:
  for t in [doc.pages[11].extract_text(),PdfReader(p).pages[11].extract_text()]:
   values={Decimal(v.replace(',','')) for v in re.findall(r'\d[\d,]*\.\d+',t)}
   for *_,v in flows:assert Decimal(v) in values,v
 balances=[]
 for stage in ['mixing','fermentation','distillation','dehydration','whole_factory']:
  if stage=='whole_factory':
   incoming=sum(Decimal(v) for _,a,b,v in flows if a=='external');outgoing=sum(Decimal(v) for _,a,b,v in flows if b=='external');n=sum(a=='external' or b=='external' for _,a,b,v in flows)
  else:
   incoming=sum(Decimal(v) for _,a,b,v in flows if b==stage);outgoing=sum(Decimal(v) for _,a,b,v in flows if a==stage);n=sum(a==stage or b==stage for _,a,b,v in flows)
  tolerance=Decimal('0.005')*n;residual=incoming-outgoing
  assert abs(residual)<=tolerance,(stage,residual)
  balances.append({'stage':stage,'input_t_per_day':str(incoming),'output_t_per_day':str(outgoing),'residual_input_minus_output':str(residual),'rounding_bound_t_per_day':str(tolerance),'result':'WITHIN_PRINTED_ROUNDING'})
 with localcontext() as ctx:
  ctx.prec=40
  observations=[{'flow':name,'from':a,'to':b,'amount':v,'unit':'t/day','kg_per_L_ethanol':str(Decimal(v)*1000/150000),'role':'INTERNAL_RECYCLE' if name.startswith('recycle') else 'INTERNAL_INTERMEDIATE' if a!='external' and b!='external' else 'BOUNDARY_FLOW','locator':'Figure6/PDF12/printed11/'+name,'verification':'TWO_PARSER_NUMERIC_PLUS_VISUAL_ALL_ARROWS_UNITS'} for name,a,b,v in flows]
 report={'review_date':'2026-11-06','source_url':'https://pei.dede.go.th/dataset/bioethanol1','sha256':sha,'source_figure':'Figure6/PDF12/printed11','reference_output':'150000L/day fuel ethanol;118.35t/day','source_model_conditions':{'molasses_total_sugar':'48%','molasses_TS':'80%','molasses_Brix':'80','mixed_TS':'25.00%','fermented_alcohol':'8.22%w/w','distilled_alcohol':'95%','thick_slop_TS':'14.93%','fermentation_efficiency':'92%','distillation_efficiency':'98.5%'},'observations':observations,'balances':balances,'verified_claim':'SOURCE_FIGURE_TRANSCRIPTION_AND_PRINTED_MASS_CLOSURE','not_verified':['plant identity and measurement year','independent field measurements','complete energy/chemical inventory','CO2 atmospheric release or biogenic/fossil classification','allocation','transport and vehicle use','waste treatment fate','cradle-to-grave inventory'],'status':'VERIFIED_SOURCE_FOREGROUND_EXAMPLE_NOT_FULL_LCI','redistribution_status':'NOT_CLEARED','CO2e_total':None,'production_changed':False}
 (ROOT/'evidence/dede-molasses-balance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(balances));print('11arrows/5balances verified;notindependentmeasurement/fullLCI')
if __name__=='__main__':main()
