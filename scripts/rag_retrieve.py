"""Local vector retrieval for the reviewed public FAQ corpus."""

import argparse
import hashlib
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from rag_gemini import summarize


ROOT = Path(__file__).resolve().parents[1]
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DATA = ROOT / "docs/rag/public-evidence.json"
STORE = ROOT / "build/rag"
# Initial cutoff for the four-card FAQ; calibrate against a larger evaluation set.
MIN_SCORE = 0.45


def retrieve(client, encoder, collection, cards, question):
    vector = next(encoder.embed([question]))
    matches = client.query_points(
        collection, query=vector.tolist(), limit=3, with_payload=False,
        score_threshold=MIN_SCORE,
    )
    return [{"score": round(point.score, 4), **cards[point.id]} for point in matches.points]


def serve(client, encoder, collection, cards, port, gemini_key=None):
    notice = ("โหมด Gemini จะส่งคำถามและข้อความจากการ์ดสาธารณะที่ค้นเจอไปยัง Google "
              "กรุณาอย่าใส่ข้อมูลส่วนตัวหรือข้อมูลภายใน" if gemini_key else
              "โหมดค้นในเครื่องใช้การ์ดหลักฐานโดยตรง")
    page = (Path(__file__).with_name("rag_demo.html")).read_text(encoding="utf-8")
    page = page.replace("<!-- mode-notice -->", notice).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def send_content(self, status, content_type, content):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            if self.path == "/":
                self.send_content(200, "text/html; charset=utf-8", page)
            else:
                self.send_error(404)

        def do_POST(self):
            if self.path != "/ask":
                self.send_error(404)
                return
            if self.headers.get("Origin") != f"http://127.0.0.1:{port}":
                self.send_error(403)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 1 <= length <= 8192 or self.headers.get_content_type() != "application/json":
                    raise ValueError
                self.connection.settimeout(5)
                question = json.loads(self.rfile.read(length))["question"].strip()
                if not 1 <= len(question) <= 500:
                    raise ValueError
            except (ValueError, TypeError, KeyError, AttributeError, TimeoutError):
                self.send_error(400)
                return
            try:
                hits = retrieve(client, encoder, collection, cards, question)
            except Exception:
                self.send_error(503, "Evidence search unavailable")
                return
            result = {"hits": hits, "summary": summarize(question, hits, gemini_key)}
            self.send_content(200, "application/json; charset=utf-8",
                              json.dumps(result, ensure_ascii=False).encode("utf-8"))

    with HTTPServer(("127.0.0.1", port), Handler) as server:
        print(f"http://127.0.0.1:{port}/", flush=True)
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cloud", action="store_true", help="Use configured Qdrant Cloud.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("index")
    search = commands.add_parser("search")
    search.add_argument("question")
    web = commands.add_parser("serve")
    web.add_argument("--port", type=int, default=8767)
    web.add_argument("--gemini", action="store_true", help="Send questions and matched public cards to Gemini.")
    args = parser.parse_args()
    if args.command == "search" and not 1 <= len(args.question.strip()) <= 500:
        parser.error("Question must have 1–500 characters.")
    gemini_key = None
    if args.command == "serve" and args.gemini:
        gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not gemini_key:
            parser.error("Set GEMINI_API_KEY in the server environment.")

    corpus = DATA.read_bytes()
    cards = json.loads(corpus)
    fingerprint = hashlib.sha256(MODEL.encode() + corpus).hexdigest()[:20]
    collection = f"public_evidence_{fingerprint}"
    STORE.mkdir(parents=True, exist_ok=True)
    if args.cloud:
        url = os.environ.get("TAMSOOD_QDRANT_URL", "")
        key = os.environ.get("TAMSOOD_QDRANT_API_KEY")
        endpoint = urlsplit(url)
        if (endpoint.scheme != "https" or not (endpoint.hostname or "").endswith(".cloud.qdrant.io")
                or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment
                or endpoint.path not in ("", "/") or not key):
            parser.error("Configure a Qdrant Cloud HTTPS endpoint and server-side API key.")
        client = QdrantClient(url=url, api_key=key, timeout=10)
    else:
        client = QdrantClient(path=str(STORE / "qdrant"))
    try:
        exists = client.collection_exists(collection)
        if args.command != "index" and (
            not exists or client.count(collection, exact=True).count != len(cards)
        ):
            parser.error("Run index for the current corpus first.")

        encoder = TextEmbedding(
            MODEL, cache_dir=str(STORE / "models"), local_files_only=args.command != "index"
        )
        if args.command == "index":
            vectors = list(encoder.embed([f"{card['title']}\n{card['text']}" for card in cards]))
            if not exists:
                client.create_collection(
                    collection, vectors_config=models.VectorParams(
                        size=len(vectors[0]), distance=models.Distance.COSINE
                    )
                )
            client.upsert(collection, [
                models.PointStruct(id=index, vector=vector.tolist())
                for index, vector in enumerate(vectors)
            ], wait=True)
            result = {"collection": collection, "points": client.count(collection, exact=True).count,
                      "model": MODEL, "dimensions": len(vectors[0])}
        elif args.command == "serve":
            serve(client, encoder, collection, cards, args.port, gemini_key)
            return
        else:
            result = retrieve(client, encoder, collection, cards, args.question.strip())
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        client.close()


if __name__ == "__main__":
    main()
