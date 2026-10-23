"""Rebuild the reference product offline, optionally loading the dedicated MySQL schema."""
import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def run(pdf_python=None,mysql=False):
    executable=pdf_python or sys.executable
    if not pdf_python and importlib.util.find_spec('pypdf') is None:
        bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
        if bundled.is_file(): executable=str(bundled)
        else: raise RuntimeError('pypdf required. Use --pdf-python PATH or install requirements-report.txt in your Python environment.')
    logs=ROOT/'build/reference-logs';logs.mkdir(parents=True,exist_ok=True)
    stages=[('thaioil',[executable,'-X','utf8','-m','src.report_pilot']),
            ('sprc',[executable,'-X','utf8','-m','src.sprc_report']),
            ('reference',[executable,'-X','utf8','-m','src.build_reusable'])]
    if mysql: stages.append(('mysql',[sys.executable,'-X','utf8','scripts/mysql_workspace.py','load-reference']))
    for name,command in stages:
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        (logs/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
        if result.returncode: raise RuntimeError(name+' failed; see '+str(logs/(name+'.log')))
        print(name+': passed',flush=True)
    print('Reference release: '+str(ROOT/'build/reusable/manifest.json'),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pdf-python');parser.add_argument('--mysql',action='store_true')
    args=parser.parse_args();run(args.pdf_python,args.mysql)
