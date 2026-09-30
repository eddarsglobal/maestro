import tempfile
import unittest
from pathlib import Path

from maestro.adaptive import AdaptiveController, AdaptivePolicyManager, PolicyKind, PolicyStatus
from maestro.outcome_governed_adaptation import (
    AdaptationStatus,
    DeterministicEvaluationProfile,
    OutcomeGovernedAdaptation,
)
from maestro.outcome_intelligence import AttributionEffect, AttributionFinding, AttributionTarget, VerifiedOutcome


def outcome(i):
    return VerifiedOutcome(
        task_id=f"T{i}",
        task_family="DIRECT",
        system_verdict="JUSTE",
        ay_verified=True,
        resource_id="r1",
        attributions=(
            AttributionFinding(
                AttributionTarget.RESOURCE,
                AttributionEffect.CREDIT,
                0.8,
                "verified",
            ),
        ),
    )


class CandidateLifecyclePersistenceTests(unittest.TestCase):

    def test_shadow_state_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidates.jsonl"
            engine = OutcomeGovernedAdaptation(path)
            candidate = engine.propose_from_outcomes([outcome(1), outcome(2), outcome(3)])[0]
            manager = AdaptivePolicyManager()
            controller = AdaptiveController(manager)
            policy = engine.stage_shadow(candidate, controller)

            self.assertEqual(policy.status, PolicyStatus.SHADOW)
            self.assertEqual(candidate.status, AdaptationStatus.SHADOW)
            self.assertIsNone(manager.active(PolicyKind.MODEL_SELECTION))

            restarted = OutcomeGovernedAdaptation(path)
            loaded = restarted.ledger.all()[0]
            self.assertEqual(loaded.status, AdaptationStatus.SHADOW)
            history = restarted.ledger.history(candidate.candidate_id)
            self.assertEqual(
                [row.status for row in history],
                [AdaptationStatus.ELIGIBLE, AdaptationStatus.SHADOW],
            )

    def test_promotion_ready_state_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidates.jsonl"
            engine = OutcomeGovernedAdaptation(path)
            candidate = engine.propose_from_outcomes([outcome(1), outcome(2), outcome(3)])[0]
            manager = AdaptivePolicyManager()
            controller = AdaptiveController(manager)
            engine.stage_shadow(candidate, controller)

            recommendation, _ = engine.prepare_promotion(
                candidate,
                replay_score=0.95,
                baseline_score=0.85,
                regression_count=0,
                shadow_success_rate=0.95,
                evaluation_samples=12,
                academy_recommended=True,
                evaluation_profile=DeterministicEvaluationProfile(
                    provider_id="ollama",
                    route="/api/generate",
                    temperature=0,
                    seed=42,
                    num_predict=64,
                    think=False,
                    suite_version="academy-v1.1.0-lifecycle-test",
                ),
                semantic_success_rate=0.95,
                format_success_rate=0.95,
                format_regression_count=0,
            )

            self.assertTrue(recommendation.ready_for_governance)
            self.assertEqual(candidate.status, AdaptationStatus.PROMOTION_READY)
            self.assertIsNone(manager.active(PolicyKind.MODEL_SELECTION))

            restarted = OutcomeGovernedAdaptation(path)
            loaded = restarted.ledger.all()[0]
            self.assertEqual(loaded.status, AdaptationStatus.PROMOTION_READY)
            history = restarted.ledger.history(candidate.candidate_id)
            self.assertEqual(
                [row.status for row in history],
                [
                    AdaptationStatus.ELIGIBLE,
                    AdaptationStatus.SHADOW,
                    AdaptationStatus.PROMOTION_READY,
                ],
            )


if __name__ == "__main__":
    unittest.main()
