"""Historical source-method pond-only estimate; neither measured nor whole-product CFP."""
import json,hashlib
from pathlib import Path
from decimal import Decimal,localcontext
import pdfplumber
from pypdf import PdfReader
from src.ethanol_demo import molasses_e10_basis
from src.carbon_calculator import characterize,partial_sum
ROOT=Path(__file__).resolve().parents[1]

def main():
 root=ROOT/'data/raw/thai-molasses-ethanol-2008';m=json.loads((root/'manifest.json').read_text())
 p=root/'source.pdf';assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256']
 with pdfplumber.open(p) as doc:
  for t in [doc.pages[4].extract_text(),PdfReader(p).pages[4].extract_text()]:
   assert '0.22' in t and 'kg/kg BOD' in t
 gp=ROOT/'data/raw/thai-compete-report/source.pdf';gh=hashlib.sha256(gp.read_bytes()).hexdigest()
 assert gh=='eb487f2fb400f1112e5ea54fcdff35b9ea180148d9a03509c91c8169a9a831c2'
 cf={'method_id':'IPCC2001_GWP100_AS_REPORTED_COMPETE_TABLE7','horizon_years':100,'gases':{'CO2_fossil':'1','CH4_biogenic':'23','N2O':'296'},'source_url':'https://www.compete-bioafrica.net/international/Annex4-2-5-COMPETE-032448-2ndReport-D4.1-Thailand-Final.pdf','source_sha256':gh,'locator':'Table7 footnote/PDF20/printed16;visual checked'}
 basis=molasses_e10_basis('13.46',assumption_id='MOE2008_FIG1_FUEL_ECONOMY_LINEAR_BASIS_V1')
 with localcontext() as ctx:
  ctx.prec=40
  bod=Decimal('106.8')*Decimal('40')/Decimal('1000')
  diverted=bod*Decimal('0.88');methane=diverted*Decimal('0.22')
  kg_per_fu=methane*Decimal(basis['physical_batch_scale_per_tonne_cane'])
  replay_gco2e_per_litre=methane*Decimal('23')/Decimal('10.17')*1000
  difference=abs(replay_gco2e_per_litre-Decimal('1870'))
  assert difference<Decimal('0.5'), 'Does not reproduce rounded source pond component'
 source={'source_url':m['source_url'],'source_sha256':m['sha256'],'locator':'Derived fromFigure1/PDF2(stillage106.8L,BODapproximately40gL),Table1/PDF3(88percentpond),Table3/PDF5(default0.22kgCH4/kgBOD);not direct measured gas'}
 one=characterize(format(kg_per_fu,'f'),'kg','CH4_biogenic',cf,basis_id='MOE2008_E10_TRAVEL13.46km',coverage_id='MOE2008_POND_CH4_ONLY',source=source)
 result={'reviewed_at':'2026-11-06','result_type':'HISTORICAL_METHOD_APPROXIMATE_POND_ONLY_SCENARIO','reference_basis':basis,'inputs':{'stillage_L_per_tonne_cane':'106.8','BOD_g_per_L':'40','BOD_is_approximate':True,'pond_fraction':'0.88','default_CH4_kg_per_kgBOD':'0.22','default_factor_is_Thai_measurement':False},'calculation_steps':{'total_BOD_kg_per_tonne_cane':str(bod),'pond_BOD_kg_per_tonne_cane':str(diverted),'estimated_CH4_kg_per_tonne_cane':str(methane),'estimated_CH4_kg_per_reference_trip':str(kg_per_fu)},'source_replay_check':{'calculated_gCO2e_per_Lethanol':str(replay_gco2e_per_litre),'reported_gCO2e_per_Lethanol':'1870','absolute_difference':str(difference),'tolerance_gCO2e_per_Lethanol':'0.5','matches_integer_display_rounding':True,'locator':'COMPETE Table7/PDF20/printed16;pondCH4 row;visual transcription','independent_validation':False,'interpretation':'Same research-line source-method replay,not independent emission measurement'},'characterized_component':one,'partial_result':partial_sum([one]),'assumptions':['Figure1stillagevolumeandBODapprox apply to samebasecase','Source defaultapplied toBODdivertedtopond without additional removalfraction;source-methodscreening only','Noadditionalfermentation/combustion/fugitive/soil emissions included','HistoricIPCC2001GWP100 reproduces reportmethod;notcurrentTGOcertificationmethod','Noavoidedelectricitycredit or capturedgasnetbenefit;notaddedtoaggregatebiodieselEF'],'missing_components':['farminputsandsoilgases','millenergyandnetallocation','ethanolprocessenergy/chemicals','capturedgasleakageandcombustion','alltransportlegs','gasolineproductionandvehicleuse'],'full_lifecycle_lci':False,'CO2e_total':None,'strict_all_inputs_Thai_verified':False,'redistribution_status':'NOT_CLEARED','production_changed':False}
 out=ROOT/'build/ethanol-carbon-demo';out.mkdir(parents=True,exist_ok=True)
 for target in [out/'report.json',ROOT/'evidence/ethanol-carbon-calculator.json']:
  target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Pond-only estimate kgCH4/tcane:',methane)
 print('Pond-only kgCO2e per13.46km:',one['amount_kgCO2e'])
 print('Whole-product CO2e:null;historic method/default scenario;notproduction')
if __name__=='__main__':main()
