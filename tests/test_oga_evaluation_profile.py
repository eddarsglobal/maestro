import tempfile
import unittest
from pathlib import Path

from maestro.adaptive import AdaptiveController, AdaptivePolicyManager
from maestro.outcome_governed_adaptation import (
    AdaptationStatus,
    DeterministicEvaluationProfile,
    OutcomeGovernedAdaptation,
)
from maestro.outcome_intelligence import (
    AttributionEffect,
    AttributionFinding,
    AttributionTarget,
    VerifiedOutcome,
)


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


def shadow_candidate(engine):
    candidate = engine.propose_from_outcomes(
        [outcome(1), outcome(2), outcome(3)]
    )[0]
    manager = AdaptivePolicyManager()
    controller = AdaptiveController(manager)
    engine.stage_shadow(candidate, controller)
    return candidate


def profile():
    return DeterministicEvaluationProfile(
        provider_id="ollama",
        route="/api/generate",
        temperature=0,
        seed=42,
        num_predict=64,
        think=False,
        suite_version="academy-v1.1.0-test",
    )


class OGAEvaluationProfileTests(unittest.TestCase):

    def test_profile_id_is_stable_and_roundtrips(self):
        first = profile()
        second = DeterministicEvaluationProfile.from_dict(first.to_dict())
        self.assertTrue(first.learning_eligible)
        self.assertEqual(first.profile_id, second.profile_id)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_positive_scores_without_profile_cannot_promote(self):
        engine = OutcomeGovernedAdaptation()
        candidate = shadow_candidate(engine)

        recommendation, _ = engine.prepare_promotion(
            candidate,
            replay_score=0.99,
            baseline_score=0.80,
            regression_count=0,
            shadow_success_rate=1.0,
            evaluation_samples=12,
            academy_recommended=True,
            semantic_success_rate=1.0,
            format_success_rate=1.0,
            format_regression_count=0,
        )

        self.assertFalse(recommendation.ready_for_governance)
        self.assertEqual(candidate.status, AdaptationStatus.EVALUATING)
        self.assertFalse(candidate.metadata["evaluation_learning_eligible"])

    def test_deterministic_semantic_format_evidence_may_promote(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidates.jsonl"
            engine = OutcomeGovernedAdaptation(path)
            candidate = shadow_candidate(engine)

            recommendation, _ = engine.prepare_promotion(
                candidate,
                replay_score=0.99,
                baseline_score=0.80,
                regression_count=0,
                shadow_success_rate=1.0,
                evaluation_samples=12,
                academy_recommended=True,
                evaluation_profile=profile(),
                semantic_success_rate=1.0,
                format_success_rate=1.0,
                format_regression_count=0,
            )

            self.assertTrue(recommendation.ready_for_governance)
            self.assertEqual(candidate.status, AdaptationStatus.PROMOTION_READY)
            self.assertTrue(candidate.metadata["evaluation_learning_eligible"])
            self.assertTrue(
                candidate.metadata["evaluation_profile_id"].startswith("EVP-")
            )

            restarted = OutcomeGovernedAdaptation(path)
            persisted = restarted.ledger.all()[0]
            self.assertEqual(
                persisted.metadata["evaluation_profile_id"],
                candidate.metadata["evaluation_profile_id"],
            )

    def test_format_regression_blocks_promotion(self):
        engine = OutcomeGovernedAdaptation()
        candidate = shadow_candidate(engine)

        recommendation, _ = engine.prepare_promotion(
            candidate,
            replay_score=0.99,
            baseline_score=0.80,
            regression_count=0,
            shadow_success_rate=1.0,
            evaluation_samples=12,
            academy_recommended=True,
            evaluation_profile=profile(),
            semantic_success_rate=1.0,
            format_success_rate=1.0,
            format_regression_count=1,
        )

        self.assertFalse(recommendation.ready_for_governance)
        self.assertEqual(candidate.status, AdaptationStatus.EVALUATING)


if __name__ == "__main__":
    unittest.main()
