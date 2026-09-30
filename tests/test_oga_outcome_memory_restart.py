import tempfile
import unittest
from pathlib import Path

from maestro.outcome_intelligence import (
    AttributionEffect,
    AttributionFinding,
    AttributionTarget,
    OutcomeIntelligence,
    VerifiedOutcome,
)


class OutcomeMemoryRestartTests(unittest.TestCase):
    def test_outcome_intelligence_reloads_verified_memory(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "outcomes.jsonl"

            oi1 = OutcomeIntelligence(path)
            row = VerifiedOutcome(
                task_id="T1",
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
            oi1.ledger.record(row)

            oi2 = OutcomeIntelligence(path)

            self.assertEqual(len(oi2.ledger.all()), 1)
            self.assertEqual(oi2.ledger.all()[0].outcome_id, row.outcome_id)


if __name__ == "__main__":
    unittest.main()
