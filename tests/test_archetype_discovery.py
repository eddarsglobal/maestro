import unittest

from maestro.adaptive.archetypes import ArchetypeDiscovery
from maestro.learning.models import ExperienceRecord, OutcomeStatus


class ArchetypeDiscoveryTests(unittest.TestCase):
    def test_structural_pattern_creates_archetype(self):
        exps = []
        for i, family in enumerate(["PAYMENT", "BILLING", "CHECKOUT"]):
            exps.append(
                ExperienceRecord(
                    task_id=f"T{i}",
                    task_family=family,
                    councils=["PM", "IT", "SC", "FN", "OP", "AY"],
                    strategies=["TRANSACTIONAL_FLOW"],
                    tool_names=["integration_test"],
                    outcome=OutcomeStatus.SUCCESS,
                    verified=True,
                )
            )
        archetypes = ArchetypeDiscovery().discover(exps, min_support=3)
        self.assertEqual(len(archetypes), 1)
        self.assertEqual(archetypes[0].support_count, 3)


if __name__ == "__main__":
    unittest.main()
