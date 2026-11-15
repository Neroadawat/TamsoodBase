"""HTTP/runtime contract for the private, containerized RAG service."""
import json
import socket
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import rag_retrieve
import package_rag_ec2
from rag_http import LocalEvidenceServer


class _CountClient:
    def count(self, collection, exact=True):
        return SimpleNamespace(count=1)


class RagServiceRuntimeTests(unittest.TestCase):
    def test_image_allowlist_contains_runtime_corpus_dependencies(self):
        required = {
            "docs/rag/public-evidence.json",
            "docs/rag/retrieval-scope.json",
            "docs/rag/statistical-facts.json",
            "docs/rag/thai-answer-copy.json",
        }
        self.assertTrue(required.issubset(set(package_rag_ec2.STATIC_FILES)))
        dockerfile = (ROOT / "deploy/Dockerfile.rag").read_text(encoding="utf-8")
        self.assertIn(
            "COPY --chown=10001:10001 docs/rag/retrieval-scope.json "
            "/app/docs/rag/retrieval-scope.json",
            dockerfile,
        )

    def test_service_health_origin_bearer_auth_and_ephemeral_feedback(self):
        captured = {}

        class CaptureServer:
            def __init__(self, address, handler):
                captured["handler"] = handler
                captured["configured_address"] = address

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def serve_forever(self):
                return None

        with tempfile.TemporaryDirectory() as folder:
            feedback_path = Path(folder) / "feedback.jsonl"
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            origin = f"http://127.0.0.1:{port}"
            card = {"id": "fame-functional-unit", "title": "FAME functional unit",
                    "text": "The functional unit is 1000 MJ.",
                    "source_url": "https://example.org/article", "locator": "Table 4"}

            with patch.object(rag_retrieve, "LocalEvidenceServer", CaptureServer), \
                    patch.object(rag_retrieve, "retrieve", return_value=[card]), \
                    patch.object(rag_retrieve, "summarize", return_value=None):
                rag_retrieve.serve(_CountClient(), object(), "collection", [card], port,
                                   host="127.0.0.1", allowed_origin=origin,
                                   service_token="s" * 40, feedback_path=feedback_path)

                self.assertEqual(captured["configured_address"], ("127.0.0.1", port))
                with LocalEvidenceServer(("127.0.0.1", port), captured["handler"]) as server:
                    worker = threading.Thread(target=server.serve_forever, daemon=True)
                    worker.start()
                    try:
                        with urlopen(origin + "/readyz", timeout=2) as response:
                            ready = json.loads(response.read())
                            self.assertEqual(response.status, 200)
                        self.assertEqual(ready["evidence_records"], 1)
                        with urlopen(origin + "/healthz", timeout=2) as response:
                            self.assertEqual(response.status, 200)

                        def post(path, payload, request_origin=origin, token="s" * 40):
                            headers = {"Content-Type": "application/json", "Origin": request_origin}
                            if token is not None:
                                headers["Authorization"] = "Bearer " + token
                            request = Request(origin + path,
                                              data=json.dumps(payload).encode("utf-8"),
                                              headers=headers)
                            try:
                                with urlopen(request, timeout=2) as response:
                                    return response.status, json.loads(response.read())
                            except HTTPError as error:
                                return error.code, None

                        code, _ = post("/ask", {"question": "FAME functional unit"},
                                       request_origin="https://attacker.invalid")
                        self.assertEqual(code, 403)
                        code, _ = post("/ask", {"question": "FAME functional unit"}, token=None)
                        self.assertEqual(code, 401)
                        code, result = post("/ask", {"question": "FAME functional unit"})
                        self.assertEqual(code, 200)
                        self.assertEqual(result["hits"][0]["id"], "fame-functional-unit")
                        code, saved = post("/review", {"search_id": result["search_id"],
                            "verdict": "uncertain", "note": "test"})
                        self.assertEqual(code, 200)
                        self.assertTrue(saved["saved"])
                        self.assertTrue(feedback_path.is_file())
                    finally:
                        server.shutdown()
                        worker.join(timeout=2)

    def test_non_loopback_bind_requires_explicit_origin(self):
        with self.assertRaisesRegex(ValueError, "exact allowed_origin"):
            rag_retrieve.serve(_CountClient(), object(), "collection", [], 8767,
                               host="0.0.0.0")


if __name__ == "__main__":
    unittest.main()
