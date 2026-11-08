from pathlib import Path
import shutil
import subprocess
import unittest


class WebRequestTests(unittest.TestCase):
    def test_stale_request_failure_and_exports(self):
        node=shutil.which('node')
        if not node:
            bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
            if bundled.is_file():node=str(bundled)
        if not node:self.skipTest('Node.js required for JavaScript behavior tests')
        result=subprocess.run([node,str(Path(__file__).with_name('web-request-behavior.cjs'))],capture_output=True,text=True,encoding='utf8',timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
