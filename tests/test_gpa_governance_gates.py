import unittest
from types import SimpleNamespace

from maestro.governed_activation import ActivationState, GovernedPolicyActivation


def candidate():
    return SimpleNamespace(
        candidate_id="OGA-CANDIDATE-2",
        task_family="DIRECT",
        status="PROMOTION_READY",
        proposed_change={"authority_change": False},
    )


class GPAGovernanceGateTests(unittest.TestCase):
    def test_ex_cannot_authorize_before_ay(self):
        engine = GovernedPolicyActivation()
        snapshot = engine.propose(
            candidate(),
            policy_kind="MODEL_SELECTION",
            policy_ref="POL-CANDIDATE",
            baseline_ref="POL-BASELINE",
            rollback_ref="POL-BASELINE",
        )

        with self.assertRaises(PermissionError):
            engine.ex_authorize(
                snapshot,
                authorized=True,
                authority_ref="EX-AUTH-1",
            )

        self.assertEqual(snapshot.state, ActivationState.PROPOSED)

    def test_model_cannot_impersonate_ex_authority(self):
        engine = GovernedPolicyActivation()
        snapshot = engine.propose(
            candidate(),
            policy_kind="MODEL_SELECTION",
            policy_ref="POL-CANDIDATE",
            baseline_ref="POL-BASELINE",
            rollback_ref="POL-BASELINE",
        )

        engine.ay_validate(
            snapshot,
            verdict="JUSTE",
            evidence_refs=["EVD-AY-1"],
        )

        with self.assertRaises(PermissionError):
            engine.ex_authorize(
                snapshot,
                authorized=True,
                authority_ref="MODEL-SAID-YES",
                actor="LLM",
            )

        self.assertEqual(snapshot.state, ActivationState.AY_VALIDATED)


if __name__ == "__main__":
    unittest.main()
