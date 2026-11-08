"""Loopback-only browser fixture: 503 or a stalled request, no model/data/feedback."""
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGE=(Path(__file__).resolve().parents[1]/'scripts/rag_demo.html').read_text(encoding='utf-8')
PAGE=PAGE.replace('<!-- card-count -->','10').replace('<!-- mode-notice -->','หน้าตรวจกรณีระบบขัดข้อง')


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        body=PAGE.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def do_POST(self):
        try:question=json.loads(self.rfile.read(min(int(self.headers.get('Content-Length','0')),8192))).get('question','')
        except (ValueError,TypeError):question=''
        if 'หมดเวลา' in question:time.sleep(13)
        try:self.send_error(503)
        except OSError:pass


if __name__=='__main__':
    with ThreadingHTTPServer(('127.0.0.1',8778),Handler) as server:
        print('Loopback browser failure fixture: http://127.0.0.1:8778/',flush=True);server.serve_forever()
