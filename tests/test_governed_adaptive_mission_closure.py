from __future__ import annotations

import ast
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.intelligence_market.governed_capability_resource_market import (
    GovernedCapabilityResourceMarket,
    IntelligenceResourceCandidate,
    ResourceEvidenceState,
    ResourceLocality,
    ResourceSelectionPolicy,
)
from maestro.orchestration.governed_adaptive_mission_closure import (
    AdaptiveMissionClosureInvariantError,
    AdaptiveRoutingState,
    ClosureEvidenceState as E,
    CouncilMissionVerdictEvidence,
    GovernedAdaptiveMissionClosure,
    MissionVerdictEvidence,
    MissionVerdictState,
    NodeClosureState,
    NodeExecutionClosureEvidence,
    RouteFailureEvidence,
    RoutingFailureKind,
)
from maestro.orchestration.governed_execution_routing import (
    ExecutionRoute,
    ExecutionWave,
    GovernedExecutionRoutingPlan,
    WorkerLocality,
    WorkerPlacement,
)
from maestro.orchestration.governed_mission_foundation import (
    CapabilityRule,
    GovernedMissionFoundation,
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
    "governed_adaptive_mission_closure.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_ADAPTIVE_MISSION_CLOSURE_CONSTITUTION.md"
)


def foundation():
    contract = MissionContract(
        objective=(
            "Analyze software without "
            "changing the mission objective"
        ),
        scope="Software analysis",
        requested_output=(
            "Accepted technical result"
        ),
        constraints=(
            "Local execution preferred",
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

    demand = GovernedMissionFoundation.analyze(
        contract,
        (
            CapabilityRule(
                "RULE-ANALYSIS",
                "SOFTWARE_ANALYSIS",
                (
                    "software",
                    "analyze",
                ),
                "Software analysis required.",
            ),
        ),
    )

    capability_graph = (
        GovernedCapabilityResourceMarket
        .synthesize_capability_graph(
            demand
        )
    )

    node = MissionPlanNode(
        node_id="NODE-1",
        capability_id="SOFTWARE_ANALYSIS",
        council_id="IT",
        resource_id="RESOURCE-OLD",
        dependency_node_ids=(),
        acceptance_evidence=(
            "NODE-EVIDENCE",
        ),
        retry_policy=RetryPolicy(
            1,
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
            "ROLLBACK",
            "checkpoint://node-1",
        ),
    )

    plan = GovernedMissionPlan(
        mission_contract_id=(
            contract.contract_id
        ),
        council_graph_id="MCG-AMC",
        capability_graph_id=(
            capability_graph.graph_id
        ),
        resource_selection_id="GRS-AMC",
        mission_acceptance_criteria=(
            contract.acceptance_criteria
        ),
        nodes=(node,),
    )

    route = ExecutionRoute(
        node_id=node.node_id,
        capability_id=(
            node.capability_id
        ),
        council_id=node.council_id,
        resource_id=node.resource_id,
        idempotency_key="EXE-AMC-NODE-1",
    )

    routing = GovernedExecutionRoutingPlan(
        plan_id=plan.plan_id,
        validation_id="GPV-AMC",
        authorization_evidence_id=(
            "EAE-AMC"
        ),
        routes=(route,),
        waves=(
            ExecutionWave(
                wave_index=1,
                route_ids=(
                    route.route_id,
                ),
                node_ids=(
                    node.node_id,
                ),
            ),
        ),
        placements=(
            WorkerPlacement(
                route_id=route.route_id,
                node_id=node.node_id,
                worker_id="WORKER-1",
                worker_node_id="FABRIC-1",
                locality=WorkerLocality.LOCAL,
                worker_evidence_id="DWE-AMC",
            ),
        ),
    )

    policy = ResourceSelectionPolicy(
        mission_contract_id=(
            contract.contract_id
        ),
        constraint_refs=(
            "Local execution preferred",
        ),
        min_evidence_quality=0.8,
        min_reliability=0.8,
        min_privacy_score=0.8,
        max_cost_units=100,
        max_latency_ms=1000,
        require_local=True,
    )

    return (
        contract,
        capability_graph,
        plan,
        routing,
        route,
        policy,
    )


def candidate(
    resource_id,
    *,
    evidence=0.95,
    reliability=0.95,
    privacy=0.95,
):
    return IntelligenceResourceCandidate(
        resource_id=resource_id,
        capabilities=(
            "SOFTWARE_ANALYSIS",
        ),
        availability=(
            ResourceEvidenceState.PASS
        ),
        evidence_quality=evidence,
        reliability=reliability,
        privacy_score=privacy,
        cost_units=10,
        latency_ms=100,
        locality=ResourceLocality.LOCAL,
    )


def failure(
    routing,
    route,
    *,
    state=E.PASS,
):
    return RouteFailureEvidence(
        routing_plan_id=(
            routing.routing_plan_id
        ),
        route_id=route.route_id,
        node_id=route.node_id,
        capability_id=(
            route.capability_id
        ),
        failed_resource_id=(
            route.resource_id
        ),
        failure_kind=(
            RoutingFailureKind
            .RESOURCE_FAILURE
        ),
        failure_detected=state,
        evidence_source_ref=(
            "test://failure"
        ),
    )


def complete_node_closure():
    (
        _,
        _,
        plan,
        routing,
        route,
        _,
    ) = foundation()

    evidence = NodeExecutionClosureEvidence(
        plan_id=plan.plan_id,
        routing_plan_id=(
            routing.routing_plan_id
        ),
        route_id=route.route_id,
        node_id=route.node_id,
        idempotency_key=(
            route.idempotency_key
        ),
        execution_state=E.PASS,
        output_ref="object://output",
        provenance_refs=(
            "provenance://resource",
        ),
        execution_evidence_refs=(
            "execution://trace",
        ),
        council_verdict_state=E.PASS,
        council_verdict_ref=(
            "verdict://it"
        ),
        acceptance_evidence_keys=(
            "NODE-EVIDENCE",
        ),
        evidence_source_ref=(
            "test://node-closure"
        ),
    )

    closure = (
        GovernedAdaptiveMissionClosure
        .close_node(
            plan,
            routing,
            evidence,
        )
    )

    return (
        plan,
        routing,
        route,
        closure,
    )


class GovernedAdaptiveMissionClosureTests(
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
                f"AMC-{number:02d}",
                text,
            )

        for invariant in (
            "REROUTE != OBJECTIVE CHANGE",
            "RESOURCE CHANGE != MISSION CHANGE",
            "REROUTE PROPOSED != REROUTE EXECUTED",
            "EXECUTION SUCCESS != EVIDENCE COMPLETE",
            "MISSING EVIDENCE != PASS",
            "DAG COMPLETE != MISSION ACCEPTED",
            "EXECUTION COMPLETE != EVIDENCE COMPLETE",
            "EVIDENCE COMPLETE != MISSION ACCEPTED",
            "MISSION VERDICT != MISSION CLOSE AUTHORITY",
            "CAN_CLOSE != STATE TRANSITION",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_failure_unknown_and_absent_fail_closed_without_reroute(self):
        (
            contract,
            graph,
            _,
            routing,
            route,
            policy,
        ) = foundation()

        unknown = (
            GovernedAdaptiveMissionClosure
            .assess_reroute(
                contract,
                graph,
                routing,
                failure(
                    routing,
                    route,
                    state=E.UNKNOWN,
                ),
                (
                    candidate(
                        "RESOURCE-NEW"
                    ),
                ),
                policy,
            )
        )

        absent = (
            GovernedAdaptiveMissionClosure
            .assess_reroute(
                contract,
                graph,
                routing,
                failure(
                    routing,
                    route,
                    state=E.FAIL,
                ),
                (
                    candidate(
                        "RESOURCE-NEW"
                    ),
                ),
                policy,
            )
        )

        self.assertIs(
            unknown.state,
            AdaptiveRoutingState.UNKNOWN,
        )

        self.assertIs(
            absent.state,
            AdaptiveRoutingState.NO_CHANGE,
        )

        self.assertIsNone(
            unknown.replacement_resource_id
        )

        self.assertIsNone(
            absent.replacement_resource_id
        )

    def test_03_detected_failure_selects_replacement_without_objective_or_council_change(self):
        (
            contract,
            graph,
            _,
            routing,
            route,
            policy,
        ) = foundation()

        result = (
            GovernedAdaptiveMissionClosure
            .assess_reroute(
                contract,
                graph,
                routing,
                failure(
                    routing,
                    route,
                ),
                (
                    candidate(
                        "RESOURCE-NEW"
                    ),
                ),
                policy,
            )
        )

        self.assertIs(
            result.state,
            AdaptiveRoutingState
            .REROUTE_PROPOSED,
        )

        self.assertEqual(
            result.replacement_resource_id,
            "RESOURCE-NEW",
        )

        self.assertEqual(
            result.council_id,
            "IT",
        )

        self.assertEqual(
            result.capability_id,
            "SOFTWARE_ANALYSIS",
        )

        self.assertFalse(
            result.objective_changed
        )

        self.assertFalse(
            result.council_changed
        )

        self.assertFalse(
            result.execution_authorized
        )

    def test_04_no_eligible_replacement_requires_replan_without_executing_it(self):
        (
            contract,
            graph,
            _,
            routing,
            route,
            policy,
        ) = foundation()

        result = (
            GovernedAdaptiveMissionClosure
            .assess_reroute(
                contract,
                graph,
                routing,
                failure(
                    routing,
                    route,
                ),
                (
                    candidate(
                        "RESOURCE-BAD",
                        privacy=0.1,
                    ),
                ),
                policy,
            )
        )

        self.assertIs(
            result.state,
            AdaptiveRoutingState
            .REPLAN_REQUIRED,
        )

        self.assertIsNone(
            result.replacement_resource_id
        )

        self.assertFalse(
            result.execution_requested
        )

        self.assertFalse(
            result
            .mission_state_transition_requested
        )

    def test_05_failure_lineage_mismatch_fails_closed(self):
        (
            contract,
            graph,
            _,
            routing,
            route,
            policy,
        ) = foundation()

        bad = replace(
            failure(
                routing,
                route,
            ),
            failed_resource_id=(
                "RESOURCE-WRONG"
            ),
        )

        with self.assertRaises(
            AdaptiveMissionClosureInvariantError
        ):
            GovernedAdaptiveMissionClosure.assess_reroute(
                contract,
                graph,
                routing,
                bad,
                (
                    candidate(
                        "RESOURCE-NEW"
                    ),
                ),
                policy,
            )

    def test_06_complete_node_evidence_closes_node(self):
        (
            _,
            _,
            _,
            closure,
        ) = complete_node_closure()

        self.assertIs(
            closure.state,
            NodeClosureState.COMPLETE,
        )

        self.assertFalse(
            closure.mission_close_authorized
        )

        self.assertFalse(
            closure.learning_authorized
        )

    def test_07_execution_success_alone_is_unknown_and_explicit_failure_rejects(self):
        (
            _,
            _,
            plan,
            routing,
            route,
            _,
        ) = foundation()

        incomplete = (
            GovernedAdaptiveMissionClosure
            .close_node(
                plan,
                routing,
                NodeExecutionClosureEvidence(
                    plan_id=plan.plan_id,
                    routing_plan_id=(
                        routing.routing_plan_id
                    ),
                    route_id=route.route_id,
                    node_id=route.node_id,
                    idempotency_key=(
                        route.idempotency_key
                    ),
                    execution_state=E.PASS,
                    output_ref=(
                        "object://output"
                    ),
                    provenance_refs=(),
                    execution_evidence_refs=(),
                    council_verdict_state=(
                        E.UNKNOWN
                    ),
                    council_verdict_ref=None,
                    acceptance_evidence_keys=(),
                    evidence_source_ref=(
                        "test://incomplete"
                    ),
                ),
            )
        )

        self.assertIs(
            incomplete.state,
            NodeClosureState.UNKNOWN,
        )

        rejected = (
            GovernedAdaptiveMissionClosure
            .close_node(
                plan,
                routing,
                NodeExecutionClosureEvidence(
                    plan_id=plan.plan_id,
                    routing_plan_id=(
                        routing.routing_plan_id
                    ),
                    route_id=route.route_id,
                    node_id=route.node_id,
                    idempotency_key=(
                        route.idempotency_key
                    ),
                    execution_state=E.FAIL,
                    output_ref=None,
                    provenance_refs=(),
                    execution_evidence_refs=(
                        "execution://failure",
                    ),
                    council_verdict_state=(
                        E.PASS
                    ),
                    council_verdict_ref=(
                        "verdict://it"
                    ),
                    acceptance_evidence_keys=(),
                    evidence_source_ref=(
                        "test://failure"
                    ),
                ),
            )
        )

        self.assertIs(
            rejected.state,
            NodeClosureState.REJECTED,
        )

    def test_08_complete_closure_acceptance_and_governed_verdicts_produce_passive_acceptance(self):
        (
            plan,
            _,
            _,
            closure,
        ) = complete_node_closure()

        evidence = MissionVerdictEvidence(
            plan_id=plan.plan_id,
            node_closures=(
                closure,
            ),
            acceptance_criteria_validated=(
                "MISSION ACCEPTED",
            ),
            council_verdicts=(
                CouncilMissionVerdictEvidence(
                    "IT",
                    E.PASS,
                    "verdict://it",
                ),
            ),
            ay_system_verdict_state=(
                E.PASS
            ),
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
                evidence,
            )
        )

        self.assertIs(
            verdict.state,
            MissionVerdictState.ACCEPTED,
        )

        self.assertTrue(
            verdict.accepted
        )

        self.assertFalse(
            verdict.mission_close_authorized
        )

        self.assertFalse(
            verdict
            .mission_state_transition_requested
        )

        self.assertFalse(
            verdict.learning_authorized
        )

    def test_09_missing_or_failed_verdict_evidence_fails_closed_and_authority_cannot_escalate(self):
        (
            plan,
            _,
            _,
            closure,
        ) = complete_node_closure()

        unknown = (
            GovernedAdaptiveMissionClosure
            .verdict(
                plan,
                MissionVerdictEvidence(
                    plan_id=plan.plan_id,
                    node_closures=(
                        closure,
                    ),
                    acceptance_criteria_validated=(),
                    council_verdicts=(),
                    ay_system_verdict_state=(
                        E.UNKNOWN
                    ),
                    ay_system_verdict_ref=None,
                    evidence_source_ref=(
                        "test://unknown"
                    ),
                ),
            )
        )

        self.assertIs(
            unknown.state,
            MissionVerdictState.UNKNOWN,
        )

        rejected = (
            GovernedAdaptiveMissionClosure
            .verdict(
                plan,
                MissionVerdictEvidence(
                    plan_id=plan.plan_id,
                    node_closures=(
                        closure,
                    ),
                    acceptance_criteria_validated=(
                        "MISSION ACCEPTED",
                    ),
                    council_verdicts=(
                        CouncilMissionVerdictEvidence(
                            "IT",
                            E.PASS,
                            "verdict://it",
                        ),
                    ),
                    ay_system_verdict_state=(
                        E.FAIL
                    ),
                    ay_system_verdict_ref=(
                        "verdict://ay/fail"
                    ),
                    evidence_source_ref=(
                        "test://rejected"
                    ),
                ),
            )
        )

        self.assertIs(
            rejected.state,
            MissionVerdictState.REJECTED,
        )

        for field_name in (
            "mission_close_authorized",
            "mission_state_transition_requested",
            "durable_commit_authorized",
            "learning_authorized",
            "promotion_authorized",
            "system_truth_asserted",
        ):
            with self.assertRaises(
                AdaptiveMissionClosureInvariantError
            ):
                replace(
                    unknown,
                    **{
                        field_name: True
                    },
                )

    def test_10_module_is_passive_and_canonical_closure_remains_downstream(self):
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
            "maestro.constitution",
            "maestro.evidence.store",
            "maestro.outcome_intelligence",
            "maestro.learning",
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
            "execute",
            "close",
            "transition",
            "move",
            "commit_durable_state",
            "authorize_durable_commit",
            "submit_verdict",
            "record",
            "promote",
            "start_node",
            "fail_dag_node",
            "succeed_dag_node",
            "write_text",
            "write_bytes",
        }

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )


if __name__ == "__main__":
    unittest.main()
