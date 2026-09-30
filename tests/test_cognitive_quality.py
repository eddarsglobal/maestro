import unittest
from maestro.cognitive_fabric import *

class QualityTests(unittest.TestCase):
    def test_empty_output_scores_zero(self):
        a=StageArtifact("s",CognitiveRole.PRODUCER,"r","p","m","",True)
        self.assertEqual(CognitiveQualityGate().stage_quality(a),0.0)

if __name__=="__main__":
    unittest.main()
