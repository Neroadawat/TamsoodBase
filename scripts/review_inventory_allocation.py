"""Reported allocation factors are not instructions to reallocate table amounts."""
import hashlib,json,re
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify_shares(shares):
    values=[Decimal(v) for v in shares.values()]
    if not values or any(not v.is_finite() or v<0 or v>100 for v in values) or sum(values)!=100:raise ValueError('Allocation percentages must sum to100')
    return True
def main():
    from pypdf import PdfReader
    raw=ROOT/'data/raw/mdpi-9415/pdf-v3';meta=json.loads((raw/'manifest.json').read_text());pdf=raw/'source.pdf'
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('PDF changed')
    reader=PdfReader(pdf);results=[]
    for process,page,patterns in [('CPO',5,{'CPO':r'(\d+)% for the CPO','Dry kernel':r'(\d+)% for the dry kernel','Shell':r'(\d+)% for the shell'}),('FAME',7,{'FAME':r'(\d+)% for FAME','Crude glycerine':r'(\d+)% for crude glycerine'})]:
        text=' '.join(reader.pages[page-1].extract_text().split());shares={}
        for product,pattern in patterns.items():
            found=re.findall(pattern,text)
            if len(found)!=1:raise ValueError('Ambiguous factor: '+product)
            shares[product]=found[0]
        verify_shares(shares)
        results.append({'process':process,'method':'ECONOMIC','reported_shares_percent':shares,'pdf_page':page,'source_url':meta['url']+'#page='+str(page),'shares_sum_verified':True,'applied_to_project_amounts':False,'tabulated_inventory_allocation_basis':'UNRESOLVED'})
    result={'source_sha256':meta['sha256'],'reviews':results,'model_ready':False,'source_values_changed':False,'further_reference':'ARDA2017 reference18 calculation sheets not acquired'}
    (ROOT/'evidence/inventory-allocation-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('CPO/FAME reported shares verified; no allocation applied')
if __name__=='__main__':main()
