"""Search-contract regressions: high similarity cannot override explicit scope."""
import json
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
HAS_RAG = all(importlib.util.find_spec(name) is not None for name in ('fastembed', 'qdrant_client'))
if HAS_RAG:
    from rag_retrieve import DATA, retrieve
    from rag_scope import load_scope


class Encoder:
    def embed(self, texts):
        return iter([SimpleNamespace(tolist=lambda: [1.0])] * len(texts))


class HighSimilarityClient:
    def query_points(self, *args, **kwargs):
        return SimpleNamespace(points=[SimpleNamespace(id=i, score=0.99 - i * .01) for i in range(kwargs['limit'])])


@unittest.skipUnless(HAS_RAG, 'Run with build/rag-verified-venv Python; optional RAG dependencies required')
class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.cards = json.loads(DATA.read_bytes())

    def test_high_similarity_cannot_override_unsupported_fuel_species_or_stage(self):
        for question in ('E20 cold start', 'E-85 CO2', 'E 20 CO2',
                         'E10 N₂O', 'E10 CH4', 'E10 CO2 และ N2O',
                         'E10 hot-start', 'E10 full driving cycle', 'E10 highway',
                         'E10 warm start', 'E10 เดินเบา', 'E10 N 2 O',
                         'E๒๐ cold start', 'H-FAME glycerine allocation เท่าไร',
                         'TSM ปล่อยมีเทนปี 2024 เท่าไร'):
            with self.subTest(question=question):
                self.assertEqual(retrieve(HighSimilarityClient(), Encoder(), 'test', self.cards, question), [])

    def test_supported_measurement_keeps_original_evidence(self):
        hits = retrieve(HighSimilarityClient(), Encoder(), 'test', self.cards, 'E10 CO₂ cold start เท่าไร')
        self.assertEqual(len(hits), 1)
        self.assertEqual({k: hits[0][k] for k in self.cards[0]}, self.cards[0])

    def test_multi_fuel_comparison_needs_evidence_for_both(self):
        self.assertEqual(retrieve(HighSimilarityClient(), Encoder(), 'test', self.cards,
                                  'E10 และ E20 cold start ต่างกันเท่าใด'), [])

    def test_unreviewed_card_requires_scope_review(self):
        with self.assertRaises(ValueError):
            load_scope(self.cards + [{'id': 'unreviewed'}])
        self.cards[0]['text'] += ' changed observation'
        with self.assertRaises(ValueError):
            load_scope(self.cards)

    def test_co2_next_to_e10_is_not_co2e_and_thai_related_is_not_numeric(self):
        hits = retrieve(HighSimilarityClient(), Encoder(), 'test', self.cards, 'CO2 E10 ตอนเครื่องเย็น')
        self.assertEqual([h['id'] for h in hits], ['e10-cold-start'])
        hits = retrieve(HighSimilarityClient(), Encoder(), 'test', self.cards, 'ชานอ้อยเกี่ยวข้องกับไฟฟ้าอย่างไร')
        self.assertIn('bagasse-steam', [h['id'] for h in hits])

    def test_new_metadata_cards_cannot_answer_missing_physical_quantities(self):
        for question in ('FAME ใช้เมทานอลกี่กิโลกรัมต่อตัน',
                         'Land seeding กี่เฮกตาร์', 'FFB เข้า CPO กี่กิโลกรัม'):
            with self.subTest(question=question):
                hits = retrieve(HighSimilarityClient(), Encoder(), 'test', self.cards, question)
                self.assertFalse(any(h['id'] in ('fame-functional-unit', 'fame-allocation-caution',
                                                'palm-upstream-basis', 'palm-cpo-provider-gap',
                                                'palm-land-unit-hold') for h in hits))


if __name__ == '__main__':
    unittest.main()
