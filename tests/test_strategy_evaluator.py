import unittest
from maestro.strategic_adaptation import *

class StrategyEvaluatorTests(unittest.TestCase):
    def test_evidence_first_scores_well_when_evidence_is_urgent(self):
        c=StrategyCandidate("s","X","obj","EVIDENCE",expected_quality=.8,expected_evidence_gain=.95,expected_cost=.4,expected_latency=.4)
        e=StrategyEvaluator().evaluate(
            c,risk_score=.8,evidence_urgency=1.0,cost_pressure=.2,latency_pressure=.2
        )
        self.assertGreater(e.score,.7)

if __name__=="__main__":
    unittest.main()
