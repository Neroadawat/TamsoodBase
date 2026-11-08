"""Offline retrieval evaluation; no LLM or source acquisition. Stop the demo first."""
import hashlib
import argparse
import importlib.metadata
import json
from datetime import datetime, timezone

from rag_retrieve import DATA, MODEL, ROOT, STORE, MIN_SCORE, EMBEDDING_THREADS, QdrantClient, TextEmbedding, retrieve
from rag_scope import SCOPE_PATH


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--questions', default='docs/rag/evaluation-questions.json')
    parser.add_argument('--output', default='evidence/rag-scoped-regression-2026-11-08.json')
    args = parser.parse_args()
    corpus = DATA.read_bytes()
    cards = json.loads(corpus)
    cases_path = ROOT / args.questions
    cases = json.loads(cases_path.read_text(encoding='utf-8'))
    collection = 'public_evidence_' + hashlib.sha256(MODEL.encode() + corpus).hexdigest()[:20]
    encoder = TextEmbedding(MODEL, cache_dir=str(STORE / 'models'), local_files_only=True, threads=EMBEDDING_THREADS)
    rows = []
    client = QdrantClient(path=str(STORE / 'qdrant'))
    try:
        assert client.count(collection, exact=True).count == len(cards)
        for case, vector in zip(cases, encoder.embed([c['question'] for c in cases])):
            points = client.query_points(collection, query=vector.tolist(), limit=len(cards)).points
            ranked = [{'id': cards[p.id]['id'], 'score': round(p.score, 6)} for p in points]
            accepted = retrieve(client, encoder, collection, cards, case['question'])
            expected = case['expected']
            passed = (not accepted if expected is None else
                      bool(accepted) and accepted[0]['id'] == expected) if expected != 'ambiguous' else None
            rows.append({**case, 'ranked': ranked, 'returned': accepted, 'passed': passed})
    finally:
        client.close()
    positives = [r for r in rows if r['expected'] not in (None, 'ambiguous')]
    negatives = [r for r in rows if r['expected'] is None]
    result = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'LOCAL_EVIDENCE_CARD_RETRIEVAL_NOT_ANSWER_ACCURACY',
        'card_count': len(cards),
        'embedding_threads': EMBEDDING_THREADS,
        'corpus_sha256': hashlib.sha256(corpus).hexdigest(),
        'questions_sha256': hashlib.sha256(cases_path.read_bytes()).hexdigest(),
        'retrieval_scope_sha256': hashlib.sha256(SCOPE_PATH.read_bytes()).hexdigest(),
        'retrieval_code_sha256': {name: hashlib.sha256((ROOT / 'scripts' / name).read_bytes()).hexdigest()
                                  for name in ('rag_scope.py', 'rag_retrieve.py')},
        'model': MODEL, 'collection': collection, 'cutoff': MIN_SCORE,
        'versions': {p: importlib.metadata.version(p) for p in ('fastembed', 'qdrant-client', 'onnxruntime', 'numpy')},
        'positive_top1_pass': sum(r['passed'] for r in positives), 'positive_count': len(positives),
        'negative_rejection_pass': sum(r['passed'] for r in negatives), 'negative_count': len(negatives),
        'baseline_raw_threshold_comparison': [{
            'cutoff': cutoff,
            'positive_top1_pass': sum(r['ranked'][0]['id'] == r['expected'] and r['ranked'][0]['score'] >= cutoff for r in positives),
            'negative_rejection_pass': sum(r['ranked'][0]['score'] < cutoff for r in negatives),
        } for cutoff in (0.35, 0.45, 0.55, 0.65, 0.70, 0.75)],
        'source_locators_present': all(c.get('source_url', '').startswith('https://') and c.get('locator') for c in cards),
        'limitations': ['Questions authored before running but not by independent human reviewers.',
                        'Bounded facet rules cover known fuels/species/stages only, not general semantic sufficiency.',
                        'Ambiguous questions inspected without a correctness score; no answer generation tested.'],
        'results': rows,
    }
    output = ROOT / args.output
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'results'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
