import unittest

from maestro.academy.replay import ReplayReport
from maestro.academy.tournament import TournamentReport, TournamentStanding
from maestro.adaptive.controller import AdaptiveController
from maestro.adaptive.models import AdaptivePolicy, PolicyKind
from maestro.adaptive.policy_manager import AdaptivePolicyManager


class AdaptiveControllerTests(unittest.TestCase):
    def test_controller_prepares_promotion_evidence_not_activation(self):
        manager = AdaptivePolicyManager()
        controller = AdaptiveController(manager)
        policy = AdaptivePolicy(PolicyKind.ROUTING, 1, "x", {"rules": {}})
        controller.stage_candidate(policy)

        replay = ReplayReport(
            "BASE", policy.policy_id, 100, 0.8, 0.9, 0, 50, 50, 0.1, []
        )
        tournament = TournamentReport(
            [TournamentStanding(policy.policy_id, 0.9, 0.95, 1, 10, 0, 1)],
            policy.policy_id,
        )
        proposal, evidence = controller.assess(
            policy, replay, tournament, shadow_success_rate=0.95
        )
        self.assertTrue(proposal.ready_for_governance)
        self.assertIsNone(manager.active(PolicyKind.ROUTING))


if __name__ == "__main__":
    unittest.main()
