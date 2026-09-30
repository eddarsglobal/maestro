import unittest
from maestro.cognitive_fabric import DiversityPlanner
from maestro.sovereign import ResourceDescriptor, IntelligenceCapability

class DiversityTests(unittest.TestCase):
    def test_prefers_different_provider(self):
        caps=frozenset({IntelligenceCapability.DIRECT})
        c=[
            ResourceDescriptor("a","p1","m1",caps),
            ResourceDescriptor("b","p2","m2",caps),
        ]
        out=DiversityPlanner().filter_candidates(
            c,
            already_used_resources={"a"},
            already_used_providers=["p1"],
            require_provider_diversity=True,
        )
        self.assertEqual([x.resource_id for x in out],["b"])

if __name__=="__main__":
    unittest.main()
