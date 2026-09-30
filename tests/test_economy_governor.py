import unittest
from maestro.cognitive_economy import *

class EconomyGovernorTests(unittest.TestCase):
    def test_blocks_token_overspend(self):
        profile=MissionEconomyProfile("T",MissionComplexity.LOW,0.1,0.1,1,0.1)
        plan=CognitiveSpendPlanner().plan(profile)
        gov=CognitiveEconomyGovernor(plan)
        with self.assertRaises(EconomyViolation):
            gov.assert_within_budget(
                stages_used=1,
                resource_calls=1,
                total_tokens=plan.max_total_tokens+1,
                elapsed_ms=1,
                cost_score=0,
            )

    def test_can_add_call(self):
        profile=MissionEconomyProfile("T",MissionComplexity.MEDIUM,0.5,0.5,0.5,0.5)
        plan=CognitiveSpendPlanner().plan(profile)
        gov=CognitiveEconomyGovernor(plan)
        self.assertTrue(gov.can_add_call(
            current_resource_calls=0,
            current_total_tokens=0,
            estimated_next_tokens=100,
        ))

if __name__=="__main__":
    unittest.main()
