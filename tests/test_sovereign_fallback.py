import unittest
from maestro.sovereign import *

class Bad:
    resource_id="bad"; provider_id="p"; model_id="bad"
    def execute(self, request): raise RuntimeError("down")

class Good:
    resource_id="good"; provider_id="p"; model_id="good"
    def execute(self, request): return IntelligenceResponse("good","p","good","OK",True)

class SovereignFallbackTests(unittest.TestCase):
    def test_replaces_failed_resource(self):
        reg = IntelligenceResourceRegistry()
        reg.register(ResourceDescriptor("bad","p","bad",frozenset({IntelligenceCapability.DIRECT}),local=True,quality_score=1.0), Bad())
        reg.register(ResourceDescriptor("good","p","good",frozenset({IntelligenceCapability.DIRECT}),local=True,quality_score=0.8), Good())
        rt = SovereignIntelligenceRuntime(reg)
        out = rt.execute(IntelligenceRequest("T1",IntelligenceCapability.DIRECT,"x"))
        self.assertEqual(out.resource_id,"good")
        self.assertEqual(out.metadata["fallback_from"],"bad")

if __name__ == "__main__":
    unittest.main()
