import tempfile
import unittest
from pathlib import Path

from maestro.outcome_governed_adaptation import OutcomeMemoryBridge
from maestro.outcome_intelligence import OutcomeLedger, VerifiedOutcome


class CrossVersionImportTests(unittest.TestCase):
    def test_import_preserves_ids_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)

            source_path = td / "old.jsonl"
            dest_path = td / "new.jsonl"

            source = OutcomeLedger(source_path)
            row = VerifiedOutcome(
                task_id="T1",
                task_family="DIRECT",
                system_verdict="JUSTE",
                ay_verified=True,
                resource_id="r1",
                outcome_id="OUT-HISTORICAL-001",
            )
            source.record(row)

            destination = OutcomeLedger(dest_path)
            bridge = OutcomeMemoryBridge()

            first = bridge.import_verified_history(
                source_path,
                destination,
            )
            second = bridge.import_verified_history(
                source_path,
                destination,
            )

            self.assertEqual(first["imported"], 1)
            self.assertEqual(second["imported"], 0)
            self.assertEqual(second["duplicates"], 1)
            self.assertEqual(len(destination.all()), 1)
            self.assertEqual(
                destination.all()[0].outcome_id,
                "OUT-HISTORICAL-001",
            )


if __name__ == "__main__":
    unittest.main()
