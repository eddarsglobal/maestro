import unittest
from maestro.cognitive_fabric import CognitiveFabricExecutor
from maestro.intelligence_market import IntelligenceMarket, MarketObservation
from maestro.sovereign import *

class R:
    def __init__(self,rid): self.resource_id=rid; self.provider_id="p"; self.model_id=rid
    def execute(self,request): return IntelligenceResponse(self.resource_id,"p",self.model_id,"ok",True)

class CognitiveExplorationBoundaryTests(unittest.TestCase):
    def test_executor_defaults_to_no_market_exploration(self):
        reg=IntelligenceResourceRegistry()
        caps=frozenset({IntelligenceCapability.DIRECT})
        reg.register(ResourceDescriptor("proven","p","proven",caps),R("proven"))
        reg.register(ResourceDescriptor("new","p","new",caps),R("new"))
        market=IntelligenceMarket(reg)
        for _ in range(3):
            market.observe(MarketObservation("proven","DIRECT",None,True,0.95))
        rt=SovereignIntelligenceRuntime(reg)
        ex=CognitiveFabricExecutor(rt,market)
        self.assertFalse(ex.allow_market_exploration)

if __name__=="__main__":
    unittest.main()
