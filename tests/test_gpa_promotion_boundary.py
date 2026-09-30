import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

from maestro.governed_activation import GovernedPolicyActivation


def candidate(status="PROMOTION_READY"):
    return SimpleNamespace(
        candidate_id="OGA-CANDIDATE-1",
        task_family="DIRECT",
        status=status,
        proposed_change={"authority_change": False},
    )


class GPAPromotionBoundaryTests(unittest.TestCase):
    def test_promotion_ready_is_required(self):
        engine = GovernedPolicyActivation()

        with self.assertRaises(PermissionError):
            engine.propose(
                candidate("EVALUATING"),
                policy_kind="MODEL_SELECTION",
                policy_ref="POL-CANDIDATE",
                baseline_ref="POL-BASELINE",
                rollback_ref="POL-BASELINE",
            )

    def test_activation_contract_is_immutable(self):
        engine = GovernedPolicyActivation()
        snapshot = engine.propose(
            candidate(),
            policy_kind="MODEL_SELECTION",
            policy_ref="POL-CANDIDATE",
            baseline_ref="POL-BASELINE",
            rollback_ref="POL-BASELINE",
        )

        with self.assertRaises(FrozenInstanceError):
            snapshot.contract.policy_ref = "MUTATED"


if __name__ == "__main__":
    unittest.main()
