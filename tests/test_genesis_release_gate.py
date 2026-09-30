import unittest
from maestro.genesis.release_gate import ProductionReleaseGate, ReleaseEvidence, ReleaseDenied

class GenesisReleaseGateTests(unittest.TestCase):
    def test_pass(self):
        ev = ReleaseEvidence(True, 0, 0, True, True, True)
        self.assertTrue(ProductionReleaseGate().authorize(ev))

    def test_test_failure_blocks(self):
        ev = ReleaseEvidence(True, 1, 0, True, True, True)
        with self.assertRaises(ReleaseDenied):
            ProductionReleaseGate().authorize(ev)

if __name__ == "__main__":
    unittest.main()
