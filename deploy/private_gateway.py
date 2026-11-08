"""Loopback-only authenticated proxy for a temporary HTTPS test tunnel.

The tunnel terminates TLS. No authorization header is forwarded to the API.
Use a persistent domain/identity provider for the eventual production site.
"""
import base64
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import urllib.error
import urllib.request

HOP={'connection','keep-alive','proxy-authenticate','proxy-authorization','te','trailers','transfer-encoding','upgrade','content-length'}

class Gateway(BaseHTTPRequestHandler):
    server_version='TamsoodGateway'
    def log_message(self,*args):pass
    def reply(self,status,body=b'',challenge=False):
        self.send_response(status)
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        if challenge:self.send_header('WWW-Authenticate','Basic realm="TamsoodBase team test", charset="UTF-8"')
        self.send_header('Content-Length',str(len(body)));self.end_headers()
        if self.command!='HEAD':self.wfile.write(body)
    def authorized(self):
        value=self.headers.get('Authorization','')
        if not value.startswith('Basic ') or len(value)>4096:return False
        token=hashlib.sha256(value.encode()).digest()
        with self.server.auth_lock:
            if self.server.cached_token is not None and hmac.compare_digest(token,self.server.cached_token):return True
        try:
            user,password=base64.b64decode(value[6:],validate=True).decode('utf-8').split(':',1)
        except (ValueError,UnicodeError):return False
        cfg=self.server.config
        if not hmac.compare_digest(user.encode(),cfg['username'].encode()):return False
        digest=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(cfg['salt']),cfg['iterations']).hex()
        valid=hmac.compare_digest(digest,cfg['password_hash'])
        if valid:
            with self.server.auth_lock:self.server.cached_token=token
        return valid
    def do_GET(self):
        if not self.authorized():return self.reply(401,b'Authentication required',True)
        if self.command not in ('GET','HEAD','OPTIONS'):return self.reply(405,b'Read-only gateway')
        if not self.path.startswith('/') or self.path.startswith('//') or len(self.path)>8192:return self.reply(400)
        headers={key:self.headers[key] for key in ('Accept','Origin','Access-Control-Request-Method','Access-Control-Request-Headers') if self.headers.get(key)}
        request=urllib.request.Request('http://127.0.0.1:8765'+self.path,headers=headers,method=self.command)
        try:
            try:response=urllib.request.urlopen(request,timeout=35)
            except urllib.error.HTTPError as e:response=e
            with response:
                body=response.read(32*1024*1024+1)
                if len(body)>32*1024*1024:return self.reply(502,b'Response too large')
                self.send_response(response.status)
                for key,value in response.headers.items():
                    if key.lower() not in HOP:self.send_header(key,value)
                # HEAD must report the origin representation length.
                size=response.headers.get('Content-Length',str(len(body))) if self.command=='HEAD' else str(len(body))
                self.send_header('Content-Length',size);self.end_headers()
                if self.command!='HEAD':self.wfile.write(body)
        except (OSError,TimeoutError,urllib.error.URLError):self.reply(502,b'Backend unavailable')
    do_HEAD=do_GET
    do_OPTIONS=do_GET
    do_POST=do_GET
    do_PUT=do_GET
    do_DELETE=do_GET
    do_PATCH=do_GET

def main():
    config=json.loads(Path(os.environ.get('TAMSOOD_GATEWAY_CONFIG','/config/access.json')).read_text())
    if config.get('iterations',0)<600000:raise RuntimeError('Insufficient password hash cost')
    server=ThreadingHTTPServer(('127.0.0.1',18766),Gateway)
    server.config=config;server.auth_lock=threading.Lock();server.cached_token=None
    server.serve_forever()

if __name__=='__main__':main()
