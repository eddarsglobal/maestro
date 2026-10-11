from __future__ import annotations

import ast
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.orchestration.governed_execution_routing import (
    DistributedWorkerEvidence,
    ExecutionAuthorizationEvidence,
    ExecutionRoutingIncompleteError,
    ExecutionRoutingInvariantError,
    GovernedExecutionRouter,
    RoutingEvidenceState as R,
    WorkerLocality,
)
from maestro.orchestration.governed_mission_plan import (
    CouncilPlanValidation,
    EffectBudgetDeclaration,
    GovernedMissionPlan,
    GovernedMissionPlanner,
    MissionPlanNode,
    PlanValidationEvidence,
    PlanValidationState,
    RecoveryBoundary,
    RetryPolicy,
    ValidationEvidenceState as V,
)


SOURCE = Path(
    "src/maestro/orchestration/"
    "governed_execution_routing.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_EXECUTION_ROUTING_CONSTITUTION.md"
)


def effect():
    return EffectBudgetDeclaration(
        effects=("LOCAL_COMPUTE",),
        permissions=("LOCAL_COMPUTE",),
        max_tool_calls=2,
        max_cost_units=10,
        max_latency_ms=100,
        sandbox_required=True,
    )


def node(
    node_id,
    capability,
    council,
    resource,
    dependencies=(),
):
    return MissionPlanNode(
        node_id=node_id,
        capability_id=capability,
        council_id=council,
        resource_id=resource,
        dependency_node_ids=dependencies,
        acceptance_evidence=(
            f"EVIDENCE-{capability}",
        ),
        retry_policy=RetryPolicy(
            1,
            "bounded",
        ),
        effects=effect(),
        recovery=RecoveryBoundary(
            "ROLLBACK",
            f"checkpoint://{node_id}",
        ),
    )


def plan_three():
    value = GovernedMissionPlan(
        mission_contract_id="MC-TEST",
        council_graph_id="MCG-TEST",
        capability_graph_id="MCAP-TEST",
        resource_selection_id="GRS-TEST",
        mission_acceptance_criteria=(
            "MISSION ACCEPTED",
        ),
        nodes=(
            node(
                "NODE-A",
                "CAP-A",
                "IT",
                "RESOURCE-A",
            ),
            node(
                "NODE-B",
                "CAP-B",
                "SC",
                "RESOURCE-B",
            ),
            node(
                "NODE-C",
                "CAP-C",
                "AI",
                "RESOURCE-C",
                (
                    "NODE-A",
                    "NODE-B",
                ),
            ),
        ),
    )

    councils = tuple(
        sorted(
            {
                item.council_id
                for item in value.nodes
            }
        )
    )

    validation = GovernedMissionPlanner.validate(
        value,
        PlanValidationEvidence(
            plan_id=value.plan_id,
            ay_validation=V.PASS,
            plan_invariants=V.PASS,
            council_validations=tuple(
                CouncilPlanValidation(
                    council,
                    V.PASS,
                    f"test://{council}",
                )
                for council in councils
            ),
            acceptance_criteria_validated=(
                value
                .mission_acceptance_criteria
            ),
            evidence_source_ref=(
                "test://validation"
            ),
        ),
    )

    assert (
        validation.state
        is PlanValidationState.ELIGIBLE
    )

    return value, validation


def authorization(
    plan,
    validation,
    *,
    ex=R.PASS,
    effects=R.PASS,
):
    return ExecutionAuthorizationEvidence(
        plan_id=plan.plan_id,
        validation_id=(
            validation.validation_id
        ),
        ex_authorization=ex,
        effect_authorization=effects,
        evidence_source_ref=(
            "test://authority"
        ),
    )


