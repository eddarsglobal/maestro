import unittest

from maestro.academy.models import AcademyScenario, PolicyVariant, ScenarioResult
from maestro.academy.replay import HistoricalReplay


class ReplayTests(unittest.TestCase):
    def test_replay_detects_regression(self):
        s1 = AcademyScenario("X", "x", {"IT"})
        s2 = AcademyScenario("Y", "y", {"SC"})
        baseline = PolicyVariant("BASE", "1", "base")
        candidate = PolicyVariant("CAND", "2", "cand")

        def runner(policy, scenario):
            if policy.policy_id == "BASE":
                selected = set(scenario.required_councils)
            else:
                selected = set() if scenario.task_family == "Y" else set(scenario.required_councils)
            return ScenarioResult(
                scenario.scenario_id, policy.policy_id, True,
                selected, set(), False,
            )

        report = HistoricalReplay().compare(
            baseline=baseline,
            candidate=candidate,
            scenarios=[s1, s2],
            runner=runner,
        )
        self.assertEqual(report.regressions, 1)
        self.assertIn(s2.scenario_id, report.regression_scenarios)


if __name__ == "__main__":
    unittest.main()
