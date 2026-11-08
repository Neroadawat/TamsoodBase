"""Check an actual DOEB monthly download before any annual NSO comparison.

Read-only intake: no deduplication, extrapolation, volume-to-mass conversion or import.
Use bundled Python with openpyxl for XLSX; CSV uses only the standard library.
"""
import argparse
from collections import Counter
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path


def inspect_rows(rows,year_ce,nso_unit):
    required={'YEAR_ID','MONTH_ID','QTY','UNIT','DATAOWNER'}
    if not rows or not required.issubset(rows[0]):raise ValueError('Missing DOEB source columns')
    if any(set(row)!=set(rows[0]) for row in rows):raise ValueError('Inconsistent source columns')
    selected=[];invalid=[]
    for line,row in enumerate(rows,2):
        try:
            year=Decimal(str(row['YEAR_ID']));month=Decimal(str(row['MONTH_ID']))
            amount=Decimal(str(row['QTY']))
            if not year.is_finite() or year!=year.to_integral_value():raise ValueError()
            if not month.is_finite() or month!=month.to_integral_value() or not 1<=month<=12:raise ValueError()
            if not amount.is_finite():raise ValueError()
            if year==year_ce+543:selected.append(row)
        except (ValueError,InvalidOperation,TypeError):invalid.append(line)
    keys=[tuple((column,str(row[column])) for column in sorted(row)) for row in selected]
    repeated=sum(count-1 for count in Counter(keys).values() if count>1)
    months=sorted({int(Decimal(str(row['MONTH_ID']))) for row in selected})
    missing=sorted(set(range(1,13))-set(months))
    units=sorted({str(row['UNIT']) for row in selected})
    blockers=[]
    if invalid:blockers.append('INVALID_SOURCE_YEAR_MONTH_OR_QUANTITY')
    if not selected:blockers.append('NO_ROWS_FOR_YEAR')
    if missing:blockers.append('INCOMPLETE_CALENDAR_YEAR')
    if repeated:blockers.append('REPEATED_SOURCE_ROWS_REQUIRE_REVIEW')
    # The supported source-unit mapping is explicit. Missing mass properties never get guessed.
    expected={'Thousand litre':'พันลิตรต่อเดือน'}.get(nso_unit)
    if expected is None or units!=[expected]:blockers.append('UNIT_MAPPING_UNRESOLVED_OR_INCOMPATIBLE')
    if any(str(row['DATAOWNER'])!='กรมธุรกิจพลังงาน' for row in selected):blockers.append('UNEXPECTED_DATA_OWNER')
    return {'year_ce':year_ce,'source_rows':len(rows),'selected_year_rows':len(selected),
            'months_present':months,'months_missing':missing,'source_units':units,'target_nso_unit':nso_unit,
            'repeated_source_row_extras':repeated,'invalid_source_lines':invalid,'blockers':blockers,
            'ready_for_further_scope_review':not blockers,'admitted_to_comparison':False,
            'annual_amount':None,'deduplication_applied':False,'source_values_changed':False,
            'limits':['Complete months do not prove complete geography/company/customer coverage.',
                      'Matching definitions, coverage and provenance are still required before summing.',
                      'Repeated rows are reported, not automatically removed as erroneous duplicates.']}


def read_rows(path):
    if path.suffix.lower()=='.csv':
        with path.open(encoding='utf-8-sig',newline='') as stream:
            reader=csv.DictReader(stream);header=reader.fieldnames
            if not header or len(set(header))!=len(header):raise ValueError('Missing or duplicate CSV source headers')
            rows=list(reader)
            if any(None in row for row in rows):raise ValueError('Unexpected extra CSV fields')
            return rows
    if path.suffix.lower()!='.xlsx':raise ValueError('Use an original CSV or XLSX download')
    import openpyxl
    workbook=openpyxl.load_workbook(path,read_only=True,data_only=False)
    try:
        if len(workbook.worksheets)!=1:raise ValueError('Select and review the source sheet explicitly')
        values=workbook.worksheets[0].iter_rows(values_only=True)
        header=next(values)
        if any(not isinstance(value,str) for value in header) or len(set(header))!=len(header):
            raise ValueError('Invalid or duplicate source headers')
        result=[]
        for row in values:
            if all(value is None for value in row):continue
            if any(isinstance(value,str) and value.startswith('=') for value in row):
                raise ValueError('Formula cells require source-specific verification')
            result.append(dict(zip(header,row)))
        return result
    finally:workbook.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('--year',type=int,required=True)
    parser.add_argument('--nso-unit',required=True)
    args=parser.parse_args()
    if not 1900<=args.year<=2100:parser.error('Use a CE year between1900 and2100')
    report=inspect_rows(read_rows(args.source),args.year,args.nso_unit)
    report.update({'source_filename':args.source.name,'source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),
                   'scope':'READ_ONLY_CANDIDATE_INTAKE_NOT_ANNUAL_AGREEMENT_OR_ACCEPTANCE'})
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
