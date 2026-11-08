"""Build and seal an isolated SQLite model release; never migrate production."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from src.activity_model_store import initialize,persist,audit,identity,canonical

ROOT=Path(__file__).resolve().parents[1]


def inputs():
    path=ROOT/'build/thai-fame-activity-chain/scenarios.json'
    evidence=json.loads((ROOT/'evidence/thai-fame-activity-chain.json').read_text(encoding='utf8'))
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=evidence['scenario_artifact_sha256']:raise ValueError('Unreviewed activity artifact')
    code_files=['src/activity_model_store.py','sql/activity-model-review.sql',
        'scripts/build_activity_model_store.py','scripts/build_thai_fame_activity_chain.py']
    code_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in code_files}
    manifest={'input_artifact_sha256':digest,'implementation_sha256':identity(code_hashes),
        'code_hashes':code_hashes,'runtime':{'python':sys.version.split()[0],'sqlite':sqlite3.sqlite_version},
        'scope':'LOCAL_APPEND_ONLY_ACTIVITY_REVIEW_NOT_PRODUCTION',
        'input_sources':{k:evidence[k] for k in ['input_sha256','mill_pdf_sha256']}}
    return json.loads(path.read_text(encoding='utf8')),manifest


def main():
    artifact,manifest=inputs();release=identity(manifest)
    directory=ROOT/'build/activity-model-store/releases'/release
    directory.mkdir(parents=True,exist_ok=True);path=directory/'models.sqlite'
    schema=(ROOT/'sql/activity-model-review.sql').read_text(encoding='utf8')
    if not path.exists():
        temporary=directory/'models.pending.sqlite'
        if temporary.exists():raise ValueError('Pending build exists; inspect before retry')
        conn=sqlite3.connect(temporary)
        try:
            initialize(conn,schema);persist(conn,artifact,manifest);report=audit(conn,artifact,manifest)
            with conn:conn.execute('INSERT INTO release_seal VALUES(?)',(release,))
        finally:conn.close()
        temporary.rename(path)
    uri=path.as_uri()+'?mode=ro';conn=sqlite3.connect(uri,uri=True)
    try:
        if conn.execute('SELECT payload_json FROM release_manifest WHERE release_id=?',(release,)).fetchone()!=(canonical(manifest),):raise ValueError('Release manifest mismatch')
        if conn.execute('SELECT release_id FROM release_seal').fetchall()!=[(release,)]:raise ValueError('Release not sealed')
        report=audit(conn,artifact,manifest,require_seal=True)
    finally:conn.close()
    report.update(release_id=release,database=str(path.relative_to(ROOT)).replace('\\','/'),
        database_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),input_manifest=manifest,sealed=True)
    (ROOT/'evidence/activity-model-store.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='input_manifest'}))


if __name__=='__main__':main()
