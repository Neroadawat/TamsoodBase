"""Independent locator-to-cell checks over saved source snapshots, not parser replay.

CSV/DOM values are read directly. Corporate re-extraction comes from the separately
executed --pdf audit and is joined to source report identities, never guessed.
"""
import calendar
from collections import Counter
import csv
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_lines(path,encoding='utf-8-sig',named=False):
    reader=(csv.DictReader if named else csv.reader)(io.StringIO(path.read_bytes().decode(encoding),newline=''))
    result={}
    for row in reader:result[reader.line_num]=row
    return result


def audit():
    contract=ROOT/'build/source-contract';cross=json.loads((contract/'crosswalk.json').read_text(encoding='utf-8'))
    export=contract/'observations-internal.jsonl'
    if digest(export)!=cross['export_sha256']:raise ValueError('Internal export hash changed')
    if not all(digest(ROOT/path)==sha for path,sha in cross['inputs'].items()):raise ValueError('Crosswalk inputs stale')
    registry={r['source_id']:r for r in csv.DictReader((ROOT/'docs/source-registry.csv').open(encoding='utf-8-sig'))}
    parent={(r['source_id'],r['source_sha256']) for r in cross['sources']}
    run=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
    cache={};counts=Counter();failures=[];ledger=[]
    pdf_audit=json.loads((ROOT/'evidence/pipeline-audit.json').read_text(encoding='utf-8'))
    pdf_stage=next(s for s in pdf_audit['stages'] if s['stage']=='reference_api_and_pdf')
    pdf_verified=pdf_stage['passed'] and pdf_stage['detail']['pdf_reextraction_requested'] and pdf_stage['detail']['pdf_records_reextracted']==101
    reports={}
    for folder in ['report-pilot','sprc-report']:
        report=json.loads((ROOT/'build'/folder/'report.json').read_text(encoding='utf-8'))
        for r in report['rows']:reports[(r['pdf_sha256'],r['metric_id'],r['year'])]=r
    eppo_manifest=json.loads((ROOT/'data/raw/eppo/manifest.json').read_text(encoding='utf-8'))['resources']
    dom=ROOT/'data/raw/mdpi-9415/table4-dom.json';cells=json.loads(dom.read_text(encoding='utf-8'))['rows']
    for line in export.open(encoding='utf-8'):
        item=json.loads(line);r=item['original'];layer=item['layer'];sid=item['source_id'];sha=item['source_sha256'];ok=True;reason=''
        try:
            if sid not in registry or (sid,sha) not in parent:raise ValueError('Unregistered source/hash')
            if layer=='dmf':
                path=ROOT/'data/raw/dmf'/run/(r['package']+'.csv')
                if path not in cache:cache[path]=(digest(path),csv_lines(path,'cp874',True))
                actual_sha,rows=cache[path];raw=rows[r['source_line']]
                if actual_sha!=sha or raw[r['amount_column']]!=r['raw_value'] or Decimal(raw[r['amount_column']])!=Decimal(r['decimal_value']):raise ValueError('DMF numeric cell/hash mismatch')
                if (int(raw['YEAR'])-543,int(raw['MONTH']),raw['BLOCK_TYPE'],raw['BLOCK'] or None,raw['SOURCE_GROUP'],raw['DAYSOFPRODUCE'])!=(r['year_ce'],r['month'],r['area'],r['block_label'],r['source_group'],r['production_days']):raise ValueError('DMF context mismatch')
            elif layer=='nso':
                path=ROOT/'data/raw/nso/yearbook-2026'/('T_'+r['table_id']+'_2026.csv')
                if path not in cache:cache[path]=(digest(path),csv_lines(path))
                actual_sha,rows=cache[path];raw=rows[r['source_line']]
                if actual_sha!=sha or raw!=r['source_row'] or raw[r['source_column']-1].strip()!=r['raw_value'] or Decimal(r['raw_value'])!=Decimal(r['amount']):raise ValueError('NSO locator/numeric mismatch')
                headers=[row for row in rows.values() if len(row)>=r['source_column'] and row[r['source_column']-1]==r['source_header']]
                if not headers or '('+str(r['reference_year'])+')' not in r['source_header']:raise ValueError('NSO year header mismatch')
            elif layer=='eppo':
                path=ROOT/'data/raw/eppo'/eppo_manifest[r['dataset_id']]['filename']
                if path not in cache:cache[path]=(digest(path),csv_lines(path,named=True))
                actual_sha,rows=cache[path];raw=rows[r['source_line']]
                if actual_sha!=sha or raw!=r['source_row'] or raw[r['source_column']].strip()!=r['raw_value'] or Decimal(r['raw_value'].replace(',',''))!=Decimal(r['amount']):raise ValueError('EPPO cell/hash mismatch')
                if raw['UNIT'].strip()!=r['unit'] or int(raw['Year'])!=r['reference_year'] or raw['Month'].strip()!=calendar.month_name[r['month']]:raise ValueError('EPPO unit/period mismatch')
                if raw[r['subject_type']].strip()!=r['subject']:raise ValueError('EPPO subject mismatch')
            elif layer=='inventory':
                row=cells[r['source_row']-1];cell=row[r['source_column']-1]['text']
                if digest(dom)!=sha or cell!=r['raw_value'] or row[1]['text']!=r['flow'] or row[5]['text']!=r['unit']:raise ValueError('DOM cell/flow/unit mismatch')
                numeric=re.fullmatch(r'(\d+(?:\.\d+)?)(?:\s+a)?',cell)
                if not numeric or Decimal(numeric[1])!=Decimal(r['amount']) or cells[0][r['source_column']-1]['text']!=r['process']:raise ValueError('DOM amount/process mismatch')
            elif layer=='corporate':
                source=reports[(sha,r['source_metric_id'],r['reference_year'])]
                if not pdf_verified or source['raw_value']!=r['raw_value'] or source['pdf_page']!=r['pdf_page'] or source['extracted_text_line']!=r['extracted_text_line'] or source['source_url']!=r['source_url']:raise ValueError('Corporate report/PDF identity mismatch')
                if Decimal(r['raw_value'].replace(',',''))*Decimal(r['scale_factor'])!=Decimal(r['scaled_amount']):raise ValueError('Corporate exact scaling mismatch')
            else:raise ValueError('Unsupported layer')
        except (ValueError,KeyError,IndexError) as error:ok=False;reason=str(error);failures.append({'layer':layer,'key':item['observation_key'],'reason':reason})
        counts[layer]+=1;ledger.append({'layer':layer,'observation_key':item['observation_key'],'source_id':sid,'source_sha256':sha,'locator':item['locator'],'matched':ok,'failure':reason})
    if dict(counts)!=cross['counts']:failures.append({'reason':'Crosswalk counts differ'})
    folder=ROOT/'build/source-cell-audit';folder.mkdir(parents=True,exist_ok=True)
    ledger_path=folder/'ledger.jsonl';ledger_path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in ledger),encoding='utf-8')
    result={'passed':not failures,'counts':dict(counts),'observations':sum(counts.values()),'sources':len(parent),'failures':failures,'pdf_records_reextracted_in_current_audit':101 if pdf_verified else 0,'pipeline_audit_sha256':digest(ROOT/'evidence/pipeline-audit.json'),'contract_id':cross['contract_id'],'ledger_sha256':digest(ledger_path),'scope':'Saved snapshots, direct CSV/DOM locator checks plus current PDF re-extraction; not live-site freshness or independent scientific verification','limitations':['DMF historical time basis unresolved','Corporate4HOLD and redistribution restrictions unchanged','Cross-publication coverage is recorded separately in evidence/cross-source-coverage.json; not independent measurement verification','DOM evidence is rendered table capture, not original HTTP/PDF bytes']}
    (ROOT/'evidence/source-cell-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));return result


if __name__=='__main__':raise SystemExit(0 if audit()['passed'] else 1)
