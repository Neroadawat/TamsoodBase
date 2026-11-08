"""New Thai acquisition-only source; never backfill the2008system by title similarity."""
import json,hashlib,re
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'data/raw/thai-ethanol-siit-2025/source.pdf';sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha=='4a3d9dc62e670069302bf27ab85caa93fb604258db1c8f40bb73e71a6d49addd'
 rows=[('cane_extraction','Fresh cane','kg','9255.96'),('cane_extraction','Burnt cane','kg','4110.78'),('cane_extraction','Hot water','L','4545.11'),('milling','Lime','kg','2.61'),('milling','Flocculant clarifier','kg','0.10'),('milling','Enzyme','kg','0.002'),('milling','Anti-scale solution','kg','0.11'),('dilution','Molasses','kg','642.28'),('dilution','RO water','L','18274.11'),('fermentation','Diluted molasses','kg','18916.39'),('fermentation','Yeast','kg','0.04'),('fermentation','Urea','kg','1.81'),('fermentation','Phosphoric acid','kg','0.05'),('fermentation','Ammonium sulphate','kg','1.56'),('fermentation','Diammonium phosphate','kg','0.01'),('fermentation','Sulfuric acid','kg','16.79'),('distillation','Alcohol','kg','18819.88'),('dehydration','Alcohol95%','kg','4187.46')]
 with pdfplumber.open(p) as doc:
  for text in [doc.pages[13].extract_text(),PdfReader(p).pages[13].extract_text()]:
   numbers={Decimal(t.replace(',','')) for t in re.findall(r'(?<![A-Za-z])\d[\d,]*\.\d+|\b\d+\b',text)}
   for _,_,_,q in rows:assert Decimal(q) in numbers,q
 obs=[{'process':stage,'name':name,'unit':unit,'amount':q,'reference_product':'1tonethanol','quantity_role':'INTERMEDIATE_DO_NOT_SUM' if name in ['Molasses','Diluted molasses','Alcohol','Alcohol95%'] else 'SOURCE_REPORTED_ACTIVITY','source_sha256':sha,'locator':'Table8/PDF14/printed187/'+name,'verification':'TWO_EXTRACTOR_NUMERIC_CHECK_PLUS_VISUAL_ROW_MAPPING','accepted_into_existing_model':False} for stage,name,unit,q in rows]
 report={'reviewed_at':'2026-11-06','source_url':'https://ph02.tci-thaijo.org/index.php/SciTechAsia/article/view/261544','pdf_url':'https://ph02.tci-thaijo.org/index.php/SciTechAsia/article/download/261544/172756/998685','doi':'10.14456/scitechasia.2025.60','source_sha256':sha,'bytes':p.stat().st_size,'pages':15,'scope':'RAW_MATERIAL_ACQUISITION_ONLY_NOT_WTW','source_method':'TGO_CFP2022+AR5claims+someEcoinvent2.xIPCC2007components','allocation':'sucrosecontent10.73percentmolasses;not2008economic10.4percent','observations':obs,'issues':[
 {'id':'SIIT01','locator':'Table9/PDF15/Lime','kind':'PRINTED_ALLOCATION_ARITHMETIC_CONFLICT','quantity':'2.61','factor':'1.0215','allocation_as_printed':'1.00','calculated_from_printed_fields':str(Decimal('2.61')*Decimal('1.0215')),'reported':'0.2866','action':'Hold;do not substitute10.73percent without explicitrule correction'},
 {'id':'SIIT02','locator':'Table6vsTable9/Freshcane','kind':'FACTOR_VERSION_OR_TYPO_UNRESOLVED','table6':'0.0157','table9':'0.0151','action':'Preserve both;no silent selection'},
 {'id':'SIIT03','locator':'Table6vsTable9/Burntcane','kind':'FACTOR_VERSION_OR_TYPO_UNRESOLVED','table6':'0.0249','table9':'0.0242','action':'Preserve both'},
 {'id':'SIIT04','locator':'Table9/ROwater','kind':'PRINTED_FACTOR_PRECISION','displayed_product':str(Decimal('18274.11')*Decimal('0.0005')),'reported':'9.6825','action':'Could reflect undisplayedprecision;notprovewrong;needunderlyingEF/version'},
 {'id':'SIIT05','locator':'Section2.3andConclusion/PDF4,9-10','kind':'INCOMPLETE_LIFECYCLE_SCOPE','action':'Noenergy/use/wastecompleteinventory;do not add2008pondcase'},
 {'id':'SIIT06','locator':'Table6/PDF14','kind':'BACKGROUND_NOT_STRICT_THAI','action':'Ecoinvent/CarbonCloud/foreignliteraturereported;do notmarkallThai'}],
 'numeric_cells_in_selected_table':18,'all_article_fields_verified':False,'same_case_as_2008':False,'CO2e_total':None,'full_lifecycle_lci':False,'redistribution_status':'NOT_CLEARED','public_raw_export':False,'production_changed':False}
 out=ROOT/'build/ethanol-siit-review';out.mkdir(parents=True,exist_ok=True);(out/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'evidence/thai-ethanol-siit-2025-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 p.parent.joinpath('manifest.json').write_text(json.dumps({k:report[k] for k in ['source_url','pdf_url','source_sha256','bytes','pages','redistribution_status','public_raw_export']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('18Table8quantities all checked;6sourceissues held;newcaseacquisitiononly/no2008join.')
if __name__=='__main__':main()
