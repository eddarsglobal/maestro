import unittest

from maestro.sovereign import *

class A:
    def __init__(self, rid):
        self.resource_id=rid; self.provider_id="p"; self.model_id=rid
    def execute(self, request):
        return IntelligenceResponse(self.resource_id,"p",self.model_id,"ok",True)

class SovereignRouterTests(unittest.TestCase):
    def test_prefers_local_then_quality(self):
        reg = IntelligenceResourceRegistry()
        reg.register(ResourceDescriptor("remote","p","x",frozenset({IntelligenceCapability.DIRECT}),local=False,quality_score=0.9), A("remote"))
        reg.register(ResourceDescriptor("local","p","y",frozenset({IntelligenceCapability.DIRECT}),local=True,quality_score=0.7), A("local"))
        d = SovereignIntelligenceRouter(reg).decide(
            IntelligenceRequest("T1",IntelligenceCapability.DIRECT,"x",preferred_local=True)
        )
        self.assertEqual(d.resource_id,"local")

if __name__ == "__main__":
    unittest.main()
