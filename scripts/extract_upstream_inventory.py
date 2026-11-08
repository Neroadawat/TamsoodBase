"""Retain upstream Tables1–3 separately; missing units and missing feedstock are not zero."""
import hashlib,json,re,sys,unicodedata,sqlite3
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NUMBER=r'\d+(?:\.\d+)?(?:\s*×\s*10\s*[−-]\s*\d+)?'
LINE=re.compile(r'^(.*?)\s+('+NUMBER+r')\s*(kg|kWh|L|m3|g)?$')
def amount(raw):
    parts=re.fullmatch(r'(\d+(?:\.\d+)?)\s*×\s*10\s*[−-]\s*(\d+)',raw)
    value=Decimal(parts[1])*(Decimal(10)**-int(parts[2])) if parts else Decimal(raw)
    if not value.is_finite() or value<0:raise ValueError('Invalid source number')
    return str(value)

def table_rows(text,table,process):
    # Both engines preserve the caption/header, with different space conventions.
    caption=re.search(r'Table\s*'+str(table)+r'\.\s*Life\s*cycle\s*inventory\s*of\s*1000\s*kg\s*'+process+r'\s*production\.',text)
    if not caption:raise ValueError('Table/basis caption changed')
    part=text[caption.end():]
    part=re.split(r'\n3\.1\.[23]\.',part,1)[0]
    rows=[];direction=None
    for line in part.splitlines():
        line=line.strip()
        if line in ('Input','Output'):direction=line.upper();continue
        m=LINE.fullmatch(line)
        if not m:continue
        label,raw,unit=m.groups()
        if not re.search(r'[A-Za-z]',label) or direction is None:continue
        rows.append({'flow':label.strip(),'raw_value':raw,'amount':amount(raw),'unit':unit,'direction':direction,'raw_line':line})
    return rows

def normlabel(label):
    # PDF subscript glyphs can be emitted on separate lines; retain original labels in records.
    return re.sub(r'[^a-z]', '',unicodedata.normalize('NFKD',label).lower())

