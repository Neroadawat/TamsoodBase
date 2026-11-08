"""Separate SQLite Flow/Unit candidate; lossless source-local identities, no migration."""
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCHEMA='''PRAGMA foreign_keys=ON;
CREATE TABLE source(source_hash TEXT PRIMARY KEY,source_id TEXT NOT NULL,url TEXT NOT NULL,licence TEXT NOT NULL);
CREATE TABLE unit(code TEXT PRIMARY KEY);
CREATE TABLE process(source_hash TEXT NOT NULL,process_id TEXT NOT NULL,reference_amount TEXT NOT NULL,reference_unit TEXT NOT NULL,geography TEXT NOT NULL,boundary TEXT NOT NULL,allocation TEXT NOT NULL,PRIMARY KEY(source_hash,process_id),FOREIGN KEY(source_hash) REFERENCES source(source_hash));
CREATE TABLE flow(flow_id TEXT PRIMARY KEY,source_hash TEXT NOT NULL,name TEXT NOT NULL,unit_code TEXT NOT NULL,flow_type TEXT NULL,compartment TEXT NULL,UNIQUE(source_hash,name,unit_code),UNIQUE(flow_id,source_hash,unit_code),FOREIGN KEY(source_hash) REFERENCES source(source_hash),FOREIGN KEY(unit_code) REFERENCES unit(code));
CREATE TABLE exchange(observation_id TEXT PRIMARY KEY,source_hash TEXT NOT NULL,process_id TEXT NOT NULL,flow_id TEXT NOT NULL,unit_code TEXT NOT NULL,amount TEXT NOT NULL,direction TEXT NOT NULL,role TEXT NOT NULL,source_row INTEGER NOT NULL CHECK(source_row>0),source_column INTEGER NOT NULL CHECK(source_column>0),original_json TEXT NOT NULL,FOREIGN KEY(source_hash,process_id) REFERENCES process(source_hash,process_id),FOREIGN KEY(flow_id,source_hash,unit_code) REFERENCES flow(flow_id,source_hash,unit_code),CHECK((direction='INPUT' AND role='INPUT') OR (direction='OUTPUT' AND role IN ('OUTPUT','REFERENCE_PRODUCT','CO_PRODUCT'))));
CREATE INDEX ix_process_direction ON exchange(source_hash,process_id,direction);
'''


def build():
    path=ROOT/'build/product-inventory/report.json';rows=json.loads(path.read_text(encoding='utf-8'))['rows']
    folder=ROOT/'build/inventory-candidate';folder.mkdir(parents=True,exist_ok=True)
    target=folder/'candidate.sqlite'
    # In-memory build prevents partially replacing the last successful artifact.
    con=sqlite3.connect(':memory:');con.executescript(SCHEMA)
    for r in rows:
        sha=r['source_snapshot_sha256'];flow=hashlib.sha256(json.dumps([sha,r['flow'],r['unit']],ensure_ascii=False).encode()).hexdigest()
        con.execute('INSERT OR IGNORE INTO source VALUES(?,?,?,?)',(sha,'MDPI-SU12229415-T4',r['source_url'],r['licence']))
        con.execute('INSERT OR IGNORE INTO unit VALUES(?)',(r['unit'],))
        con.execute('INSERT OR IGNORE INTO process VALUES(?,?,?,?,?,?,?)',(sha,r['process'],r['reference_amount'],r['reference_unit'],r['geography'],r['boundary'],r['allocation']))
        con.execute('INSERT OR IGNORE INTO flow VALUES(?,?,?,?,NULL,NULL)',(flow,sha,r['flow'],r['unit']))
        con.execute('INSERT INTO exchange VALUES(?,?,?,?,?,?,?,?,?,?,?)',(r['observation_id'],sha,r['process'],flow,r['unit'],r['amount'],r['direction'],r['role'],r['source_row'],r['source_column'],json.dumps(r,ensure_ascii=False,sort_keys=True)))
    actual={r[0]:json.loads(r[1]) for r in con.execute('SELECT observation_id,original_json FROM exchange')}
    if actual!={r['observation_id']:r for r in rows}:raise ValueError('Original payload differs')
    typed={r[0]:r[1:] for r in con.execute('SELECT e.observation_id,p.process_id,f.name,e.unit_code,e.amount,e.direction,e.role,p.reference_amount,p.reference_unit,p.geography,p.boundary,p.allocation,e.source_row,e.source_column FROM exchange e JOIN process p ON p.source_hash=e.source_hash AND p.process_id=e.process_id JOIN flow f ON f.flow_id=e.flow_id')}
    expected_typed={r['observation_id']:(r['process'],r['flow'],r['unit'],r['amount'],r['direction'],r['role'],r['reference_amount'],r['reference_unit'],r['geography'],r['boundary'],r['allocation'],r['source_row'],r['source_column']) for r in rows}
    if typed!=expected_typed:raise ValueError('Typed joined columns differ from source report')
    checks=[]
    for process in ['FAME','H-FAME']:
        for direction in ['INPUT','OUTPUT']:
            ids=sorted(r[0] for r in con.execute('SELECT e.observation_id FROM exchange e JOIN flow f ON f.flow_id=e.flow_id JOIN unit u ON u.code=e.unit_code JOIN process p ON p.source_hash=e.source_hash AND p.process_id=e.process_id WHERE e.process_id=? AND e.direction=?',(process,direction)))
            expected=sorted(r['observation_id'] for r in rows if r['process']==process and r['direction']==direction)
            checks.append({'process':process,'direction':direction,'records':len(ids),'equal':ids==expected})
    con.commit();negative={}
    for name,sql in [('role_direction',"UPDATE exchange SET direction='INPUT' WHERE role='CO_PRODUCT'"),('unit_fk',"UPDATE exchange SET unit_code='unregistered'"),('process_fk',"UPDATE exchange SET process_id='missing'")]:
        try:con.execute(sql)
        except sqlite3.IntegrityError:negative[name]=True
        else:negative[name]=False
        finally:con.rollback()
    if not all(r['equal'] for r in checks) or not all(negative.values()) or con.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Candidate validation failed')
    counts={t:con.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ['source','unit','process','flow','exchange']}
    with sqlite3.connect(target) as dest:con.backup(dest)
    con.close();(folder/'schema.sql').write_text(SCHEMA,encoding='utf-8')
    result={'passed':True,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'tables':counts,'full_payload_roundtrip':len(actual),'typed_join_roundtrip':len(typed),'query_checks':checks,'negative_checks':negative,'flow_type_compartment':'NULL when not established; no inferred classification','production_migrated':False,'scope':'Source-local Flow + Unit candidate only; text decimal amounts preserved; no global ontology, conversion engine or 5NF claim'}
    (ROOT/'evidence/inventory-candidate.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':build()
