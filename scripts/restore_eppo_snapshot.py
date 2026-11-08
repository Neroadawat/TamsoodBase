"""Restore the recorded EPPO CSVs only when bytes exactly match the old manifest."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]


def main():
    manifest=json.loads((ROOT/'evidence/eppo-import.json').read_bytes())['source_manifest']
    folder=ROOT/'data/raw/eppo';folder.mkdir(parents=True,exist_ok=True)
    checks=[]
    for dataset,source in manifest['resources'].items():
        path=folder/source['filename']
        try:
            if path.exists():body=path.read_bytes()
            else:
                with urlopen(source['url'],timeout=18) as response:body=response.read(8_000_001)
            equal=len(body)<=8_000_000 and hashlib.sha256(body).hexdigest()==source['sha256']
            if equal and not path.exists():path.write_bytes(body)
            checks.append({'dataset':dataset,'exact_recorded_bytes':equal,'expected_sha256':source['sha256']})
        except OSError as error:checks.append({'dataset':dataset,'exact_recorded_bytes':False,'error_type':type(error).__name__})
    imported=False
    if all(c['exact_recorded_bytes'] for c in checks):
        (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/import_eppo.py'),
            '--evidence-output',str(ROOT/'evidence/eppo-restored-import-2026-11-08.json')],capture_output=True,timeout=30)
        imported=result.returncode==0
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'imported':imported,
            'production_changed':False,'scope':'EXACT_SOURCE_RESTORATION_NOT_NEW_ACCEPTANCE'}
    (ROOT/'evidence/eppo-restoration-2026-11-08.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
