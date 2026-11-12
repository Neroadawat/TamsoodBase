import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RagMemoryGateTests(unittest.TestCase):
    def test_upgrade_runtime_floor_uses_exact_320_mib_kib_value(self):
        script = (ROOT / "deploy/upgrade_rag_ec2.sh").read_text(encoding="utf-8")
        guards = re.findall(r"MemAvailable:/ \{print \$2\}.*?\)\"?\s*>=\s*(\d+)", script)
        self.assertEqual(guards, ["327680", "327680"], "both startup and health-wait guards must enforce 320 MiB")
        self.assertIn("available_kb >= 327680", script, "pre-update guard must enforce 320 MiB")
        self.assertIn("320 MiB safety floor (327680 KiB)", script)
        self.assertNotIn("320000", script, "decimal KB approximation is below the documented binary MiB floor")

    def test_initial_install_reserves_container_ceiling_plus_320_mib_host_floor(self):
        script = (ROOT / "deploy/install_rag_ec2.sh").read_text(encoding="utf-8")
        self.assertIn("MIN_INSTALL_AVAILABLE_KB=851968", script)
        self.assertIn("available_kb >= MIN_INSTALL_AVAILABLE_KB", script)
        self.assertEqual(851968, 512 * 1024 + 320 * 1024)
        self.assertIn("832 MiB (851968 KiB: 512 MiB container ceiling + 320 MiB host reserve)", script)
        self.assertGreaterEqual(script.count("host_available_kb >= 327680"), 2)


if __name__ == "__main__":
    unittest.main()
