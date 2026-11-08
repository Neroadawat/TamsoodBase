import unittest
from datetime import datetime,timezone
from scripts.check_operational_readiness import backup_age
class OperationalPolicy(unittest.TestCase):
    def test_stale_missing_and_future_backup_are_not_fresh(self):
        now=datetime(2026,11,6,tzinfo=timezone.utc)
        self.assertEqual(backup_age({'created_at':'20261105T120000Z'},now),12)
        self.assertGreater(backup_age({'created_at':'20261028T073422Z'},now),24)
        self.assertIsNone(backup_age({},now));self.assertIsNone(backup_age({'created_at':'20271106T000000Z'},now))
