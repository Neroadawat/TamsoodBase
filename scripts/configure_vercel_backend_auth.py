"""Set upstream authentication over stdin; never print or bundle credentials."""
import base64
import json
from pathlib import Path
import shutil
import subprocess

def main():
    root=Path(__file__).resolve().parents[1]
    credentials=json.loads((root/'.local/https-test-credentials.json').read_text())
    value='Basic '+base64.b64encode((credentials['username']+':'+credentials['password']).encode()).decode()
    command=shutil.which('npx')
    result=subprocess.run([command,'--yes','vercel@65.5.0','env','add','TAMSOOD_BACKEND_AUTH','production'],input=(value+'\n').encode(),capture_output=True,cwd=root)
    if result.returncode:raise RuntimeError('Vercel server-only environment setup failed; inspect variable state')
    print('Server-only backend credential configured; no credential printed or copied into assets.')

if __name__=='__main__':main()
