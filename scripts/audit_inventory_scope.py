"""Review current saved inventory without rebuilding or changing source values."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.inventory_scope import study_scope

def main():
    path=ROOT/'build/product-inventory/report.json'
    report=json.loads(path.read_text(encoding='utf8'))
    context=(ROOT/'data/raw/mdpi-9415/article-visible.txt').read_text(encoding='utf8')
    raw=ROOT/'data/raw/mdpi-9415/table4-dom.json'
    if hashlib.sha256(raw.read_bytes()).hexdigest()!=report['source_snapshot_sha256']:raise ValueError('Source table changed')
    profile=study_scope(report['rows'],context)
    profile.update({'inventory_report_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'verified_exchanges':len(report['rows']),'report_modified':False,'production_backend_updated':False})
    (ROOT/'evidence/inventory-scope-review.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'verified_exchanges':len(report['rows']),'processes':len(profile['processes']),'coverage_status':profile['coverage_status'],'full_lifecycle_inventory':False},indent=2))
if __name__=='__main__':main()
