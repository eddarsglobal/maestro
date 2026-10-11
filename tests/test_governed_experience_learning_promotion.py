from __future__ import annotations

import ast
import unittest

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

from maestro.learning.governed_experience_learning_promotion import (
    EvidenceState,
    ExperienceCaptureIncompleteError,
    ExperienceLearningPromotionInvariantError,
    ExperienceOutcome,
    GovernedExperienceLearningPromotion,
    LearningCandidateIncompleteError,
    LearningCandidateKind,
    PromotionDecisionState,
    PromotionEvaluationEvidence,
    PromotionPolicy,
    ResourcePerformanceEvidence,
)
from maestro.orchestration.governed_adaptive_mission_closure import (
    ClosureEvidenceState,
    CouncilMissionVerdictEvidence,
    GovernedAdaptiveMissionClosure,
    MissionVerdictEvidence,
    NodeExecutionClosureEvidence,
)
from maestro.orchestration.governed_durable_mission_recovery import (
    DurableCouncilState,
    DurableRecoveryInformation,
    DurableRetryRecord,
    GovernedDurableMission,
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
    "src/maestro/learning/"
    "governed_experience_learning_promotion.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_EXPERIENCE_LEARNING_PROMOTION_CONSTITUTION.md"
)


def durable_fixture(
    suffix="A",
):
    contract = MissionContract(
        objective=(
            "Learn only from verified "
            f"experience {suffix}"
        ),
        scope="Learning governance",
        requested_output="Verified result",
        constraints=(
            "No direct production mutation",
        ),
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
        node_id=f"NODE-{suffix}",
        capability_id="CAPABILITY-1",
        council_id="IT",
        resource_id=f"RESOURCE-{suffix}",
        dependency_node_ids=(),
        acceptance_evidence=(
            "NODE-EVIDENCE",
        ),
        retry_policy=RetryPolicy(
            2,
            "bounded",
        ),
        effects=EffectBudgetDeclaration(
            effects=("LOCAL_COMPUTE",),
            permissions=("LOCAL_COMPUTE",),
            max_tool_calls=2,
            max_cost_units=20,
            max_latency_ms=500,
            sandbox_required=True,
        ),
        recovery=RecoveryBoundary(
            "RECOVERY",
            f"checkpoint://{suffix}",
        ),
    )

    plan = GovernedMissionPlan(
        mission_contract_id=(
            contract.contract_id
        ),
        council_graph_id=(
            f"MCG-{suffix}"
        ),
        capability_graph_id=(
            f"MCAP-{suffix}"
        ),
        resource_selection_id=(
            f"GRS-{suffix}"
        ),
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
        idempotency_key=(
            f"EXE-{suffix}"
        ),
    )

    routing = GovernedExecutionRoutingPlan(
        plan_id=plan.plan_id,
        validation_id=f"GPV-{suffix}",
        authorization_evidence_id=(
            f"EAE-{suffix}"
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
                worker_id=(
                    f"WORKER-{suffix}"
                ),
                worker_node_id=(
                    f"FABRIC-{suffix}"
                ),
                locality=(
                    WorkerLocality.LOCAL
                ),
                worker_evidence_id=(
                    f"DWE-{suffix}"
                ),
            ),
        ),
    )

    execution = NodeExecutionClosureEvidence(
        plan_id=plan.plan_id,
        routing_plan_id=(
            routing.routing_plan_id
        ),
        route_id=route.route_id,
        node_id=node.node_id,
        idempotency_key=(
            route.idempotency_key
        ),
        execution_state=(
            ClosureEvidenceState.PASS
        ),
        output_ref=(
            f"object://result-{suffix}"
        ),
        provenance_refs=(
            f"provenance://{suffix}",
        ),
        execution_evidence_refs=(
            f"execution://{suffix}",
        ),
        council_verdict_state=(
            ClosureEvidenceState.PASS
        ),
        council_verdict_ref=(
            f"verdict://it/{suffix}"
        ),
        acceptance_evidence_keys=(
            "NODE-EVIDENCE",
        ),
        evidence_source_ref=(
            f"test://execution/{suffix}"
        ),
    )

    closure = (
        GovernedAdaptiveMissionClosure
        .close_node(
            plan,
            routing,
            execution,
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
                ClosureEvidenceState.PASS,
                f"verdict://it/{suffix}",
            ),
        ),
        ay_system_verdict_state=(
            ClosureEvidenceState.PASS
        ),
        ay_system_verdict_ref=(
            f"verdict://ay/{suffix}"
        ),
        evidence_source_ref=(
            f"test://verdict/{suffix}"
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
            "task_id": (
                f"MISSION-{suffix}"
            ),
            "objective": (
                contract.objective
            ),
            "state": "EXECUTING",
        },
        contract=contract,
        plan=plan,
        routing=routing,
        node_execution_evidence=(
            execution,
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
                max_attempts=2,
                last_failure_ref=(
                    f"failure://prior/{suffix}"
                ),
            ),
        ),
        councils=(
            DurableCouncilState(
                council_id="IT",
                runtime_state="READY",
                state_ref=(
                    f"council://it/{suffix}"
                ),
                evidence_refs=(
                    f"evidence://it/{suffix}",
                ),
            ),
        ),
        recovery=DurableRecoveryInformation(
            last_stable_checkpoint_ref=(
                f"checkpoint://stable/{suffix}"
            ),
            last_stable_generation=1,
            rollback_checkpoint_ref=(
                f"checkpoint://rollback/{suffix}"
            ),
            recovery_checkpoint_ref=(
                f"checkpoint://recovery/{suffix}"
            ),
            recovery_evidence_refs=(
                f"recovery://{suffix}",
            ),
        ),
        runtime_checkpoint_schema=(
            "maestro.checkpoint.v0.2"
        ),
        runtime_checkpoint_sha256=(
            "a" * 64
        ),
        generation=1,
    )

    return (
        contract,
        plan,
        routing,
        verdict,
        checkpoint,
    )


