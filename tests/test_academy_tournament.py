import unittest

from maestro.academy.models import AcademyScenario, PolicyVariant, ScenarioResult
from maestro.academy.tournament import ShadowPolicyTournament


class TournamentTests(unittest.TestCase):
    def test_better_policy_is_recommended_only(self):
        scenario = AcademyScenario("X", "x", {"IT"})
        policies = [
            PolicyVariant("BAD", "1", "bad"),
            PolicyVariant("GOOD", "1", "good"),
        ]

        def runner(policy, scenario):
            return ScenarioResult(
                scenario.scenario_id,
                policy.policy_id,
                success=True,
                selected_councils={"IT"} if policy.policy_id == "GOOD" else {"CM"},
                gates_observed=set(),
                human_approval_requested=False,
                retries=0 if policy.policy_id == "GOOD" else 3,
            )

        report = ShadowPolicyTournament().run(
            policies=policies,
            scenarios=[scenario],
            runner=runner,
        )
        self.assertEqual(report.recommended_policy_id, "GOOD")
        self.assertIn("recommendation", report.note.lower())


if __name__ == "__main__":
    unittest.main()
