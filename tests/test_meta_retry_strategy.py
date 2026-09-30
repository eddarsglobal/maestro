import unittest
from maestro.meta_cognition import *

class MetaRetryStrategyTests(unittest.TestCase):
    def test_retry_loop_changes_strategy(self):
        cp=StrategyCheckpoint(
            "T","S","x",0.2,0.2,3,5,0.7,0.7,
            assumptions={"a":EpistemicFlag.ASSUMED},
        )
        a=MetaCognitionController().assess(
            checkpoint=cp,
            claims=[],
            required_criteria=["c"],
            evidence_by_criterion={},
            verified_fraction=0.0,
            assumption_fraction=1.0,
        )
        self.assertIn(MetaAction.CHANGE_STRATEGY,a.recommended_actions)
        self.assertIn(MetaAction.REVALIDATE_ASSUMPTIONS,a.recommended_actions)

if __name__=="__main__":
    unittest.main()
