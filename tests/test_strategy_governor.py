import unittest
from maestro.strategic_adaptation import *

class StrategyGovernorTests(unittest.TestCase):
    def test_cannot_change_objective(self):
        g=StrategyAdaptationGovernor()
        with self.assertRaises(StrategyAuthorityViolation):
            g.validate_transition(old_objective="A",new_objective="B")

    def test_cannot_claim_authority_mutation(self):
        c=StrategyCandidate("s","X","A","m")
        with self.assertRaises(StrategyAuthorityViolation):
            StrategyAdaptationGovernor().validate_candidate(c,{"tool_permissions"})

if __name__=="__main__":
    unittest.main()
