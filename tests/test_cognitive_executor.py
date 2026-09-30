import unittest
from maestro.cognitive_fabric import *
from maestro.intelligence_market import IntelligenceMarket, MarketObservation
from maestro.sovereign import *

class R:
    def __init__(self,rid,p):
        self.resource_id=rid; self.provider_id=p; self.model_id=rid
    def execute(self,request):
        upstream=request.metadata.get("upstream_artifacts",[])
        text=request.metadata["cognitive_role"] + ":" + str(len(upstream))
        return IntelligenceResponse(self.resource_id,self.provider_id,self.model_id,text,True,{})

class CognitiveExecutorTests(unittest.TestCase):
    def test_multistage_maestro_mediated_execution(self):
        reg=IntelligenceResourceRegistry()
        caps=frozenset({IntelligenceCapability.GENERAL_REASONING})
        reg.register(ResourceDescriptor("a","p1","a",caps,local=True),R("a","p1"))
        reg.register(ResourceDescriptor("b","p2","b",caps,local=True),R("b","p2"))
        rt=SovereignIntelligenceRuntime(reg)
        market=IntelligenceMarket(reg)
        # Fully sample both so market can exploit and diversity can choose alternatives.
        for _ in range(3):
            market.observe(MarketObservation("a","GENERAL_REASONING",None,True,0.9))
            market.observe(MarketObservation("b","CRITIQUE",None,True,0.9))
        plan=CognitivePlanCompiler().reason_and_critique("T","solve")
        report=CognitiveFabricExecutor(rt,market).execute(plan)
        self.assertTrue(report.completed)
        self.assertEqual(len(report.artifacts),2)
        self.assertNotEqual(report.artifacts[0].resource_id,report.artifacts[1].resource_id)
        self.assertEqual(report.artifacts[1].output,"CRITIC:1")

if __name__=="__main__":
    unittest.main()
