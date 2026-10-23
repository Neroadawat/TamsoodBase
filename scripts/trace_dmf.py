"""Display a candidate and its original CSV row without network access."""
import argparse
import csv
import hashlib
import io
import json
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def trace(package, line):
    run=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
    with sqlite3.connect(ROOT/'build/dmf'/run/'candidates.sqlite') as con:
        con.row_factory=sqlite3.Row
        row=con.execute('SELECT * FROM traceable_candidate WHERE package=? AND source_line=?',(package,line)).fetchone()
    if row is None: raise ValueError('Candidate not found; inspect rejected.csv for rejected rows')
    body=(ROOT/'data/raw/dmf'/run/(package+'.csv')).read_bytes()
    if hashlib.sha256(body).hexdigest()!=row['csv_sha256']: raise ValueError('Raw snapshot changed')
    reader=csv.DictReader(io.StringIO(body.decode('cp874'),newline=''))
    original=None
    for source_row in reader:
        if reader.line_num==line: original=source_row;break
    if original!=json.loads(row['raw_json']): raise ValueError('Staging does not match original source row')
    result=dict(row)
    result['original_row_verified']=True
    result['original_file']=str(ROOT/'data/raw/dmf'/run/(package+'.csv'))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('package',choices=['production-oil','production-condensate','production-natural-gas'])
    parser.add_argument('line',type=int)
    args=parser.parse_args();trace(args.package,args.line)
