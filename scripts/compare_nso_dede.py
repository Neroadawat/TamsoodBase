"""Compare the comparable manufacturing sub-sector, not the broader industry total."""
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]


def main():
    raw=ROOT/'data/raw/dede';pdf=raw/'source.pdf';meta=json.loads((raw/'manifest.json').read_text(encoding='utf-8'))
    digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest!=meta['sha256']:raise ValueError('DEDE snapshot changed')
    text=PdfReader(pdf).pages[7].extract_text(extraction_mode='layout')
    match=re.search(r'อุตสาหกรรมการผลิต\s+([\d,]+)\s+ktoe',text)
    if not match or '2567' not in text or '134 ktoe' not in text or '140 ktoe' not in text:
        raise ValueError('Manufacturing footnote context changed')
    report=json.loads((ROOT/'build/nso/report.json').read_text(encoding='utf-8'))
    row=[r for r in report['rows'] if r['table_id']=='13.10' and r['measure']=='จำนวน' and r['label']=='รวมยอด' and r['reference_year']==2024]
    if len(row)!=1:raise ValueError('NSO observation not unique')
    row=row[0];nso=Decimal(row['amount']);dede=Decimal(match[1].replace(',',''));delta=nso-dede
    result=dict(scope='One selected 2024 manufacturing energy total; not all273 NSO observations',
                year=2024,unit='10^3 ton of oil equivalent',nso_value=str(nso),dede_preliminary_value=str(dede),
                difference_nso_minus_dede=str(delta),status='MATCH_AT_DISPLAY_PRECISION' if abs(delta)<=1 else 'DIFFERENT_PUBLICATIONS_REVIEW_REQUIRED',
                nso_observation_id=row['observation_id'],nso_source_url=row['source_url'],nso_source_sha256=row['source_sha256'],
                dede_source_url=meta['url'],dede_pdf_sha256=digest,dede_pdf_page=8,dede_locator='Footnote3: manufacturing, excluding mining134 and construction140 ktoe',
                dede_extracted_line=next(line for line in text.splitlines() if match[0] in line),
                source_relationship='NSO republishes DEDE statistics; comparison of publications, not independent measurement',
                interpretation='Difference exceeds rounding; revision and definition must be reviewed. Cause is not established.',
                actions=['Keep both values and their publication context','Do not replace NSO with preliminary DEDE value','Do not compare manufacturing30350 directly with broader industry29261'],
                original_values_changed=False)
    (ROOT/'evidence/nso-dede-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
