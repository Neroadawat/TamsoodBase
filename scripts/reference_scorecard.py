"""Measure the selected release; never estimate competition scores or national coverage."""
import hashlib
import json
import re
from collections import Counter,defaultdict
from datetime import datetime,timezone
from decimal import Decimal,InvalidOperation
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def measure(rows,manifest):
    required=('observation_id','source_metric_id','reference_year','raw_value','raw_unit_label',
              'scaled_amount','unit_code','source_scope','source_url','pdf_sha256','pdf_page',
              'policy_version','trace_verification','decision','rights_status')
    missing=[];bad_scaling=[];coverage=defaultdict(Counter)
    for row in rows:
        absent=[field for field in required if row.get(field) is None or row.get(field)=='']
        if absent:missing.append({'observation_id':row.get('observation_id'),'fields':absent})
        try:
            raw_text=row['raw_value']
            if not re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?',raw_text):
                raise ValueError('Invalid grouped source number')
            raw=Decimal(raw_text.replace(',',''));scale=Decimal(row['scale_factor']);amount=Decimal(row['scaled_amount'])
            valid=all(n.is_finite() for n in (raw,scale,amount)) and scale>0 and amount>=0 and raw*scale==amount
        except (KeyError,InvalidOperation,ValueError,TypeError):valid=False
        if not valid:bad_scaling.append(row.get('observation_id'))
        coverage[(row['publisher'],row['reference_year'])][row['decision']]+=1
    ids=Counter(row['observation_id'] for row in rows)
    accepted=[row for row in rows if row['decision']=='ACCEPTED_REFERENCE']
    metric_years=defaultdict(set)
    for row in rows:metric_years[(row['pdf_sha256'],row['source_metric_id'])].add(row['reference_year'])
    # Gaps only inside the selected series' observed range, not promised national coverage.
    gaps=[{'document':doc,'metric':metric,'missing_years':sorted(set(range(min(years),max(years)+1))-years)}
          for (doc,metric),years in sorted(metric_years.items()) if set(range(min(years),max(years)+1))-years]
    checks={'required_context_complete':not missing,'exact_scale_arithmetic':not bad_scaling,
            'unique_observation_ids':all(n==1 for n in ids.values()),
            'release_membership':all(row['release_id']==manifest['release_id'] for row in rows),
            'decision_accounting':len(accepted)==manifest['accepted_reference'] and len(rows)-len(accepted)==manifest['held_context'],
            'source_count_accounting':len(rows)==manifest['source_observations'],
            'trace_marker_complete':all(row['trace_verification']=='PDF_HASH_AND_REEXTRACTED_COLUMN_MATCH' for row in rows)}
    return {'release_id':manifest['release_id'],'checks':checks,'passed':all(checks.values()),
            'source_observations':len(rows),'accepted_reference':len(accepted),
            'held_context':len(rows)-len(accepted),'publishers':len({r['publisher'] for r in rows}),
            'documents':len({r['pdf_sha256'] for r in rows}),'years':sorted({r['reference_year'] for r in rows}),
            'accepted_kinds':dict(sorted(Counter(r['data_kind'] for r in accepted).items())),
            'coverage':[{'publisher':publisher,'year':year,**dict(sorted(counts.items()))}
                        for (publisher,year),counts in sorted(coverage.items())],
            'selected_series_gaps':gaps,'missing_context':missing,'scale_errors':bad_scaling,
            'duplicate_ids':[key for key,count in ids.items() if count>1],
            'limitations':['Checks concern the selected release, not all available Thai fuel data',
                           'Trace markers are checked here; original PDF re-extraction is a separate recorded check',
                           'Arithmetic consistency is not independent verification of publisher measurements',
                           '97 accepted reference observations are not 97 independent LCI flows',
                           'No competition score, national coverage percentage or human verification is inferred']}


def main():
    path=ROOT/'build/reusable/all-reference.json';body=path.read_bytes()
    manifest=json.loads((path.parent/'manifest.json').read_text(encoding='utf-8'))
    if hashlib.sha256(body).hexdigest()!=manifest['files']['all-reference.json']:
        raise ValueError('Release export hash mismatch')
    result=measure(json.loads(body),manifest)
    result.update(checked_at=datetime.now(timezone.utc).isoformat(),input_sha256=hashlib.sha256(body).hexdigest())
    target=ROOT/'evidence/reference-scorecard.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:result[key] for key in ('passed','source_observations','accepted_reference','held_context','publishers','documents','years')},indent=2))
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
