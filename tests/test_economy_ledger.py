import unittest
from maestro.cognitive_economy import *

class EconomyLedgerTests(unittest.TestCase):
    def test_best_efficiency_prefers_quality_per_spend(self):
        l=CognitiveEconomyLedger()
        l.record(SpendObservation("CODE","IT",EconomyTier.DEEP,True,0.95,20000,60000,0.6,4,5,True))
        l.record(SpendObservation("CODE","IT",EconomyTier.STANDARD,True,0.90,5000,10000,0.1,3,3,True))
        best=l.best_efficiency("CODE","IT")
        self.assertEqual(best.tier,EconomyTier.STANDARD)

if __name__=="__main__":
    unittest.main()
