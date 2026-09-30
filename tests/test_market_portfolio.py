import unittest
from maestro.intelligence_market import ResourceScoreCard, IntelligencePortfolio

class PortfolioTests(unittest.TestCase):
    def test_primary_secondary(self):
        cards=[
            ResourceScoreCard("a","X",None,3,1,0.9,100,0,1,1,1,1,0.95),
            ResourceScoreCard("b","X",None,3,1,0.8,100,0,1,1,1,1,0.85),
        ]
        p=IntelligencePortfolio().build(cards,2)
        self.assertEqual(p[0].role,"PRIMARY")
        self.assertEqual(p[1].role,"SECONDARY")

if __name__ == "__main__":
    unittest.main()
