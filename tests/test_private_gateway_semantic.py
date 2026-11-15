"""Gateway /semantic-search: Basic auth required, token injected server-side, everything else stays read-only."""
import base64
import hashlib
import importlib.util
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("gw", Path(__file__).resolve().parents[1] / "deploy/private_gateway.py")
gw = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gw)
TOKEN = "s" * 40
SEEN = []


class Fake(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        SEEN.append((self.path, self.headers.get("Authorization"), json.loads(body)))
        data = json.dumps({"corpus_version": "v", "hits": []}).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)


def serve(handler, port=0):
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class GatewaySemanticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fake = serve(Fake)
        salt = bytes(range(16))
        cls.config = {"username": "u", "salt": salt.hex(), "iterations": 600000,
                      "password_hash": hashlib.pbkdf2_hmac("sha256", b"pw", salt, 600000).hex(),
                      "semantic_url": f"http://127.0.0.1:{cls.fake.server_port}", "semantic_token": TOKEN}
        cls.server = serve(gw.Gateway)
        cls.server.config = cls.config
        cls.server.auth_lock = threading.Lock()
        cls.server.cached_token = None
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.auth = "Basic " + base64.b64encode(b"u:pw").decode()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.fake.shutdown()

    def call(self, method="POST", path="/semantic-search", body=b'{"question":"x","k":3}', auth=True, ctype="application/json"):
        headers = {"Content-Type": ctype}
        if auth:
            headers["Authorization"] = self.auth
        request = urllib.request.Request(self.url + path, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=10) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def test_requires_basic_auth(self):
        SEEN.clear()
        self.assertEqual(self.call(auth=False)[0], 401)
        self.assertEqual(SEEN, [])

    def test_forwards_with_server_side_token(self):
        SEEN.clear()
        status, body = self.call()
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["corpus_version"], "v")
        self.assertEqual(SEEN, [("/search", f"Bearer {TOKEN}", {"question": "x", "k": 3})])

    def test_rejects_bad_input(self):
        SEEN.clear()
        self.assertEqual(self.call(body=b"not json")[0], 400)
        self.assertEqual(self.call(body=b"[1]")[0], 400)
        self.assertEqual(self.call(ctype="text/plain")[0], 400)
        self.assertEqual(self.call(body=b"x" * 5000)[0], 400)
        self.assertEqual(SEEN, [])

    def test_other_posts_stay_blocked(self):
        self.assertEqual(self.call(path="/api/records")[0], 405)
        self.assertEqual(self.call(path="/semantic-search/extra")[0], 405)

    def test_unconfigured_route_is_hidden(self):
        saved = self.server.config
        self.server.config = {k: v for k, v in saved.items() if not k.startswith("semantic")}
        try:
            self.assertEqual(self.call()[0], 404)
        finally:
            self.server.config = saved

    def test_service_down_is_502(self):
        saved = self.server.config
        self.server.config = {**saved, "semantic_url": "http://127.0.0.1:9"}
        try:
            self.assertEqual(self.call()[0], 502)
        finally:
            self.server.config = saved


if __name__ == "__main__":
    unittest.main()
