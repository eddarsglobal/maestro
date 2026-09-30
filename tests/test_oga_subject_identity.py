import unittest

from maestro.outcome_governed_adaptation import (
    OutcomeGovernedAdaptation,
    OutcomePatternDetector,
)
from maestro.outcome_intelligence import (
    AttributionEffect,
    AttributionFinding,
    AttributionTarget,
    VerifiedOutcome,
)


def resource_outcome(
    i: int,
    resource_id: str,
    effect: AttributionEffect = AttributionEffect.CREDIT,
):
    return VerifiedOutcome(
        task_id=f"T{i}",
        task_family="DIRECT",
        system_verdict="JUSTE",
        ay_verified=True,
        resource_id=resource_id,
        attributions=(
            AttributionFinding(
                AttributionTarget.RESOURCE,
                effect,
                0.8,
                "verified",
            ),
        ),
    )


class SubjectIdentityTests(unittest.TestCase):
    def test_different_resources_cannot_form_one_pattern(self):
        detector = OutcomePatternDetector()
        patterns = detector.detect([
            resource_outcome(1, "r1"),
            resource_outcome(2, "r2"),
            resource_outcome(3, "r3"),
        ])
        self.assertEqual(patterns, [])

    def test_same_resource_forms_subject_bound_candidate(self):
        engine = OutcomeGovernedAdaptation()
        candidates = engine.propose_from_outcomes([
            resource_outcome(1, "r1"),
            resource_outcome(2, "r1"),
            resource_outcome(3, "r1"),
        ])
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.proposed_change["subject_id"], "r1")
        self.assertEqual(candidate.metadata["subject_id"], "r1")
        self.assertIn(":r1:", candidate.key)

    def test_missing_non_resource_subject_is_not_learned(self):
        outcomes = []
        for i in range(3):
            outcomes.append(
                VerifiedOutcome(
                    task_id=f"C{i}",
                    task_family="DIRECT",
                    system_verdict="JUSTE",
                    ay_verified=True,
                    attributions=(
                        AttributionFinding(
                            AttributionTarget.CONTEXT,
                            AttributionEffect.CREDIT,
                            0.8,
                            "verified",
                        ),
                    ),
                )
            )
        detector = OutcomePatternDetector()
        self.assertEqual(detector.detect(outcomes), [])


if __name__ == "__main__":
    unittest.main()
