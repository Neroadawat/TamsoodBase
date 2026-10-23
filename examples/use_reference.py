"""Read exact-decimal reference data without assuming cross-source comparability."""
import argparse
import json
from decimal import Decimal
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('path',type=Path);parser.add_argument('--year',type=int)
parser.add_argument('--metric',default='natural_gas')
args=parser.parse_args()
rows=json.loads(args.path.read_text(encoding='utf-8'))
for row in rows:
    if row['decision']!='ACCEPTED_REFERENCE' or row['source_metric_id']!=args.metric: continue
    if args.year and row['reference_year']!=args.year: continue
    amount=Decimal(row['scaled_amount'])
    print(f"{row['publisher']} | {row['reference_year']} | {amount} {row['unit_code']} | {row['source_scope']}")
    print(f"  Source: {row['source_url']}#page={row['pdf_page']}")
    print(f"  Usage: {row['usage_profile']}; redistribution: {row['redistribution_status']}")
# This example deliberately performs no cross-source sum, allocation or ranking.
