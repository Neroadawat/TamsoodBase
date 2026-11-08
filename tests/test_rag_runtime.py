"""Runtime trust boundaries, optional synthesis fallback, and local feedback."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from rag_gemini import summarize, validate_summary
from rag_review import ReviewInbox
from rag_lineage import Lineage, LineageUnavailable
from rag_evidence_page import render_observation

CARDS = json.loads((Path(__file__).resolve().parents[1] / 'docs/rag/public-evidence.json').read_bytes())


class RuntimeTests(unittest.TestCase):
    def test_source_view_preserves_null_and_escapes_untrusted_text(self):
        page = render_observation({'observation_id':'0'*64,'flow':'<script>alert(1)</script>',
            'amount':'0.4800','unit':None,'status':'HOLD_MISSING_UNIT', 'source_url':'javascript:alert(1)'}).decode()
        self.assertIn('0.4800', page); self.assertIn('พักการใช้', page)
        self.assertIn('&lt;script&gt;', page); self.assertNotIn('<script>', page)
        self.assertNotIn('href="javascript:', page); self.assertIn('ยังไม่ระบุ', page)
    def test_supported_summary_preserves_measurement_and_scope(self):
        result = validate_summary({'answer':'รถ E10 สตาร์ตเย็นมี CO₂ 934.990 กรัม/กม.',
                                   'source_ids':['e10-cold-start']}, CARDS[:1])
        self.assertIsNotNone(result)

    def test_unseen_values_units_fuels_species_and_citations_are_rejected(self):
        for answer in ('รถ E10 มี CO₂ 9999 กรัม/กม.', 'รถ E10 มี CO₂ 934.990 kg/km',
                       'รถ E20 สตาร์ตเย็นมี CO₂ 934.990 กรัม/กม.', 'รถ E10 ปล่อย N₂O 2.36 กรัม/กม.',
                       'รถ E10 เครื่องร้อนปล่อย CO₂ 934.990 กรัม/กม.'):
            with self.subTest(answer=answer):
                self.assertIsNone(validate_summary({'answer':answer,'source_ids':['e10-cold-start']}, CARDS[:1]))
        self.assertIsNone(validate_summary({'answer':'มีข้อมูล','source_ids':['unknown']}, CARDS[:1]))
        allocation = [card for card in CARDS if card['id'] == 'fame-allocation-caution']
        self.assertIsNone(validate_summary({'answer':'H-FAME จัดสรรภาระ 70% ให้เชื้อเพลิง',
                                           'source_ids':['fame-allocation-caution']}, allocation))

    def test_no_hits_and_no_key_never_call_provider(self):
        with patch('rag_gemini.http.client.HTTPSConnection') as connection:
            self.assertIsNone(summarize('question', [], 'test-key'))
            self.assertIsNone(summarize('question', CARDS[:1], None))
            connection.assert_not_called()

    def test_selected_model_keeps_fixed_host_and_family_specific_options(self):
        for model in ('gemini-2.5-flash-lite','gemini-3.5-flash-lite'):
            with self.subTest(model=model),patch('rag_gemini.http.client.HTTPSConnection') as factory:
                factory.return_value.getresponse.return_value.status=403
                self.assertIsNone(summarize('question',CARDS[:1],'fixture-key',model=model))
                self.assertEqual(factory.call_args.args[0],'generativelanguage.googleapis.com')
                request=factory.return_value.request.call_args
                self.assertEqual(request.args[1],'/v1beta/models/'+model+':generateContent')
                config=json.loads(request.kwargs['body'])['generationConfig']
                self.assertEqual('thinkingConfig' in config,model.startswith('gemini-2.5-'))
                self.assertEqual(config['responseMimeType'],'application/json')
                self.assertEqual(request.kwargs['headers']['x-goog-api-key'],'fixture-key')
        for model in ('https://evil.invalid/model','gemini-x/../../other','gemini-x?key=secret','gemini-x\r\nInjected: value',''):
            with self.subTest(model=model),patch('rag_gemini.http.client.HTTPSConnection') as factory:
                self.assertIsNone(summarize('question',CARDS[:1],'fixture-key',model=model))
                factory.assert_not_called()

    def test_quota_timeout_and_connection_failure_fall_back(self):
        with patch('rag_gemini.http.client.HTTPSConnection', side_effect=TimeoutError):
            self.assertIsNone(summarize('question', CARDS[:1], 'test-key'))
        with patch('rag_gemini.http.client.HTTPSConnection') as factory:
            connection = factory.return_value
            connection.getresponse.return_value.status = 429
            self.assertIsNone(summarize('question', CARDS[:1], 'test-key'))
            connection.close.assert_called_once()

    def test_valid_and_invalid_provider_responses(self):
        for answer, expected in (('รถ E10 สตาร์ตเย็นมี CO₂ 934.990 กรัม/กม.', True),
                                 ('รถ E10 สตาร์ตเย็นมี CO₂ 9999 กรัม/กม.', False)):
            with patch('rag_gemini.http.client.HTTPSConnection') as factory:
                response = factory.return_value.getresponse.return_value; response.status = 200
                content = {'answer':answer,'source_ids':['e10-cold-start']}
                response.read.return_value = json.dumps({'candidates':[{'finishReason':'STOP',
                    'content':{'parts':[{'text':json.dumps(content)}]}}]}).encode()
                self.assertEqual(summarize('E10 CO2 cold start', CARDS[:1], 'test-key') is not None, expected)

    def test_feedback_is_bound_to_real_results_and_saved_once(self):
        with tempfile.TemporaryDirectory() as folder:
            inbox = ReviewInbox('corpus', Path(folder) / 'feedback.jsonl')
            token = inbox.issue('คำถามทดสอบ', CARDS[:1])
            with self.assertRaises(ValueError): inbox.record('invented', 'sufficient')
            self.assertTrue(inbox.record(token, 'insufficient', 'ผิดขอบเขต')['saved'])
            with self.assertRaises(ValueError): inbox.record(token, 'sufficient')
            record = json.loads(inbox.path.read_text(encoding='utf-8'))
            self.assertEqual(record['card_ids'], ['e10-cold-start'])
            self.assertFalse(record['independent_human_review_verified'])

    def test_changed_lineage_file_is_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Lineage.__new__(Lineage); store.path = Path(folder) / 'store.sqlite'
            store.path.write_bytes(b'changed'); store.manifest = {'database_sha256':'0'*64}
            with self.assertRaises(LineageUnavailable):
                with store.connect(): pass

    @unittest.skipUnless((Path(__file__).resolve().parents[1] / 'build/handoff/current.json').exists(), 'Requires restored review store')
    def test_actual_lineage_preserves_hold_and_blocks_unapproved_rows(self):
        store = Lineage(); link = store.card('palm-land-unit-hold')
        self.assertEqual(link['count'], 1)
        row = store.observation(link['observations'][0]['observation_id'])
        self.assertIsNone(row['unit']); self.assertEqual(row['status'], 'HOLD_MISSING_UNIT')
        with self.assertRaises(ValueError): store.observation("' OR 1=1 --")
        with store.connect() as con:
            private = con.execute('SELECT id FROM observation WHERE public=0 LIMIT 1').fetchone()[0]
        with self.assertRaises(LookupError): store.observation(private)


if __name__ == '__main__': unittest.main()
