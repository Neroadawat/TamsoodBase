import json,hashlib
from pathlib import Path
from decimal import Decimal,localcontext
from src.reported_balance import reported_balance
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'data/raw/thai-compete-report/source.pdf';sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha=='eb487f2fb400f1112e5ea54fcdff35b9ea180148d9a03509c91c8169a9a831c2'
 rows=[
 ('farm',None,'260.2','454.6'),('fertilizer_herbicide','farm','66.8','116.7'),('farm_diesel','farm','21.3','37.3'),('labour','farm','38.2','66.7'),('farm_transport','farm','39.0','68.2'),('soil_N2O','farm','69.4','121.2'),('trash_burning','farm','25.5','44.5'),
 ('milling',None,'5.8','10.2'),('milling_biomass','milling','3.7','6.6'),('milling_transport','milling','2.1','3.6'),('grid_credit',None,'-71.8','-125.4'),
 ('conversion',None,'3119.4','3119.4'),('coal','conversion','1150.1','1150.1'),('rice_husk','conversion','2.1','2.1'),('biogas','conversion','0.3','0.3'),('pond_CH4','conversion','1870','1870'),('conversion_transport','conversion','96.9','96.9')]
 cases=[]
 for column,year,total,net,percent in [(2,'2005','3313.5','674.6','25.6'),(3,'2006','3458.7','819.8','31.3')]:
  obs=[{'id':r[0],'ancestor_ids':[r[1]] if r[1] else [],'value':r[column],'unit':'gCO2eq/Lethanol','kind':'REPORTED_CHARACTERIZED_CONTRIBUTION_NOT_GAS_MASS','source_sha256':sha,'locator':f'Table7/PDF20/printed16/{r[0]}/{year}','verification':'VISUAL_RASTER_TRANSCRIPTION_ONLY'} for r in rows]
  stages=reported_balance([x for x in obs if not x['ancestor_ids']],total)
  subchecks={parent:reported_balance([x for x in obs if parent in x['ancestor_ids']],next(x['value'] for x in obs if x['id']==parent)) for parent in ['farm','milling','conversion']}
  with localcontext() as ctx:
   ctx.prec=40;rate=Decimal(net)/Decimal('2638.9')*100
  cases.append({'allocation_year_label':year,'observations':obs,'stage_sum_audit':stages,'subgroup_audit':subchecks,'reported_total_gCO2eq_per_Lethanol':total,'reported_gross_avoided_gCO2eq_per_Lethanol':'-2638.9','reported_net_increase':net,'reported_percent_increase':percent,'recalculated_percent_from_displayed_values':str(rate),'percent_matches_1decimal_display':abs(rate-Decimal(percent))<=Decimal('0.05'),'used_as_our_whole_product_total':False})
 result={'reviewed_at':'2026-11-06','source_url':'https://www.compete-bioafrica.net/international/Annex4-2-5-COMPETE-032448-2ndReport-D4.1-Thailand-Final.pdf','source_sha256':sha,'scope':'SOURCE_REPORTED_HISTORIC_PRODUCTION_GHG_NOT_FULL_LCI','method':'GWP100_IPCC2001','source_includes_labour':True,'cases':cases,'percent2006_issue':'Table31.3versuscalculated~31.1/sourceprose31.1;preservednotcorrected','energy_table_review':{'locator':'Tables5-6/PDF18/printed14','visual_checked':True,'all_numeric_cells_imported':False,'reason':'Primaryenergy accountingincludesrecoveredenergy/credits;MJcannotbe treatedasdirectfuelquantitywithoutfuelbasis/providerdata'},'redistribution_status':'NOT_CLEARED','full_lifecycle_lci':False,'CO2e_total':None,'production_changed':False}
 (ROOT/'evidence/ethanol-reported-stage-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('34 characterized component cells transcribed;stage/subgroup balanceschecked;2006percentissue held.')
if __name__=='__main__':main()
