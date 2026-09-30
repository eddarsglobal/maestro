import unittest
from maestro.intelligence_market import *

class CouncilSpecificTests(unittest.TestCase):
    def test_different_winners_by_council(self):
        l=IntelligenceMarketLedger()
        for _ in range(3):
            l.record(MarketObservation("coder","CODE","IT",True,0.95,100))
            l.record(MarketObservation("general","CODE","IT",True,0.70,100))
            l.record(MarketObservation("coder","VALIDATION","AY",True,0.60,100))
            l.record(MarketObservation("general","VALIDATION","AY",True,0.95,100))
        s=IntelligenceMarketSelector(l, MarketPolicy(min_samples_for_confidence=3))
        it=s.select(eligible_resource_ids=["coder","general"],task_family="CODE",council_id="IT",allow_exploration=False)
        ay=s.select(eligible_resource_ids=["coder","general"],task_family="VALIDATION",council_id="AY",allow_exploration=False)
        self.assertEqual(it.resource_id,"coder")
        self.assertEqual(ay.resource_id,"general")

if __name__ == "__main__":
    unittest.main()
