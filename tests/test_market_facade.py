import unittest
from maestro.intelligence_market import IntelligenceMarket, MarketObservation
from maestro.sovereign import *

class A:
    def __init__(self,rid): self.resource_id=rid; self.provider_id="p"; self.model_id=rid
    def execute(self,request): return IntelligenceResponse(self.resource_id,"p",self.model_id,"ok",True)

class MarketFacadeTests(unittest.TestCase):
    def test_eligibility_before_market(self):
        reg=IntelligenceResourceRegistry()
        reg.register(ResourceDescriptor("a","p","a",frozenset({IntelligenceCapability.CODE})),A("a"))
        reg.register(ResourceDescriptor("b","p","b",frozenset({IntelligenceCapability.DIRECT})),A("b"))
        m=IntelligenceMarket(reg)
        for _ in range(3):
            m.observe(MarketObservation("a","CODE","IT",True,0.9))
            m.observe(MarketObservation("b","CODE","IT",True,1.0))
        d=m.choose(capability=IntelligenceCapability.CODE,task_family="CODE",council_id="IT",allow_exploration=False)
        self.assertEqual(d.resource_id,"a")

if __name__ == "__main__":
    unittest.main()
