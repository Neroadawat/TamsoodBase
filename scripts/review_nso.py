"""Check explicitly additive NSO table sections with displayed-precision tolerance."""
import hashlib
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def totals(rows):
    groups=defaultdict(list)
    # 13.5 contains nested subtotals; 13.8 mixes volume and mass. Never sum them blindly.
    for row in rows:
        if row['table_id'] in ('13.6','13.7','13.10'):
            groups[(row['table_id'],row['measure'],row['reference_year'],row['unit'])].append(row)
    checks=[]
    for (table,measure,year,unit),group in sorted(groups.items()):
        total=[r for r in group if r['label']=='รวมยอด'];parts=[r for r in group if r['label']!='รวมยอด']
        if len(total)!=1 or not parts:raise ValueError('Missing total or components')
        values=[Decimal(r['raw_value']) for r in group]
        tolerance=sum(Decimal(1).scaleb(v.as_tuple().exponent)/2 for v in values)
        delta=Decimal(total[0]['amount'])-sum(Decimal(r['amount']) for r in parts)
        checks.append(dict(table_id=table,measure=measure,year=year,unit=unit,total=total[0]['amount'],
                           delta=str(delta),tolerance=str(tolerance),passed=abs(delta)<=tolerance,
                           observation_ids=[r['observation_id'] for r in group]))
    return checks


def main():
    path=ROOT/'build/nso/report.json';body=path.read_bytes();report=json.loads(body)
    checks=totals(report['rows'])
    result=dict(input_sha256=hashlib.sha256(body).hexdigest(),checks=checks,checks_count=len(checks),
                passed_count=sum(c['passed'] for c in checks),
                limitations=['Internal arithmetic consistency only; not independent source accuracy',
                             'No data values corrected; rounding tolerance based on displayed decimal places',
                             'No summation across units, nested subtotals or different source boundaries'])
    (ROOT/'evidence/nso-total-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"NSO additive checks: {result['passed_count']}/{len(checks)} within displayed-precision tolerance")
    if not all(c['passed'] for c in checks):raise SystemExit(1)


if __name__=='__main__':main()
