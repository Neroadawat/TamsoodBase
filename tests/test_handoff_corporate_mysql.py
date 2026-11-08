from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import verify_handoff_corporate_mysql as verification


class CorporateEngineGuardTests(unittest.TestCase):
    def test_decimal_comparison_preserves_all_30_digits_and_raw_precision(self):
        left='123456789012345678.123456789012';right='123456789012345678.123456789013'
        self.assertEqual(verification.canonical(left,'scaled_amount'),Decimal(left))
        self.assertNotEqual(verification.canonical(left,'scaled_amount'),verification.canonical(right,'scaled_amount'))
        self.assertEqual(verification.canonical('1.000000000000','scale_factor'),Decimal('1'))
        self.assertNotEqual(verification.canonical('1.00','raw_value'),verification.canonical('1','raw_value'))

    def test_schema_identifier_rejects_statements_and_qualification(self):
        for value in ('db; DROP DATABASE x','db.other','x`','../x','a'*65):
            with self.subTest(value=value),self.assertRaises(ValueError):verification.identifier(value)

    def test_unowned_lab_is_rejected_before_any_sql_or_source_loading(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);folder=root/'build/handoff';folder.mkdir(parents=True)
            (folder/'engines.json').write_text(json.dumps({'mysql_container':'unowned-fixture'}))
            with patch.object(verification,'ROOT',root),patch.object(verification,'owned',return_value=False),patch.object(verification,'docker') as docker:
                with self.assertRaisesRegex(ValueError,'Owned isolated MySQL'):verification.main()
                docker.assert_not_called()


if __name__=='__main__':unittest.main()
