import unittest
from maestro.strategic_adaptation import *

class StrategyEngineTests(unittest.TestCase):
    def test_propose_select_and_authorize(self):
        e=StrategicAdaptationEngine()
        current=StrategyCandidate("current","X","objective","CURRENT")
        selected, evaluations, decision=e.propose_and_select(
            task_id="T",
            objective="objective",
            family="X",
            current_strategy_id=current.strategy_id,
            current_method=current.method,
            trigger=StrategyTrigger.EVIDENCE_GAP,
            available_capabilities={"MULTI_RESOURCE"},
            risk_score=.7,
            evidence_urgency=1.0,
            cost_pressure=.2,
            latency_pressure=.2,
        )
        self.assertNotEqual(selected.strategy_id,current.strategy_id)
        tr=e.authorize_transition(
            task_id="T",
            current_strategy=current,
            selected_strategy=selected,
            trigger=StrategyTrigger.EVIDENCE_GAP,
            authorized=True,
        )
        self.assertTrue(tr.authorized)
        self.assertEqual(e.journal.last_for_task("T")["to_strategy_id"],selected.strategy_id)

if __name__=="__main__":
    unittest.main()
