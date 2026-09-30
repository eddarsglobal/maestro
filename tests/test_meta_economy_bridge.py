import unittest
from maestro.meta_cognition import *

class MetaEconomyBridgeTests(unittest.TestCase):
    def test_deepen_mapping(self):
        a=MetaAssessment(
            "T",0.4,0.5,0,0,[],
            [MetaAction.DEEPEN_COGNITION],
            EpistemicFlag.UNKNOWN,
            True,
        )
        self.assertEqual(MetaEconomyBridge().recommend_depth_change(a),"DEEPEN")

if __name__=="__main__":
    unittest.main()
