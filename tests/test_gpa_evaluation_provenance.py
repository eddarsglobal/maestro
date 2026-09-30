import tempfile
import unittest

from maestro import ProductionGenesisSystem
from maestro.outcome_governed_adaptation import (
    AdaptationCandidate,
    AdaptationDomain,
    AdaptationStatus,
)


class GPAEvaluationProvenanceTests(unittest.TestCase):

    def test_persisted_promotion_ready_without_eval_profile_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)

            candidate = AdaptationCandidate(
                domain=AdaptationDomain.MODEL_SELECTION,
                task_family="DIRECT",
                key="MODEL_SELECTION:DIRECT:RESOURCE:rX:CREDIT",
                statement="synthetic legacy promotion",
                proposed_change={
                    "action": "PREFER_CONDITIONALLY",
                    "subject_id": "rX",
                    "authority_change": False,
                },
                pattern_id="PAT-LEGACY",
                support_outcome_ids=("O1", "O2", "O3"),
                confidence=0.8,
                status=AdaptationStatus.PROMOTION_READY,
            )

            system.outcome_governed_adaptation.ledger.record(candidate)

            with self.assertRaises(PermissionError):
                system.governed_activation.propose(
                    candidate,
                    policy_kind="MODEL_SELECTION",
                    policy_ref="POL-LEGACY",
                    baseline_ref="POL-BASELINE",
                    rollback_ref="POL-BASELINE",
                )


if __name__ == "__main__":
    unittest.main()
