import unittest
from maestro.cognitive_economy import *

class EconomyFabricBridgeTests(unittest.TestCase):
    def test_spend_plan_becomes_cognitive_budget(self):
        profile=MissionEconomyProfile("T",MissionComplexity.HIGH,0.8,0.8,0.2,0.8)
        plan=CognitiveSpendPlanner().plan(profile)
        b=CognitiveEconomyFabricBridge().to_cognitive_budget(plan)
        self.assertEqual(b.max_stages,plan.max_stages)
        self.assertEqual(b.max_resource_calls,plan.max_resource_calls)

if __name__=="__main__":
    unittest.main()
