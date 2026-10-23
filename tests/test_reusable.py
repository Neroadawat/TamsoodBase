import csv
import io
import json
import sqlite3
import unittest
from decimal import Decimal
from pathlib import Path
from src.build_reusable import classification
from src.reusable_api import catalog,export_csv


class ReferenceSemanticsTests(unittest.TestCase):
    def test_intensity_and_context_are_not_input_flows(self):
        self.assertEqual(classification({'metric_id':'fuel_intensity','direction':'CONTEXT'}),('REPORTED_INTENSITY','INTENSITY'))
        self.assertEqual(classification({'metric_id':'throughput','direction':'CONTEXT'}),('CONTEXT_METRIC','CONTEXT'))
        self.assertEqual(classification({'metric_id':'fuel_total','direction':'INPUT'}),('ORGANIZATION_INPUT','TOTAL'))
        self.assertEqual(classification({'metric_id':'natural_gas','direction':'INPUT'}),('ORGANIZATION_INPUT','COMPONENT'))


@unittest.skipUnless(Path('build/reusable/manifest.json').exists(),'Reusable release required')
class ReferenceReleaseTests(unittest.TestCase):
    def test_default_export_excludes_holds_and_preserves_usage_profile(self):
        data=catalog({},True)
        self.assertEqual(data['total'],97)
        self.assertTrue(all(r['decision']=='ACCEPTED_REFERENCE' and r['usage_profile']=='LOCAL_RESEARCH_REFERENCE'
                            and r['redistribution_status']=='NOT_CLEARED' and not r['is_normalized_lci_exchange'] for r in data['rows']))
        self.assertEqual(catalog({'decision':'HOLD_CONTEXT'},True)['total'],4)
        self.assertEqual(catalog({'decision':'all'},True)['total'],101)

    def test_parameterized_filters_and_csv_roundtrip(self):
        data=catalog({'publisher':'SPRC','year':'2024','data_kind':'REPORTED_INTENSITY'},True)
        self.assertEqual(data['total'],1)
        self.assertEqual(Decimal(data['rows'][0]['scaled_amount']),Decimal('2.57'))
        self.assertEqual(data['rows'][0]['unit_code'],'GJ/t throughput')
        csv_rows=list(csv.DictReader(io.StringIO(export_csv({'publisher':'SPRC','year':'2024','data_kind':'REPORTED_INTENSITY'}).decode('utf-8-sig'))))
        self.assertEqual(csv_rows[0]['source_url'],data['rows'][0]['source_url'])
        self.assertEqual(catalog({'q':"' OR 1=1 --"},True)['total'],0)
        with self.assertRaises(ValueError): catalog({'data_kind':'invented'})

    def test_every_exported_value_matches_typed_database(self):
        rows=json.loads(Path('build/reusable/all-reference.json').read_text(encoding='utf-8'))
        actual={r['observation_id']:r for r in catalog({'decision':'all'},True)['rows']}
        self.assertEqual(rows,catalog({'decision':'all'},True)['rows'])
        for row in rows:
            self.assertEqual(Decimal(actual[row['observation_id']]['scaled_amount']),Decimal(row['scaled_amount']))
            self.assertEqual(actual[row['observation_id']]['unit_code'],row['unit_code'])
            self.assertEqual(actual[row['observation_id']]['decision'],row['decision'])

    def test_empty_export_preserves_full_schema(self):
        full=csv.DictReader(io.StringIO(export_csv({}).decode('utf-8-sig')))
        empty=csv.DictReader(io.StringIO(export_csv({'year':'1900'}).decode('utf-8-sig')))
        self.assertEqual(empty.fieldnames,full.fieldnames)
        self.assertIn('source_scope',empty.fieldnames)
        self.assertIn('raw_value',empty.fieldnames)
        self.assertEqual(list(empty),[])

    def test_pagination_has_no_missing_or_repeated_records(self):
        pages=[catalog({'page':str(page)}) for page in range(1,5)]
        ids=[r['observation_id'] for page in pages for r in page['rows']]
        self.assertEqual(len(ids),97)
        self.assertEqual(len(set(ids)),97)
        self.assertEqual(ids,[r['observation_id'] for r in catalog({},True)['rows']])
        self.assertEqual(catalog({'page':'5'})['rows'],[])

    def test_search_metacharacters_are_literal(self):
        all_rows=catalog({},True)['rows']
        for query in ('%','_','\\',"' OR 1=1 --"):
            expected=[r['observation_id'] for r in all_rows
                      if query in r['label'] or query in r['source_metric_id']]
            self.assertEqual([r['observation_id'] for r in catalog({'q':query},True)['rows']],expected)
        for query in ({'page':'0'},{'page':'-1'},{'page':'bad'},
                      {'publisher':'unknown'},{'year':'2024 OR 1=1'},{'q':'x'*161}):
            with self.assertRaises(ValueError):catalog(query)

    def test_foreign_keys_reject_cross_document_scope(self):
        source=sqlite3.connect('file:build/reusable/reference.sqlite?mode=ro',uri=True)
        memory=sqlite3.connect(':memory:');source.backup(memory);source.close()
        memory.execute('PRAGMA foreign_keys=ON')
        metric=memory.execute('SELECT metric_key,document_id FROM metric LIMIT 1').fetchone()
        context=memory.execute('SELECT context_id FROM context WHERE document_id<>? LIMIT 1',(metric[1],)).fetchone()[0]
        with self.assertRaises(sqlite3.IntegrityError): memory.execute('UPDATE metric SET context_id=? WHERE metric_key=?',(context,metric[0]))
        memory.close()
