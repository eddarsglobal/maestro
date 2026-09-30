import unittest

from maestro.adaptive.tool_policy import ToolPolicyLearner, ToolObservation
from maestro.enums import CouncilId, SideEffectLevel
from maestro.tools.registry import ToolRegistry, ToolSpec


class ToolPolicyLearnerTests(unittest.TestCase):
    def test_rank_prefers_successful_allowed_tool(self):
        reg = ToolRegistry()
        reg.register(
            ToolSpec("fast", "x", ("repo.read",), frozenset({CouncilId.IT}), SideEffectLevel.A0_READ_ONLY),
            lambda: None,
        )
        reg.register(
            ToolSpec("bad", "x", ("repo.read",), frozenset({CouncilId.IT}), SideEffectLevel.A0_READ_ONLY),
            lambda: None,
        )
        learner = ToolPolicyLearner()
        for _ in range(5):
            learner.observe(ToolObservation("CODE", "IT", "fast", True, 10, 1))
            learner.observe(ToolObservation("CODE", "IT", "bad", False, 10, 1))
        ranked = learner.rank(registry=reg, council=CouncilId.IT, task_family="CODE", capability="repo.read")
        self.assertEqual(ranked[0].tool_name, "fast")


if __name__ == "__main__":
    unittest.main()
