import unittest

from maestro.academy.models import ScenarioResult
from maestro.autonomous.shadow import ShadowObservation
from maestro.os.academy_feedback import OnlineAcademyFeedback


class OnlineAcademyFeedbackTests(unittest.TestCase):
    def test_feedback_snapshot_and_clear(self):
        f = OnlineAcademyFeedback()
        f.record_scenario_result(ScenarioResult("S1", "P1", True, {"IT"}, set(), False))
        f.record_shadow(ShadowObservation("T1", "P1", "P2", 0.5, 0.6))
        snap = f.snapshot()
        self.assertEqual(len(snap.scenario_results), 1)
        self.assertEqual(len(snap.shadow_observations), 1)
        f.clear()
        self.assertEqual(len(f.snapshot().scenario_results), 0)


if __name__ == "__main__":
    unittest.main()
