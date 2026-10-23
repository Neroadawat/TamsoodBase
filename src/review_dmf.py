"""Conservative duplicate disposition and bounded report spot-check for DMF CSVs."""
import csv
import calendar
import hashlib
import json
import sqlite3
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def classify(rows):
    """Exact payload equality only. Conflicting groups have no winner."""
    if len(rows)==1:
        return {rows[0]['source_line']: ('SINGLETON',None)}
    payloads={json.dumps(json.loads(r['raw_json']),sort_keys=True,ensure_ascii=False) for r in rows}
    if len(payloads)!=1:
        return {r['source_line']: ('HOLD_CONFLICT',None) for r in rows}
    representative=min(r['source_line'] for r in rows)
    return {r['source_line']: ('EXACT_REPRESENTATIVE',None) if r['source_line']==representative
            else ('EXCLUDE_EXACT_COPY',representative) for r in rows}


def investigation(rows):
    """A pattern for prioritizing review, never proof of non-overlapping subperiods."""
    days=[int(Decimal(r['production_days'])) for r in rows]
    month_days=calendar.monthrange(rows[0]['year_ce'],rows[0]['month'])[1]
    pattern='POSSIBLE_SUBPERIOD' if sum(days)==month_days else 'DAYS_EXCEED_MONTH' if sum(days)>month_days else 'PARTIAL_OR_OVERLAPPING_UNKNOWN'
    return {'identity_sha256':rows[0]['identity_sha256'],'package':rows[0]['package'],
        'source_group':rows[0]['source_group'],'year_ce':rows[0]['year_ce'],'month':rows[0]['month'],
        'source_lines':[r['source_line'] for r in rows],'production_days':days,'sum_days':sum(days),
        'calendar_days':month_days,'pattern':pattern,'disposition':'HOLD_CONFLICT',
        'automatic_merge_allowed':False,
        'reason':'Days adding to a calendar month do not establish non-overlapping dates or compatible rate denominators'}


