"""Build a bounded hypothetical freight sensitivity from reviewed Thai source rows."""
from html.parser import HTMLParser
from pathlib import Path
import json,hashlib
from src.transport_scenario import freight_scenario
ROOT=Path(__file__).resolve().parents[1]
class Rows(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.row=[]
        if tag in ('td','th') and self.row is not None:self.cell=[]
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:self.row.append(' '.join(' '.join(self.cell).split()));self.cell=None
        if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None

def build():
    source=ROOT/'data/raw/tgo-cfp-2026-11-03/page.html';sha=hashlib.sha256(source.read_bytes()).hexdigest()
    if sha!='58a5f2cc45396724cb4dcf4f26548cd321c9f549a355ff9123703c99cb1caf06':raise ValueError('Review new source version before extraction')
    parser=Rows();parser.feed(source.read_text(encoding='utf-8'));rows=[r for r in parser.rows if r and r[0].strip('. ') in ['230','231','232','233']]
    if len(rows)!=4 or any(len(r)!=7 for r in rows):raise ValueError('Source table changed')
    factors=[]
    for row in rows:
        factors.append({'id':'TGO-CFP-'+row[0].strip('.')+'-April2026','name':row[1],'description':row[2],'activity_unit':row[3],'value':row[4],'source_reference':row[5],'version':row[6],'result_unit':'kgCO2e','geography':'TH','provenance_class':'THAI_NATIONAL_LCI_REPORTED','underlying_all_inputs_thai_audited':False,'method':'IPCC 2013 GWP 100a V1.03','source_url':'https://thaicarbonlabel.tgo.or.th/index.php?lang=TH&mod=Y0hKdlpIVmpkSE5mWlcxcGMzTnBiMjQ9','source_sha256':sha,'locator':'CFP table row '+row[0].strip('.'),'rights_status':'NOT_CLEARED_FOR_REDISTRIBUTION'})
    basis=json.loads((ROOT/'build/thai-b100-properties-2021/conditional-scenario.json').read_text(encoding='utf-8'))
    if basis['scope']!='CONDITIONAL_FUEL_PROPERTY_SCENARIO_NOT_MODEL_FUEL_REPLACEMENT' or not basis['assumption_id']:raise ValueError('Conditional fuel-basis contract missing')
    results=[freight_scenario(basis['mass_kg'],distance,factor,assumption_id='TEAM_HYPOTHETICAL_DISTANCE_'+distance+'_KM_NOT_MEASURED_ROUTE') for factor in factors if factor['activity_unit']=='tkm' for distance in ['10','50','100']]
    out=ROOT/'build/transport-sensitivity';out.mkdir(exist_ok=True);(out/'report.json').write_text(json.dumps({'factors':factors,'scenarios':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'scope':'THAI_TRUCK_FACTOR_SCREENING_NOT_FULL_ROUTE','source_sha256':sha,'source_rows_reviewed':[230,231,232,233],'factors_tkm_used':[231,232,233],'km_row230_not_used_as_tkm':True,'source_row_cells_preserved':True,'scenario_count':len(results),'distances_km':['10','50','100'],'distance_status':'HYPOTHETICAL_NOT_OBSERVED','loading_sensitivity_percent':[50,75,100],'empty_return_convention':'UNKNOWN_NOT_ADDED','not_combined_with_existing_factors':True,'production_changed':False,'strict_all_inputs_thai_verified':False}
if __name__=='__main__':
    r=build();(ROOT/'evidence/transport-sensitivity.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
