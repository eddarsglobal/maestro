import tempfile
import unittest
from maestro.genesis.health import HealthInspector
from maestro.genesis.models import HealthStatus

class GenesisHealthTests(unittest.TestCase):
    def test_healthy(self):
        with tempfile.TemporaryDirectory() as td:
            report = HealthInspector().inspect(runtime_dir=td)
            self.assertEqual(report.status, HealthStatus.HEALTHY)

    def test_degraded_on_stale_workers(self):
        with tempfile.TemporaryDirectory() as td:
            report = HealthInspector().inspect(runtime_dir=td, stale_workers=2)
            self.assertEqual(report.status, HealthStatus.DEGRADED)

if __name__ == "__main__":
    unittest.main()
