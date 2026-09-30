import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from maestro.adaptive import (
    AdaptiveController,
    AdaptivePolicy,
    PersistentAdaptivePolicyManager,
    PolicyKind,
    PromotionEvidence,
)
from maestro.governed_activation import (
    ActivationState,
    CanaryEvidence,
    RuntimeCommitOperation,
    RuntimeCommitRecord,
    RuntimeCommitState,
    StrictGovernedPolicyActivation,
)


CANDIDATE_ID = "OGA-TXN-CANDIDATE"


def promotion_evidence(candidate_id=CANDIDATE_ID):
    return PromotionEvidence(
        replay_score=0.95,
        baseline_score=0.80,
        regression_count=0,
        shadow_success_rate=1.0,
        evaluation_samples=12,
        academy_recommended=True,
        learning_candidate_id=candidate_id,
    )


def promoted_candidate():
    return SimpleNamespace(
        candidate_id=CANDIDATE_ID,
        task_family="DIRECT",
        status="PROMOTION_READY",
        proposed_change={"authority_change": False},
    )


def build_ready(td):
    root = Path(td)

    manager = PersistentAdaptivePolicyManager(
        root / "adaptive_state.json"
    )

    baseline = AdaptivePolicy(
        kind=PolicyKind.MODEL_SELECTION,
        version=1,
        description="baseline",
        parameters={
            "subject_id": "baseline",
            "source_candidate_id": "BASELINE",
        },
    )
    manager.bootstrap_active(baseline)

    candidate = AdaptivePolicy(
        kind=PolicyKind.MODEL_SELECTION,
        version=2,
        description="candidate",
        parameters={
            "subject_id": "candidate",
            "source_candidate_id": CANDIDATE_ID,
        },
    )
    AdaptiveController(manager).stage_candidate(candidate)

    engine = StrictGovernedPolicyActivation(
        root / "activation.jsonl"
    )

    snapshot = engine.propose(
        promoted_candidate(),
        policy_kind=PolicyKind.MODEL_SELECTION.value,
        policy_ref=candidate.policy_id,
        baseline_ref=baseline.policy_id,
        rollback_ref=baseline.policy_id,
    )

    ay = engine.issue_ay_validation(
        snapshot,
        verdict="JUSTE",
        evidence_refs=["EVD-AY"],
    )
    engine.ay_validate(snapshot, attestation=ay)

    ex = engine.issue_ex_authorization(
        snapshot,
        authorized=True,
        authority_ref="EX-AUTH",
        evidence_refs=["EVD-EX"],
    )
    engine.ex_authorize(snapshot, attestation=ex)

    engine.begin_canary(snapshot)
    engine.observe_canary(
        snapshot,
        CanaryEvidence(
            success_rate=1.0,
            regression_count=0,
            observed_samples=5,
            evidence_refs=("EVD-CANARY",),
            latency_budget_pass=True,
        ),
    )

    return (
        engine,
        manager,
        snapshot,
        baseline,
        candidate,
    )


