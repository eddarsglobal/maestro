import unittest

from maestro.adaptive.skills import SkillFactory
from maestro.learning.models import ExperienceRecord, OutcomeStatus


class SkillFactoryTests(unittest.TestCase):
    def test_repeated_verified_success_creates_skill_candidate(self):
        exps = [
            ExperienceRecord(
                task_id=f"T{i}",
                task_family="WEBHOOK",
                councils=["IT", "SC", "OP"],
                strategies=["IDEMPOTENT_HANDLER"],
                tool_names=["test"],
                outcome=OutcomeStatus.SUCCESS,
                verified=True,
            )
            for i in range(3)
        ]
        skills = SkillFactory().discover(exps, min_support=3)
        self.assertEqual(len(skills), 1)
        self.assertEqual(skills[0].task_family, "WEBHOOK")


if __name__ == "__main__":
    unittest.main()
