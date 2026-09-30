import unittest
from maestro.meta_cognition import *

class MetaControllerTests(unittest.TestCase):
    def test_contradiction_requests_evidence_and_ay(self):
        cp=StrategyCheckpoint(
            "T","S1","x",0.5,0.5,0,1,0.2,0.2,
            assumptions={"a":EpistemicFlag.VERIFIED},
        )
        a=MetaCognitionController().assess(
            checkpoint=cp,
            claims=[{"key":"x","value":"YES"},{"key":"x","value":"NO"}],
            required_criteria=["c1"],
            evidence_by_criterion={"c1":["E1"]},
            verified_fraction=1.0,
            assumption_fraction=0.0,
        )
        self.assertIn(MetaAction.REQUEST_MORE_EVIDENCE,a.recommended_actions)
        self.assertIn(MetaAction.ESCALATE_AY,a.recommended_actions)

    def test_human_auth_blocks(self):
        cp=StrategyCheckpoint("T","S","x",1,1,0,1,0,0)
        a=MetaCognitionController().assess(
            checkpoint=cp,
            claims=[],
            required_criteria=[],
            evidence_by_criterion={},
            verified_fraction=1,
            assumption_fraction=0,
            human_authorization_required=True,
        )
        self.assertFalse(a.safe_to_continue)
        self.assertIn(MetaAction.REQUEST_HUMAN_APPROVAL,a.recommended_actions)
        self.assertIn(MetaAction.BLOCK,a.recommended_actions)

if __name__=="__main__":
    unittest.main()
