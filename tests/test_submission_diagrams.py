import unittest
from pathlib import Path
from scripts.build_submission_evidence import SCHEMAS,ROOT,parse_schema,split_definitions,mermaid


class SubmissionDiagramTests(unittest.TestCase):
    def test_all_real_schema_tables_and_foreign_keys_are_included(self):
        for name,path in SCHEMAS.items():
            with self.subTest(schema=name):
                sql=(ROOT/path).read_text(encoding='utf-8');tables,links=parse_schema(sql)
                self.assertEqual(len(tables),sql.count('CREATE TABLE IF NOT EXISTS'))
                self.assertEqual(len(links),sql.count('FOREIGN KEY('))
                self.assertIn('erDiagram',mermaid(tables,links))

    def test_composite_subtype_is_one_to_optional_one(self):
        tables,links=parse_schema((ROOT/SCHEMAS['supplemental']).read_text(encoding='utf-8'))
        link=next(x for x in links if x['child']=='national_statistic')
        self.assertEqual((link['parent_end'],link['child_end']),('||','o|'))
        self.assertEqual(set(link['local']),{'snapshot_id','observation_id'})
        _,links=parse_schema((ROOT/SCHEMAS['dmf']).read_text(encoding='utf-8'))
        optional=next(x for x in links if 'representative_line' in x['local'])
        self.assertEqual((optional['parent_end'],optional['child_end']),('o|','o{'))

    def test_decimal_and_quoted_commas_do_not_split_columns(self):
        self.assertEqual(split_definitions("amount DECIMAL(30,12), CHECK(kind IN ('A,B','C')), label TEXT"),["amount DECIMAL(30,12)","CHECK(kind IN ('A,B','C'))","label TEXT"])
