import unittest
from maestro.cognitive_economy import MarginalUtilityEngine

class EconomyUtilityTests(unittest.TestCase):
    def test_continue_when_gain_is_material(self):
        d=MarginalUtilityEngine().decide(
            current_quality=0.6,
            expected_next_quality=0.85,
            current_evidence=0.5,
            expected_next_evidence=0.8,
            added_token_fraction=0.2,
            added_latency_fraction=0.2,
            added_cost_fraction=0.1,
        )
        self.assertTrue(d.continue_spending)

    def test_stop_when_gain_is_tiny(self):
        d=MarginalUtilityEngine().decide(
            current_quality=0.9,
            expected_next_quality=0.905,
            current_evidence=0.95,
            expected_next_evidence=0.951,
            added_token_fraction=0.5,
            added_latency_fraction=0.5,
            added_cost_fraction=0.5,
        )
        self.assertFalse(d.continue_spending)

if __name__=="__main__":
    unittest.main()