def performance(
    suffix="A",
):
    return ResourcePerformanceEvidence(
        resource_id=f"RESOURCE-{suffix}",
        capability_id="CAPABILITY-1",
        success_state=EvidenceState.PASS,
        quality_score=0.95,
        reliability_score=0.97,
        cost_units=12,
        latency_ms=180,
        evidence_refs=(
            f"resource://evidence/{suffix}",
        ),
    )


def experience(
    suffix="A",
    *,
    corrections=(),
):
    (
        _,
        _,
        _,
        verdict,
        checkpoint,
    ) = durable_fixture(
        suffix
    )

    return (
        GovernedExperienceLearningPromotion
        .capture(
            checkpoint,
            verdict,
            outcome=ExperienceOutcome.SUCCESS,
            verified_result_ref=(
                f"verified://result/{suffix}"
            ),
            failure_refs=(),
            retry_evidence_refs=(
                f"retry://{suffix}",
            ),
            routing_quality_score=0.94,
            resource_performance=(
                performance(suffix),
            ),
            human_correction_refs=(
                corrections
            ),
            evidence_refs=(
                f"experience://evidence/{suffix}",
            ),
            cost_units=12,
            latency_ms=180,
        )
    )


def candidate():
    a = experience("A")
    b = experience(
        "B",
        corrections=(
            "human://correction/B",
        ),
    )

    value = (
        GovernedExperienceLearningPromotion
        .propose_learning(
            (
                a,
                b,
            ),
            kind=(
                LearningCandidateKind
                .ROUTING_POLICY
            ),
            key="routing:CAPABILITY-1",
            statement=(
                "Prefer evidence-backed "
                "resource routing."
            ),
        )
    )

    return (
        a,
        b,
        value,
    )


def promotion_evidence(
    learning_candidate,
    *,
    ay=EvidenceState.PASS,
    ex=EvidenceState.PASS,
    baseline=0.70,
    candidate_score=0.90,
    replay=0.92,
    shadow=0.95,
    regressions=0,
    samples=20,
):
    return PromotionEvaluationEvidence(
        candidate_id=(
            learning_candidate.candidate_id
        ),
        samples=samples,
        baseline_score=baseline,
        candidate_score=candidate_score,
        replay_score=replay,
        shadow_success_rate=shadow,
        regression_count=regressions,
        comparison_ref=(
            "comparison://baseline-vs-candidate"
        ),
        rollback_ref=(
            "rollback://policy-v1"
        ),
        ay_validation=ay,
        ex_authorization=ex,
        evidence_refs=(
            "evaluation://replay",
            "evaluation://shadow",
        ),
    )


