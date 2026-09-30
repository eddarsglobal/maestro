import unittest
from maestro.cognitive_fabric import *
from maestro.intelligence_market import IntelligenceMarket
from maestro.sovereign import *

class Bad:
    resource_id="bad"; provider_id="p"; model_id="bad"
    def execute(self,request): raise RuntimeError("boom")

class FailureIsolationTests(unittest.TestCase):
    def test_stage_failure_does_not_destroy_plan_state(self):
        reg=IntelligenceResourceRegistry()
        reg.register(
            ResourceDescriptor("bad","p","bad",frozenset({IntelligenceCapability.DIRECT}),local=True),
            Bad()
        )
        rt=SovereignIntelligenceRuntime(reg)
        market=IntelligenceMarket(reg)
        plan=CognitivePlanCompiler().direct("T","x")
        report=CognitiveFabricExecutor(rt,market).execute(plan)
        self.assertFalse(report.completed)
        self.assertEqual(report.failed_stage_ids,["produce"])
        self.assertEqual(report.task_id,"T")

if __name__=="__main__":
    unittest.main()
