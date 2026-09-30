import unittest

from maestro.adaptive.context_policy import AdaptiveContextPolicy
from maestro.adaptive.models import AdaptivePolicy, PolicyKind


class AdaptiveContextTests(unittest.TestCase):
    def test_high_risk_increases_evidence_limit(self):
        policy = AdaptivePolicy(
            kind=PolicyKind.CONTEXT,
            version=1,
            description="ctx",
            parameters={"base_max_chars": 8000},
        )
        d = AdaptiveContextPolicy().decide(
            policy,
            council="SC",
            task_family="AUTH",
            risk=5,
        )
        self.assertGreaterEqual(d.evidence_limit, 64)
        self.assertTrue(d.include_project_summary)


if __name__ == "__main__":
    unittest.main()
