from __future__ import annotations

import ast
import json
import tempfile
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.governance.governed_failure_containment_recovery import (
    EvidenceState as RE,
    FailureState,
    RecoveryAssessmentState,
    RecoveryPlanAction,
)
from maestro.orchestration.governed_adaptive_mission_closure import (
    AdaptiveRoutingState,
    ClosureEvidenceState as CE,
    CouncilMissionVerdictEvidence,
    GovernedAdaptiveMissionClosure,
    MissionVerdictEvidence,
    NodeExecutionClosureEvidence,
)
from maestro.orchestration.governed_durable_mission_recovery import (
    DURABLE_MISSION_SCHEMA,
    DurableCouncilState,
    DurableMissionIntegrityError,
    DurableMissionRecoveryInvariantError,
    DurableMissionSchemaError,
    DurableRecoveryInformation,
    DurableRetryRecord,
    GovernedAutonomousMissionRecovery,
    GovernedDurableMission,
    GovernedDurableMissionCheckpoint,
    GovernedDurableMissionStore,
    MissionRecoveryEvidence,
    RecoveryDecisionState,
)
from maestro.orchestration.governed_execution_routing import (
    ExecutionRoute,
    ExecutionWave,
    GovernedExecutionRoutingPlan,
    WorkerLocality,
    WorkerPlacement,
)
from maestro.orchestration.governed_mission_foundation import (
    MissionContract,
)
from maestro.orchestration.governed_mission_plan import (
    EffectBudgetDeclaration,
    GovernedMissionPlan,
    MissionPlanNode,
    RecoveryBoundary,
    RetryPolicy,
)


SOURCE = Path(
    "src/maestro/orchestration/"
    "governed_durable_mission_recovery.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_DURABLE_MISSION_RECOVERY_CONSTITUTION.md"
)


def fixture():
    contract = MissionContract(
        objective="Recover durable mission",
        scope="Durability and recovery",
        requested_output="Recovered result",
        constraints=("Preserve semantics",),
        acceptance_criteria=(
            "MISSION ACCEPTED",
        ),
        authority_requirements=(
            "AY acceptance",
            "EX routing",
        ),
        evidence_obligations=(
            "NODE-EVIDENCE",
        ),
    )

    node = MissionPlanNode(
        node_id="NODE-1",
        capability_id="CAPABILITY-1",
        council_id="IT",
        resource_id="RESOURCE-1",
        dependency_node_ids=(),
        acceptance_evidence=(
            "NODE-EVIDENCE",
        ),
        retry_policy=RetryPolicy(
            3,
            "bounded-linear",
        ),
        effects=EffectBudgetDeclaration(
            effects=("LOCAL_COMPUTE",),
            permissions=("LOCAL_COMPUTE",),
            max_tool_calls=3,
            max_cost_units=20,
            max_latency_ms=500,
            sandbox_required=True,
        ),
        recovery=RecoveryBoundary(
            "RECOVERY",
            "checkpoint://node-1",
        ),
    )

    plan = GovernedMissionPlan(
        mission_contract_id=(
            contract.contract_id
        ),
        council_graph_id="MCG-DMR",
        capability_graph_id="MCAP-DMR",
        resource_selection_id="GRS-DMR",
        mission_acceptance_criteria=(
            contract.acceptance_criteria
        ),
        nodes=(node,),
    )

    route = ExecutionRoute(
        node_id=node.node_id,
        capability_id=node.capability_id,
        council_id=node.council_id,
        resource_id=node.resource_id,
        idempotency_key="EXE-DMR-NODE-1",
    )

    routing = GovernedExecutionRoutingPlan(
        plan_id=plan.plan_id,
        validation_id="GPV-DMR",
        authorization_evidence_id=(
            "EAE-DMR"
        ),
        routes=(route,),
        waves=(
            ExecutionWave(
                1,
                (route.route_id,),
                (node.node_id,),
            ),
        ),
        placements=(
            WorkerPlacement(
                route_id=route.route_id,
                node_id=node.node_id,
                worker_id="WORKER-1",
                worker_node_id="FABRIC-1",
                locality=WorkerLocality.LOCAL,
                worker_evidence_id="DWE-DMR",
            ),
        ),
    )

    execution_evidence = (
        NodeExecutionClosureEvidence(
            plan_id=plan.plan_id,
            routing_plan_id=(
                routing.routing_plan_id
            ),
            route_id=route.route_id,
            node_id=node.node_id,
            idempotency_key=(
                route.idempotency_key
            ),
            execution_state=CE.PASS,
            output_ref="object://result",
            provenance_refs=(
                "provenance://resource",
            ),
            execution_evidence_refs=(
                "execution://trace",
            ),
            council_verdict_state=CE.PASS,
            council_verdict_ref=(
                "verdict://it"
            ),
            acceptance_evidence_keys=(
                "NODE-EVIDENCE",
            ),
            evidence_source_ref=(
                "test://node-evidence"
            ),
        )
    )

    closure = (
        GovernedAdaptiveMissionClosure
        .close_node(
            plan,
            routing,
            execution_evidence,
        )
    )

    verdict_evidence = MissionVerdictEvidence(
        plan_id=plan.plan_id,
        node_closures=(closure,),
        acceptance_criteria_validated=(
            "MISSION ACCEPTED",
        ),
        council_verdicts=(
            CouncilMissionVerdictEvidence(
                "IT",
                CE.PASS,
                "verdict://it",
            ),
        ),
        ay_system_verdict_state=CE.PASS,
        ay_system_verdict_ref=(
            "verdict://ay/system"
        ),
        evidence_source_ref=(
            "test://mission-verdict"
        ),
    )

    verdict = (
        GovernedAdaptiveMissionClosure
        .verdict(
            plan,
            verdict_evidence,
        )
    )

    checkpoint = GovernedDurableMission.checkpoint(
        canonical_mission={
            "task_id": "MISSION-DMR",
            "objective": (
                contract.objective
            ),
            "state": "EXECUTING",
            "metadata": {
                "owner": "MAESTRO",
            },
        },
        contract=contract,
        plan=plan,
        routing=routing,
        node_execution_evidence=(
            execution_evidence,
        ),
        node_closures=(closure,),
        mission_verdict_evidence=(
            verdict_evidence
        ),
        mission_verdict=verdict,
        retries=(
            DurableRetryRecord(
                node_id=node.node_id,
                attempts_used=1,
                max_attempts=3,
                last_failure_ref=(
                    "failure://prior"
                ),
            ),
        ),
        councils=(
            DurableCouncilState(
                council_id="IT",
                runtime_state="READY",
                state_ref="council://it/state",
                evidence_refs=(
                    "evidence://it",
                ),
            ),
        ),
        recovery=DurableRecoveryInformation(
            last_stable_checkpoint_ref=(
                "checkpoint://stable/7"
            ),
            last_stable_generation=7,
            rollback_checkpoint_ref=(
                "checkpoint://rollback/6"
            ),
            recovery_checkpoint_ref=(
                "checkpoint://recovery/7"
            ),
            recovery_evidence_refs=(
                "recovery://evidence",
            ),
        ),
        runtime_checkpoint_schema=(
            "maestro.checkpoint.v0.2"
        ),
        runtime_checkpoint_sha256=(
            "a" * 64
        ),
        generation=7,
    )

    return (
        contract,
        plan,
        routing,
        execution_evidence,
        closure,
        verdict_evidence,
        verdict,
        checkpoint,
    )


