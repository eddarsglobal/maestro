import unittest

from maestro.enums import CouncilId, MissionState
from maestro.models import Mission
from maestro.state_machine import InvalidTransition, transition


class StateMachineTests(unittest.TestCase):
    def test_only_ex_can_transition(self):
        mission = Mission("x")
        with self.assertRaises(PermissionError):
            transition(mission, CouncilId.IT, MissionState.ANALYSIS)

    def test_valid_transition(self):
        mission = Mission("x")
        transition(mission, CouncilId.EX, MissionState.ANALYSIS)
        self.assertEqual(mission.state, MissionState.ANALYSIS)

    def test_invalid_transition(self):
        mission = Mission("x")
        with self.assertRaises(InvalidTransition):
            transition(mission, CouncilId.EX, MissionState.TASK_COMPLETE)


if __name__ == "__main__":
    unittest.main()
