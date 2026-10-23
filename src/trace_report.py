"""Verify one report row against original PDF bytes and re-extracted columns."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCES={'THAIOIL_2024_REPORT':('report-pilot','thaioil'),'SPRC_2024_REPORT':('sprc-report','sprc')}


def trace(source,metric,year):
    from pypdf import PdfReader
    folder,publisher=SOURCES[source]
    report=json.loads((ROOT/'build'/folder/'report.json').read_text(encoding='utf-8'))
    matches=[r for r in report['rows'] if r['metric_id']==metric and r['year']==year]
    if len(matches)!=1: raise ValueError('No unique report metric for this year')
    row=matches[0];raw=ROOT/'data/raw'/publisher/'2024'
    manifest=json.loads((raw/'manifest.json').read_text(encoding='utf-8'))
    pdf=raw/'sustainability-report.pdf';digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest!=row['pdf_sha256'] or digest!=manifest['sha256'] or manifest['source_url']!=row['source_url']:
        raise ValueError('Original evidence mismatch')
    text=PdfReader(pdf).pages[row['pdf_page']-1].extract_text(extraction_mode='layout')
    if publisher=='thaioil':
        from src.report_pilot import extract_values
        line,values=extract_values(text,row['source_label'],row['source_unit']);first_year=2021
    else:
        from src.sprc_report import table_row
        count=3 if row['pdf_page']==49 else 4
        if count==3:
            if 'Cubic meter per year' not in text: raise ValueError('Unit header changed')
            text='\n'.join(line.replace(row['source_label'],row['source_label']+' m3/year',1)
                if line.strip().startswith(row['source_label']) else line for line in text.splitlines())
        line,values=table_row(text,row['source_label'],row['source_unit'],count);first_year=2025-count
    if values[year-first_year]!=row['raw_value'] or line!=row['extracted_text_line']:
        raise ValueError('Re-extracted source value does not match stored row')
    return {'verification':'PDF_HASH_AND_REEXTRACTED_COLUMN_MATCH','source':source,'record':row,
            'competition_accepted':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',choices=list(SOURCES));parser.add_argument('metric');parser.add_argument('year',type=int)
    args=parser.parse_args();print(json.dumps(trace(args.source,args.metric,args.year),ensure_ascii=False,indent=2))
