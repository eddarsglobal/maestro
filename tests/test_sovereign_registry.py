import unittest

from maestro.sovereign import (
    IntelligenceCapability, IntelligenceRequest, IntelligenceResponse,
    ResourceDescriptor, IntelligenceResourceRegistry
)

class FakeAdapter:
    resource_id = "r1"
    provider_id = "p"
    model_id = "m"
    def execute(self, request):
        return IntelligenceResponse("r1","p","m","ok",True)

class SovereignRegistryTests(unittest.TestCase):
    def test_register_and_eligible(self):
        r = IntelligenceResourceRegistry()
        r.register(
            ResourceDescriptor(
                "r1","p","m",
                frozenset({IntelligenceCapability.DIRECT})
            ),
            FakeAdapter()
        )
        self.assertEqual(len(r.eligible(IntelligenceCapability.DIRECT)),1)

if __name__ == "__main__":
    unittest.main()
