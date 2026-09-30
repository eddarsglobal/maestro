import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from maestro.governed_activation import (
    ActivationState,
    CanaryEvidence,
    GovernedPolicyActivation,
)


class GPARollbackPersistenceTests(unittest.TestCase):
    def test_degraded_canary_rolls_back_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "activation.jsonl"

            engine = GovernedPolicyActivation(path)

            candidate = SimpleNamespace(
                candidate_id="OGA-CANDIDATE-4",
                task_family="DIRECT",
                status="PROMOTION_READY",
                proposed_change={"authority_change": False},
            )

            snapshot = engine.propose(
                candidate,
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
            engine.begin_canary(snapshot)
            engine.observe_canary(
                snapshot,
                CanaryEvidence(
                    success_rate=0.50,
                    regression_count=1,
                    observed_samples=5,
                    evidence_refs=("EVD-CANARY-BAD",),
                    latency_budget_pass=True,
                ),
            )

            self.assertEqual(snapshot.state, ActivationState.ROLLED_BACK)

            restarted = GovernedPolicyActivation(path)
            persisted = restarted.ledger.latest(snapshot.contract_id)

            self.assertIsNotNone(persisted)
            self.assertEqual(persisted.state, ActivationState.ROLLED_BACK)

            history = restarted.ledger.history(snapshot.contract_id)
            self.assertEqual(
                [row.state for row in history],
                [
                    ActivationState.PROPOSED,
                    ActivationState.AY_VALIDATED,
                    ActivationState.EX_AUTHORIZED,
                    ActivationState.CANARY,
                    ActivationState.ROLLED_BACK,
                ],
            )


if __name__ == "__main__":
    unittest.main()
