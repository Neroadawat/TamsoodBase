import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from src.wsgi import application


class WSGITests(unittest.TestCase):
    def call(self,path='/',method='GET',origin='',query=''):
        result={}
        def start(status,headers):result.update(status=status,headers=dict(headers))
        result['body']=b''.join(application(dict(REQUEST_METHOD=method,PATH_INFO=path,QUERY_STRING=query,HTTP_ORIGIN=origin),start))
        return result

    def test_health_method_and_unknown_path(self):
        self.assertEqual(json.loads(self.call('/healthz')['body'])['status'],'ok')
        self.assertEqual(self.call('/healthz','HEAD')['body'],b'')
        self.assertTrue(self.call('/api/reference','POST')['status'].startswith('405'))
        self.assertTrue(self.call('/.local/ec2-deploy.pem')['status'].startswith('404'))

    def test_explicit_empty_year_reaches_eppo_as_all_years(self):
        with patch('src.wsgi.explorer.eppo_records',return_value={'rows':[]}) as records:
            response=self.call('/api/eppo',query='dataset=11_13&year=&page=1')
            self.assertTrue(response['status'].startswith('200'))
            self.assertEqual(records.call_args.args[0]['year'],'')
            self.assertEqual(records.call_args.args[0]['dataset'],'11_13')

    def test_deployment_frontend_assets_are_served(self):
        for path in ('/config.js','/api.js','/favicon.svg'):
            self.assertTrue(self.call(path)['status'].startswith('200'))

    def test_cors_exact_allowlist_only(self):
        with patch.dict('os.environ',{'TAMSOOD_ALLOWED_ORIGINS':'https://example.org'}):
            self.assertEqual(self.call('/healthz',origin='https://example.org')['headers']['Access-Control-Allow-Origin'],'https://example.org')
            self.assertNotIn('Access-Control-Allow-Origin',self.call('/healthz',origin='https://evil.example')['headers'])

    def test_readiness_refuses_missing_dmf_database(self):
        with tempfile.TemporaryDirectory() as tmp, patch('src.wsgi.explorer.ROOT',Path(tmp)):
            p=Path(tmp)/'data/raw/dmf/latest.json';p.parent.mkdir(parents=True)
            p.write_text(json.dumps({'run_id':'fixture'}))
            self.assertTrue(self.call('/readyz')['status'].startswith('503'))
            self.assertEqual(json.loads(self.call('/readyz')['body']),{'ready':False})

    def test_s3_not_configured_and_key_traversal_rejected(self):
        from src.s3_storage import client,object_key
        with patch.dict('os.environ',{'TAMSOOD_S3_BUCKET':'','TAMSOOD_S3_PREFIX':'tamsoodbase'}):
            with self.assertRaises(RuntimeError):client()
            self.assertEqual(object_key('releases/manifest.json'),'tamsoodbase/releases/manifest.json')
            for value in ['/private','../secret','a/../secret','a\\secret']:
                with self.assertRaises(ValueError):object_key(value)
