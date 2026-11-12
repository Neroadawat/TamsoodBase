"""Local vector retrieval for the reviewed public FAQ corpus."""

import argparse
import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from rag_gemini import summarize, valid_model, MODEL as GEMINI_MODEL
from rag_scope import compatible, constraints, load_scope, normalized_question
from rag_review import ReviewInbox
from rag_http import LocalEvidenceServer


ROOT = Path(__file__).resolve().parents[1]
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DATA = ROOT / "docs/rag/public-evidence.json"
STORE = ROOT / "build/rag"
# Initial cutoff for the four-card FAQ; calibrate against a larger evaluation set.
MIN_SCORE = 0.45
EMBEDDING_THREADS = 2


def retrieve(client, encoder, collection, cards, question):
    scope, wanted = load_scope(cards), constraints(question)
    variants = list(dict.fromkeys((question, normalized_question(question))))
    candidates = {}
    for vector in encoder.embed(variants):
        matches = client.query_points(
            collection, query=vector.tolist(), limit=len(cards), with_payload=False,
            # Retrieve a narrow band below the normal cutoff so the reviewed
            # FAME-period caveat can answer a metadata question without opening
            # lower-confidence hits for other cards.
            score_threshold=MIN_SCORE - 0.04,
        )
        for point in matches.points:
            card = cards[point.id]
            floor = (MIN_SCORE - 0.04 if card['id'] == 'fame-measurement-period'
                     and wanted['fame_period_question'] else MIN_SCORE)
            if point.score >= floor and compatible(scope[card['id']], wanted):
                candidates[point.id] = max(candidates.get(point.id, -1), point.score)
    preferred = wanted['preferred_card']
    ordered = sorted(candidates, key=lambda index: (
        cards[index]['id'] != preferred, -candidates[index], index
    ))[:3]
    return [{"score": round(candidates[index], 4), **cards[index]} for index in ordered]


