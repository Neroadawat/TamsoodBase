import json,sqlite3,subprocess,unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class Choices(HTMLParser):
    def __init__(self):super().__init__();self.active=False;self.values=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='select':self.active=attrs.get('id')=='dmf-topic'
        if tag=='option' and self.active and attrs.get('value'):self.values.append(attrs['value'])
    def handle_endtag(self,tag):
        if tag=='select':self.active=False

class GuidedDiscoveryTests(unittest.TestCase):
    def test_behavior_and_real_source_choices(self):
        result=subprocess.run(['node',str(ROOT/'tests/guided-discovery.cjs')],capture_output=True,text=True,encoding='utf8',timeout=25)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_fixed_dmf_suggestions_have_source_records(self):
        parser=Choices();parser.feed((ROOT/'web/index.html').read_text(encoding='utf8'))
        self.assertGreaterEqual(len(parser.values),5)
        run=json.loads((ROOT/'data/raw/dmf/latest.json').read_text())['run_id']
        con=sqlite3.connect((ROOT/'build/dmf'/run/'candidates.sqlite').as_uri()+'?mode=ro',uri=True)
        try:
            for value in parser.values:
                self.assertGreater(con.execute('SELECT COUNT(*) FROM candidate WHERE source_group LIKE ?',('%'+value+'%',)).fetchone()[0],0,value)
        finally:con.close()
