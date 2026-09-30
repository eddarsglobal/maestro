import unittest
from maestro.cognitive_fabric import CognitivePlanCompiler, CognitiveRole

class CognitiveCompilerTests(unittest.TestCase):
    def test_code_review_plan(self):
        p = CognitivePlanCompiler().code_review("T1","implement")
        self.assertEqual([s.role for s in p.stages],[
            CognitiveRole.SCOUT,
            CognitiveRole.PRODUCER,
            CognitiveRole.CRITIC,
            CognitiveRole.VERIFIER,
        ])
        self.assertEqual(p.stages[-1].depends_on,("produce","critic"))

if __name__=="__main__":
    unittest.main()
