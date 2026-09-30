import tempfile
import unittest
from pathlib import Path

from maestro.outcome_governed_adaptation import AdaptationCandidate, AdaptationCandidateLedger, AdaptationDomain


class OGALedgerTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidates.jsonl"
            ledger = AdaptationCandidateLedger(path)
            candidate = AdaptationCandidate(
                domain=AdaptationDomain.MODEL_SELECTION,
                task_family="DIRECT",
                key="k",
                statement="s",
                proposed_change={"authority_change": False},
                pattern_id="P1",
                support_outcome_ids=("O1", "O2", "O3"),
                confidence=0.8,
            )
            ledger.record(candidate)
            loaded = AdaptationCandidateLedger(path)
            loaded.load()
            self.assertEqual(len(loaded.all()), 1)
            self.assertEqual(loaded.all()[0].candidate_id, candidate.candidate_id)

if __name__ == "__main__":
    unittest.main()