def recovery_evidence(
    checkpoint,
    *,
    integrity=RE.PASS,
    failure=FailureState.DETECTED,
    fcr_state=(
        RecoveryAssessmentState
        .RECOVERY_REQUIRED
    ),
    action=RecoveryPlanAction.RECOVERY,
    adaptive=AdaptiveRoutingState.NO_CHANGE,
    adaptive_decision_id=None,
    target_generation=None,
):
    return MissionRecoveryEvidence(
        checkpoint_id=(
            checkpoint.checkpoint_id
        ),
        checkpoint_payload_sha256=(
            checkpoint.payload_sha256
        ),
        objective_fingerprint=(
            checkpoint.objective_fingerprint
        ),
        checkpoint_integrity=integrity,
        failure_state=failure,
        fcr_assessment_state=fcr_state,
        fcr_action=action,
        fcr_plan_id=(
            "FCR-PLAN"
            if action is not None
            else None
        ),
        adaptive_state=adaptive,
        adaptive_decision_id=(
            adaptive_decision_id
        ),
        target_generation=(
            checkpoint.generation
            if target_generation is None
            else target_generation
        ),
        evidence_source_ref=(
            "test://recovery"
        ),
    )


class GovernedDurableMissionRecoveryTests(
    unittest.TestCase
):
    def test_01_constitution_contains_laws_and_separations(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(
            1,
            11,
        ):
            self.assertIn(
                f"DMR-{number:02d}",
                text,
            )

        for invariant in (
            "MISSION SNAPSHOT != COMPLETE DURABLE MISSION",
            "CHECKPOINT PRESENT != CHECKPOINT INTACT",
            "RESUME != OBJECTIVE CHANGE",
            "CHECKPOINTED != AUTHORIZED",
            "FCR PLAN != RECOVERY EXECUTION",
            "AUTONOMOUS DECISION != AUTONOMOUS EXECUTION",
            "REPLAN PROPOSED != REPLAN EXECUTED",
            "RESTORED STATE != AY APPROVAL",
            "RESTORED STATE != EX AUTHORIZATION",
            "RECOVERY READY != RECOVERY EXECUTED",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_checkpoint_contains_complete_phase2_surface(self):
        *_, checkpoint = fixture()

        payload = checkpoint.payload

        self.assertEqual(
            set(payload),
            {
                "schema",
                "generation",
                "runtime_checkpoint",
                "mission",
                "mission_contract",
                "mission_plan",
                "dag_state",
                "routing",
                "node_execution_evidence",
                "node_closures",
                "mission_verdict_evidence",
                "mission_verdict",
                "retry_state",
                "council_state",
                "recovery_information",
            },
        )

        self.assertTrue(
            payload["mission_plan"]["nodes"]
        )

        self.assertTrue(
            payload["routing"]["routes"]
        )

        self.assertEqual(
            payload[
                "node_execution_evidence"
            ][0]["idempotency_key"],
            "EXE-DMR-NODE-1",
        )

        self.assertEqual(
            payload[
                "node_execution_evidence"
            ][0]["provenance_refs"],
            [
                "provenance://resource"
            ],
        )

    def test_03_save_load_roundtrip_preserves_exact_semantics(self):
        *_, checkpoint = fixture()

        with tempfile.TemporaryDirectory() as tmp:
            path = (
                Path(tmp)
                / "mission.dmr.json"
            )

            GovernedDurableMissionStore.save(
                checkpoint,
                path,
            )

            restored = (
                GovernedDurableMissionStore
                .load(path)
            )

        self.assertEqual(
            restored.checkpoint_id,
            checkpoint.checkpoint_id,
        )

        self.assertEqual(
            restored.payload_sha256,
            checkpoint.payload_sha256,
        )

        self.assertEqual(
            restored.payload_json,
            checkpoint.payload_json,
        )

        self.assertEqual(
            restored.objective_fingerprint,
            checkpoint.objective_fingerprint,
        )

        self.assertEqual(
            restored.plan_id,
            checkpoint.plan_id,
        )

        self.assertEqual(
            restored.routing_plan_id,
            checkpoint.routing_plan_id,
        )

    def test_04_payload_or_envelope_tampering_fails_closed(self):
        *_, checkpoint = fixture()

        envelope = (
            checkpoint.to_envelope()
        )

        tampered = json.loads(
            json.dumps(envelope)
        )

        tampered["body"]["payload"][
            "mission"
        ]["objective"] = "CHANGED"

        with self.assertRaises(
            DurableMissionIntegrityError
        ):
            GovernedDurableMissionCheckpoint.from_envelope(
                tampered
            )

        tampered = json.loads(
            json.dumps(envelope)
        )

        tampered["sha256"] = "0" * 64

        with self.assertRaises(
            DurableMissionIntegrityError
        ):
            GovernedDurableMissionCheckpoint.from_envelope(
                tampered
            )

    def test_05_unknown_schema_and_lineage_drift_fail_closed(self):
        *_, checkpoint = fixture()

        with self.assertRaises(
            DurableMissionSchemaError
        ):
            replace(
                checkpoint,
                schema=(
                    "maestro.phase2."
                    "durable-mission.v999"
                ),
            )

        with self.assertRaises(
            DurableMissionIntegrityError
        ):
            replace(
                checkpoint,
                plan_id="GMP-WRONG",
            )

    def test_06_checkpoint_is_authority_neutral(self):
        *_, checkpoint = fixture()

        for field_name in (
            "durable_commit_authorized",
            "mission_state_transition_requested",
            "execution_authorized",
            "learning_authorized",
            "system_truth_asserted",
        ):
            self.assertFalse(
                getattr(
                    checkpoint,
                    field_name,
                )
            )

            with self.assertRaises(
                DurableMissionRecoveryInvariantError
            ):
                replace(
                    checkpoint,
                    **{
                        field_name: True
                    },
                )

    def test_07_fcr_recovery_states_compose_to_passive_proposals(self):
        *_, checkpoint = fixture()

        cases = (
            (
                RecoveryAssessmentState
                .CONTAINMENT_REQUIRED,
                RecoveryPlanAction
                .CONTAINMENT,
                RecoveryDecisionState
                .CONTAINMENT_PROPOSED,
            ),
            (
                RecoveryAssessmentState
                .ROLLBACK_REQUIRED,
                RecoveryPlanAction.ROLLBACK,
                RecoveryDecisionState
                .ROLLBACK_PROPOSED,
            ),
            (
                RecoveryAssessmentState
                .RECOVERY_REQUIRED,
                RecoveryPlanAction.RECOVERY,
                RecoveryDecisionState
                .RESUME_PROPOSED,
            ),
        )

        for (
            fcr_state,
            action,
            expected,
        ) in cases:
            with self.subTest(
                state=fcr_state.value
            ):
                result = (
                    GovernedAutonomousMissionRecovery
                    .compose(
                        checkpoint,
                        recovery_evidence(
                            checkpoint,
                            fcr_state=fcr_state,
                            action=action,
                        ),
                    )
                )

                self.assertIs(
                    result.state,
                    expected,
                )

                self.assertFalse(
                    result.recovery_executed
                )

                self.assertFalse(
                    result.rollback_executed
                )

    def test_08_unknown_corrupt_and_unrecoverable_fail_closed(self):
        *_, checkpoint = fixture()

        unknown = (
            GovernedAutonomousMissionRecovery
            .compose(
                checkpoint,
                recovery_evidence(
                    checkpoint,
                    integrity=RE.UNKNOWN,
                ),
            )
        )

        self.assertIs(
            unknown.state,
            RecoveryDecisionState.UNKNOWN,
        )

        corrupt = (
            GovernedAutonomousMissionRecovery
            .compose(
                checkpoint,
                recovery_evidence(
                    checkpoint,
                    integrity=RE.FAIL,
                ),
            )
        )

        self.assertIs(
            corrupt.state,
            RecoveryDecisionState.UNRECOVERABLE,
        )

        unrecoverable = (
            GovernedAutonomousMissionRecovery
            .compose(
                checkpoint,
                recovery_evidence(
                    checkpoint,
                    fcr_state=(
                        RecoveryAssessmentState
                        .UNRECOVERABLE
                    ),
                    action=None,
                ),
            )
        )

        self.assertIs(
            unrecoverable.state,
            RecoveryDecisionState.UNRECOVERABLE,
        )

    def test_09_replan_preserves_objective_and_requires_ay_ex(self):
        *_, checkpoint = fixture()

        result = (
            GovernedAutonomousMissionRecovery
            .compose(
                checkpoint,
                recovery_evidence(
                    checkpoint,
                    fcr_state=(
                        RecoveryAssessmentState
                        .RECOVERY_REQUIRED
                    ),
                    action=(
                        RecoveryPlanAction
                        .RECOVERY
                    ),
                    adaptive=(
                        AdaptiveRoutingState
                        .REPLAN_REQUIRED
                    ),
                    adaptive_decision_id=(
                        "ARD-REPLAN"
                    ),
                ),
            )
        )

        self.assertIs(
            result.state,
            RecoveryDecisionState
            .REPLAN_PROPOSED,
        )

        self.assertEqual(
            result.objective_fingerprint,
            checkpoint.objective_fingerprint,
        )

        self.assertTrue(
            result.ay_revalidation_required
        )

        self.assertTrue(
            result.ex_reauthorization_required
        )

        for field_name in (
            "replanning_executed",
            "mission_state_transition_requested",
            "execution_authorized",
            "effect_authorized",
            "durable_commit_authorized",
            "learning_authorized",
            "system_truth_asserted",
        ):
            self.assertFalse(
                getattr(
                    result,
                    field_name,
                )
            )

            with self.assertRaises(
                DurableMissionRecoveryInvariantError
            ):
                replace(
                    result,
                    **{
                        field_name: True
                    },
                )

    def test_10_module_does_not_import_or_call_downstream_execution_authority(self):
        tree = ast.parse(
            SOURCE.read_text(
                encoding="utf-8"
            )
        )

        imports = set()
        calls = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Import,
            ):
                imports.update(
                    alias.name
                    for alias in node.names
                )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):
                if node.module:
                    imports.add(
                        node.module
                    )

            elif isinstance(
                node,
                ast.Call,
            ):
                if isinstance(
                    node.func,
                    ast.Name,
                ):
                    calls.add(
                        node.func.id
                    )

                elif isinstance(
                    node.func,
                    ast.Attribute,
                ):
                    calls.add(
                        node.func.attr
                    )

        forbidden_import_roots = (
            "maestro.runtime.kernel",
            "maestro.state_machine",
            "maestro.fabric.queue",
            "maestro.autonomous.executor",
            "maestro.learning",
            "subprocess",
            "socket",
            "requests",
        )

        bad_imports = {
            name
            for name in imports
            if any(
                name == root
                or name.startswith(
                    root + "."
                )
                for root
                in forbidden_import_roots
            )
        }

        self.assertEqual(
            bad_imports,
            set(),
        )

        forbidden_calls = {
            "execute",
            "close",
            "transition",
            "move",
            "start_node",
            "dispatch",
            "lease",
            "commit_durable_state",
            "authorize_durable_commit",
            "promote",
            "learn",
        }

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )


if __name__ == "__main__":
    unittest.main()
