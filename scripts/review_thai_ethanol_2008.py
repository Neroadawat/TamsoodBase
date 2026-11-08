"""Verify a selected published transport subset; no cross-study inventory stitching."""
import json,hashlib
from pathlib import Path
from decimal import Decimal
import pdfplumber
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
def main():
 records=[]
 for name,pages in [('thai-cassava-ethanol-2008',8),('thai-molasses-ethanol-2008',11)]:
  p=ROOT/'data/raw'/name/'source.pdf';m=json.loads((p.parent/'manifest.json').read_text())
  assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256']
  reader=PdfReader(p);assert len(reader.pages)==pages
  records.append({'id':name,'pages':pages,'sha256':m['sha256'],'bytes':m['bytes'],'redistribution_status':'NOT_CLEARED'})
 p=ROOT/'data/raw/thai-cassava-ethanol-2008/source.pdf'
 rows=[('Cassava chips from cassava processing plants to CE plants','15–20','100'),('Ethanol from factories to oil refineries','10–12','150'),('Gasohol from oil refineries to gas stations','10–12','180')]
 with pdfplumber.open(p) as doc:
  text=doc.pages[3].extract_text()
  second=PdfReader(p).pages[3].extract_text()
  selected=[]
  for label,capacity,distance in rows:
   expected=f'{label} Diesel truck {capacity} {distance}'
   for extraction in [text,second]:assert expected in ' '.join(extraction.split()),expected
   selected.append({'material_route':label,'mode':'Diesel truck','capacity_tonnes_as_printed':capacity,'average_distance_km':distance,'role':'SOURCE_STUDY_ASSUMPTION_NOT_CURRENT_ROUTE_MEASUREMENT','locator':'Table3/PDF4/printed150','source_sha256':records[0]['sha256']})
 m=ROOT/'data/raw/thai-molasses-ethanol-2008/source.pdf'
 with pdfplumber.open(m) as doc:
  text=doc.pages[2].extract_text();second=PdfReader(m).pages[2].extract_text()
  for extraction in [text,second]:
   compact=''.join(extraction.split())
   for fragment in ['12%spentwash','88%senttoananaerobicpond','89.6%and10.4%']:
    assert fragment in compact,fragment
 result={'reviewed_at':'2026-11-06','documents':records,'selected_transport_rows':selected,'transport_all_selected_fields_checked_two_parsers_and_visual':True,'molasses_scope_visual_page':3,'molasses_waste_and_allocation_text_checked_two_parsers':True,'molasses_base_case':{'spent_wash_biogas_recovery_percent':'12','spent_wash_to_pond_percent':'88','coverage':'reportedstudybasecase','locator':'Table1/PDF3/printed303'},'molasses_allocation':{'type':'ECONOMIC','sugar_percent':'89.6','molasses_percent':'10.4','locator':'Section2.2/PDF3/printed303','apply_to_existing_B100_model':False},'quality_issue':{'source':'cassava','locator':'Table4/PDF4/printed150','field':'acidification','reported_CG':'3.00','reported_E10_b':'3.07','reported_percent_change':'-6.8','recalculated_from_displayed_values':str((Decimal('3.07')/Decimal('3.00')-1)*100),'status':'SOURCE_TABLE_SIGN_VALUE_INCONSISTENCY_VISUALLY_CONFIRMED','action':'Preserve values;exclude this impact row from comparative demo until resolved;never silently correct.'},'all_published_inventory_cells_verified':False,'complete_elementary_inventory_available':False,'all_background_inputs_thai':False,'public_numeric_release':False,'existing_model_changed':False,'CO2e_total':None}
 assert Decimal('12')+Decimal('88')==100 and Decimal('89.6')+Decimal('10.4')==100
 (ROOT/'evidence/thai-ethanol-2008-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('2 PDF hashes/pages;3 full transport rows;waste split/allocation;issue preserved. No production import.')
if __name__=='__main__':main()
