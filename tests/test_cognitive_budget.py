import unittest
from maestro.cognitive_fabric import *
from maestro.sovereign import IntelligenceCapability

class CognitiveBudgetTests(unittest.TestCase):
    def test_too_many_stages_blocked(self):
        stages=[
            CognitiveStage(str(i),CognitiveRole.PRODUCER,IntelligenceCapability.DIRECT,"X",None,"x")
            for i in range(3)
        ]
        plan=CognitivePlan("T",stages)
        gov=CognitiveBudgetGovernor(CognitiveBudget(max_stages=2))
        with self.assertRaises(BudgetViolation):
            gov.validate_plan(plan)

if __name__=="__main__":
    unittest.main()