def workers(
    plan,
):
    rows = []

    mapping = {
        "NODE-A": (
            "IT",
            "CAP-A",
        ),
        "NODE-B": (
            "SC",
            "CAP-B",
        ),
        "NODE-C": (
            "AI",
            "CAP-C",
        ),
    }

    for index, (
        node_id,
        (
            council,
            capability,
        ),
    ) in enumerate(
        mapping.items(),
        start=1,
    ):
        rows.append(
            DistributedWorkerEvidence(
                worker_id=(
                    f"WORKER-{index}"
                ),
                node_id=(
                    f"FABRIC-NODE-{index}"
                ),
                councils=(council,),
                capabilities=(capability,),
                locality=(
                    WorkerLocality.DISTRIBUTED
                    if index > 1
                    else WorkerLocality.LOCAL
                ),
                online=R.PASS,
                lease_valid=R.PASS,
                duplicate_guard=R.PASS,
                recovery_ready=R.PASS,
                leased_plan_id=(
                    plan.plan_id
                ),
                leased_node_ids=(
                    node_id,
                ),
                load_milli=(
                    index * 100
                ),
                max_active_routes=2,
                current_active_routes=0,
                evidence_source_ref=(
                    f"test://worker-{index}"
                ),
            )
        )

    return tuple(rows)


