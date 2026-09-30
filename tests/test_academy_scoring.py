import unittest

from maestro.academy.models import AcademyScenario, ScenarioResult
from maestro.academy.scoring import score_result


class ScoringTests(unittest.TestCase):
    def test_perfect_result_beats_overrouted_result(self):
        scenario = AcademyScenario(
            task_family="X",
            objective="x",
            required_councils={"IT", "SC"},
            forbidden_councils={"CM"},
            required_gates={"AY"},
        )
        perfect = ScenarioResult(
            scenario_id=scenario.scenario_id,
            policy_id="P1",
            success=True,
            selected_councils={"IT", "SC"},
            gates_observed={"AY"},
            human_approval_requested=False,
        )
        over = ScenarioResult(
            scenario_id=scenario.scenario_id,
            policy_id="P2",
            success=True,
            selected_councils={"IT", "SC", "CM"},
            gates_observed={"AY"},
            human_approval_requested=False,
        )
        self.assertGreater(score_result(scenario, perfect).total, score_result(scenario, over).total)


if __name__ == "__main__":
    unittest.main()
