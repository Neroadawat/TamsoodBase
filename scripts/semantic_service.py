"""Semantic retrieval service for the public chat (embedding + Qdrant).

POST /search {"question": str, "k": int<=5} -> hits with chunk IDs and scores.
It returns IDs and scores only; the chat function resolves text/locators from
its own bundled corpus, so this service never serves content that was not
released. Questions are embedded in memory and are not stored or logged.
Auth: server-to-server bearer token. Not meant to be exposed to browsers.
"""
import argparse
import hashlib
import hmac
import json
import math
import os
import time
from collections import Counter
from http.server import BaseHTTPRequestHandler
from pathlib import Path

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from rag_http import LocalEvidenceServer

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "docs/rag/semantic-corpus.json"
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
STORE = ROOT / "build/rag"
MAX_K = 5
MAX_QUESTION = 500


def load_corpus():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    body = json.dumps(corpus["chunks"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if hashlib.sha256(body.encode("utf-8")).hexdigest()[:16] != corpus["corpus_version"]:
        raise ValueError("semantic-corpus.json version does not match its chunks; rebuild it")
    return corpus


LEXICAL_WEIGHT = 0.5  # fixed, not tuned: hybrid = cosine + 0.5 * char-bigram TF-IDF cosine


def _grams(text):
    text = "".join(ch for ch in text.lower() if not ch.isspace())
    return Counter(text[i:i + 2] for i in range(len(text) - 1))


class Lexical:
    """Character-bigram TF-IDF cosine. Language-agnostic, so it works on unsegmented Thai."""

    def __init__(self, texts):
        docs = [_grams(t) for t in texts]
        df = Counter(g for d in docs for g in d)
        self.idf = {g: math.log((1 + len(docs)) / (1 + n)) + 1 for g, n in df.items()}
        self.vecs = [self._vec(d) for d in docs]

    def _vec(self, counts):
        v = {g: n * self.idf.get(g, 1.0) for g, n in counts.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {g: x / norm for g, x in v.items()}

    def scores(self, question):
        q = self._vec(_grams(question))
        return [sum(w * d.get(g, 0.0) for g, w in q.items()) for d in self.vecs]


class Index:
    """In-memory Qdrant collection named by corpus version + model, rebuilt at start."""

    def __init__(self, corpus=None, cache_dir=None, local_only=True):
        self.corpus = corpus or load_corpus()
        self.chunks = self.corpus["chunks"]
        self.version = self.corpus["corpus_version"]
        self.encoder = TextEmbedding(MODEL, cache_dir=str(cache_dir or STORE / "models"),
                                     local_files_only=local_only, threads=2)
        self.client = QdrantClient(":memory:")
        self.collection = f"semantic_{self.version}"
        texts = [f"{c['title']}\n{c['text']}\n{c.get('search_hint', '')}" for c in self.chunks]
        self.lexical = Lexical(texts)
        # batch_size=1 keeps peak memory low (the host is shared; 384 MB container limit)
        vectors = list(self.encoder.embed(texts, batch_size=1))
        self.dimensions = len(vectors[0])
        self.client.create_collection(self.collection, vectors_config=models.VectorParams(
            size=self.dimensions, distance=models.Distance.COSINE))
        self.client.upsert(self.collection, [models.PointStruct(id=i, vector=v.tolist())
                                             for i, v in enumerate(vectors)], wait=True)

    def search(self, question, k=3, mode="hybrid"):
        """mode: 'semantic' (vectors only), 'lexical' (keywords only), 'hybrid' (default)."""
        k = max(1, min(int(k), MAX_K))
        scores = [0.0] * len(self.chunks)
        if mode in ("semantic", "hybrid"):
            vector = next(iter(self.encoder.embed([question]))).tolist()
            for p in self.client.query_points(self.collection, query=vector, limit=len(self.chunks)).points:
                scores[p.id] += float(p.score)
        if mode in ("lexical", "hybrid"):
            weight = 1.0 if mode == "lexical" else LEXICAL_WEIGHT
            for i, s in enumerate(self.lexical.scores(question)):
                scores[i] += weight * s
        order = sorted(range(len(scores)), key=lambda i: (-scores[i], i))[:k]
        return [{"id": self.chunks[i]["id"], "score": round(scores[i], 4)} for i in order]

    def count(self):
        return self.client.count(self.collection, exact=True).count


def serve(index, port, host, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):  # never log request lines (they carry no question, but stay quiet)
            pass

        def send_json(self, status, payload):
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path in ("/healthz", "/readyz"):
                ready = index.count() == len(index.chunks)
                self.send_json(200 if ready or self.path == "/healthz" else 503, {
                    "status": "ok" if ready else "not_ready", "service": "tamsoodbase-semantic",
                    "corpus_version": index.version, "chunks": len(index.chunks)})
            else:
                self.send_error(404)

        def do_POST(self):
            if self.path != "/search":
                self.send_error(404)
                return
            if not hmac.compare_digest(self.headers.get("Authorization", ""), f"Bearer {token}"):
                self.send_error(401)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 1 <= length <= 4096 or self.headers.get_content_type() != "application/json":
                    raise ValueError
                self.connection.settimeout(5)
                payload = json.loads(self.rfile.read(length))
                question = payload["question"].strip()
                if not 1 <= len(question) <= MAX_QUESTION:
                    raise ValueError
                k = int(payload.get("k", 3))
            except (ValueError, TypeError, KeyError, AttributeError, TimeoutError):
                self.send_error(400)
                return
            started = time.perf_counter()
            try:
                hits = index.search(question, k)
            except Exception:
                self.send_error(503)
                return
            self.send_json(200, {"corpus_version": index.version, "model": MODEL,
                                 "hits": hits, "ms": round((time.perf_counter() - started) * 1000, 1)})

    with LocalEvidenceServer((host, port), Handler) as server:
        print(f"semantic service on http://{host}:{port}/ corpus {index.version}", flush=True)
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8768)
    parser.add_argument("--host", choices=("127.0.0.1", "0.0.0.0"), default="127.0.0.1")
    args = parser.parse_args()
    token = os.environ.get("SEMANTIC_API_TOKEN", "")
    if not 32 <= len(token) <= 512:
        parser.error("Set SEMANTIC_API_TOKEN (32-512 characters) in the server environment.")
    serve(Index(), args.port, args.host, token)


if __name__ == "__main__":
    main()
