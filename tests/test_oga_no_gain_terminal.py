import tempfile
import unittest
from pathlib import Path

from maestro.outcome_governed_adaptation import (
    AdaptationCandidate,
    AdaptationDomain,
    AdaptationStatus,
    OutcomeGovernedAdaptation,
)


def evaluating_candidate():
    return AdaptationCandidate(
        domain=AdaptationDomain.MODEL_SELECTION,
        task_family="DIRECT",
        key="MODEL_SELECTION:DIRECT:RESOURCE:r1:CREDIT",
        statement="test",
        proposed_change={
            "action": "PREFER_CONDITIONALLY",
            "subject_id": "r1",
            "authority_change": False,
        },
        pattern_id="PAT-TEST",
        support_outcome_ids=("O1", "O2", "O3"),
        confidence=0.6,
        status=AdaptationStatus.EVALUATING,
    )


class NoGainTerminalTests(unittest.TestCase):

    def test_redundant_candidate_becomes_rejected_and_persists(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "candidates.jsonl"
            engine = OutcomeGovernedAdaptation(path)
            candidate = evaluating_candidate()
            engine.ledger.record(candidate)

            closed = engine.close_no_gain(
                candidate,
                replay_delta=0.0,
                improvement_count=0,
                regression_count=0,
                academy_recommended=False,
                baseline_equivalent=True,
            )

            self.assertEqual(closed.status, AdaptationStatus.REJECTED)
            self.assertEqual(
                closed.metadata["terminal_disposition"],
                "NO_GAIN_REDUNDANT",
            )

            restarted = OutcomeGovernedAdaptation(path)
            rows = restarted.ledger.all()

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].status, AdaptationStatus.REJECTED)

            history = restarted.ledger.history(candidate.candidate_id)
            self.assertEqual(
                [row.status for row in history],
                [
                    AdaptationStatus.EVALUATING,
                    AdaptationStatus.REJECTED,
                ],
            )

    def test_positive_delta_cannot_be_closed_as_no_gain(self):
        engine = OutcomeGovernedAdaptation()
        candidate = evaluating_candidate()

        with self.assertRaises(ValueError):
            engine.close_no_gain(
                candidate,
                replay_delta=0.05,
                improvement_count=1,
                regression_count=0,
                academy_recommended=True,
                baseline_equivalent=False,
            )

        self.assertEqual(candidate.status, AdaptationStatus.EVALUATING)

    def test_shadow_candidate_cannot_skip_evaluation_to_terminal_rejection(self):
        engine = OutcomeGovernedAdaptation()
        candidate = evaluating_candidate()
        candidate.status = AdaptationStatus.SHADOW

        with self.assertRaises(ValueError):
            engine.close_no_gain(
                candidate,
                replay_delta=0.0,
                improvement_count=0,
                regression_count=0,
                academy_recommended=False,
                baseline_equivalent=True,
            )

        self.assertEqual(candidate.status, AdaptationStatus.SHADOW)


if __name__ == "__main__":
    unittest.main()
