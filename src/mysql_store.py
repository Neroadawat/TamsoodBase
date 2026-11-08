"""Explicit MySQL read store. No fallback to SQLite after a MySQL error.

Read-only DB grants enforce the boundary. JSON representation preserves the API's
source decimal strings; filtering/joins use the project's typed MySQL tables.
"""
from contextlib import closing
from functools import lru_cache
import json
import os


def enabled():
    mode=os.environ.get('TAMSOOD_DATA_BACKEND','sqlite')
    if mode not in ('sqlite','mysql'):raise RuntimeError('Unknown data backend')
    return mode=='mysql'


def connect():
    import pymysql
    password=os.environ.get('TAMSOOD_MYSQL_PASSWORD','')
    if not password or not os.environ.get('TAMSOOD_MYSQL_HOST'):raise RuntimeError('MySQL configuration missing')
    con=pymysql.connect(host=os.environ['TAMSOOD_MYSQL_HOST'],port=int(os.environ.get('TAMSOOD_MYSQL_PORT','3306')),
        user=os.environ.get('TAMSOOD_MYSQL_USER','tamsood_reader'),password=password,database='tamsood_api',charset='utf8mb4',
        connect_timeout=5,read_timeout=30,write_timeout=10,autocommit=False,cursorclass=pymysql.cursors.DictCursor)
    try:
        with con.cursor() as c:c.execute('SET TRANSACTION READ ONLY');c.execute('START TRANSACTION READ ONLY')
        return con
    except Exception:con.close();raise


class Row(dict):
    def __getitem__(self,key):
        return list(self.values())[key] if isinstance(key,int) else super().__getitem__(key)


class Cursor:
    def __init__(self,rows,description):self.rows=[Row(r) for r in rows];self.description=description
    def fetchone(self):return self.rows[0] if self.rows else None
    def fetchall(self):return self.rows
    def __iter__(self):return iter(self.rows)


class Connection:
    def __init__(self):self.connection=connect()
    def execute(self,sql,values=()):
        if not sql.lstrip().upper().startswith('SELECT '):raise ValueError('Read store only accepts SELECT')
        sql=sql.replace('?', '%s')
        with self.connection.cursor() as c:
            c.execute(sql,tuple(values));return Cursor(c.fetchall(),c.description)
    def close(self):self.connection.close()


@lru_cache(maxsize=32)
def artifact(name):
    # Metadata is immutable for the seeded release; new releases use fresh workers.
    with closing(connect()) as con,con.cursor() as c:
        c.execute('SELECT payload FROM artifact WHERE name=%s',(name,));row=c.fetchone()
    if row is None:raise RuntimeError('MySQL artifact missing: '+name)
    return json.loads(row['payload'])


def dataset(name):
    data=dict(artifact(name))
    with closing(connect()) as con,con.cursor() as c:
        c.execute('SELECT o.payload FROM tamsood_supplemental.observation o JOIN row_order r ON r.observation_id=o.observation_id AND r.dataset=%s WHERE o.snapshot_id=%s ORDER BY r.ordinal',
                  (name,data.pop('mysql_snapshot_id')))
        data['rows']=[json.loads(r['payload']) for r in c.fetchall()]
    return data


def like(value):return '%'+value.replace('!','!!').replace('%','!%').replace('_','!_')+'%'


