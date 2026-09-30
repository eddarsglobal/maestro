import unittest
from maestro.meta_cognition import ContradictionDetector

class MetaContradictionTests(unittest.TestCase):
    def test_detects_conflicting_claims(self):
        claims=[
            {"key":"status","value":"PASS"},
            {"key":"status","value":"FAIL"},
            {"key":"owner","value":"IT"},
        ]
        self.assertGreater(ContradictionDetector().score(claims),0)

    def test_no_conflict(self):
        claims=[{"key":"status","value":"PASS"},{"key":"status","value":"PASS"}]
        self.assertEqual(ContradictionDetector().score(claims),0)

if __name__=="__main__":
    unittest.main()
