import unittest
from maestro.strategic_adaptation import StrategyRollbackManager

class StrategyRollbackTests(unittest.TestCase):
    def test_rolls_back_quality_regression(self):
        self.assertTrue(StrategyRollbackManager().should_rollback(
            baseline_quality=.9,new_quality=.6,
            baseline_evidence=.8,new_evidence=.8,
            baseline_cost=.3,new_cost=.4
        ))

    def test_keeps_improvement(self):
        self.assertFalse(StrategyRollbackManager().should_rollback(
            baseline_quality=.7,new_quality=.9,
            baseline_evidence=.6,new_evidence=.9,
            baseline_cost=.3,new_cost=.35
        ))

if __name__=="__main__":
    unittest.main()
