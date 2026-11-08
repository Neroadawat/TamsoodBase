"""Build the public frontend from an isolated source allowlist, without research data."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
FILES=['vercel.json','api/[route].js','scripts/build_frontend.mjs']+[
    'web/'+name for name in ('index.html','style.css','api.js','app.js','config.js','favicon.svg','upstream-inventory.json','case-study.js','case-study.json','discovery.js','story.js','theme.css','noto-sans-thai-06310198b08f.woff2','FONT-LICENSE.txt')]


def verify():
    node=shutil.which('node')
    if not node:raise RuntimeError('Node.js required')
    with tempfile.TemporaryDirectory(prefix='tamsood-public-cleanroom-') as temporary:
        root=Path(temporary)
        for name in FILES:
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/name,target)
        result=subprocess.run([node,str(root/'scripts/build_frontend.mjs')],env=os.environ|{'VERCEL':'1','TAMSOOD_DEPLOY_MODE':'proxy','TAMSOOD_API_BASE_URL':''},capture_output=True,text=True,timeout=30)
        if result.returncode:raise RuntimeError('Isolated build failed: '+result.stderr)
        manifest=json.loads((root/'build/frontend/build-manifest.json').read_text())
        if manifest['containsPrivateResearchData'] or manifest['containsRawDocuments']:raise ValueError('Unsafe public build')
        checks={entry['path']:hashlib.sha256((root/'build/frontend'/entry['path']).read_bytes()).hexdigest()==entry['sha256'] for entry in manifest['files']}
        if not all(checks.values()):raise ValueError('Build hash mismatch')
        return {'scope':'PUBLIC_FRONTEND_ONLY_NOT_FULL_RESEARCH_PIPELINE','source_files':len(FILES),'asset_hashes_checked':len(checks),'passed':True,
          'no_raw_or_private_inputs':True,'backend_database_rebuilt':False,'source_manifest':[{ 'path':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name in FILES]}


if __name__=='__main__':
    report=verify()
    (ROOT/'evidence/frontend-cleanroom.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='source_manifest'}))
