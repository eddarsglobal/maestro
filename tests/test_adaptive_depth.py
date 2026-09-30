import unittest
from maestro.cognitive_economy import *

class AdaptiveDepthTests(unittest.TestCase):
    def test_repeated_low_spend_success_recommends_lower_tier(self):
        rows=[
            SpendObservation("X",None,EconomyTier.MINIMAL,True,0.9,500,1000,0,1,1,True)
            for _ in range(3)
        ]
        rec=AdaptiveDepthController().recommend_tier(rows,EconomyTier.STANDARD)
        self.assertEqual(rec,EconomyTier.MINIMAL)

    def test_insufficient_history_keeps_default(self):
        rows=[SpendObservation("X",None,EconomyTier.MINIMAL,True,0.9,500,1000,0,1,1,True)]
        rec=AdaptiveDepthController().recommend_tier(rows,EconomyTier.DEEP)
        self.assertEqual(rec,EconomyTier.DEEP)

if __name__=="__main__":
    unittest.main()