def reference_catalog(params,export=False):
    if __package__:
        from .reusable_api import KINDS
    else:
        from reusable_api import KINDS
    manifest=artifact('reference_manifest');clauses=['v.release_id=%s'];values=[manifest['release_id']]
    for field,allowed in [('data_kind',KINDS),('decision',{'ACCEPTED_REFERENCE','HOLD_CONTEXT','all'})]:
        value=params.get(field,'ACCEPTED_REFERENCE' if field=='decision' else '')
        if value:
            if value not in allowed:raise ValueError('Unknown '+field)
            if value!='all':clauses.append('v.'+field+'=%s');values.append(value)
    if params.get('year'):
        value=params['year']
        if not value.isdigit() or not 1900<=int(value)<=2100:raise ValueError('Invalid year')
        clauses.append('v.reference_year=%s');values.append(int(value))
    if params.get('publisher'):
        publishers={'THAIOIL':'Thai Oil Public Company Limited','SPRC':'Star Petroleum Refining Public Company Limited'}
        if params['publisher'] not in publishers:raise ValueError('Unknown publisher')
        clauses.append('v.publisher=%s');values.append(publishers[params['publisher']])
    search=params.get('q','').strip()
    if len(search)>160:raise ValueError('Search too long')
    if search:
        clauses.append("(LOWER(v.label) LIKE %s ESCAPE '!' OR LOWER(v.source_metric_id) LIKE %s ESCAPE '!')");values.extend([like(search.lower())]*2)
    page=int(params.get('page','1'))
    if not 1<=page<=100000:raise ValueError('Invalid page')
    base=' FROM tamsood_reusable.reference_catalog v JOIN reference_representation p ON p.observation_id=v.observation_id WHERE '+' AND '.join(clauses)
    with closing(connect()) as con,con.cursor() as c:
        c.execute('SELECT COUNT(*) AS n'+base,values);count=c.fetchone()['n']
        query='SELECT p.payload'+base+' ORDER BY v.reference_year DESC,v.publisher,v.source_metric_id';args=list(values)
        if not export:query+=' LIMIT 30 OFFSET %s';args.append((page-1)*30)
        c.execute(query,args);rows=[json.loads(r['payload']) for r in c.fetchall()]
    return dict(manifest=manifest,total=count,page=page,page_size=30,fields=artifact('reference_fields'),rows=rows)


def eppo_records(params):
    dataset=params.get('dataset','11_13');year=params.get('year','2024');search=params.get('q','').strip().casefold();page=int(params.get('page','1'))
    if dataset not in ('11_13','11_14') or not 1<=page<=10000 or (year and (not year.isdigit() or not 1900<=int(year)<=2100)):raise ValueError('Invalid EPPO filters')
    if len(search)>160:raise ValueError('Search too long')
    clauses=['s.dataset_id=%s'];values=[dataset]
    if year:clauses.append('o.reference_year=%s');values.append(int(year))
    if search:clauses.append("LOWER(o.subject) LIKE %s ESCAPE '!'");values.append(like(search))
    base=' FROM tamsood_eppo.observation o JOIN tamsood_eppo.source_snapshot s USING(snapshot_id) JOIN row_order r ON r.observation_id=o.observation_id AND r.dataset=\'eppo\' WHERE '+' AND '.join(clauses)
    with closing(connect()) as con,con.cursor() as c:
        c.execute('SELECT COUNT(*) AS n'+base,values);count=c.fetchone()['n']
        c.execute('SELECT o.payload'+base+' ORDER BY r.ordinal LIMIT 40 OFFSET %s',values+[(page-1)*40]);rows=[json.loads(r['payload']) for r in c.fetchall()]
    report=artifact('eppo')
    return dict(rows=rows,total=count,page=page,page_size=40,counts_by_dataset=report['counts_by_dataset'],limitations=report['limitations'])


def ready():
    try:
        with closing(connect()) as con,con.cursor() as c:
            c.execute("SELECT payload FROM artifact WHERE name='runtime_info'");info=json.loads(c.fetchone()['payload'])
            if not os.environ.get('TAMSOOD_DATASET_RELEASE') or info['dataset_release']!=os.environ['TAMSOOD_DATASET_RELEASE']:return False
            for sql,n in [('SELECT COUNT(*) AS n FROM candidate',info['counts']['dmf']),
                          ('SELECT COUNT(*) AS n FROM tamsood_reusable.reference_catalog',info['counts']['reference']),
                          ('SELECT COUNT(*) AS n FROM tamsood_supplemental.observation',info['counts']['nso']+info['counts']['inventory']),
                          ('SELECT COUNT(*) AS n FROM tamsood_eppo.observation',info['counts']['eppo'])]:
                c.execute(sql)
                if c.fetchone()['n']!=n:return False
        return True
    except Exception:return False
