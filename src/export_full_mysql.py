"""Export the full reviewed snapshot with exact decimals and every raw record."""
import csv
import hashlib
import io
import json
import sqlite3
from decimal import Decimal, localcontext
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PRODUCTS={'production-oil':('crude_oil','น้ำมันดิบ','OIL'),
          'production-condensate':('condensate','คอนเดนเสท','CONDENSATE'),
          'production-natural-gas':('natural_gas','ก๊าซธรรมชาติ','GAS')}


def text_sql(value):
    if value is None: return 'NULL'
    return "CONVERT(X'"+str(value).encode('utf-8').hex()+"' USING utf8mb4)"


def exact_decimal(value):
    with localcontext() as ctx:
        ctx.prec=80
        number=Decimal(value)
        if not number.is_finite() or number<0 or number>=Decimal('1e18') or number!=number.quantize(Decimal('0.000000000001')):
            raise ValueError('Amount is not exactly representable as DECIMAL(30,12): '+str(value))
        return format(number,'f')


def snapshot_id(entry):
    return hashlib.sha256((entry['package']+entry['csv_sha256']+entry['metadata_sha256']).encode()).hexdigest()


def export():
    run=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
    folder=ROOT/'data/raw/dmf'/run
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    con=sqlite3.connect((ROOT/'build/dmf'/run/'candidates.sqlite').as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
    if not manifest.get('complete'): raise ValueError('Incomplete snapshot')
    expected=[];raw_count=0;output=ROOT/'build/full-mysql.sql';temporary=output.with_suffix('.sql.tmp')
    with temporary.open('w',encoding='utf-8') as f:
        f.write("SET NAMES utf8mb4;\nUSE tamsood_research;\nSET SESSION sql_mode='STRICT_ALL_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';\nSTART TRANSACTION;\n")
        def insert(table,rows):
            if rows: f.write('INSERT INTO '+table+' VALUES '+','.join('('+','.join(row)+')' for row in rows)+';\n')
        f.write("INSERT INTO publisher VALUES('DMF',"+text_sql('กรมเชื้อเพลิงธรรมชาติ')+") ON DUPLICATE KEY UPDATE publisher_id=publisher_id;\n")
        for name,(code,title,_) in PRODUCTS.items():
            f.write('INSERT INTO product VALUES('+text_sql(code)+','+text_sql(title)+') ON DUPLICATE KEY UPDATE product_code=product_code;\n')
            f.write('INSERT INTO source_resource VALUES('+','.join(map(text_sql,[name,'DMF',code,title]))+') ON DUPLICATE KEY UPDATE package=package;\n')
        for entry in manifest['packages']:
            name=entry['package'];sid=snapshot_id(entry)
            body=(folder/(name+'.csv')).read_bytes();meta=(folder/(name+'.metadata.json')).read_bytes()
            if hashlib.sha256(body).hexdigest()!=entry['csv_sha256'] or hashlib.sha256(meta).hexdigest()!=entry['metadata_sha256']:
                raise ValueError('Original hash mismatch')
            metadata=json.loads(meta)['result']
            # Replace only this exact content-addressed snapshot, not other versions.
            for table in ['duplicate_disposition','rejected_record','observation','source_record','resource_snapshot']:
                f.write('DELETE FROM '+table+' WHERE snapshot_id='+text_sql(sid)+';\n')
            insert('resource_snapshot',[[text_sql(v) for v in [sid,name,run,manifest['acquired_at'],entry['csv_url'],entry['csv_sha256'],entry['metadata_sha256'],metadata.get('unit_of_measure'),metadata.get('unit_of_multiplier'),metadata.get('license_id'),json.dumps(metadata,ensure_ascii=False)]]])
            original={}
            reader=csv.DictReader(io.StringIO(body.decode('cp874'),newline=''))
            for row in reader: original[reader.line_num]=row
            staging=list(con.execute('SELECT * FROM staging WHERE package=? ORDER BY source_line',(name,)))
            raw_count+=len(staging)
            if len(staging)!=len(original): raise ValueError('Staging count differs from original CSV')
            raw_batch=[]
            for row in staging:
                payload=json.loads(row['raw_json'])
                if payload!=original.get(row['source_line']): raise ValueError('Staging content differs from original CSV')
                fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                raw_batch.append([text_sql(sid),str(row['source_line']),text_sql(row['raw_json']),text_sql(fingerprint)])
                if len(raw_batch)==250: insert('source_record',raw_batch);raw_batch=[]
            insert('source_record',raw_batch)
            rows=list(con.execute('SELECT * FROM candidate JOIN duplicate_disposition USING(package,source_line) WHERE package=? ORDER BY source_line',(name,)))
            contexts={};observations=[];dispositions=[]
            for row in rows:
                raw=original[row['source_line']]
                if Decimal(raw[PRODUCTS[name][2]])!=Decimal(row['decimal_value']) or raw[PRODUCTS[name][2]]!=row['raw_value']:
                    raise ValueError('Parsed amount differs from raw snapshot')
                # Reject stale or altered parsed context and calendar values, too.
                if (int(raw['YEAR'])-543,int(raw['MONTH']),raw['BLOCK_TYPE'],raw['BLOCK'] or None,raw['SOURCE_GROUP'],raw['DAYSOFPRODUCE']) != (row['year_ce'],row['month'],row['area'],row['block_label'],row['source_group'],row['production_days']):
                    raise ValueError('Parsed context differs from raw snapshot')
                context=[name,row['area'],row['block_label'],row['source_group']]
                cid=hashlib.sha256(json.dumps(context,ensure_ascii=False).encode()).hexdigest();contexts[cid]=context
                amount=exact_decimal(row['decimal_value']);line=row['source_line']
                observations.append([text_sql(sid),str(line),text_sql(cid),text_sql(f"{row['year_ce']:04}-{row['month']:02}-01"),text_sql(row['raw_value']),amount,str(int(Decimal(row['production_days']))),text_sql(row['identity_sha256']),"'UNCONFIRMED'","'PENDING'"])
                dispositions.append([text_sql(sid),str(line),text_sql(row['status']),str(row['representative_line']) if row['representative_line'] is not None else 'NULL'])
                expected.append([sid,line,amount,row['status']])
            for cid,context in contexts.items():
                f.write('INSERT INTO production_context VALUES('+','.join(text_sql(v) for v in [cid]+context)+') ON DUPLICATE KEY UPDATE context_id=context_id;\n')
            for index in range(0,len(observations),250): insert('observation',observations[index:index+250])
            for index in range(0,len(dispositions),250): insert('duplicate_disposition',dispositions[index:index+250])
            rejected=con.execute('SELECT * FROM rejected WHERE package=? ORDER BY source_line',(name,)).fetchall()
            insert('rejected_record',[[text_sql(sid),str(r['source_line']),text_sql(r['reasons_json'])] for r in rejected])
        f.write('COMMIT;\n')
    con.close();temporary.replace(output)
    expected_path=ROOT/'build/full-mysql-expected.json'
    expected_path.write_text(json.dumps({'run_id':run,'rows':expected,'raw_rows':raw_count,
        'snapshot_ids':[snapshot_id(e) for e in manifest['packages']]},ensure_ascii=False),encoding='utf-8')
    print(f'Exported {len(expected)} observations and all source rows: {output}')
    return output


if __name__=='__main__': export()
