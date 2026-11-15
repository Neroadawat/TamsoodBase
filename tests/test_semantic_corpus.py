"""The semantic corpus must be exactly what the released pack and its reviewed hints produce."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_semantic_corpus as build  # noqa: E402


class SemanticCorpusTest(unittest.TestCase):
    def test_committed_corpus_is_current(self):
        committed = json.loads(build.OUT.read_text(encoding="utf-8"))
        self.assertEqual(committed, build.build(), "run scripts/build_semantic_corpus.py")

    def test_version_hashes_chunks(self):
        corpus = json.loads(build.OUT.read_text(encoding="utf-8"))
        body = json.dumps(corpus["chunks"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        self.assertEqual(corpus["corpus_version"], hashlib.sha256(body.encode()).hexdigest()[:16])

    def test_only_released_text_and_no_numeric_tables(self):
        pack = json.loads(build.PACK.read_text(encoding="utf-8"))
        corpus = json.loads(build.OUT.read_text(encoding="utf-8"))
        self.assertEqual(corpus["pack_sha256"], pack["content_sha256"])
        self.assertEqual(len(corpus["chunks"]), len(pack["notes"]) + len(pack["catalogue"]))
        self.assertEqual(len({c["id"] for c in corpus["chunks"]}), len(corpus["chunks"]))
        self.assertTrue(all(c["kind"] in ("note", "catalogue") for c in corpus["chunks"]))
        self.assertFalse(any("rows" in c for c in corpus["chunks"]))

    def test_every_chunk_has_reviewed_hint(self):
        self.assertEqual(set(build.HINTS), {c["id"] for c in build.build()["chunks"]})

    def test_eval_questions_reference_real_ids(self):
        ids = {c["id"] for c in build.build()["chunks"]}
        for name in ("semantic-eval-questions.json", "semantic-eval-questions-v2.json"):
            data = json.loads((ROOT / "docs/rag" / name).read_text(encoding="utf-8"))
            for row in data["paraphrase"]:
                self.assertTrue(set(row["relevant"]) <= ids, row["q"])
            for row in data["adversarial"]:
                self.assertTrue(set(row["acceptable_ids"]) <= ids, row["q"])


if __name__ == "__main__":
    unittest.main()
