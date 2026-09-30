import unittest
from maestro.genesis.e2e import EndToEndMissionHarness

class GenesisE2ETests(unittest.TestCase):
    def test_full_constitutional_happy_path(self):
        result = EndToEndMissionHarness().run()
        self.assertTrue(result.dag_complete)
        self.assertTrue(result.ay_system_juste)
        self.assertTrue(result.tx_committed)
        self.assertTrue(result.mission_complete)
        self.assertEqual(result.evidence_count, 3)

if __name__ == "__main__":
    unittest.main()
