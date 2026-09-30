import unittest
from maestro.meta_cognition import EvidenceSufficiencyEvaluator

class MetaEvidenceTests(unittest.TestCase):
    def test_partial_evidence(self):
        s=EvidenceSufficiencyEvaluator().score(
            required_criteria=["a","b"],
            evidence_by_criterion={"a":["E1"]},
        )
        self.assertEqual(s,0.5)

if __name__=="__main__":
    unittest.main()
