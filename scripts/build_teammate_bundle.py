"""Package current reviewed source changes relative to HEAD, excluding local runtime data."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIXES = ('docs/', 'scripts/', 'evidence/', 'tests/', 'src/', 'sql/', 'api/', 'web/')
ROOT_FILES = {'PROJECT_BRIEF.md','PROJECT_STATE.md','AGENTS.md','README.md','CODEX_PROJECT_GUIDE_TH.md',
              'requirements-rag.txt','.gitignore','.gitattributes','vercel.json'}
EXTENSIONS = {'.md','.json','.py','.html','.txt','.cypher','.sql','.js','.mjs','.cjs','.css','.svg','.woff2'}


def git(*args): return subprocess.check_output(['git',*args], cwd=ROOT)


def git_patch(entries,base,directory):
    """Prepare a Git-native patch with a private index; never stage the user's files."""
    index=Path(git('rev-parse','--git-path','index').decode().strip())
    if not index.is_absolute():index=ROOT/index
    before=hashlib.sha256(index.read_bytes()).hexdigest() if index.exists() else None
    with tempfile.TemporaryDirectory(prefix='patch-index-',dir=directory) as temporary:
        work=Path(temporary).resolve()
        if not work.is_relative_to(directory.resolve()):raise ValueError('Unsafe patch staging directory')
        env=os.environ|{'GIT_INDEX_FILE':str(work/'index')}
        def command(*args):return subprocess.check_output(['git',*args],cwd=ROOT,env=env,stderr=subprocess.PIPE)
        command('read-tree',base)
        command('add','--force','--',*sorted(entries))
        patch=command('diff','--cached','--binary',base,'--')
        indexed=command('ls-files','--stage','-z').decode().split('\0')
        blobs={record.split('\t',1)[1]:record.split()[1] for record in indexed if record}
    after=hashlib.sha256(index.read_bytes()).hexdigest() if index.exists() else None
    if before!=after:raise ValueError('Real Git index changed concurrently; inspect before handing off')
    if git('rev-parse','HEAD').decode().strip()!=base:raise ValueError('HEAD changed during packaging')
    return patch,{name:blobs[name] for name in entries}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date',default=datetime.now().date().isoformat(),help='Handoff date YYYY-MM-DD used in artifact names')
    args=parser.parse_args()
    try:datetime.strptime(args.date,'%Y-%m-%d')
    except ValueError:parser.error('Use a valid YYYY-MM-DD date')
    base = git('rev-parse','HEAD').decode().strip()
    branch = git('branch','--show-current').decode().strip()
    names = set(git('diff','--name-only','HEAD','-z').decode().split('\0'))
    names.update(git('ls-files','--others','--exclude-standard','-z').decode().split('\0'))
    entries = {}; deleted = []; excluded = []
    for name in sorted(names - {''}):
        path = (ROOT / name).resolve()
        allowed = name in ROOT_FILES or (name.startswith(PREFIXES) and Path(name).suffix in EXTENSIONS)
        if (not allowed or not path.is_relative_to(ROOT) or (ROOT/name).is_symlink()
                or any(part in ('.git','.local','data','build','tmp','output','__pycache__') for part in Path(name).parts)):
            excluded.append(name); continue
        if not path.exists(): deleted.append(name); continue
        body = path.read_bytes()
        # Detect recognisable credential material without printing matches or values.
        if re.search(rb'AIza[0-9A-Za-z_-]{30,}|AKIA[0-9A-Z]{16}|github_pat_[0-9A-Za-z_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', body):
            raise ValueError('Review possible credential material in ' + name)
        entries[name] = body
    directory = ROOT/'build/handoff-package';directory.mkdir(parents=True,exist_ok=True)
    if deleted:raise ValueError('Review deleted paths before producing a Git patch')
    patch,blobs=git_patch(entries,base,directory)
    patch_path=directory/f'TamsoodBase-handoff-{args.date}.patch';patch_path.write_bytes(patch)
    target=directory/f'TamsoodBase-handoff-{args.date}.zip'
    manifest = {'created_at_utc':datetime.now(timezone.utc).isoformat(),'base_commit':base,'branch':branch,
                'bundle_filename':target.name,'handoff_date':args.date,
                'kind':'WORKING_TREE_SOURCE_OVERLAY_NOT_COMMITTED_OR_PUSHED',
                'files':{name:{'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'git_blob':blobs[name]} for name,body in entries.items()},
                'git_patch':{'filename':patch_path.name,'sha256':hashlib.sha256(patch).hexdigest(),
                             'text_format':'Git canonical text and binary assets; working tree CRLF may normalize to LF',
                             'real_index_unchanged':True},
                'deleted_paths_require_manual_review':deleted,'excluded_changed_paths':excluded,
                'excluded_runtime':['data/raw/','build/','.local/','.git/','credentials'],
                'note':'Apply only after checking base commit and local edits. No raw snapshots or credentials included.'}
    temporary = target.with_suffix('.tmp')
    readme = ('เริ่มที่ docs/TEAMMATE_NEXT_STEPS_TH.md และ MANIFEST.json\n'
              'ชุดนี้เป็นไฟล์เพิ่ม/แก้จาก working tree ยังไม่ใช่ commit/push และไม่รวมข้อมูล runtime\n'
              'ตรวจ base commit และงานค้างก่อนนำเข้า ห้ามทับงานของสมาชิกโดยไม่เทียบ diff\n')
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,body in entries.items(): archive.writestr(name,body)
        archive.writestr('MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        archive.writestr('START_HERE_TH.txt',readme)
    with zipfile.ZipFile(temporary) as archive:
        if archive.testzip() is not None: raise ValueError('Archive integrity failure')
        if set(archive.namelist()) != set(entries) | {'MANIFEST.json','START_HERE_TH.txt'}: raise ValueError('Archive paths differ')
        for name,expected in manifest['files'].items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected['sha256']: raise ValueError('Archive content differs')
    temporary.replace(target)
    (directory/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'bundle':str(target),'source_files':len(entries),'bytes':target.stat().st_size,
                      'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'base_commit':base,
                      'excluded_changed_paths':excluded,'deleted_paths':deleted},ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
