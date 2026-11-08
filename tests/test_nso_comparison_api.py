import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.explorer import nso_comparison


class ComparisonAPITests(unittest.TestCase):
    def test_revised_context_and_arithmetic_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'evidence').mkdir()
            original=dict(nso_observation_id='one',year=2024,nso_value='30350',unit='ktoe',dede_preliminary_value='28987')
            (root/'evidence/nso-dede-comparison.json').write_text(json.dumps(original),encoding='utf-8')
            with patch('src.explorer.ROOT',root):
                self.assertNotIn('revised',nso_comparison())
                revised=original|dict(dede_revised_value='30350',difference_nso_minus_revised='0',exact_displayed_value_match=True)
                path=root/'evidence/nso-dede-revised-comparison.json';path.write_text(json.dumps(revised),encoding='utf-8')
                self.assertEqual(nso_comparison()['revised']['dede_revised_value'],'30350')
                for changed in [revised|dict(nso_observation_id='wrong'),revised|dict(difference_nso_minus_revised='1')]:
                    path.write_text(json.dumps(changed),encoding='utf-8')
                    with self.assertRaises(ValueError):nso_comparison()
