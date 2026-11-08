"""Verify the source overlay in a clean copy of its exact base commit."""
import argparse
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract(archive, destination, skip=()):
    for member in archive.infolist():
        if member.filename in skip: continue
        target = (destination / member.filename).resolve()
        if not target.is_relative_to(destination): raise ValueError('Unsafe archive path')
        if member.is_dir(): target.mkdir(parents=True,exist_ok=True)
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(archive.read(member))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python',type=Path,default=Path(sys.executable))
    parser.add_argument('--node',type=Path,default=shutil.which('node'))
    parser.add_argument('--bundle',type=Path,help='Explicit ZIP; otherwise use the latest MANIFEST.json bundle')
    args = parser.parse_args()
    if args.node is None:parser.error('Node.js is required for the RAG browser behavior checks')
    folder = ROOT/'build/handoff-package'
    latest=json.loads((folder/'MANIFEST.json').read_bytes()) if args.bundle is None else None
    filename=latest.get('bundle_filename','TamsoodBase-handoff-2026-11-08.zip') if latest else None
    if filename is not None and Path(filename).name!=filename:raise ValueError('Invalid bundle filename')
    bundle=args.bundle.resolve() if args.bundle else folder/filename
    checks = []
    with zipfile.ZipFile(bundle) as overlay:
        manifest = json.loads(overlay.read('MANIFEST.json'))
        if manifest['deleted_paths_require_manual_review']: raise ValueError('Cleanroom needs explicit deletion review')
        base = subprocess.check_output(['git','archive','--format=zip',manifest['base_commit']],cwd=ROOT)
        patch_info=manifest['git_patch'];patch=bundle.parent/patch_info['filename']
        if patch.resolve().parent!=bundle.resolve().parent or hashlib.sha256(patch.read_bytes()).hexdigest()!=patch_info['sha256']:
            raise ValueError('Invalid Git patch path/hash')
        for mode in ('overlay','git_patch'):
            with tempfile.TemporaryDirectory(prefix='verify-'+mode+'-',dir=folder) as temporary:
                destination = Path(temporary).resolve()
                if not destination.is_relative_to(folder.resolve()): raise ValueError('Invalid temporary workspace')
                with zipfile.ZipFile(io.BytesIO(base)) as original: extract(original,destination)
                if mode=='overlay':
                    extract(overlay,destination,skip=('MANIFEST.json','START_HERE_TH.txt'))
                    for name,expected in manifest['files'].items():
                        if hashlib.sha256((destination/name).read_bytes()).hexdigest()!=expected['sha256']:
                            raise ValueError('Overlay differs from manifest')
                else:
                    subprocess.run(['git','init','--quiet',str(destination)],check=True,capture_output=True)
                    subprocess.run(['git','apply','--check',str(patch.resolve())],cwd=destination,check=True,capture_output=True)
                    subprocess.run(['git','apply',str(patch.resolve())],cwd=destination,check=True,capture_output=True)
                    for name,expected in manifest['files'].items():
                        blob=subprocess.check_output(['git','hash-object','--path='+name,name],cwd=destination).decode().strip()
                        if blob!=expected['git_blob']:raise ValueError('Applied patch differs from canonical Git source')
                for pattern in ('test_rag_runtime.py','test_rag_scope.py','test_rag_http.py',
                                'test_dmf.py','test_dmf_snapshot.py','test_explorer_bounds.py',
                                'test_mysql_store.py','test_wsgi.py','test_submission_diagrams.py',
                                'test_report_acquisition.py','test_doeb_monthly_candidate.py','test_handoff_preparation.py',
                                'test_handoff_corporate_mysql.py','test_handoff_store.py'):
                    result = subprocess.run([str(args.python.resolve()),'-X','utf8','-m','unittest','discover','-s','tests','-p',pattern,'-v'],
                                            cwd=destination,capture_output=True,timeout=60)
                    output=(result.stdout+result.stderr).decode('utf-8',errors='replace')
                    (folder/('cleanroom-'+mode+'-'+pattern+'.log')).write_text(output,encoding='utf-8')
                    checks.append({'mode':mode,'suite':pattern,'exit_code':result.returncode,'summary':output.strip().splitlines()[-4:]})
                result=subprocess.run([str(args.node.resolve()),'tests/rag-ui-behavior.cjs'],
                                      cwd=destination,capture_output=True,timeout=30)
                output=(result.stdout+result.stderr).decode('utf-8',errors='replace')
                (folder/('cleanroom-'+mode+'-rag-ui-behavior.log')).write_text(output,encoding='utf-8')
                checks.append({'mode':mode,'suite':'rag-ui-behavior.cjs','exit_code':result.returncode,'summary':output.strip().splitlines()[-4:]})
    report = {'bundle':bundle.name,'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),
              'base_commit':manifest['base_commit'],'source_files_verified':len(manifest['files']),
              'git_patch_verified':True,'git_patch_sha256':patch_info['sha256'],
              'clean_base_plus_overlay':True,'tests':checks,'passed':all(c['exit_code']==0 for c in checks),
              'limits':['Runtime-data-dependent test skips are recorded in logs; no data snapshot transferred.',
                        'This verifies the source handoff, not a production deployment or full source replay.']}
    (folder/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if not report['passed']: raise SystemExit(1)


if __name__=='__main__': main()
