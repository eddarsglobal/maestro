import tempfile
import unittest
from pathlib import Path

from maestro.outcome_intelligence import OutcomeLedger, VerifiedOutcome


class OutcomeLedgerTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "outcomes.jsonl"
            ledger = OutcomeLedger(path)
            row = VerifiedOutcome(
                task_id="T1",
                task_family="DIRECT",
                system_verdict="JUSTE",
                ay_verified=True,
                resource_id="r1",
            )
            ledger.record(row)
            loaded = OutcomeLedger(path)
            loaded.load()
            self.assertEqual(len(loaded.all()), 1)
            self.assertEqual(loaded.all()[0].outcome_id, row.outcome_id)

if __name__ == "__main__":
    unittest.main()