def serve(client, encoder, collection, cards, port, gemini_key=None, lineage=None,
          gemini_model=GEMINI_MODEL, host="127.0.0.1", allowed_origin=None,
          service_token=None, feedback_path=None):
    explicit_allowed_origin = allowed_origin is not None
    allowed_origin = allowed_origin or f"http://127.0.0.1:{port}"
    origin = urlsplit(allowed_origin)
    if (origin.scheme not in ("http", "https") or not origin.hostname or origin.username
            or origin.password or origin.path not in ("", "/") or origin.query or origin.fragment):
        raise ValueError("allowed_origin must be one exact HTTP(S) origin")
    if host == "0.0.0.0" and not explicit_allowed_origin:
        raise ValueError("An exact allowed_origin is required when binding outside loopback")
    if service_token is not None and not 32 <= len(service_token) <= 512:
        raise ValueError("RAG_API_TOKEN must contain 32–512 characters")
    review = ReviewInbox(hashlib.sha256(DATA.read_bytes()).hexdigest(), path=feedback_path)
    notice = ("โหมด Gemini จะส่งคำถามและข้อความจากการ์ดสาธารณะที่ค้นเจอไปยัง Google "
              "กรุณาอย่าใส่ข้อมูลส่วนตัวหรือข้อมูลภายใน" if gemini_key else
              "โหมดค้นในเครื่องใช้การ์ดหลักฐานโดยตรง")
    page = (Path(__file__).with_name("rag_demo.html")).read_text(encoding="utf-8")
    page = page.replace('<!-- card-count -->', str(len(cards)))
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
            parsed = urlsplit(self.path)
            if parsed.path in ("/healthz", "/readyz"):
                try:
                    count = client.count(collection, exact=True).count
                except Exception:
                    count = -1
                ready = count == len(cards)
                payload = {"status": "ok" if ready else "not_ready",
                           "service": "tamsoodbase-rag", "evidence_records": max(0, count)}
                status = 200 if parsed.path == "/healthz" or ready else 503
                self.send_content(status, "application/json; charset=utf-8",
                                  json.dumps(payload, ensure_ascii=False).encode("utf-8"))
                return
            if parsed.path in ('/evidence', '/evidence/view', '/graph'):
                if lineage is None:
                    self.send_error(503, 'Local lineage not enabled'); return
                try:
                    ids = parse_qs(parsed.query).get('id', [])
                    if len(ids) != 1: raise ValueError('Exactly one observation ID required')
                    oid = ids[0]
                    payload = lineage.observation(oid)
                    if parsed.path == '/evidence/view':
                        from rag_evidence_page import render_observation
                        self.send_content(200, 'text/html; charset=utf-8', render_observation(
                            payload, graph_available=(ROOT / 'build/handoff/engines.json').exists()))
                        return
                    if parsed.path == '/graph':
                        from verify_handoff_engines import graph_observation
                        engine = json.loads((ROOT / 'build/handoff/engines.json').read_bytes())
                        if engine['release'] != lineage.manifest['release']: raise ValueError('Graph release changed')
                        payload = {'release': engine['release'], 'rows': graph_observation(engine['neo4j_container'], oid)}
                    self.send_content(200, 'application/json; charset=utf-8', json.dumps(payload, ensure_ascii=False).encode())
                except ValueError: self.send_error(400)
                except LookupError: self.send_error(404)
                except Exception: self.send_error(503, 'Local lineage unavailable')
                return
            if self.path == "/":
                self.send_content(200, "text/html; charset=utf-8", page)
            else:
                self.send_error(404)

        def do_POST(self):
            if self.path not in ("/ask", "/review"):
                self.send_error(404)
                return
            if self.headers.get("Origin") != allowed_origin:
                self.send_error(403)
                return
            if service_token is not None:
                supplied = self.headers.get("Authorization", "")
                if not hmac.compare_digest(supplied, f"Bearer {service_token}"):
                    self.send_error(401)
                    return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 1 <= length <= 8192 or self.headers.get_content_type() != "application/json":
                    raise ValueError
                self.connection.settimeout(5)
                payload = json.loads(self.rfile.read(length))
                if self.path == '/review':
                    saved = review.record(payload['search_id'], payload['verdict'], payload.get('note', ''))
                    self.send_content(200, 'application/json; charset=utf-8', json.dumps(saved).encode()); return
                question = payload["question"].strip()
                if not 1 <= len(question) <= 500:
                    raise ValueError
            except (ValueError, TypeError, KeyError, AttributeError, TimeoutError):
                self.send_error(400)
                return
            except OSError:
                self.send_error(503, 'Local review storage unavailable')
                return
            try:
                hits = retrieve(client, encoder, collection, cards, question)
                if lineage is not None:
                    for hit in hits: hit['lineage'] = lineage.card(hit['id'])
            except Exception:
                self.send_error(503, "Evidence search unavailable")
                return
            result = {"hits": hits, "summary": summarize(question, hits, gemini_key,model=gemini_model),
                      "search_id": review.issue(question, hits)}
            self.send_content(200, "application/json; charset=utf-8",
                              json.dumps(result, ensure_ascii=False).encode("utf-8"))

    with LocalEvidenceServer((host, port), Handler) as server:
        display_host = "127.0.0.1" if host == "0.0.0.0" else host
        print(f"http://{display_host}:{port}/", flush=True)
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cloud", action="store_true", help="Use configured Qdrant Cloud.")
    parser.add_argument("--in-memory", action="store_true",
                        help="Build a temporary Qdrant index at startup for a small corpus.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("index")
    search = commands.add_parser("search")
    search.add_argument("question")
    web = commands.add_parser("serve")
    web.add_argument("--port", type=int, default=8767)
    web.add_argument("--host", choices=("127.0.0.1", "0.0.0.0"), default="127.0.0.1")
    web.add_argument("--allowed-origin", help="Exact HTTP(S) browser origin allowed to POST.")
    web.add_argument("--gemini", action="store_true", help="Send questions and matched public cards to Gemini.")
    web.add_argument('--gemini-model',help='Gemini model ID available to this account; requires --gemini.')
    web.add_argument('--lineage', action='store_true', help='Link reviewed local source rows and the isolated graph lab.')
    args = parser.parse_args()
    if args.in_memory and (args.command != "serve" or args.cloud):
        parser.error("--in-memory is supported only for local serve mode.")
    if args.command == "search" and not 1 <= len(args.question.strip()) <= 500:
        parser.error("Question must have 1–500 characters.")
    gemini_key = None
    if args.command == "serve" and args.gemini:
        if args.gemini_model and not valid_model(args.gemini_model):
            parser.error('Use a Gemini model ID, without a URL or path.')
        gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not gemini_key:
            parser.error("Set GEMINI_API_KEY in the server environment.")
    elif args.command == 'serve' and args.gemini_model:
        parser.error('--gemini-model requires --gemini.')

    corpus = DATA.read_bytes()
    cards = json.loads(corpus)
    fingerprint = hashlib.sha256(MODEL.encode() + corpus).hexdigest()[:20]
    collection = f"public_evidence_{fingerprint}"
    if not args.in_memory:
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
    elif args.in_memory:
        client = QdrantClient(":memory:")
    else:
        client = QdrantClient(path=str(STORE / "qdrant"))
    try:
        exists = client.collection_exists(collection)
        if args.command != "index" and not args.in_memory and (
            not exists or client.count(collection, exact=True).count != len(cards)
        ):
            parser.error("Run index for the current corpus first.")

        encoder = TextEmbedding(
            MODEL, cache_dir=str(STORE / "models"), local_files_only=args.command != "index",
            threads=EMBEDDING_THREADS,
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
            if args.in_memory:
                vectors = list(encoder.embed(
                    [f"{card['title']}\n{card['text']}" for card in cards], batch_size=1
                ))
                if not vectors:
                    parser.error("The in-memory corpus must contain at least one card.")
                client.create_collection(collection, vectors_config=models.VectorParams(
                    size=len(vectors[0]), distance=models.Distance.COSINE
                ))
                client.upsert(collection, [models.PointStruct(id=index, vector=vector.tolist())
                                           for index, vector in enumerate(vectors)], wait=True)
            lineage = None
            if args.lineage:
                from rag_lineage import Lineage
                lineage = Lineage()
            allowed_origin = args.allowed_origin or os.environ.get(
                "RAG_ALLOWED_ORIGIN", f"http://127.0.0.1:{args.port}"
            )
            token = os.environ.get("RAG_API_TOKEN") or None
            if args.host == "0.0.0.0" and not args.allowed_origin and not os.environ.get("RAG_ALLOWED_ORIGIN"):
                parser.error("Set --allowed-origin or RAG_ALLOWED_ORIGIN when binding outside loopback.")
            if token is not None and not 32 <= len(token) <= 512:
                parser.error("RAG_API_TOKEN must contain 32–512 characters.")
            feedback_path = Path(os.environ["RAG_FEEDBACK_PATH"]) if os.environ.get("RAG_FEEDBACK_PATH") else None
            serve(client, encoder, collection, cards, args.port, gemini_key, lineage,
                  args.gemini_model or GEMINI_MODEL, args.host, allowed_origin, token, feedback_path)
            return
        else:
            result = retrieve(client, encoder, collection, cards, args.question.strip())
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        client.close()


if __name__ == "__main__":
    main()
