"""Verify selected Thai measured use-phase means, never auto-join production inventories."""
import json,re,hashlib
from pathlib import Path
from decimal import Decimal
from pypdf import PdfReader
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'data/raw/thai-vehicle-co2-2017/source.pdf';sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha=='e4f87bc8518b8cc748099c705b157f8b497d1101a95cb9f640f27cb10059ecfd'
 raw={'gasohol91':[('204.6','43.5'),('183.7','43.1'),('174.2','37.1')],'gasoholE20':[('162.4','28.2'),('141.8','23.6'),('135.1','20.9')]}
 with pdfplumber.open(p) as pdf:
  for text in [pdf.pages[5].extract_text(),PdfReader(p).pages[5].extract_text()]:
   nums=set(re.findall(r'\d+\.\d+',text))
   for vals in raw.values():
    for mean,sd in vals:assert mean in nums and sd in nums
 rows=[]
 for fuel,values in raw.items():
  for speed,(mean,sd) in zip(['0-20','20-40','40-80'],values):
   rows.append({'fuel':fuel,'vehicle':'LDG passenger car 2000cc EUROIII(2005 standard)','speed_km_h':speed,'mean_CO2_g_per_km':mean,'reported_plus_minus_g_per_km':sd,'basis':'Bangkok driving cycle;chassis dynamometer;hot soak;5vehicles per fuel(Table1)','locator':'PDF6/printed70/Sec2.1/'+fuel+'/'+speed,'verification':'TWO_PARSER_NUMERIC_PLUS_VISUAL_CONTEXT','example_10km_CO2_kg':str(Decimal(mean)*10/1000),'example_10km_scope':'hypothetical10km within this test condition;not lifecycle CO2e;no national fleet inference'})
 report={'review_date':'2026-11-06','source_url':'https://ph01.tci-thaijo.org/index.php/aer/article/view/76815','doi':'10.35762/AER.2017.39.1.7','sha256':sha,'publication_year':2017,'measurement_year':None,'selected_numeric_cells':12,'observations':rows,'gas':'CO2_total_tailpipe','fossil_biogenic_split':None,'CH4':None,'N2O':None,'actual_ethanol_supplier':None,'join_to_DEDE_or_2008':'NOT_VERIFIED_NO_AUTOMATIC_JOIN','remaining_use_gaps':['fuel consumption L/km for same sample','CO2 fossil/biogenic fraction','CH4 and N2O','evaporation emissions','fuel batch upstream supplier and year'],'full_lifecycle_lci':False,'CO2e_total':None,'production_changed':False,'redistribution_status':'NOT_CLEARED'}
 (ROOT/'evidence/thai-vehicle-co2-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('12numeric cells /6Thai measured tailpipe conditions verified;10km unit examples;no wholeLCIsum')
if __name__=='__main__':main()
