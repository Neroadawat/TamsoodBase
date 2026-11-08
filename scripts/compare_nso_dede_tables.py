"""Additional exact-context comparisons from retained DEDE2023 tables2/25/30/31."""
from decimal import Decimal
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NUMBER=r'(?:\(\d[\d,]*(?:\.\d+)?\)|\d[\d,]*(?:\.\d+)?)'
SUPPLY={'รวมยอด':'TOTAL','พลังงานเชิงพาณิชย์':'COMMERCIAL ENERGY','แอนทราไซต์':'ANTHRACITE','บิทูมินัส':'BITUMINOUS','ถ่านโค้ก':'COKE','ลิกไนต์':'LIGNITE','ถ่านอัดและอื่น ๆ':'BRIQUETTES & OTHER COAL','น้ำมันดิบ':'CRUDE OIL','คอนเดนเสท':'CONDENSATE','ก๊าซธรรมชาติ':'NATURAL GAS','ก๊าซโซลีนธรรมชาติ':'NATURAL GASOLINE','น้ำมันสำเร็จรูป':'PETROLEUM PRODUCTS','ไฟฟ้า':'ELECTRICITY','เชื้อเพลิงชีวภาพ':'BIOFUEL','พลังงานอื่น ๆ':'OTHER ENERGY'}
PRODUCTS={'ก๊าซปิโตรเลียมเหลว':0,'เบนซินไร้สารตะกั่ว ออกเทน 91':1,'เบนซินไร้สารตะกั่ว ออกเทน 95':2,'แก๊สโซฮอล์ อี10 ออกเทน 91':3,'แก๊สโซฮอล์ อี10 ออกเทน 95':4,'แก๊สโซฮอล์ อี20 ออกเทน 95':5,'แก๊สโซฮอล์ อี85':6,'น้ำมันเครื่องบิน':7,'น้ำมันก๊าด':8,'ดีเซลหมุนเร็ว':9,'น้ำมันเตา':11,'รวมยอด':12}
IMPORTS={'ก๊าซปิโตรเลียมเหลว(1)':'LPG','แก๊สโซฮอล์ อี10 ออกเทน 91(2)':'GASOHOL E10 RON 91','น้ำมันเครื่องบิน(3)':'JET FUEL','ดีเซลหมุนเร็ว(4)':'HSD','น้ำมันเตา':'FUEL OIL','รวมยอด':'TOTAL'}
def amount(raw):return Decimal(raw.replace(',','').replace('(','-').replace(')',''))
def annual_line(text,label):
    pattern=r'('+NUMBER+r')\s+('+NUMBER+r')\s+('+NUMBER+r')\s+('+NUMBER+r')\s+('+NUMBER+r')\s+'+re.escape(label)+r'(?:\s*[1-9]/)?\s*$'
    found=[(line,re.search(pattern,line)) for line in text.splitlines() if re.search(pattern,line)]
    if len(found)!=1:raise ValueError('Annual source row not unique: '+label)
    return found[0][0],found[0][1].groups()
def production(page,year,measure):
    words=page.extract_words();low,high=(200,330) if measure=='การผลิต' else (600,750)
    anchors=[w for w in words if w['text']==str(year) and w['x0']>520 and low<w['top']<high]
    if len(anchors)!=1:raise ValueError('Production/consumption year ambiguous')
    line=sorted([w for w in words if abs(w['top']-anchors[0]['top'])<2],key=lambda w:w['x0'])
    tokens=[w['text'] for w in line]
    if len(tokens)!=15 or tokens[0]!=str(year+543) or tokens[-1]!=str(year):raise ValueError('Product row shape changed')
    return ' '.join(tokens),tokens[1:-1]
def main():
    import pdfplumber
    pdf=ROOT/'data/raw/dede/balance-2023/source.pdf';meta=json.loads((pdf.parent/'manifest.json').read_text())
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('PDF hash changed')
    path=ROOT/'build/nso/report.json';rows=json.loads(path.read_text(encoding='utf-8'))['rows'];checks=[]
    with pdfplumber.open(pdf) as d:
        supply=d.pages[26].extract_text();prod=d.pages[49];imports=d.pages[53].extract_text()
        if not all(s in supply for s in ('TABLE 2','PRIMARY ENERGY SUPPLY','ktoe','2019 2020 2021 2022 2023')):raise ValueError('Supply context changed')
        pt=prod.extract_text()
        if not all(s in pt for s in ('TABLE 25','million litre','Excluding HSD and Fuel oil consumption for electricity generation')):raise ValueError('Production scope changed')
        volume,value=imports.split('TABLE 31',1)
        if 'million litre' not in volume or 'million Baht' not in value:raise ValueError('Import units changed')
        for r in rows:
            y=r['reference_year'];table=r['table_id'];label=r['label']
            if y not in (2022,2023):continue
            if table=='13.5' and label in SUPPLY:
                if r['unit']!='10^3 ton of oil equivalent':raise ValueError('Supply unit mismatch')
                line,values=annual_line(supply,SUPPLY[label]);raw=values[y-2019];page=27;source_table='2'
            elif table=='13.6':
                if r['unit']!='Million litre':raise ValueError('Product unit mismatch')
                line,values=production(prod,y,r['measure']);raw=values[PRODUCTS[label]];page=50;source_table='25'
            elif table=='13.7':
                text=volume if r['unit']=='Million litre' else value if r['unit']=='Million Baht' else None
                if text is None:raise ValueError('Import unit mismatch')
                line,values=annual_line(text,IMPORTS[label]);raw=values[y-2019];page=54;source_table='30' if text==volume else '31'
            else:continue
            if raw=='-':raise ValueError('Missing cell cannot be zero')
            val=amount(raw);delta=Decimal(r['amount'])-val
            checks.append({**{k:r[k] for k in ('table_id','reference_year','label','measure','unit')},'nso_observation_id':r['observation_id'],'nso_source_sha256':r['source_sha256'],'nso_value':r['amount'],'dede_value':str(val),'difference':str(delta),'exact_displayed_value_match':delta==0,'pdf_page':page,'source_table':source_table,'raw_cell':raw,'source_row_text':line})
    result={'comparisons':checks,'compared_unique':len(checks),'exact_displayed_matches':sum(c['exact_displayed_value_match'] for c in checks),'source':meta,'nso_report_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_values_changed':False,'independent_measurements_verified':0,'excluded':'Renewable primary supply has different aggregation; no automatic sum. Percentages not derived and counted as source comparisons.'}
    (ROOT/'evidence/nso-dede-tables.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('comparisons','source')},indent=2))
if __name__=='__main__':main()
