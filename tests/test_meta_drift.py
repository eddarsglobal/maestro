import unittest
from maestro.meta_cognition import StrategyDriftDetector

class MetaDriftTests(unittest.TestCase):
    def test_low_progress_high_spend_drifts(self):
        d=StrategyDriftDetector().score(
            progress_score=0.1,
            evidence_score=0.1,
            retries=3,
            resource_calls=6,
            cost_fraction=0.9,
            latency_fraction=0.9,
        )
        self.assertGreaterEqual(d,0.6)

if __name__=="__main__":
    unittest.main()
