import tempfile
import unittest
from pathlib import Path

from maestro.outcome_governed_adaptation import OutcomeGovernedAdaptation
from maestro.outcome_intelligence import (
    AttributionEffect,
    AttributionFinding,
    AttributionTarget,
    OutcomeIntelligence,
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


class OutcomeMemoryBridgeTests(unittest.TestCase):
    def test_engine_can_propose_directly_from_persistent_outcome_memory(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)

            oi = OutcomeIntelligence(td / "outcomes.jsonl")
            for i in range(1, 4):
                oi.ledger.record(outcome(i))

            oga = OutcomeGovernedAdaptation(td / "candidates.jsonl")

            created = oga.propose_from_memory(
                oi,
                task_family="DIRECT",
                resource_id="r1",
            )

            self.assertEqual(len(created), 1)
            self.assertEqual(
                created[0].proposed_change["subject_id"],
                "r1",
            )


if __name__ == "__main__":
    unittest.main()
