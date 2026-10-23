"""Local, read-only data explorer over the reviewed DMF snapshot."""
import argparse
import csv
import io
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
if __package__:
    from .reusable_api import catalog as reference_catalog, export_csv as reference_csv
else:
    from reusable_api import catalog as reference_catalog, export_csv as reference_csv

ROOT=Path(__file__).resolve().parents[1]
LABELS={'production-oil':'น้ำมันดิบ','production-condensate':'คอนเดนเสท','production-natural-gas':'ก๊าซธรรมชาติ'}
STATUSES={'SINGLETON','EXACT_REPRESENTATIVE','EXCLUDE_EXACT_COPY','HOLD_CONFLICT'}


def database():
    run=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
    path=ROOT/'build/dmf'/run/'candidates.sqlite'
    con=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
    con.row_factory=sqlite3.Row
    return run,con


def with_units(row,run):
    meta=json.loads((ROOT/'data/raw/dmf'/run/(row['package']+'.metadata.json')).read_bytes())['result']
    row['metadata_multiplier']=meta.get('unit_of_multiplier','')
    row['unit_label']=(row['metadata_multiplier'] or '')+(row.get('metadata_unit') or '')
    row['unit_time_basis']='UNCONFIRMED'
    row['snapshot_run_id']=run
    return row


def selection(params):
    clauses=[];values=[]
    product=params.get('product','')
    if product:
        if product not in LABELS: raise ValueError('Unknown product')
        clauses.append('c.package=?');values.append(product)
    area=params.get('area','')
    if area:
        if area not in ('บนบก','ในทะเล'): raise ValueError('Unknown area')
        clauses.append('c.area=?');values.append(area)
    year=params.get('year','')
    if year:
        if not year.isdigit() or not 1900<=int(year)<=2100: raise ValueError('Invalid year')
        clauses.append('c.year_ce=?');values.append(int(year))
    status=params.get('status','eligible')
    if status=='eligible': clauses.append("d.status IN ('SINGLETON','EXACT_REPRESENTATIVE')")
    elif status in STATUSES: clauses.append('d.status=?');values.append(status)
    elif status!='all': raise ValueError('Unknown status')
    query=params.get('q','').strip()
    if len(query)>160: raise ValueError('Search too long')
    if query:
        clauses.append('(c.source_group LIKE ? ESCAPE "\\" OR c.block_label LIKE ? ESCAPE "\\")')
        escaped=query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
        values.extend(['%'+escaped+'%']*2)
    return (' WHERE '+' AND '.join(clauses) if clauses else ''),values


FROM=' FROM candidate c JOIN duplicate_disposition d USING(package,source_line) JOIN resource r USING(package)'
FIELDS='c.package,c.source_line,c.year_ce,c.month,c.area,c.block_label,c.source_group,c.raw_value,c.amount_column,c.review_status,d.status AS duplicate_status,r.metadata_unit,r.url,r.csv_sha256,r.acquired_at'


def records(params,export=False):
    where,values=selection(params)
    run,con=database()
    try:
        total=con.execute('SELECT COUNT(*)'+FROM+where,values).fetchone()[0]
        if export:
            result=[dict(r) for r in con.execute('SELECT '+FIELDS+FROM+where+' ORDER BY c.package,c.year_ce DESC,c.month DESC,c.source_line',values)]
            # Metadata is shared by package, so read it only once per package.
            enriched={}
            for row in result:
                if row['package'] not in enriched:
                    sample=with_units(dict(row),run)
                    enriched[row['package']]={k:sample[k] for k in ('metadata_multiplier','unit_label','unit_time_basis','snapshot_run_id')}
                row.update(enriched[row['package']])
            return result
        page=int(params.get('page','1'))
        if not 1<=page<=100000: raise ValueError('Invalid page')
        rows=con.execute('SELECT '+FIELDS+FROM+where+' ORDER BY c.year_ce DESC,c.month DESC,c.package,c.source_line LIMIT 30 OFFSET ?',values+[(page-1)*30]).fetchall()
        return {'run_id':run,'total':total,'page':page,'page_size':30,'rows':[with_units(dict(r),run) for r in rows]}
    finally: con.close()


def summary():
    run,con=database()
    try:
        report=json.loads((ROOT/'build/dmf'/run/'review-report.json').read_text(encoding='utf-8'))
        quality=json.loads((ROOT/'build/dmf'/run/'quality-report.json').read_text(encoding='utf-8'))
        return {'run_id':run,'acquired_at':con.execute('SELECT acquired_at FROM resource LIMIT 1').fetchone()[0],
            'report':report,'quality':quality,
            'years':[r[0] for r in con.execute('SELECT DISTINCT year_ce FROM candidate ORDER BY year_ce DESC')],
            'sources':[with_units(dict(r),run) for r in con.execute('SELECT * FROM resource ORDER BY package')],
            'coverage':[dict(r) for r in con.execute('SELECT year_ce,COUNT(*) AS n FROM deduplicated_candidates GROUP BY year_ce ORDER BY year_ce')]}
    finally: con.close()


