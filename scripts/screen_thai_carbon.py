"""Review one actual TGO Thai biodiesel factor and calculate user-entered kg only."""
import argparse
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from src.thai_carbon import screen_activity

ROOT=Path(__file__).resolve().parents[1]


class FactorRows(HTMLParser):
    def __init__(self):
        super().__init__();self.rows=[];self.row=None;self.cell=None

    def handle_starttag(self, tag, attrs):
        if tag=='tr':self.row=[]
        if tag in ('td','th'):self.cell=[]

    def handle_data(self, data):
        if self.cell is not None:self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('td','th') and self.cell is not None:
            if self.row is not None:self.row.append(' '.join(' '.join(self.cell).split()))
            self.cell=None
        if tag=='tr' and self.row is not None:
            self.rows.append(self.row);self.row=None


def verify_selected_row(html, selected):
    parser=FactorRows();parser.feed(html)
    matches=[r for r in parser.rows if 'ไบโอดีเซล, ค่าเฉลี่ยประเทศไทย' in r]
    if len(matches)!=1 or selected!=matches:
        raise ValueError('Every selected cell must match the retained HTML source')


def reviewed_factor():
    raw=ROOT/'data/raw/tgo-cfp-2026-11-03'
    meta=json.loads((raw/'manifest.json').read_text(encoding='utf8'))
    if hashlib.sha256((raw/'page.html').read_bytes()).hexdigest()!=meta['sha256']:
        raise ValueError('Snapshot hash mismatch')
    rows=json.loads((raw/'selected-row.json').read_text(encoding='utf8'))
    verify_selected_row((raw/'page.html').read_text(encoding='utf8'),rows)
    if len(rows)!=1:
        raise ValueError('Expected one factor row')
    row=rows[0]
    if row[:2]!=['307.','ไบโอดีเซล, ค่าเฉลี่ยประเทศไทย'] or row[3:5]!=['kg','1.0372']:
        raise ValueError('Factor identity/value changed')
    if row[6]!='Update_April2026' or not row[5].startswith('Thai National LCI Database, TIIS-MTEC-NSTDA'):
        raise ValueError('Unreviewed source/version')
    return {'id':'TGO-CFP-307-April2026','name':row[1], 'description':row[2],
      'activity_unit':row[3], 'value':row[4], 'result_unit':'kgCO2e',
      'geography':'TH', 'provenance_class':'THAI_NATIONAL_LCI_REPORTED',
      'underlying_all_inputs_thai_audited':False,
      'method':'IPCC 2013 GWP 100a V1.03', 'version':row[6],
      'source_url':meta['url'], 'source_sha256':meta['sha256'], 'locator':'CFP table row 307',
      'rights_status':meta['rights_status'], 'boundary_status':'NOT_CONFIRMED_FOR_FULL_LIFECYCLE_SUM',
      'automatically_combined_with_foreground':False}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--kg',required=True)
    args=parser.parse_args();factor=reviewed_factor();result=screen_activity(args.kg,'kg',factor)
    result['activity_evidence_class']='USER_ENTERED_SCENARIO_NOT_MEASUREMENT'
    out=ROOT/'build/thai-carbon-screening';out.mkdir(parents=True,exist_ok=True)
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (ROOT/'evidence/thai-carbon-factor-review.json').write_text(json.dumps(factor,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=True))


if __name__=='__main__':main()
