"""Exercise actual local sockets for unfinished requests and recovery."""
import socket
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from rag_http import LocalEvidenceServer


class TestHandler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        self.send_response(200);self.send_header('Content-Length','2');self.end_headers();self.wfile.write(b'ok')


class HttpResilienceTests(unittest.TestCase):
    def test_incomplete_headers_timeout_and_next_request_recovers(self):
        with LocalEvidenceServer(('127.0.0.1',0),TestHandler) as server:
            server.request_read_timeout=.15
            worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
            try:
                slow=socket.create_connection(server.server_address,timeout=2)
                slow.sendall(b'GET / HTTP/1.1\r\nHost:')
                started=time.monotonic()
                with urlopen('http://127.0.0.1:'+str(server.server_port)+'/',timeout=2) as response:
                    self.assertEqual(response.read(),b'ok')
                self.assertLess(time.monotonic()-started,1.5)
                slow.close()
            finally:server.shutdown();worker.join(timeout=2)


if __name__=='__main__':unittest.main()
