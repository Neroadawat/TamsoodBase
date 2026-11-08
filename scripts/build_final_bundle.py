"""Package review artifacts with exact allowlist; internal derived data stays separate."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def archive(path,members,scope):
    manifest={'scope':scope,'submitted':False,'public_redistribution_cleared':False,'files':[]}
    for name,p in sorted(members.items()):
        if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Unsafe file')
        manifest['files'].append({'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for name,p in members.items():z.write(p,name)
        z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(path) as z:
        if z.testzip():raise ValueError('Archive CRC failed')
        for item in manifest['files']:
            if hashlib.sha256(z.read(item['path'])).hexdigest()!=item['sha256']:raise ValueError('Archive member changed')
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'files':len(members)+1,'bytes':path.stat().st_size}


def build():
    out=ROOT/'output/final-review';out.mkdir(parents=True,exist_ok=True)
    docs=['output/pdf/TamsoodBase-SRS-review.pdf','output/pdf/TamsoodBase-final-slides-review.pdf','output/presentations/TamsoodBase-final-review.pptx','build/submission-evidence/tamsood-evidence-review.zip','docs/submission/MEMBER_INPUTS.md','docs/submission/FINAL_DELIVERY_PLAN.md','docs/final-gap-plan.md','docs/source-contract.md','build/inventory-candidate/schema.sql']
    result={'review_only':True,'submitted':False,'documents':archive(out/'TamsoodBase-documents-review.zip',{p:ROOT/p for p in docs},'INTERNAL_DOCUMENT_REVIEW_NOT_FINAL_SUBMISSION')}
    data=['crosswalk.json','observations-internal.csv','observations-internal.jsonl']
    result['internal_data']=archive(out/'TamsoodBase-internal-data-review.zip',{p:ROOT/'build/source-contract'/p for p in data},'INTERNAL_REVIEW_ONLY_MIXED_REFERENCE_STATISTICS_PENDING_NOT_ALL_ACCEPTED_LCI')
    (ROOT/'evidence/final-review-bundles.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':build()
