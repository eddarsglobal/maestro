import unittest

from maestro.models import Mission
from maestro.outcome_intelligence import MissionOutcomeBridge, OutcomeNotVerified


class OutcomeVerificationGateTests(unittest.TestCase):
    def test_unverified_mission_cannot_become_outcome(self):
        with self.assertRaises(OutcomeNotVerified):
            MissionOutcomeBridge().from_mission(
                Mission("test"),
                task_family="DIRECT",
                resource_id="r1",
                dimensions=[],
            )

if __name__ == "__main__":
    unittest.main()
