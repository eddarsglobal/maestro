import unittest

from maestro.autonomous.skills_runtime import SkillRuntime
from maestro.adaptive.skills import SkillCandidate


class SkillRuntimeTests(unittest.TestCase):
    def test_compile(self):
        skill = SkillCandidate(
            "WEBHOOK_SKILL", "WEBHOOK", ["IT", "SC"], ["IDEMPOTENT"], ["test"], ["E1", "E2", "E3"]
        )
        plan = SkillRuntime().compile(skill, inputs={"repo": "x"})
        self.assertEqual(plan.councils, ["IT", "SC"])
        self.assertEqual(plan.inputs["repo"], "x")


if __name__ == "__main__":
    unittest.main()
