"""Package the team reference subset for LOCAL use, with per-file checksums."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def package():
    folder=ROOT/'build/reusable';release=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    for name in ('accepted-reference.json','accepted-reference.csv','reference.sqlite','load-mysql.sql'):
        if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=release['files'][name]: raise ValueError('Export changed: '+name)
    readme='''TamsoodBase: team reference data v1
Usage profile: LOCAL_RESEARCH_REFERENCE
These records are source-attributed annual corporate metrics and reported intensities.
They are NOT product-normalized LCI exchanges. Preserve units, scope and year.
Do not sum TOTAL and COMPONENT records together. Context rows are not extra flows.
Company-report reuse/redistribution permission is NOT granted by this package.
No raw PDFs or personal credentials are included. See team-data-policy.md.
Quantity values are strings; years and page numbers are integers. Use decimal.Decimal.
The CSV and JSON contain the same accepted reference subset; holds are excluded.
The SQLite database and MySQL load script preserve all source observations and holds.
Query accepted_reference with the release_id in package-manifest.json for the usable subset.
To use SQLite: open reference.sqlite with Python sqlite3, then SELECT from accepted_reference.
To use MySQL: run load-mysql.sql against your own local database environment.
'''
    (folder/'README-reuse.txt').write_text(readme,encoding='utf-8')
    files={name:folder/name for name in ('accepted-reference.json','accepted-reference.csv','reference.sqlite','load-mysql.sql','README-reuse.txt')}
    files.update({'team-data-policy.md':ROOT/'docs/team-data-policy.md',
                  'reusable-schema.sql':ROOT/'sql/mysql/reusable-schema.sql',
                  'reusable-queries.sql':ROOT/'sql/mysql/reusable-queries.sql',
                  'use_reference.py':ROOT/'examples/use_reference.py'})
    manifest={k:release[k] for k in ('release_id','policy_version','usage_profile','accepted_reference','held_context','normalized_lci_exchanges','redistribution_status','limitations')}
    manifest['files']={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in files.items()}
    (folder/'package-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    target=folder/'reference-data-local.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,path in files.items(): archive.write(path,name)
        archive.write(folder/'package-manifest.json','package-manifest.json')
    with zipfile.ZipFile(target) as archive:
        if set(archive.namelist())!=set(files)|{'package-manifest.json'}: raise ValueError('Archive contents mismatch')
        for name,expected in manifest['files'].items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=expected: raise ValueError('Archive hash mismatch')
    print(json.dumps({'package':str(target),'files_checked':len(files),'accepted_reference':release['accepted_reference'],'usage_profile':release['usage_profile']},indent=2))


if __name__=='__main__': package()
