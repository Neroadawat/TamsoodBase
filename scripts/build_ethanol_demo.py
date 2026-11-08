"""Build a private, explicitly partial, same-study ethanol example and gap audit."""
import hashlib,json
from pathlib import Path
from src.ethanol_demo import molasses_e10_basis
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]

def main():
 sources=[]
 for name,pages in [('thai-molasses-ethanol-2008',11),('thai-cassava-ethanol-2008',8)]:
  p=ROOT/'data/raw'/name/'source.pdf';m=json.loads((p.parent/'manifest.json').read_text())
  assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256']
  r=PdfReader(p);assert len(r.pages)==pages
  sources.append({'id':name,'sha256':m['sha256'],'pages_read_for_gap_audit':list(range(1,pages+1)),'source_url':m['source_url'],'redistribution_status':'NOT_CLEARED'})
 model=molasses_e10_basis('13.46',assumption_id='MOE2008_FIG1_FUEL_ECONOMY_LINEAR_BASIS_V1')
 model['source_url']=sources[0]['source_url'];model['source_sha256']=sources[0]['sha256']
 model['locators']={'physical_batch_flows':'Figure1/PDF2/printed302; basis1tonnecane','fuel_economy':'Section2.1/PDF2/printed302','economic_allocation':'Section2.2/PDF3/printed303'}
 model['verification']={'physical_figure_values':'VISUAL_TRANSCRIPTION_RASTER_FIGURE_NOT_TWO_TEXT_EXTRACTORS','fuel_economy':'PYPDF_TEXT_AND_RENDERED_PAGE','economic_allocation':'TWO_EXTRACTORS_AND_RENDERED_PAGE_PREVIOUS_REVIEW','scientific_independent_reviewer':False}
 gaps={
 'molasses':[
  {'stage':'cultivation','available':'cane/trash batch basis,economicallocation andcontextualN/P2O5/K2Oratesperha inSection3.4','missing':'allinputamounts linked byverifiedyield to sameFU;herbicide/diesel/water andelementarysoilairflows'},
  {'stage':'sugar_milling','available':'sugar/molasses/bagasse quantities','missing':'actualsteam/electricity/auxiliaryfuel amounts and exactnetcredit;incomplete massbalance'},
  {'stage':'ethanol_conversion','available':'ethanol/stillage yield and partialenergyparameters','missing':'completecoal/ricehusk/electricity/chemical/water inputs and fermentationCO2 mass'},
  {'stage':'waste','available':'12/88split/BODapprox40gL/defaultCH4parameter','missing':'fulltreatment/sludgeleakage/nutrient fate;defaultEFnotThaisiteCH4measurement'},
  {'stage':'transport_distribution','available':'described in scope and collectionprocedure','missing':'alllegdistances/payload/loads/fuel consumption per referenceflow'},
  {'stage':'vehicle_use','available':'E10/CGfuel economy and blenddefinition','missing':'completeperFUelementarymassCO2CH4N2Oetc;Table5isLCIA notphysicalLCI'},
  {'stage':'background','available':'source modelreferences','missing':'reproducibleThai-onlyproviderinventory/versions/LCIexports'}],
 'cassava':[
  {'stage':'cultivation_conversion','available':'process flow and energy scenarios','missing':'numericrawinput/outputtable for allprocesses;Figure1mostlylabels'},
  {'stage':'transport','available':'3routecapacities/distancesverified','missing':'referenceflowmass/actualfuel/returnroute for reproducibleemissions'},
  {'stage':'waste','available':'stillage/biogas/drysludgepaths','missing':'settledportionquantification/fateexplicitlynotincluded due lackofinformation Section1.2/PDF2'},
  {'stage':'vehicle_use','available':'CG/E10ThaiPTTreference;E85modelestimate','missing':'completeperFUgasinventory;E85notThaiobservedfleettest inTable2'},
  {'stage':'background_quality','available':'GREET/IPCC/DMUNERIreferences','missing':'Thai-onlybackgroundreplay;acidificationTable4held due numeric inconsistency'}]}
 report={'reviewed_at':'2026-11-06','sources':sources,'same_study_partial_example':model,'book_by_book_gap_audit':gaps,'recommended_next_source':{'title':'Fuel ethanol from cane molasses in Thailand: Environmental and cost performance','doi':'10.1016/j.enpol.2008.01.008','url':'https://www.sciencedirect.com/science/article/abs/pii/S0301421508000049','reason':'Publisher explicitly identifies Table7 asLCIresults forE10a/b/c/CG;mustverifyactualtable,basis andcompatibilitybeforeusing','status':'USER_TU_NOT_SUBSCRIBED_OPEN_AUTHOR_REPORT_FOUND_BUT_NOT_GAS_LCI','possible_output':'reportedaggregateairinventory notnecessarilyunitprocesscompleteLCI'},'full_lifecycle_lci':False,'CO2e_total':None,'production_changed':False,'numeric_publication':False}
 out=ROOT/'build/ethanol-demo';out.mkdir(parents=True,exist_ok=True)
 (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'evidence/ethanol-demo-completion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Private partial example built: E10 litres',model['E10_litres'])
 print('Both books audited;fullLCI remains false;12 explicit stage gaps preserved.')
if __name__=='__main__':main()
