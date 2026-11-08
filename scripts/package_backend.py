"""Explicit deployment allowlist: derived data + metadata, no raw CSV/PDF or credentials."""
import hashlib
import json
import tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def deploy_files(root=ROOT):
    paths=[root/'requirements-backend.txt',root/'deploy/Dockerfile',root/'web/upstream-inventory.json',root/'web/case-study.json']
    for folder,extensions in [('src',{'.py'}),('web',{'.html','.css','.js','.svg'})]:
        paths.extend(p for p in (root/folder).glob('*') if p.suffix in extensions)
    run=json.loads((root/'data/raw/dmf/latest.json').read_text(encoding='utf-8'))['run_id']
    if not run or any(c not in '0123456789TZ' for c in run):raise ValueError('Invalid snapshot run')
    names=['build/source-contract/crosswalk.json','build/reusable/manifest.json','build/reusable/reference.sqlite',
        'build/nso/report.json','build/product-inventory/report.json','build/eppo/report.json',
        'build/report-pilot/report.json','build/sprc-report/report.json',
        'evidence/nso-dede-comparison.json','evidence/nso-dede-revised-comparison.json',
        'data/raw/dmf/latest.json',f'build/dmf/{run}/candidates.sqlite',
        f'build/dmf/{run}/review-report.json',f'build/dmf/{run}/quality-report.json']
    names.extend(f'data/raw/dmf/{run}/{name}.metadata.json' for name in ('production-oil','production-condensate','production-natural-gas'))
    paths.extend(root/name for name in names)
    for path in paths:
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Missing or unsafe deployment file: '+str(path))
    return sorted(set(paths))


def main():
    files=deploy_files();out=ROOT/'build/deploy';out.mkdir(parents=True,exist_ok=True)
    manifest=dict(scope='PRIVATE_TEAM_BACKEND_DERIVED_DATA_AND_METADATA',contains_raw_csv_pdf=False,
        public_redistribution_cleared=False,files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in files])
    payload=json.dumps(manifest,sort_keys=True,indent=2).encode();release=hashlib.sha256(payload).hexdigest()[:16]
    target=out/('backend-'+release+'.tar.gz')
    with tarfile.open(target,'w:gz') as archive:
        for path in files:archive.add(path,arcname=path.relative_to(ROOT).as_posix())
    (out/'manifest.json').write_bytes(payload)
    result=dict(release_id=release,archive=str(target),archive_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),files=len(files),bytes=target.stat().st_size)
    (out/'package.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
