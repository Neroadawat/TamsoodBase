import unittest
from scripts.benchmark_sql import root_time


class ServerTimingTests(unittest.TestCase):
    def test_uses_root_completion_time_not_sum_of_nested_nodes(self):
        plan='-> Filter (actual time=0.1..2.5 rows=100 loops=1)\n -> Scan (actual time=0.01..2.0 rows=34000 loops=1)'
        self.assertEqual(root_time(plan),2.5)

    def test_missing_actual_measurement_is_not_zero(self):
        with self.assertRaises(ValueError): root_time('cost=100 rows=10')
