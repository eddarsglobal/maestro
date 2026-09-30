import unittest
from maestro.sovereign import IntelligenceResponse, MultiResourceSynthesizer

class MultiResourceTests(unittest.TestCase):
    def test_agreement_ratio(self):
        r = [
            IntelligenceResponse("a","p","m","YES",True),
            IntelligenceResponse("b","p","m","YES",True),
            IntelligenceResponse("c","p","m","NO",True),
        ]
        self.assertAlmostEqual(MultiResourceSynthesizer().agreement_ratio(r), 2/3)

if __name__ == "__main__":
    unittest.main()
