import unittest
from maestro.meta_cognition import *

class MetaGovernorTests(unittest.TestCase):
    def test_block_detected(self):
        a=MetaAssessment(
            "T",0.5,0.5,0,0,[],
            [MetaAction.BLOCK],
            EpistemicFlag.BLOCKED,
            False,
        )
        self.assertTrue(MetaCognitionGovernor().requires_hard_stop(a))

if __name__=="__main__":
    unittest.main()
