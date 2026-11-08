"""Audit the local corpus expansion and its recorded provenance, without network calls."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / 'docs/rag/public-evidence.json'
    cards = json.loads(path.read_bytes())
    baseline = json.loads(subprocess.check_output(
        ['git', 'show', '67db1ad:docs/rag/public-evidence.json'], cwd=ROOT))
    scope = json.loads((ROOT / 'docs/rag/retrieval-scope.json').read_bytes())
    source = json.loads((ROOT / 'evidence/upstream-inventory-review.json').read_bytes())['source']
    reviewed = []
    checks = {
        'original_four_cards_unchanged': cards[:len(baseline)] == baseline and len(baseline) == 4,
        'ten_unique_card_ids': len(cards) == len({c['id'] for c in cards}) == 10,
        'scope_ids_match': set(scope['cards']) == {c['id'] for c in cards},
        'scope_hash_matches': scope['corpus_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest(),
        'recorded_article_rights': source['rights_status'] == 'ARTICLE_CC_BY_4_0',
    }
    for card in cards[len(baseline):]:
        files = [{
            'path': name, 'sha256': hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        } for name in card['review_basis']]
        valid = (card['licence'] == 'CC BY 4.0' and bool(card['attribution'])
                 and bool(card['locator']) and bool(card['claim_type'])
                 and card['source_url'] == 'https://doi.org/10.3390/su12229415' and len(files) >= 2)
        checks[card['id']] = valid
        reviewed.append({'id': card['id'], 'claim_type': card['claim_type'], 'licence': card['licence'],
                         'source_url': card['source_url'], 'locator': card['locator'], 'review_files': files})
    report = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'CORPUS_EXPANSION_LOCAL_PROVENANCE_NOT_NEW_SOURCE_MEASUREMENT',
        'baseline_commit': '67db1ad', 'card_count_before': len(baseline), 'card_count_after': len(cards),
        'corpus_sha256': scope['corpus_sha256'], 'passed': all(checks.values()), 'checks': checks,
        'recorded_source_pdf_sha256': source['sha256'],
        'source_pdf_hash_reverified_this_round': False,
        'primary_source_access': 'Official publisher PDF text accessed via web; Section 2.1, Tables 1-4 and CC BY 4.0 notice checked. Not a full visual re-audit.',
        'added_cards': reviewed,
        'limits': ['Licence/provenance checks here apply to six new cards, not blanket clearance of historical source documents.',
                   'Summaries and team caveats are distinct from new measurements or model-ready inventory.'],
    }
    (ROOT / 'evidence/rag-corpus-expansion-2026-11-08.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'cards': len(cards), 'added': len(reviewed)}))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
