import unittest
from maestro.meta_cognition import *
from maestro.strategic_adaptation import *

class MetaStrategyBridgeTests(unittest.TestCase):
    def test_retry_loop_maps_to_trigger(self):
        assessment=MetaAssessment(
            "T",.4,.4,0,.8,
            [MetaSignal(MetaSignalType.RETRY_LOOP,.8,1.0)],
            [MetaAction.CHANGE_STRATEGY],
            EpistemicFlag.UNKNOWN,
            True,
        )
        t=MetaStrategyBridge().trigger_from_assessment(assessment)
        self.assertEqual(t,StrategyTrigger.RETRY_LOOP)

if __name__=="__main__":
    unittest.main()