class GovernedExecutionRoutingTests(
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
                f"GER-{number:02d}",
                text,
            )

        for invariant in (
            "ROUTED BY EX != AUTHORITY TRANSFERRED",
            "WORKER EXECUTES != WORKER AUTHORIZES",
            "EX AUTHORIZED != EFFECT AUTHORIZED",
            "ROUTE CREATED != NODE EXECUTED",
            "PARALLEL ELIGIBLE != PARALLEL EXECUTED",
            "AVAILABLE PARALLELISM != UNBOUNDED EXECUTION",
            "WORKER AVAILABLE != WORKER ELIGIBLE",
            "LEASE VALID != MISSION AUTHORITY",
            "PLACEMENT != AUTHORITY",
            "ROUTING PLAN != EXECUTION",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_execution_requires_eligible_validation_and_authorization(self):
        plan, validation = plan_three()

        result = GovernedExecutionRouter.build(
            plan,
            validation,
            authorization(
                plan,
                validation,
            ),
            workers(plan),
            max_parallelism=2,
        )

        self.assertTrue(
            result.ex_authority_observed
        )

        self.assertFalse(
            result.execution_performed
        )

        self.assertEqual(
            len(result.routes),
            3,
        )

    def test_03_failed_or_unknown_authorization_fails_closed(self):
        plan, validation = plan_three()

        with self.assertRaises(
            PermissionError
        ):
            GovernedExecutionRouter.build(
                plan,
                validation,
                authorization(
                    plan,
                    validation,
                    ex=R.FAIL,
                ),
                workers(plan),
                max_parallelism=2,
            )

        with self.assertRaises(
            ExecutionRoutingIncompleteError
        ):
            GovernedExecutionRouter.build(
                plan,
                validation,
                authorization(
                    plan,
                    validation,
                    effects=R.UNKNOWN,
                ),
                workers(plan),
                max_parallelism=2,
            )

    def test_04_route_preserves_council_resource_and_idempotency(self):
        plan, validation = plan_three()

        result = GovernedExecutionRouter.build(
            plan,
            validation,
            authorization(
                plan,
                validation,
            ),
            workers(plan),
            max_parallelism=2,
        )

        by_node = {
            item.node_id: item
            for item in result.routes
        }

        self.assertEqual(
            by_node["NODE-A"].council_id,
            "IT",
        )

        self.assertEqual(
            by_node["NODE-A"].resource_id,
            "RESOURCE-A",
        )

        self.assertTrue(
            by_node["NODE-A"]
            .idempotency_key
            .startswith("EXE-")
        )

    def test_05_independent_nodes_share_wave_and_dependency_waits(self):
        plan, validation = plan_three()

        result = GovernedExecutionRouter.build(
            plan,
            validation,
            authorization(
                plan,
                validation,
            ),
            workers(plan),
            max_parallelism=2,
        )

        self.assertEqual(
            result.waves[0].node_ids,
            (
                "NODE-A",
                "NODE-B",
            ),
        )

        self.assertEqual(
            result.waves[1].node_ids,
            (
                "NODE-C",
            ),
        )

    def test_06_parallelism_is_explicitly_bounded(self):
        plan, validation = plan_three()

        result = GovernedExecutionRouter.build(
            plan,
            validation,
            authorization(
                plan,
                validation,
            ),
            workers(plan),
            max_parallelism=1,
        )

        self.assertEqual(
            tuple(
                wave.node_ids
                for wave in result.waves
            ),
            (
                ("NODE-A",),
                ("NODE-B",),
                ("NODE-C",),
            ),
        )

    def test_07_worker_requires_council_capability_lease_guard_and_recovery(self):
        plan, validation = plan_three()

        bad = list(
            workers(plan)
        )

        bad[0] = replace(
            bad[0],
            lease_valid=R.FAIL,
        )

        with self.assertRaises(
            ExecutionRoutingIncompleteError
        ):
            GovernedExecutionRouter.build(
                plan,
                validation,
                authorization(
                    plan,
                    validation,
                ),
                tuple(bad),
                max_parallelism=2,
            )

        bad = list(
            workers(plan)
        )

        bad[0] = replace(
            bad[0],
            duplicate_guard=R.UNKNOWN,
        )

        with self.assertRaises(
            ExecutionRoutingIncompleteError
        ):
            GovernedExecutionRouter.build(
                plan,
                validation,
                authorization(
                    plan,
                    validation,
                ),
                tuple(bad),
                max_parallelism=2,
            )

    def test_08_worker_capacity_and_exact_lease_binding_fail_closed(self):
        plan, validation = plan_three()

        bad = list(
            workers(plan)
        )

        bad[0] = replace(
            bad[0],
            current_active_routes=2,
        )

        with self.assertRaises(
            ExecutionRoutingIncompleteError
        ):
            GovernedExecutionRouter.build(
                plan,
                validation,
                authorization(
                    plan,
                    validation,
                ),
                tuple(bad),
                max_parallelism=2,
            )

        bad = list(
            workers(plan)
        )

        bad[0] = replace(
            bad[0],
            leased_plan_id="GMP-WRONG",
        )

        with self.assertRaises(
            ExecutionRoutingIncompleteError
        ):
            GovernedExecutionRouter.build(
                plan,
                validation,
                authorization(
                    plan,
                    validation,
                ),
                tuple(bad),
                max_parallelism=2,
            )

    def test_09_routing_is_deterministic_and_transfers_no_authority(self):
        plan, validation = plan_three()

        a = GovernedExecutionRouter.build(
            plan,
            validation,
            authorization(
                plan,
                validation,
            ),
            workers(plan),
            max_parallelism=2,
        )

        b = GovernedExecutionRouter.build(
            plan,
            validation,
            authorization(
                plan,
                validation,
            ),
            tuple(
                reversed(
                    workers(plan)
                )
            ),
            max_parallelism=2,
        )

        self.assertEqual(
            a.routing_plan_id,
            b.routing_plan_id,
        )

        for field_name in (
            "adapter_authority_granted",
            "provider_authority_granted",
            "model_authority_granted",
            "worker_authority_granted",
            "mission_authority_transferred",
            "system_truth_asserted",
            "execution_performed",
        ):
            self.assertFalse(
                getattr(
                    a,
                    field_name,
                )
            )

            with self.assertRaises(
                ExecutionRoutingInvariantError
            ):
                replace(
                    a,
                    **{
                        field_name: True
                    },
                )

    def test_10_module_is_passive_and_execution_engines_are_downstream(self):
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
            "maestro.autonomous.executor",
            "maestro.os.async_runtime",
            "maestro.fabric",
            "maestro.runtime.kernel",
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
            "run_many",
            "enqueue",
            "lease",
            "lease_next",
            "complete",
            "start_node",
            "dispatch",
            "commit",
            "write_text",
            "write_bytes",
        }

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )


if __name__ == "__main__":
    unittest.main()
