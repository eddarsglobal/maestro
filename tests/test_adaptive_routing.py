import unittest

from maestro.adaptive.models import AdaptivePolicy, PolicyKind
from maestro.adaptive.routing import AdaptiveRoutingEngine


class AdaptiveRoutingTests(unittest.TestCase):
    def test_family_and_tag_rules(self):
        policy = AdaptivePolicy(
            kind=PolicyKind.ROUTING,
            version=1,
            description="routing",
            parameters={
                "rules": {"PAYMENT": ["PM", "IT", "SC", "FN", "OP", "AY"]},
                "tag_rules": {"privacy": ["JR", "DT"]},
                "default": ["AY"],
            },
        )
        d = AdaptiveRoutingEngine().route(
            policy,
            task_family="PAYMENT",
            tags={"privacy"},
        )
        self.assertTrue({"PM", "IT", "SC", "FN", "OP", "AY", "JR", "DT"}.issubset(d.councils))


if __name__ == "__main__":
    unittest.main()
