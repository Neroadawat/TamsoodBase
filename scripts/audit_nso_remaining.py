"""Review remaining cells without guessing missing cells or silently fixing publisher years."""
from decimal import Decimal
import hashlib,json,re
from pathlib import Path
from compare_nso_dede_tables import IMPORTS,PRODUCTS,amount
ROOT=Path(__file__).resolve().parents[1]

def percentage(value,total,reported):
    if total<=0:raise ValueError('Nonpositive denominator')
    expected=value/total*100
    return expected,abs(expected-reported)<=Decimal('0.000000005')

def main():
    import pdfplumber
    report=ROOT/'build/nso/report.json'
    rows=json.loads(report.read_text(encoding='utf8'))['rows']
    pdf=ROOT/'data/raw/dede/balance-2024/source.pdf'
    meta=json.loads(pdf.with_name('manifest.json').read_text(encoding='utf8'))
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('Changed report')
    checks=[]
    with pdfplumber.open(pdf) as d:
        text=d.pages[55].extract_text()
        if not all(x in text for x in ('2020 2021 2022 2023 2024','million litre','million Baht')):raise ValueError('Import context changed')
        # Headers occur after both numeric tables in this PDF: split on unit marker.
        volume,value=text.split('TABLE 31',1)
        for r in rows:
            if r['reference_year']!=2024 or r['table_id'] not in ('13.6','13.7'):continue
            c={'nso_observation_id':r['observation_id'],'table_id':r['table_id'],'label':r['label'],'measure':r['measure'],'nso_value':r['amount'],'unit':r['unit']}
            if r['table_id']=='13.6':
                words=d.pages[51].extract_words();top=295.99 if r['measure']=='การผลิต' else 620.9167
                line=sorted([w for w in words if abs(w['top']-top)<2],key=lambda w:w['x0'])
                tokens=[w['text'] for w in line]
                if tokens[0]!='2567' or tokens[-1]!='2034':raise ValueError('Publisher year anomaly changed; review again')
                c.update(status='HOLD_PUBLISHER_YEAR_CONFLICT',pdf_page=52,source_row=' '.join(tokens),thai_year=2567,printed_western_year=2034)
            else:
                label=IMPORTS[r['label']]
                # Value-table chart overlaps text extraction; use only each physical table band.
                low,high=(165,355) if r['unit']=='Million litre' else (530,722)
                words=[w for w in d.pages[55].extract_words() if low<w['top']<high]
                candidates=[]
                for anchor in [w for w in words if 375<w['x0']<405]:
                    line=' '.join(w['text'] for w in sorted([w for w in words if abs(w['top']-anchor['top'])<2],key=lambda w:w['x0']))
                    if re.search(re.escape(label)+r'\s*(?:[1-9]/)?(?:\s|$)',line):candidates.append((line,anchor['text']))
                if len(candidates)!=1:raise ValueError('Import label ambiguous: '+label)
                line,raw=candidates[0]
                c.update(pdf_page=56,raw_cell=raw,source_row=line)
                if raw=='-':c['status']='HOLD_DASH_NOT_NUMERIC_ZERO'
                else:
                    val=amount(raw);delta=Decimal(r['amount'])-val
                    c.update(dede_value=str(val),difference=str(delta),status='EXACT_PUBLICATION_MATCH' if delta==0 else 'SOURCE_DIVERGENCE_REVIEW_REQUIRED')
            checks.append(c)
    derived=[]
    for r in rows:
        if r['table_id']!='13.10' or r['measure']!='ร้อยละ':continue
        group=[x for x in rows if x['table_id']=='13.10' and x['reference_year']==r['reference_year'] and x['measure']!='ร้อยละ']
        numerator=[x for x in group if x['label']==r['label']]
        total=[x for x in group if x['label']=='รวมยอด']
        if len(numerator)!=1 or len(total)!=1:raise ValueError('Formula identity ambiguous')
        expected,ok=percentage(Decimal(numerator[0]['amount']),Decimal(total[0]['amount']),Decimal(r['amount']))
        derived.append({'nso_observation_id':r['observation_id'],'numerator_id':numerator[0]['observation_id'],'denominator_id':total[0]['observation_id'],'formula':'quantity / annual total * 100','expected':str(expected),'reported':r['amount'],'within_8_decimal_rounding':ok,'status':'DERIVED_CONSISTENCY_ONLY','direct_external_comparison':False})
    from collections import Counter
    result={'source':meta,'nso_report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),'checks':checks,'status_counts':dict(Counter(c['status'] for c in checks)),'derived_checks':derived,'derived_passed':sum(c['within_8_decimal_rounding'] for c in derived),'source_values_changed':False,'limitation':'No repair of publisher year2034 to2024; no dash-to-zero substitution; derived ratios are not direct external observations.'}
    (ROOT/'evidence/nso-remaining-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result['status_counts']));print('derived',result['derived_passed'],len(derived))
if __name__=='__main__':main()