def promotion_policy():
    return PromotionPolicy(
        min_support=2,
        min_samples=10,
        min_replay_score=0.80,
        min_shadow_success_rate=0.90,
        min_improvement=0.05,
        max_regressions=0,
    )


class GovernedExperienceLearningPromotionTests(
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
                f"ELP-{number:02d}",
                text,
            )

        for invariant in (
            "OBSERVATION != VERIFIED EXPERIENCE",
            "EXPERIENCE != LEARNING AUTHORITY",
            "EXPERIENCE != POLICY",
            "LEARNING CANDIDATE != PRODUCTION BEHAVIOR",
            "LEARN != PROMOTE",
            "PROPOSE != APPROVE",
            "EVALUATED != PROMOTED",
            "PROMOTION READY != ACTIVATED",
            "PROMOTION_ELIGIBLE != PROMOTED",
            "PROMOTED != ACTIVATED",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_experience_capture_is_deterministic_immutable_and_complete(self):
        a = experience(
            "A",
            corrections=(
                "human://correction/A",
            ),
        )

        b = experience(
            "A",
            corrections=(
                "human://correction/A",
            ),
        )

        self.assertEqual(
            a.experience_id,
            b.experience_id,
        )

        self.assertEqual(
            a.experience_sha256,
            b.experience_sha256,
        )

        self.assertEqual(
            a.human_correction_refs,
            (
                "human://correction/A",
            ),
        )

        self.assertEqual(
            a.retry_evidence_refs,
            (
                "retry://A",
            ),
        )

        self.assertTrue(
            a.resource_performance
        )

        with self.assertRaises(
            FrozenInstanceError
        ):
            a.cost_units = 999

    def test_03_capture_requires_durable_verified_verdict_and_success_result(self):
        (
            _,
            _,
            _,
            verdict,
            checkpoint,
        ) = durable_fixture("A")

        with self.assertRaises(
            ExperienceCaptureIncompleteError
        ):
            GovernedExperienceLearningPromotion.capture(
                checkpoint,
                verdict,
                outcome=ExperienceOutcome.SUCCESS,
                verified_result_ref=None,
                failure_refs=(),
                retry_evidence_refs=(),
                routing_quality_score=0.9,
                resource_performance=(
                    performance("A"),
                ),
                human_correction_refs=(),
                evidence_refs=(
                    "evidence://x",
                ),
                cost_units=1,
                latency_ms=1,
            )

        wrong = replace(
            verdict,
            plan_id="GMP-WRONG",
        )

        with self.assertRaises(
            ExperienceLearningPromotionInvariantError
        ):
            GovernedExperienceLearningPromotion.capture(
                checkpoint,
                wrong,
                outcome=ExperienceOutcome.SUCCESS,
                verified_result_ref=(
                    "verified://x"
                ),
                failure_refs=(),
                retry_evidence_refs=(),
                routing_quality_score=0.9,
                resource_performance=(
                    performance("A"),
                ),
                human_correction_refs=(),
                evidence_refs=(
                    "evidence://x",
                ),
                cost_units=1,
                latency_ms=1,
            )

    def test_04_experience_never_grants_learning_or_mutation_authority(self):
        value = experience("A")

        for field_name in (
            "learning_authorized",
            "policy_mutation_authorized",
            "memory_authority_granted",
            "routing_authority_granted",
            "council_authority_granted",
            "core_mutation_authorized",
            "promotion_authorized",
        ):
            self.assertFalse(
                getattr(
                    value,
                    field_name,
                )
            )

            with self.assertRaises(
                ExperienceLearningPromotionInvariantError
            ):
                replace(
                    value,
                    **{
                        field_name: True
                    },
                )

    def test_05_learning_candidate_requires_multiple_distinct_immutable_experiences(self):
        a = experience("A")

        with self.assertRaises(
            LearningCandidateIncompleteError
        ):
            GovernedExperienceLearningPromotion.propose_learning(
                (a,),
                kind=(
                    LearningCandidateKind
                    .ROUTING_POLICY
                ),
                key="routing:test",
                statement="Test candidate.",
            )

        with self.assertRaises(
            LearningCandidateIncompleteError
        ):
            GovernedExperienceLearningPromotion.propose_learning(
                (
                    a,
                    a,
                ),
                kind=(
                    LearningCandidateKind
                    .ROUTING_POLICY
                ),
                key="routing:test",
                statement="Test candidate.",
            )

        _, _, value = candidate()

        self.assertEqual(
            len(
                value
                .support_experience_ids
            ),
            2,
        )

    def test_06_learning_candidate_cannot_mutate_policy_memory_routing_council_or_core(self):
        _, _, value = candidate()

        for field_name in (
            "policy_mutation_authorized",
            "memory_authority_granted",
            "routing_authority_granted",
            "council_authority_granted",
            "core_mutation_authorized",
            "production_behavior_changed",
            "promotion_authorized",
        ):
            self.assertFalse(
                getattr(
                    value,
                    field_name,
                )
            )

            with self.assertRaises(
                ExperienceLearningPromotionInvariantError
            ):
                replace(
                    value,
                    **{
                        field_name: True
                    },
                )

    def test_07_promotion_requires_comparison_rollback_support_and_ay_ex(self):
        _, _, value = candidate()

        decision = (
            GovernedExperienceLearningPromotion
            .evaluate_promotion(
                value,
                promotion_evidence(
                    value
                ),
                promotion_policy(),
            )
        )

        self.assertIs(
            decision.state,
            PromotionDecisionState
            .PROMOTION_ELIGIBLE,
        )

        self.assertTrue(
            decision.promotion_eligible
        )

        self.assertEqual(
            decision.comparison_ref,
            "comparison://baseline-vs-candidate",
        )

        self.assertEqual(
            decision.rollback_ref,
            "rollback://policy-v1",
        )

    def test_08_unknown_or_failed_ay_ex_and_bad_evaluation_fail_closed(self):
        _, _, value = candidate()

        unknown = (
            GovernedExperienceLearningPromotion
            .evaluate_promotion(
                value,
                promotion_evidence(
                    value,
                    ay=EvidenceState.UNKNOWN,
                ),
                promotion_policy(),
            )
        )

        self.assertIs(
            unknown.state,
            PromotionDecisionState.UNKNOWN,
        )

        failed = (
            GovernedExperienceLearningPromotion
            .evaluate_promotion(
                value,
                promotion_evidence(
                    value,
                    ex=EvidenceState.FAIL,
                ),
                promotion_policy(),
            )
        )

        self.assertIs(
            failed.state,
            PromotionDecisionState.REJECTED,
        )

        regression = (
            GovernedExperienceLearningPromotion
            .evaluate_promotion(
                value,
                promotion_evidence(
                    value,
                    regressions=1,
                ),
                promotion_policy(),
            )
        )

        self.assertIs(
            regression.state,
            PromotionDecisionState.REJECTED,
        )

        no_gain = (
            GovernedExperienceLearningPromotion
            .evaluate_promotion(
                value,
                promotion_evidence(
                    value,
                    baseline=0.90,
                    candidate_score=0.91,
                ),
                promotion_policy(),
            )
        )

        self.assertIs(
            no_gain.state,
            PromotionDecisionState.REJECTED,
        )

    def test_09_promotion_eligibility_never_activates_or_mutates_production(self):
        _, _, value = candidate()

        decision = (
            GovernedExperienceLearningPromotion
            .evaluate_promotion(
                value,
                promotion_evidence(
                    value
                ),
                promotion_policy(),
            )
        )

        for field_name in (
            "policy_mutation_authorized",
            "memory_mutation_authorized",
            "routing_mutation_authorized",
            "council_mutation_authorized",
            "core_mutation_authorized",
            "production_activation_authorized",
            "execution_authorized",
            "system_truth_asserted",
        ):
            self.assertFalse(
                getattr(
                    decision,
                    field_name,
                )
            )

            with self.assertRaises(
                ExperienceLearningPromotionInvariantError
            ):
                replace(
                    decision,
                    **{
                        field_name: True
                    },
                )

    def test_10_module_is_passive_and_existing_learning_activation_remains_downstream(self):
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
            "maestro.learning.promotion",
            "maestro.learning.experience_store",
            "maestro.adaptive",
            "maestro.governed_activation",
            "maestro.runtime.kernel",
            "maestro.state_machine",
            "subprocess",
            "socket",
            "requests",
            "sqlite3",
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
            "promote",
            "activate",
            "execute",
            "apply",
            "commit",
            "record",
            "store",
            "learn",
            "mutate",
            "write_text",
            "write_bytes",
        }

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )


if __name__ == "__main__":
    unittest.main()
