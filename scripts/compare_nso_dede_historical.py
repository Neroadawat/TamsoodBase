"""Compare new 2022/2023 manufacturing cells to DEDE 2023 Table14.

Read actual source cells, with year/column/context guards. This adds comparison
evidence only: no new observations, no source corrections or acceptance changes.
"""
from datetime import datetime,timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
LABELS=['ถ่านหิน','น้ำมันสำเร็จรูป','ก๊าซธรรมชาติ','ไฟฟ้า','พลังงานหมุนเวียน','รวมยอด']

def cells(page):
    text=page.extract_text()
    if 'TABLE 14' not in text or 'MANUFACTURING' not in text or 'ktoe' not in text:
        raise ValueError('Table/year/unit context missing')
    words=page.extract_words();result={}
    for year in (2022,2023):
        anchors=[w for w in words if w['text']==str(year) and w['x0']>520 and 600<w['top']<750]
        if len(anchors)!=1:raise ValueError('Year row not unique')
        line=sorted([w for w in words if abs(w['top']-anchors[0]['top'])<2],key=lambda w:w['x0'])
        tokens=[w['text'] for w in line]
        if len(tokens)!=9 or tokens[0]!=str(year+543) or tokens[-1]!=str(year) or tokens[6]!='-':
            raise ValueError('Manufacturing row shape changed')
        raw=tokens[1:6]+[tokens[7]]
        if any(not re.fullmatch(r'\d{1,3}(?:,\d{3})*',s) for s in raw):raise ValueError('Unexpected numeric cell')
        values=[Decimal(s.replace(',','')) for s in raw]
        if sum(values[:5])!=values[5]:raise ValueError('Manufacturing components do not reconcile')
        result[year]=list(zip(raw,values))
    return result

def main():
    import pdfplumber
    folder=ROOT/'data/raw/dede/balance-2023';pdf=folder/'source.pdf'
    digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
    manifest_path=folder/'manifest.json'
    if manifest_path.exists():
        manifest=json.loads(manifest_path.read_text())
        if digest!=manifest['sha256']:raise ValueError('DEDE PDF hash changed')
    else:
        manifest={'url':'https://www.dede.go.th/uploads/2566_forweb_b67cef3cc6.pdf',
          'catalog_url':'https://pei.dede.go.th/en/dataset/2566-energy-balance-of-thailand-2023',
          'acquired_at':datetime.now(timezone.utc).isoformat(),'sha256':digest,
          'rights_status':'CATALOG_CC_ATTRIBUTION_VERSION_NOT_SPECIFIED','method':'HTTPS download with certificate validation; no raw redistribution'}
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    with pdfplumber.open(pdf) as document:values=cells(document.pages[37])
    nso_path=ROOT/'build/nso/report.json';rows=json.loads(nso_path.read_text(encoding='utf-8'))['rows'];comparisons=[]
    for year,items in values.items():
        for label,(raw,value) in zip(LABELS,items):
            matches=[r for r in rows if r['table_id']=='13.10' and r['reference_year']==year and r['measure']=='จำนวน' and r['label']==label and r['unit']=='10^3 ton of oil equivalent']
            if len(matches)!=1:raise ValueError('NSO context not unique')
            row=matches[0];delta=Decimal(row['amount'])-value
            comparisons.append({**{k:row[k] for k in ('observation_id','table_id','reference_year','measure','label','unit')},
              'nso_observation_id':row['observation_id'],'nso_source_sha256':row['source_sha256'],'nso_value':row['amount'],
              'dede_raw_value':raw,'dede_value':str(value),'difference':str(delta),'exact_displayed_value_match':delta==0,
              'pdf_page':38,'printed_page':'24','table':'14','column_index':LABELS.index(label)+1})
    result={'checked_at':datetime.now(timezone.utc).isoformat(),'comparisons':comparisons,'compared_unique':len(comparisons),
      'exact_displayed_matches':sum(c['exact_displayed_value_match'] for c in comparisons),
      'nso_report_sha256':hashlib.sha256(nso_path.read_bytes()).hexdigest(),'source':manifest,
      'source_observations_added':0,'source_values_changed':False,'independent_measurements_verified':0,
      'limitation':'NSO republishes DEDE; publication consistency only. Quantity cells only, no derived percentages counted.'}
    (ROOT/'evidence/nso-dede-historical.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='comparisons'},indent=2))

if __name__=='__main__':main()
