import unittest
from maestro.meta_cognition import ConfidenceEstimator

class MetaConfidenceTests(unittest.TestCase):
    def test_verified_evidence_yields_high_confidence(self):
        c=ConfidenceEstimator().estimate(
            evidence_sufficiency=1,
            contradiction_score=0,
            verified_fraction=1,
            assumption_fraction=0,
            retry_penalty=0,
        )
        self.assertGreaterEqual(c,0.95)

    def test_assumption_and_contradiction_reduce_confidence(self):
        c=ConfidenceEstimator().estimate(
            evidence_sufficiency=0.5,
            contradiction_score=0.8,
            verified_fraction=0.2,
            assumption_fraction=0.8,
            retry_penalty=1,
        )
        self.assertLess(c,0.5)

if __name__=="__main__":
    unittest.main()
