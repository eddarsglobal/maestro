import unittest
from types import SimpleNamespace

from maestro.governed_activation import (
    ActivationState,
    CanaryEvidence,
    GovernedPolicyActivation,
)


def candidate():
    return SimpleNamespace(
        candidate_id="OGA-CANDIDATE-3",
        task_family="DIRECT",
        status="PROMOTION_READY",
        proposed_change={"authority_change": False},
    )


def authorized_snapshot(engine):
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
    engine.ex_authorize(
        snapshot,
        authorized=True,
        authority_ref="EX-AUTH-1",
    )
    return snapshot


class GPACanaryActivationTests(unittest.TestCase):
    def test_active_is_blocked_before_verified_canary(self):
        engine = GovernedPolicyActivation()
        snapshot = authorized_snapshot(engine)

        with self.assertRaises(PermissionError):
            engine.activate(snapshot)

        self.assertEqual(snapshot.state, ActivationState.EX_AUTHORIZED)

    def test_healthy_canary_may_reach_active(self):
        engine = GovernedPolicyActivation()
        snapshot = authorized_snapshot(engine)

        engine.begin_canary(snapshot)
        engine.observe_canary(
            snapshot,
            CanaryEvidence(
                success_rate=1.0,
                regression_count=0,
                observed_samples=5,
                evidence_refs=("EVD-CANARY-1",),
                latency_budget_pass=True,
            ),
        )

        self.assertEqual(snapshot.state, ActivationState.CANARY_VERIFIED)
        engine.activate(snapshot)
        self.assertEqual(snapshot.state, ActivationState.ACTIVE)


if __name__ == "__main__":
    unittest.main()
