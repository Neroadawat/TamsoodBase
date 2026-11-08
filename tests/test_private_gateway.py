import base64
import hashlib
import http.client
import io
import threading
import unittest
from email.message import Message
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from deploy.private_gateway import Gateway

class Response(io.BytesIO):
    status=200
    def __init__(self):
        super().__init__(b'{"ok":true}');self.headers=Message()
        self.headers['Content-Type']='application/json'

class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Gateway)
        self.server.config={'username':'team','salt':'00'*16,'iterations':1,
          'password_hash':hashlib.pbkdf2_hmac('sha256',b'test-password',bytes(16),1).hex()}
        self.server.cached_token=None;self.server.auth_lock=threading.Lock()
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join()
    def call(self,method='GET',auth=None,path='/api/reference'):
        con=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        try:
            con.request(method,path,headers={'Authorization':auth} if auth else {})
            r=con.getresponse();return r.status,dict(r.getheaders()),r.read()
        finally:con.close()
    def token(self):return 'Basic '+base64.b64encode(b'team:test-password').decode()
    def test_every_path_requires_authentication(self):
        for path in ('/','/healthz','/api/reference','/api/reference.csv'):
            status,headers,_=self.call(path=path)
            self.assertEqual(status,401);self.assertIn('WWW-Authenticate',headers)
    def test_invalid_auth_never_contacts_origin(self):
        with patch('deploy.private_gateway.urllib.request.urlopen') as origin:
            for value in ('Basic !!!','Bearer secret','Basic '+base64.b64encode(b'team:wrong').decode()):
                self.assertEqual(self.call(auth=value)[0],401)
            origin.assert_not_called()
    def test_valid_request_strips_credentials_and_proxies(self):
        with patch('deploy.private_gateway.urllib.request.urlopen',return_value=Response()) as origin:
            self.assertEqual(self.call(auth=self.token())[0],200)
            request=origin.call_args.args[0]
            self.assertNotIn('Authorization',request.headers)
            self.assertEqual(request.full_url,'http://127.0.0.1:8765/api/reference')
    def test_write_methods_blocked_even_with_auth(self):
        with patch('deploy.private_gateway.urllib.request.urlopen') as origin:
            self.assertEqual(self.call('POST',self.token())[0],405)
            origin.assert_not_called()
    def test_head_unauthenticated_has_no_body(self):
        status,_,body=self.call('HEAD');self.assertEqual(status,401);self.assertEqual(body,b'')

if __name__=='__main__':unittest.main()
