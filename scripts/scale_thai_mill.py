"""CLI for one mill's activity quantities, from the source-verified review."""
import argparse
import json
from scripts.review_thai_mill_2019 import ROOT, build
from src.mill_inventory_scaling import scale_mill


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mill',type=int,choices=range(1,7),required=True)
    parser.add_argument('--cpo-kg',required=True)
    args=parser.parse_args()
    # Revalidate original PDF/extractors rather than trusting an editable build JSON.
    result=scale_mill(build(),f'Mill {args.mill}',args.cpo_kg)
    folder=ROOT/'build/thai-mill-2019-scaling';folder.mkdir(parents=True,exist_ok=True)
    path=folder/f'mill-{args.mill}.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if json.loads(path.read_text(encoding='utf8'))!=result:
        raise ValueError('Roundtrip changed scaled/source quantities')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}))


if __name__=='__main__':main()
