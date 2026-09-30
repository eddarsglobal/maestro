import unittest
from maestro.strategic_adaptation import *

class StrategySelectorTests(unittest.TestCase):
    def test_selects_best(self):
        rows=[
            StrategyEvaluation("a",.6,.7,.7,.6,.5,.5,True),
            StrategyEvaluation("b",.9,.8,.9,.9,.5,.5,True),
        ]
        d=StrategySelector().select(rows,current_strategy_id="a",trigger=StrategyTrigger.META_DRIFT)
        self.assertEqual(d.selected_strategy_id,"b")
        self.assertTrue(d.switch_required)

if __name__=="__main__":
    unittest.main()