def review():
    run=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
    out=ROOT/'build/dmf'/run
    evidence_path=ROOT/'evidence/dmf-report-2026-01-sample.json'
    evidence_bytes=evidence_path.read_bytes()
    evidence=json.loads(evidence_bytes)
    con=sqlite3.connect(out/'candidates.sqlite');con.row_factory=sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    # Verify original bytes and metadata before deriving dispositions.
    manifest=json.loads((ROOT/'data/raw/dmf'/run/'manifest.json').read_text(encoding='utf-8'))
    for entry in manifest['packages']:
        for suffix,hash_key in [('.csv','csv_sha256'),('.metadata.json','metadata_sha256')]:
            if hashlib.sha256((ROOT/'data/raw/dmf'/run/(entry['package']+suffix)).read_bytes()).hexdigest()!=entry[hash_key]:
                raise ValueError('Original snapshot hash mismatch')
    con.executescript('''
    DROP VIEW IF EXISTS deduplicated_candidates;
    DROP TABLE IF EXISTS duplicate_disposition;
    CREATE TABLE duplicate_disposition (
      package TEXT NOT NULL,source_line INTEGER NOT NULL,status TEXT NOT NULL,
      representative_line INTEGER,PRIMARY KEY(package,source_line),
      FOREIGN KEY(package,source_line) REFERENCES candidate);
    CREATE VIEW deduplicated_candidates AS SELECT c.*,d.status AS duplicate_status
      FROM traceable_candidate c JOIN duplicate_disposition d USING(package,source_line)
      WHERE d.status IN ('SINGLETON','EXACT_REPRESENTATIVE');
    ''')
    totals=Counter();package_reports=[];investigations=[]
    for package in sorted({e['package'] for e in manifest['packages']}):
        groups={}
        for row in con.execute('SELECT * FROM candidate JOIN staging USING(package,source_line) WHERE package=? ORDER BY source_line',(package,)):
            groups.setdefault(row['identity_sha256'],[]).append(dict(row))
        counts=Counter();conflicting_groups=0;exact_groups=0
        for rows in groups.values():
            dispositions=classify(rows)
            statuses={v[0] for v in dispositions.values()}
            conflicting_groups+=int('HOLD_CONFLICT' in statuses)
            exact_groups+=int('EXACT_REPRESENTATIVE' in statuses)
            if 'HOLD_CONFLICT' in statuses: investigations.append(investigation(rows))
            for line,(status,representative) in dispositions.items():
                con.execute('INSERT INTO duplicate_disposition VALUES(?,?,?,?)',(package,line,status,representative))
                counts[status]+=1
        totals.update(counts)
        package_reports.append({'package':package,'row_dispositions':dict(counts),
                                'conflict_groups':conflicting_groups,'exact_copy_groups':exact_groups})
    with (out/'duplicate-disposition.csv').open('w',encoding='utf-8-sig',newline='') as f:
        cursor=con.execute('''SELECT c.package,c.source_line,d.status,d.representative_line,
          c.identity_sha256,c.year_ce,c.month,c.area,c.block_label,c.source_group,c.raw_value,s.raw_json
          FROM candidate c JOIN duplicate_disposition d USING(package,source_line)
          JOIN staging s USING(package,source_line) WHERE d.status!='SINGLETON'
          ORDER BY c.package,c.identity_sha256,c.source_line''')
        writer=csv.writer(f);writer.writerow([d[0] for d in cursor.description]);writer.writerows(cursor)
    year,month=map(int,evidence['period'].split('-'))
    checks=[]
    for selected in evidence['rows']:
        for package in sorted({e['package'] for e in manifest['packages']}):
            rows=con.execute('''SELECT * FROM candidate WHERE package=? AND year_ce=? AND month=?
               AND area=? AND source_group=?''',(package,year,month,selected['area'],selected['source_group'])).fetchall()
            check={'package':package,'period':evidence['period'],'source_group':selected['source_group'],
                   'report_url':evidence['source_url'],'evidence_artifact_sha256':hashlib.sha256(evidence_bytes).hexdigest()}
            if len(rows)!=1:
                check.update(status='HOLD_AMBIGUOUS_MATCH',candidate_matches=len(rows))
            else:
                row=rows[0];col=row['amount_column']
                difference=abs(Decimal(row['raw_value'])-Decimal(selected[col]))
                # Strictly inside half a displayed unit; exact half-ties stay pending.
                match=difference < Decimal('0.005')
                check.update(source_line=row['source_line'],csv_value=row['raw_value'],report_value=selected[col],
                    absolute_difference=str(difference),numeric_match_at_display_precision=match,
                    csv_block=row['block_label'],report_block=selected['block'],
                    exact_block_match=row['block_label']==selected['block'],
                    report_unit=evidence['units_as_displayed'][col],
                    status='SPOTCHECK_VALUE_MATCH' if match else 'HOLD_VALUE_MISMATCH')
            checks.append(check)
    con.commit()
    count=con.execute('SELECT COUNT(*) FROM deduplicated_candidates').fetchone()[0]
    cursor=con.execute('SELECT * FROM deduplicated_candidates ORDER BY package,source_line')
    with (out/'deduplicated-candidates.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow([d[0] for d in cursor.description]);writer.writerows(cursor)
    con.close()
    report={'run_id':run,'policy':'Exact full-source-row equality; hold every row in a conflicting identity group',
            'packages':package_reports,'total_row_dispositions':dict(totals),
            'deduplicated_candidates_pending_review':count,'competition_accepted':0,
            'unit_review':{'status':'PARTIAL_EVIDENCE_ONLY','report_period':evidence['period'],
                'numeric_sample_matches':sum(c.get('numeric_match_at_display_precision',False) for c in checks),
                'checks':len(checks),'exact_block_matches':sum(c.get('exact_block_match',False) for c in checks),
                'historical_unit_confirmation':False,'monthly_volume_conversion_performed':False,
                'evidence_level':evidence['evidence_level']},'spotchecks':checks,
            'conflict_investigations':investigations,
            'conflict_patterns':dict(Counter(item['pattern'] for item in investigations))}
    (out/'review-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['spotchecks','packages','conflict_investigations']},ensure_ascii=False,indent=2))
    return report


if __name__=='__main__':
    review()
