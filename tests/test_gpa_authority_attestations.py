import tempfile
import unittest
from types import SimpleNamespace

from maestro import ProductionGenesisSystem
from maestro.governed_activation import (
    ActivationState,
    GovernanceAction,
    GovernanceAttestation,
    StrictGovernedPolicyActivation,
)


def candidate(candidate_id="OGA-AUTH-CANDIDATE"):
    return SimpleNamespace(
        candidate_id=candidate_id,
        task_family="DIRECT",
        status="PROMOTION_READY",
        proposed_change={"authority_change": False},
    )


def proposed(engine, candidate_id="OGA-AUTH-CANDIDATE"):
    return engine.propose(
        candidate(candidate_id),
        policy_kind="MODEL_SELECTION",
        policy_ref="POL-CANDIDATE",
        baseline_ref="POL-BASELINE",
        rollback_ref="POL-BASELINE",
    )


class GPAAuthorityAttestationTests(unittest.TestCase):

    def test_attestation_id_is_deterministic_and_contract_bound(self):
        engine = StrictGovernedPolicyActivation()
        snapshot = proposed(engine)

        first = engine.issue_ay_validation(
            snapshot,
            verdict="JUSTE",
            evidence_refs=("EVD-AY",),
        )
        second = engine.issue_ay_validation(
            snapshot,
            verdict="JUSTE",
            evidence_refs=("EVD-AY",),
        )

        self.assertEqual(
            first.attestation_id,
            second.attestation_id,
        )

        other = StrictGovernedPolicyActivation()
        other_snapshot = proposed(other, "OTHER-CANDIDATE")

        with self.assertRaises(PermissionError):
            first.assert_bound(
                other_snapshot,
                actor="AY",
                action=GovernanceAction.AY_VALIDATE,
            )

    def test_strict_ay_rejects_legacy_and_accepts_attestation(self):
        engine = StrictGovernedPolicyActivation()
        snapshot = proposed(engine)

        with self.assertRaises(PermissionError):
            engine.ay_validate(
                snapshot,
                verdict="JUSTE",
                evidence_refs=["EVD-AY"],
            )

        ay = engine.issue_ay_validation(
            snapshot,
            verdict="JUSTE",
            evidence_refs=["EVD-AY"],
        )
        engine.ay_validate(
            snapshot,
            attestation=ay,
        )

        self.assertEqual(
            snapshot.state,
            ActivationState.AY_VALIDATED,
        )
        self.assertEqual(
            snapshot.metadata["ay_attestation_id"],
            ay.attestation_id,
        )

    def test_ex_attestation_is_chained_to_ay(self):
        engine = StrictGovernedPolicyActivation()
        snapshot = proposed(engine)

        ay = engine.issue_ay_validation(
            snapshot,
            verdict="JUSTE",
            evidence_refs=["EVD-AY"],
        )
        engine.ay_validate(snapshot, attestation=ay)

        ex = engine.issue_ex_authorization(
            snapshot,
            authorized=True,
            authority_ref="EX-AUTH-1",
            evidence_refs=["EVD-EX"],
        )

        self.assertEqual(
            ex.parent_attestation_id,
            ay.attestation_id,
        )

        engine.ex_authorize(
            snapshot,
            attestation=ex,
        )

        self.assertEqual(
            snapshot.state,
            ActivationState.EX_AUTHORIZED,
        )
        self.assertEqual(
            snapshot.metadata["ex_attestation_id"],
            ex.attestation_id,
        )

    def test_wrong_ex_parent_is_rejected(self):
        engine = StrictGovernedPolicyActivation()
        snapshot = proposed(engine)

        ay = engine.issue_ay_validation(
            snapshot,
            verdict="JUSTE",
            evidence_refs=["EVD-AY"],
        )
        engine.ay_validate(snapshot, attestation=ay)

        forged = GovernanceAttestation(
            actor="EX",
            action=GovernanceAction.EX_AUTHORIZE,
            contract_id=snapshot.contract_id,
            decision="AUTHORIZED",
            evidence_refs=("EVD-EX",),
            authority_ref="EX-AUTH-1",
            parent_attestation_id="GAT-WRONG",
        )

        with self.assertRaises(PermissionError):
            engine.ex_authorize(
                snapshot,
                attestation=forged,
            )

    def test_runtime_rollback_rejects_legacy_booleans(self):
        engine = StrictGovernedPolicyActivation()
        snapshot = proposed(engine)
        snapshot.state = ActivationState.ACTIVE

        with self.assertRaises(PermissionError):
            engine.rollback_manager(
                snapshot,
                manager=None,
                kind="MODEL_SELECTION",
                reason="RUNTIME_DEGRADED",
                evidence_ref="EVD-DEGRADED",
                ex_authorized=True,
                ay_acknowledged=True,
                ex_authority_ref="EX-LEGACY",
                ay_ack_ref="AY-LEGACY",
            )

    def test_production_genesis_uses_strict_engine(self):
        with tempfile.TemporaryDirectory() as td:
            system = ProductionGenesisSystem(td)
            self.assertIsInstance(
                system.governed_activation,
                StrictGovernedPolicyActivation,
            )


if __name__ == "__main__":
    unittest.main()
