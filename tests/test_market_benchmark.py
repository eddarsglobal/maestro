import unittest
from maestro.intelligence_market import BenchmarkScenario, MarketBenchmark
from maestro.sovereign import IntelligenceRequest, IntelligenceResponse, IntelligenceCapability

class A:
    def __init__(self,rid,text): self.resource_id=rid; self.text=text
    def execute(self,request): return IntelligenceResponse(self.resource_id,"p",self.resource_id,self.text,True,{})

class BenchmarkTests(unittest.TestCase):
    def test_same_scenario_multiple_resources(self):
        sc=BenchmarkScenario(
            "S1","DIRECT","EX",
            IntelligenceRequest("T",IntelligenceCapability.DIRECT,"say OK"),
            lambda r: 1.0 if r.output=="OK" else 0.0
        )
        out=MarketBenchmark().run(sc,{"a":A("a","OK"),"b":A("b","NO")})
        self.assertEqual(len(out),2)
        self.assertEqual(out[0].quality,1.0)
        self.assertEqual(out[1].quality,0.0)

if __name__ == "__main__":
    unittest.main()
