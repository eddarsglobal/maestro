import unittest
from maestro.intelligence_market import MarketObservation, ScoreCardEngine

class MarketScoreCardTests(unittest.TestCase):
    def test_better_resource_scores_higher(self):
        rows = [
            MarketObservation("a","CODE","IT",True,0.95,100,0.1,1,1,True),
            MarketObservation("a","CODE","IT",True,0.90,120,0.1,1,1,True),
            MarketObservation("b","CODE","IT",True,0.60,50,0.0,1,1,True),
            MarketObservation("b","CODE","IT",False,0.30,60,0.0,1,1,True),
        ]
        e = ScoreCardEngine()
        a = e.build(rows,resource_id="a",task_family="CODE",council_id="IT")
        b = e.build(rows,resource_id="b",task_family="CODE",council_id="IT")
        self.assertGreater(a.market_score,b.market_score)

if __name__ == "__main__":
    unittest.main()
