import unittest
from maestro.cognitive_economy import *

class EconomyPlannerTests(unittest.TestCase):
    def test_medium_gets_standard(self):
        profile=MissionEconomyProfile("T",MissionComplexity.MEDIUM,0.5,0.5,0.5,0.5)
        plan=CognitiveSpendPlanner().plan(profile)
        self.assertEqual(plan.tier,EconomyTier.STANDARD)
        self.assertTrue(plan.require_verifier)

    def test_critical_requires_critic_and_verifier(self):
        profile=MissionEconomyProfile("T",MissionComplexity.CRITICAL,1,1,0,1)
        plan=CognitiveSpendPlanner().plan(profile)
        self.assertTrue(plan.require_critic)
        self.assertTrue(plan.require_verifier)
        self.assertEqual(plan.tier,EconomyTier.MAX_GOVERNED)

if __name__=="__main__":
    unittest.main()