def main():
    from pypdf import PdfReader
    import pdfplumber
    raw=ROOT/'data/raw/mdpi-9415/pdf-v3';pdf=raw/'source.pdf';meta=json.loads((raw/'manifest.json').read_text())
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('PDF hash changed')
    reader=PdfReader(pdf);records=[];comparisons=[]
    if 'creativecommons.org/licenses/by/4.0/' not in reader.pages[-1].extract_text():raise ValueError('License evidence changed')
    with pdfplumber.open(pdf) as other:
        for table,process,page,expected in ((1,'FFB',5,19),(2,'CPO',6,12),(3,'RBDPO',6,11)):
            text=reader.pages[page-1].extract_text()
            a=table_rows(text,table,process);b=table_rows(other.pages[page-1].extract_text(),table,process)
            if len(a)!=expected or len(b)!=expected:raise ValueError('Table row count changed: '+str(table))
            for index,(left,right) in enumerate(zip(a,b),1):
                if any(left[k]!=right[k] for k in ('amount','unit','direction')) or normlabel(left['flow'])!=normlabel(right['flow']):raise ValueError('PDF engine mismatch: '+left['flow'])
                oid=hashlib.sha256(f'{meta["sha256"]}:{table}:{index}'.encode()).hexdigest()
                record=left|{'observation_id':oid,'process':process,'reference_amount':'1000','reference_unit':'kg','reference_flow':process,'publication_year':2020,'data_period':None,'geography':'Thailand study context','table_id':str(table),'pdf_page':page,'table_data_row':index,'source_url':meta['url']+'#page='+str(page),'source_sha256':meta['sha256'],'doi':meta['doi'],'licence':'CC BY 4.0','role':'REFERENCE_PRODUCT' if left['direction']=='OUTPUT' and left['flow']==process else left['direction'],'status':'SOURCE_REPORTED_UPSTREAM_CANDIDATE' if left['unit'] else 'HOLD_MISSING_UNIT','is_full_lci_dataset':False,'allocation_applied_by_this_project':False}
                records.append(record);comparisons.append({'observation_id':oid,'amount_unit_direction_match':True,'normalized_label_match':True,'source_amount':left['amount'],'unit':left['unit'],'pdf_page':page,'table_id':str(table)})
    issues=[{'process':'FFB','reason':'Land seeding unit absent in Table1','action':'Hold row; do not infer area unit'},
            {'process':'CPO','reason':'FFB input quantity absent in selected Table2','action':'No FFB-to-CPO provider link or mass balance claim'},
            {'process':'RBDPO','reason':'Water reported as0.11kg in Table3','action':'Preserve kg; no silent conversion to m3'},
            {'process':'CPO/FAME','reason':'Economic allocation discussed, application to tabulated quantities unresolved','action':'Do not apply allocation again'},
            {'process':'FAME','reason':'Narrative mentions NaOH while Table4 reports Potassium hydroxide','action':'Preserve table label and record source inconsistency'}]
    result={'source':meta,'rows':records,'issues':issues,'counts':{'observed_cells':len(records),'unit_present':sum(r['unit'] is not None for r in records),'held_missing_unit':sum(r['unit'] is None for r in records),'processes':3},'cross_engine_checks':comparisons,'full_lifecycle_inventory':False,'production_imported':False,'independent_measurements_verified':0,'limitation':'Two PDF extractors agree with visually inspected tables; source-local inventory candidates, not completed or independently reviewed LCI datasets'}
    out=ROOT/'build/upstream-inventory';out.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(':memory:');con.execute('PRAGMA foreign_keys=ON')
    con.executescript('''CREATE TABLE process(process_id TEXT PRIMARY KEY,reference_amount TEXT NOT NULL,reference_unit TEXT NOT NULL,source_sha256 TEXT NOT NULL);
    CREATE TABLE exchange(observation_id TEXT PRIMARY KEY,process_id TEXT NOT NULL REFERENCES process(process_id),direction TEXT NOT NULL CHECK(direction IN ('INPUT','OUTPUT')),role TEXT NOT NULL CHECK(role IN ('INPUT','OUTPUT','REFERENCE_PRODUCT')),amount TEXT NOT NULL,unit TEXT,status TEXT NOT NULL CHECK(status IN ('SOURCE_REPORTED_UPSTREAM_CANDIDATE','HOLD_MISSING_UNIT')),payload TEXT NOT NULL,
      CHECK((status='HOLD_MISSING_UNIT' AND unit IS NULL) OR (status='SOURCE_REPORTED_UPSTREAM_CANDIDATE' AND unit IS NOT NULL)),CHECK(role!='REFERENCE_PRODUCT' OR direction='OUTPUT'));
    CREATE VIEW unit_present_candidate AS SELECT * FROM exchange WHERE status='SOURCE_REPORTED_UPSTREAM_CANDIDATE';''')
    con.executemany('INSERT INTO process VALUES (?,?,?,?)',[(p,'1000','kg',meta['sha256']) for p in ('FFB','CPO','RBDPO')])
    con.executemany('INSERT INTO exchange VALUES (?,?,?,?,?,?,?,?)',[(r['observation_id'],r['process'],r['direction'],r['role'],r['amount'],r['unit'],r['status'],json.dumps(r,ensure_ascii=False)) for r in records])
    actual={oid:json.loads(payload) for oid,payload in con.execute('SELECT observation_id,payload FROM exchange')}
    if actual!={r['observation_id']:r for r in records} or con.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Candidate database roundtrip failed')
    con.commit();negative={}
    for name,sql in [('missing_process',"UPDATE exchange SET process_id='missing'"),('hold_unit',"UPDATE exchange SET status='SOURCE_REPORTED_UPSTREAM_CANDIDATE' WHERE unit IS NULL")]:
        try:con.execute(sql)
        except sqlite3.IntegrityError:negative[name]=True
        else:negative[name]=False
        finally:con.rollback()
    if not all(negative.values()):raise ValueError('Candidate constraint did not reject invalid change')
    with sqlite3.connect(out/'candidate.sqlite') as dest:con.backup(dest)
    con.close()
    result['database_checks']={'roundtrip_rows':len(actual),'foreign_key_violations':0,'negative_checks':negative,'production_migrated':False}
    (out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (ROOT/'evidence/upstream-inventory-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result['counts']))
if __name__=='__main__':main()
