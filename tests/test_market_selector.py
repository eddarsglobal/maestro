import unittest
from maestro.intelligence_market import IntelligenceMarketLedger, MarketObservation, IntelligenceMarketSelector, MarketPolicy

class MarketSelectorTests(unittest.TestCase):
    def test_explores_under_tested_resource(self):
        l=IntelligenceMarketLedger()
        for _ in range(3):
            l.record(MarketObservation("a","CODE","IT",True,0.9))
        l.record(MarketObservation("b","CODE","IT",True,0.8))
        s=IntelligenceMarketSelector(l, MarketPolicy(min_samples_for_confidence=3))
        d=s.select(eligible_resource_ids=["a","b"],task_family="CODE",council_id="IT",allow_exploration=True)
        self.assertTrue(d.explored)
        self.assertEqual(d.resource_id,"b")

    def test_exploits_best_when_fully_sampled(self):
        l=IntelligenceMarketLedger()
        for _ in range(3):
            l.record(MarketObservation("a","CODE","IT",True,0.95,100))
            l.record(MarketObservation("b","CODE","IT",True,0.70,100))
        s=IntelligenceMarketSelector(l, MarketPolicy(min_samples_for_confidence=3))
        d=s.select(eligible_resource_ids=["a","b"],task_family="CODE",council_id="IT",allow_exploration=True)
        self.assertFalse(d.explored)
        self.assertEqual(d.resource_id,"a")

if __name__ == "__main__":
    unittest.main()
