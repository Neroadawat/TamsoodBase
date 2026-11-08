import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from deploy import rollback_private,upgrade_private


class PrivateOperationTests(unittest.TestCase):
    def test_rollback_default_is_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)/'tamsoodbase';base.mkdir()
            (base/('backend.env.before-'+'a'*16)).write_text('TAMSOOD_S3_BUCKET=\n')
            def container(name):
                release='b'*16 if 'rollback' in name else 'a'*16
                return {'Config':{'Labels':{'org.tamsood.project':'TamsoodBase','org.tamsood.release':release}},'State':{'Running':'rollback' not in name},'HostConfig':{'PortBindings':{'8000/tcp':[{'HostIp':'127.0.0.1','HostPort':'8765'}]}}}
            with patch.object(Path,'home',return_value=Path(folder)),patch.object(rollback_private,'info',side_effect=container),patch.object(rollback_private.subprocess,'check_output',return_value=b'tamsoodbase-api\n'),patch.object(rollback_private.subprocess,'run') as mutate,patch.object(sys,'argv',['rollback','--current','a'*16,'--previous','b'*16]),patch('builtins.print'):
                rollback_private.main()
                mutate.assert_not_called()
                self.assertFalse((base/'rollback-result.json').exists())

    def test_rollback_refuses_other_project(self):
        bad={'Config':{'Labels':{'org.tamsood.project':'OtherProject'}}}
        with patch.object(rollback_private,'info',return_value=bad),patch.object(rollback_private.subprocess,'run') as mutate,patch.object(sys,'argv',['rollback','--current','a'*16,'--previous','b'*16]):
            with self.assertRaisesRegex(RuntimeError,'identity mismatch'):rollback_private.main()
            mutate.assert_not_called()

    def test_new_service_is_loopback_and_hardened(self):
        with patch.object(upgrade_private,'docker') as docker, patch.object(Path,'read_text',return_value=''):
            upgrade_private.run_container('tamsoodbase-stage-test','image:test',18765,Path('/private/backend.env'),'a'*16)
            args=docker.call_args.args
            self.assertIn('127.0.0.1:18765:8000',args)
            self.assertIn('--read-only',args)
            self.assertIn('no-new-privileges:true',args)
            self.assertIn(str(Path('/private/backend.env')),args)
            self.assertNotIn('0.0.0.0:18765:8000',args)