def detail(package,line):
    if package not in LABELS or line<2: raise ValueError('Invalid record')
    run,con=database()
    try:
        row=con.execute('''SELECT c.*,d.status AS duplicate_status,s.raw_json FROM traceable_candidate c
             JOIN duplicate_disposition d USING(package,source_line) JOIN staging s USING(package,source_line)
             WHERE c.package=? AND c.source_line=?''',(package,line)).fetchone()
        if row is None: raise LookupError('Record not found')
        row=with_units(dict(row),run);row['raw_fields']=json.loads(row.pop('raw_json'))
        row['related']=[dict(r) for r in con.execute('''SELECT c.source_line,c.raw_value,s.raw_json,d.status
           FROM candidate c JOIN staging s USING(package,source_line)
           JOIN duplicate_disposition d USING(package,source_line)
           WHERE c.package=? AND c.identity_sha256=? ORDER BY c.source_line''',(package,row['identity_sha256']))]
        row['run_id']=run
        row['unit_status']='ยังไม่ยืนยันฐานเวลาตลอดชุดข้อมูล'
        report=json.loads((ROOT/'build/dmf'/run/'review-report.json').read_text(encoding='utf-8'))
        row['conflict_investigation']=next((item for item in report.get('conflict_investigations',[])
            if item['package']==package and item['identity_sha256']==row['identity_sha256']),None)
        return row
    finally: con.close()


def csv_export(rows):
    fields=['package','source_line','year_ce','month','area','block_label','source_group','raw_value','amount_column','metadata_unit','metadata_multiplier','unit_label','unit_time_basis','snapshot_run_id','review_status','duplicate_status','url','csv_sha256','acquired_at']
    out=io.StringIO(newline='');writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader()
    for row in rows:
        # Neutralize spreadsheet formulas in text while retaining positive numeric values.
        safe={k:("'"+str(v) if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')) else v) for k,v in row.items()}
        writer.writerow(safe)
    return ('\ufeff'+out.getvalue()).encode('utf-8')


def report_pilot():
    path=ROOT/'build/report-pilot/report.json'
    if not path.exists(): return {'rows':[],'row_count':0,'competition_accepted':0}
    return json.loads(path.read_text(encoding='utf-8'))


def reports():
    result=[]
    for folder,title in [('report-pilot','ไทยออยล์ · รายงาน 2024'),('sprc-report','SPRC · รายงาน 2024')]:
        path=ROOT/'build'/folder/'report.json'
        if path.exists():
            report=json.loads(path.read_text(encoding='utf-8'));report['display_name']=title
            result.append(report)
    return {'sources':result,'competition_accepted':0}


def eppo_records(params):
    report=json.loads((ROOT/'build/eppo/report.json').read_text(encoding='utf-8'))
    dataset=params.get('dataset','11_13');year=params.get('year','2024');query=params.get('q','').strip().casefold()
    page=int(params.get('page','1'))
    if dataset not in ('11_13','11_14') or page<1 or page>10000 or (year and (not year.isdigit() or not 1900<=int(year)<=2100)):
        raise ValueError('Invalid EPPO filters')
    rows=[r for r in report['rows'] if r['dataset_id']==dataset and (not year or r['reference_year']==int(year)) and (not query or query in r['subject'].casefold())]
    return dict(rows=rows[(page-1)*40:page*40],total=len(rows),page=page,page_size=40,
        counts_by_dataset=report['counts_by_dataset'],limitations=report['limitations'])


class Handler(BaseHTTPRequestHandler):
    def respond(self,body,kind='application/json; charset=utf-8',status=200,headers=None):
        if not isinstance(body,bytes): body=json.dumps(body,ensure_ascii=False).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type',kind)
        self.send_header('Content-Length',str(len(body)));self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        for k,v in (headers or {}).items(): self.send_header(k,v)
        self.end_headers();self.wfile.write(body)

    def do_GET(self):
        parsed=urlparse(self.path);params={k:v[0] for k,v in parse_qs(parsed.query).items()}
        try:
            if parsed.path=='/api/summary': return self.respond(summary())
            if parsed.path=='/api/report-pilot': return self.respond(report_pilot())
            if parsed.path=='/api/reports': return self.respond(reports())
            if parsed.path=='/api/eppo': return self.respond(eppo_records(params))
            if parsed.path=='/api/nso':
                return self.respond(json.loads((ROOT/'build/nso/report.json').read_text(encoding='utf-8')))
            if parsed.path=='/api/product-inventory':
                return self.respond(json.loads((ROOT/'build/product-inventory/report.json').read_text(encoding='utf-8')))
            if parsed.path=='/api/nso-comparison':
                return self.respond(json.loads((ROOT/'evidence/nso-dede-comparison.json').read_text(encoding='utf-8')))
            if parsed.path=='/api/reference': return self.respond(reference_catalog(params))
            if parsed.path=='/api/reference.json': return self.respond(reference_catalog(params,True),headers={'Content-Disposition':'attachment; filename="tamsood-reference.json"'})
            if parsed.path=='/api/reference.csv': return self.respond(reference_csv(params),'text/csv; charset=utf-8',headers={'Content-Disposition':'attachment; filename="tamsood-reference.csv"'})
            if parsed.path=='/api/records': return self.respond(records(params))
            if parsed.path=='/api/record': return self.respond(detail(params.get('package',''),int(params.get('line','0'))))
            if parsed.path=='/api/export':
                return self.respond(csv_export(records(params,True)),'text/csv; charset=utf-8',headers={'Content-Disposition':'attachment; filename="tamsood-candidates.csv"'})
            paths={'/':('index.html','text/html; charset=utf-8'),'/app.js':('app.js','text/javascript; charset=utf-8'),'/style.css':('style.css','text/css; charset=utf-8')}
            if parsed.path not in paths: return self.respond({'error':'Not found'},status=404)
            filename,kind=paths[parsed.path];return self.respond((ROOT/'web'/filename).read_bytes(),kind)
        except (ValueError,LookupError) as error: self.respond({'error':str(error)},status=400)
        except Exception:
            self.respond({'error':'Data unavailable. Run the project pipeline first.'},status=503)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'TamsoodBase explorer: http://127.0.0.1:{server.server_port}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