class RuntimeTransactionRecoveryTests(unittest.TestCase):

    def test_happy_activation_commits_both_participants(self):
        with tempfile.TemporaryDirectory() as td:
            (
                engine,
                manager,
                snapshot,
                _,
                candidate,
            ) = build_ready(td)

            engine.activate_manager(
                snapshot,
                manager,
                evidence=promotion_evidence(),
            )

            self.assertEqual(
                snapshot.state,
                ActivationState.ACTIVE,
            )
            self.assertEqual(
                manager.active(
                    PolicyKind.MODEL_SELECTION
                ).policy_id,
                candidate.policy_id,
            )
            self.assertEqual(
                engine.runtime_commit_journal.pending(),
                [],
            )

            rows = engine.runtime_commit_journal._events
            self.assertEqual(
                [row.state for row in rows[-3:]],
                [
                    RuntimeCommitState.PREPARED,
                    RuntimeCommitState.MANAGER_COMMITTED,
                    RuntimeCommitState.GPA_COMMITTED,
                ],
            )

    def test_recovery_completes_crash_after_manager_commit(self):
        with tempfile.TemporaryDirectory() as td:
            (
                engine,
                manager,
                snapshot,
                baseline,
                candidate,
            ) = build_ready(td)

            txn = RuntimeCommitRecord(
                contract_id=snapshot.contract_id,
                operation=RuntimeCommitOperation.ACTIVATE,
                kind=PolicyKind.MODEL_SELECTION.value,
                before_active_policy_id=baseline.policy_id,
                after_active_policy_id=candidate.policy_id,
                gpa_before_state=snapshot.state.value,
                gpa_after_state=ActivationState.ACTIVE.value,
            )
            engine.runtime_commit_journal.append(txn)

            engine.runtime_bridge.activate(
                snapshot,
                manager,
                evidence=promotion_evidence(),
            )

            restarted_manager = PersistentAdaptivePolicyManager(
                Path(td) / "adaptive_state.json"
            )
            restarted_engine = StrictGovernedPolicyActivation(
                Path(td) / "activation.jsonl"
            )

            result = (
                restarted_engine
                .recover_runtime_transactions(
                    restarted_manager
                )
            )

            self.assertEqual(
                result[-1].state,
                RuntimeCommitState.GPA_COMMITTED,
            )
            self.assertEqual(
                restarted_engine.ledger.latest(
                    snapshot.contract_id
                ).state,
                ActivationState.ACTIVE,
            )

    def test_prepared_without_manager_commit_aborts_safely(self):
        with tempfile.TemporaryDirectory() as td:
            (
                engine,
                manager,
                snapshot,
                baseline,
                candidate,
            ) = build_ready(td)

            txn = RuntimeCommitRecord(
                contract_id=snapshot.contract_id,
                operation=RuntimeCommitOperation.ACTIVATE,
                kind=PolicyKind.MODEL_SELECTION.value,
                before_active_policy_id=baseline.policy_id,
                after_active_policy_id=candidate.policy_id,
                gpa_before_state=snapshot.state.value,
                gpa_after_state=ActivationState.ACTIVE.value,
            )
            engine.runtime_commit_journal.append(txn)

            result = engine.recover_runtime_transactions(
                manager
            )

            self.assertEqual(
                result[-1].state,
                RuntimeCommitState.ABORTED,
            )
            self.assertEqual(
                manager.active(
                    PolicyKind.MODEL_SELECTION
                ).policy_id,
                baseline.policy_id,
            )

    def test_rollback_is_journaled_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            (
                engine,
                manager,
                snapshot,
                baseline,
                _,
            ) = build_ready(td)

            engine.activate_manager(
                snapshot,
                manager,
                evidence=promotion_evidence(),
            )

            ay = engine.issue_rollback_ay_ack(
                snapshot,
                acknowledged=True,
                reason="RUNTIME_DEGRADED",
                evidence_ref="EVD-DEGRADED",
            )
            ex = engine.issue_rollback_ex_authorization(
                snapshot,
                authorized=True,
                reason="RUNTIME_DEGRADED",
                evidence_ref="EVD-DEGRADED",
                authority_ref="EX-ROLLBACK",
                ay_attestation=ay,
            )

            engine.rollback_manager(
                snapshot,
                manager,
                kind=PolicyKind.MODEL_SELECTION,
                reason="RUNTIME_DEGRADED",
                evidence_ref="EVD-DEGRADED",
                ay_attestation=ay,
                ex_attestation=ex,
            )

            restarted_manager = PersistentAdaptivePolicyManager(
                Path(td) / "adaptive_state.json"
            )
            restarted_engine = StrictGovernedPolicyActivation(
                Path(td) / "activation.jsonl"
            )

            self.assertEqual(
                restarted_manager.active(
                    PolicyKind.MODEL_SELECTION
                ).policy_id,
                baseline.policy_id,
            )
            self.assertEqual(
                restarted_engine.ledger.latest(
                    snapshot.contract_id
                ).state,
                ActivationState.ROLLED_BACK,
            )
            self.assertEqual(
                restarted_engine.runtime_commit_journal.pending(),
                [],
            )

    def test_recovery_completes_rollback_after_manager_commit(self):
        with tempfile.TemporaryDirectory() as td:
            (
                engine,
                manager,
                snapshot,
                baseline,
                candidate,
            ) = build_ready(td)

            engine.activate_manager(
                snapshot,
                manager,
                evidence=promotion_evidence(),
            )

            ay = engine.issue_rollback_ay_ack(
                snapshot,
                acknowledged=True,
                reason="RUNTIME_DEGRADED",
                evidence_ref="EVD-DEGRADED",
            )
            ex = engine.issue_rollback_ex_authorization(
                snapshot,
                authorized=True,
                reason="RUNTIME_DEGRADED",
                evidence_ref="EVD-DEGRADED",
                authority_ref="EX-ROLLBACK",
                ay_attestation=ay,
            )

            txn = RuntimeCommitRecord(
                contract_id=snapshot.contract_id,
                operation=RuntimeCommitOperation.ROLLBACK,
                kind=PolicyKind.MODEL_SELECTION.value,
                before_active_policy_id=candidate.policy_id,
                after_active_policy_id=baseline.policy_id,
                gpa_before_state=ActivationState.ACTIVE.value,
                gpa_after_state=ActivationState.ROLLED_BACK.value,
                reason="RUNTIME_DEGRADED",
                evidence_ref="EVD-DEGRADED",
                governance={
                    "ay_attestation": ay.to_dict(),
                    "ex_attestation": ex.to_dict(),
                },
            )
            engine.runtime_commit_journal.append(txn)

            engine.runtime_bridge.rollback(
                snapshot,
                manager,
                kind=PolicyKind.MODEL_SELECTION,
                ex_authorized=True,
                ay_acknowledged=True,
                reason="RUNTIME_DEGRADED",
            )

            restarted_manager = PersistentAdaptivePolicyManager(
                Path(td) / "adaptive_state.json"
            )
            restarted_engine = StrictGovernedPolicyActivation(
                Path(td) / "activation.jsonl"
            )

            result = (
                restarted_engine
                .recover_runtime_transactions(
                    restarted_manager
                )
            )

            self.assertEqual(
                result[-1].state,
                RuntimeCommitState.GPA_COMMITTED,
            )
            self.assertEqual(
                restarted_manager.active(
                    PolicyKind.MODEL_SELECTION
                ).policy_id,
                baseline.policy_id,
            )
            self.assertEqual(
                restarted_engine.ledger.latest(
                    snapshot.contract_id
                ).state,
                ActivationState.ROLLED_BACK,
            )

    def test_strict_runtime_commit_rejects_ephemeral_manager(self):
        from maestro.adaptive import AdaptivePolicyManager

        with tempfile.TemporaryDirectory() as td:
            (
                engine,
                _,
                snapshot,
                _,
                _,
            ) = build_ready(td)

            with self.assertRaises(PermissionError):
                engine.activate_manager(
                    snapshot,
                    AdaptivePolicyManager(),
                    evidence=promotion_evidence(),
                )


if __name__ == "__main__":
    unittest.main()
