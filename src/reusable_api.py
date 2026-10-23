"""Read-only, parameterized access to the current typed reference-data release."""
import csv
import io
import json
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
KINDS={'ORGANIZATION_INPUT','ORGANIZATION_OUTPUT','REPORTED_INTENSITY','CONTEXT_METRIC'}


def catalog(params,export=False):
    folder=ROOT/'build/reusable';manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    clauses=['release_id=?'];values=[manifest['release_id']]
    for field,allowed in [('data_kind',KINDS),('decision',{'ACCEPTED_REFERENCE','HOLD_CONTEXT','all'})]:
        value=params.get(field,'ACCEPTED_REFERENCE' if field=='decision' else '')
        if value:
            if value not in allowed: raise ValueError('Unknown '+field)
            if value!='all': clauses.append(field+'=?');values.append(value)
    if params.get('year'):
        value=params['year']
        if not value.isdigit() or not 1900<=int(value)<=2100: raise ValueError('Invalid year')
        clauses.append('reference_year=?');values.append(int(value))
    if params.get('publisher'):
        value=params['publisher']
        publishers={'THAIOIL':'Thai Oil Public Company Limited','SPRC':'Star Petroleum Refining Public Company Limited'}
        if value not in publishers: raise ValueError('Unknown publisher')
        clauses.append('publisher=?');values.append(publishers[value])
    search=params.get('q','').strip()
    if len(search)>160: raise ValueError('Search too long')
    if search:
        clauses.append('(label LIKE ? ESCAPE "\\" OR source_metric_id LIKE ? ESCAPE "\\")')
        literal=search.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
        values.extend(['%'+literal+'%']*2)
    where=' WHERE '+' AND '.join(clauses)
    con=sqlite3.connect((folder/'reference.sqlite').as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
    try:
        count=con.execute('SELECT COUNT(*) FROM reference_catalog'+where,values).fetchone()[0]
        page=int(params.get('page','1'))
        if not 1<=page<=100000: raise ValueError('Invalid page')
        sql='SELECT * FROM reference_catalog'+where+' ORDER BY reference_year DESC,publisher,source_metric_id'
        args=values
        if not export: sql+=' LIMIT 30 OFFSET ?';args=[*values,(page-1)*30]
        cursor=con.execute(sql,args)
        fields=[column[0] for column in cursor.description]
        extras=['redistribution_status','is_normalized_lci_exchange','reference_product_amount','allocation_method']
        rows=[dict(r) for r in cursor]
        for row in rows:
            row.update(redistribution_status='NOT_CLEARED',is_normalized_lci_exchange=False,
                       reference_product_amount=None,allocation_method=None)
        return {'manifest':manifest,'total':count,'page':page,'page_size':30,'fields':fields+extras,'rows':rows}
    finally: con.close()


def export_csv(params):
    data=catalog(params,True);rows=data['rows'];out=io.StringIO(newline='')
    # A header-only export is valid for filters that have no results.
    fields=data['fields']
    writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader()
    for row in rows:
        safe={k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')) else v) for k,v in row.items()}
        writer.writerow(safe)
    return ('\ufeff'+out.getvalue()).encode('utf-8')
