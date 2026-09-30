import tempfile
import unittest
from pathlib import Path

from maestro.outcome_governed_adaptation import OutcomeGovernedAdaptation
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


class CandidateMemoryRestartTests(unittest.TestCase):
    def test_candidate_ledger_survives_restart_without_duplicate(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidates.jsonl"

            first = OutcomeGovernedAdaptation(path)
            created = first.propose_from_outcomes(
                [outcome(1), outcome(2), outcome(3)]
            )
            self.assertEqual(len(created), 1)

            second = OutcomeGovernedAdaptation(path)
            self.assertEqual(len(second.ledger.all()), 1)

            duplicate = second.propose_from_outcomes(
                [outcome(4), outcome(5), outcome(6)]
            )

            self.assertEqual(duplicate, [])
            self.assertEqual(len(second.ledger.all()), 1)


if __name__ == "__main__":
    unittest.main()
