"""Verify checkout policy without staging/committing anything in the real repo."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('git'),'Git required')
class GitLineEndingTests(unittest.TestCase):
    def test_text_normalization_and_binary_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            def git(*args):
                return subprocess.run(['git','-C',str(folder),*args],check=True,capture_output=True).stdout.strip()
            git('init','-q');git('config','core.autocrlf','true')
            shutil.copyfile(ROOT/'.gitattributes',folder/'.gitattributes')
            hashes={}
            for name in ('fixture.py','fixture.pdf'):
                file=folder/name
                file.write_bytes(b'first\r\nsecond\r\n');crlf=git('hash-object','--path='+name,name)
                file.write_bytes(b'first\nsecond\n');lf=git('hash-object','--path='+name,name)
                hashes[name]=(crlf,lf)
            self.assertEqual(*hashes['fixture.py'])
            self.assertNotEqual(*hashes['fixture.pdf'])
            self.assertIn(b'eol: lf',git('check-attr','eol','--','fixture.py'))
