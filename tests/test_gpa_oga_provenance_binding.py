import tempfile
import unittest
from types import SimpleNamespace

from maestro import ProductionGenesisSystem
from maestro.outcome_governed_adaptation import (
    AdaptationCandidate,
    AdaptationDomain,
    AdaptationStatus,
)


def persisted_candidate():
    return AdaptationCandidate(
        domain=AdaptationDomain.MODEL_SELECTION,
        task_family="DIRECT",
        key="MODEL_SELECTION:DIRECT:RESOURCE:r1:CREDIT",
        statement="verified real candidate",
        proposed_change={
            "action": "PREFER_CONDITIONALLY",
            "subject_id": "r1",
            "authority_change": False,
        },
        pattern_id="PAT-PROVENANCE",
        support_outcome_ids=("O1", "O2", "O3"),
        confidence=0.8,
        status=AdaptationStatus.PROMOTION_READY,
        metadata={
            "evaluation_learning_eligible": True,
            "evaluation_profile_id": "EVP-TEST-PROVENANCE",
        },
    )


class GPAOGAProvenanceBindingTests(unittest.TestCase):

    def test_fabricated_promotion_ready_candidate_is_rejected_in_genesis(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)

            fake = SimpleNamespace(
                candidate_id="FAKE-CANDIDATE",
                task_family="DIRECT",
                status="PROMOTION_READY",
                proposed_change={
                    "action": "PREFER_CONDITIONALLY",
                    "subject_id": "r1",
                    "authority_change": False,
                },
            )

            with self.assertRaises(PermissionError):
                system.governed_activation.propose(
                    fake,
                    policy_kind="MODEL_SELECTION",
                    policy_ref="POL-FAKE",
                    baseline_ref="POL-BASELINE",
                    rollback_ref="POL-BASELINE",
                )

    def test_persisted_promotion_ready_candidate_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)

            candidate = persisted_candidate()
            system.outcome_governed_adaptation.ledger.record(candidate)

            snapshot = system.governed_activation.propose(
                candidate,
                policy_kind="MODEL_SELECTION",
                policy_ref="POL-CANDIDATE",
                baseline_ref="POL-BASELINE",
                rollback_ref="POL-BASELINE",
            )

            self.assertEqual(
                snapshot.candidate_id,
                candidate.candidate_id,
            )

    def test_tampered_candidate_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)

            candidate = persisted_candidate()
            system.outcome_governed_adaptation.ledger.record(candidate)

            tampered = SimpleNamespace(
                candidate_id=candidate.candidate_id,
                task_family=candidate.task_family,
                status="PROMOTION_READY",
                key=candidate.key,
                proposed_change={
                    **candidate.proposed_change,
                    "subject_id": "attacker-resource",
                },
            )

            with self.assertRaises(PermissionError):
                system.governed_activation.propose(
                    tampered,
                    policy_kind="MODEL_SELECTION",
                    policy_ref="POL-TAMPERED",
                    baseline_ref="POL-BASELINE",
                    rollback_ref="POL-BASELINE",
                )


if __name__ == "__main__":
    unittest.main()
