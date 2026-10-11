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
from maestro.orchestration.governed_mission_foundation import (
    CapabilityRule,
    CouncilCapabilityBinding,
    GovernedMissionFoundation,
    MissionContract,
)
from maestro.orchestration.governed_mission_plan import (
    CapabilityPlanDirective,
    CouncilPlanValidation,
    EffectBudgetDeclaration,
    GovernedMissionPlanner,
    MissionPlanIncompleteError,
    MissionPlanInvariantError,
    PlanValidationEvidence,
    PlanValidationState,
    RecoveryBoundary,
    RetryPolicy,
    ValidationEvidenceState as E,
)


SOURCE = Path(
    "src/maestro/orchestration/"
    "governed_mission_plan.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_MISSION_PLAN_CONSTITUTION.md"
)


def foundation():
    contract = MissionContract(
        objective="Build and verify software",
        scope="Software and security",
        requested_output="Verified implementation",
        constraints=("Local execution",),
        acceptance_criteria=(
            "Implementation evidence passes",
            "Security evidence passes",
        ),
        authority_requirements=(
            "AY acceptance",
            "EX routing",
        ),
        evidence_obligations=(
            "Implementation evidence",
            "Security evidence",
        ),
    )

    demand = GovernedMissionFoundation.analyze(
        contract,
        (
            CapabilityRule(
                "R-IT",
                "SOFTWARE_IMPLEMENTATION",
                ("software", "implementation"),
                "Implementation required.",
            ),
            CapabilityRule(
                "R-SC",
                "SECURITY_REVIEW",
                ("security", "verify"),
                "Security review required.",
            ),
        ),
    )

    council_graph = (
        GovernedMissionFoundation
        .synthesize_council_graph(
            contract,
            demand,
            (
                CouncilCapabilityBinding(
                    "IT",
                    ("SOFTWARE_IMPLEMENTATION",),
                ),
                CouncilCapabilityBinding(
                    "SC",
                    ("SECURITY_REVIEW",),
                ),
            ),
        )
    )

    capability_graph = (
        GovernedCapabilityResourceMarket
        .synthesize_capability_graph(
            demand
        )
    )

    policy = ResourceSelectionPolicy(
        mission_contract_id=(
            contract.contract_id
        ),
        constraint_refs=(
            "Local execution",
        ),
        min_evidence_quality=0.8,
        min_reliability=0.8,
        min_privacy_score=0.8,
        max_cost_units=100,
        max_latency_ms=1000,
        require_local=True,
    )

    candidates = (
        IntelligenceResourceCandidate(
            resource_id="RESOURCE-IT",
            capabilities=(
                "SOFTWARE_IMPLEMENTATION",
            ),
            availability=(
                ResourceEvidenceState.PASS
            ),
            evidence_quality=0.95,
            reliability=0.95,
            privacy_score=0.95,
            cost_units=10,
            latency_ms=100,
            locality=ResourceLocality.LOCAL,
        ),
        IntelligenceResourceCandidate(
            resource_id="RESOURCE-SC",
            capabilities=(
                "SECURITY_REVIEW",
            ),
            availability=(
                ResourceEvidenceState.PASS
            ),
            evidence_quality=0.95,
            reliability=0.95,
            privacy_score=0.95,
            cost_units=10,
            latency_ms=100,
            locality=ResourceLocality.LOCAL,
        ),
    )

    selection = (
        GovernedCapabilityResourceMarket
        .select(
            capability_graph,
            candidates,
            policy,
        )
    )

    return (
        contract,
        council_graph,
        capability_graph,
        selection,
    )


def effect():
    return EffectBudgetDeclaration(
        effects=("LOCAL_COMPUTE",),
        permissions=("LOCAL_COMPUTE",),
        max_tool_calls=4,
        max_cost_units=50,
        max_latency_ms=500,
        sandbox_required=True,
    )


def directives():
    return (
        CapabilityPlanDirective(
            capability_id=(
                "SOFTWARE_IMPLEMENTATION"
            ),
            depends_on_capabilities=(),
            acceptance_evidence=(
                "Implementation evidence",
            ),
            retry_policy=RetryPolicy(
                2,
                "bounded-linear",
            ),
            effects=effect(),
            recovery=RecoveryBoundary(
                "ROLLBACK",
                "checkpoint://implementation",
            ),
        ),
        CapabilityPlanDirective(
            capability_id="SECURITY_REVIEW",
            depends_on_capabilities=(
                "SOFTWARE_IMPLEMENTATION",
            ),
            acceptance_evidence=(
                "Security evidence",
            ),
            retry_policy=RetryPolicy(
                1,
                "no-retry",
            ),
            effects=effect(),
            recovery=RecoveryBoundary(
                "RECOVERY",
                "checkpoint://security",
            ),
        ),
    )


def plan():
    values = foundation()

    result = GovernedMissionPlanner.synthesize(
        *values,
        directives(),
    )

    return (*values, result)


class GovernedMissionPlanTests(
    unittest.TestCase
):
    def test_01_constitution_contains_laws_and_separations(self):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(1, 11):
            self.assertIn(
                f"GMP-{number:02d}",
                text,
            )

        for invariant in (
            "NODE CREATED != NODE EXECUTED",
            "DAG VALID != DAG EXECUTED",
            "OUTPUT PRODUCED != ACCEPTANCE PROVEN",
            "RETRY POLICY != RETRY EXECUTION",
            "EFFECT DECLARED != EFFECT AUTHORIZED",
            "PERMISSION DECLARED != PERMISSION GRANTED",
            "SANDBOX REQUIRED != SANDBOX EXECUTED",
            "EXECUTION_ELIGIBLE != EXECUTION_AUTHORIZED",
            "PLAN VALIDATED != EFFECT AUTHORIZED",
            "PLAN SYNTHESIS != RUNTIME EXECUTION",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_plan_is_deterministic_and_order_independent(self):
        values = foundation()

        a = GovernedMissionPlanner.synthesize(
            *values,
            directives(),
        )

        b = GovernedMissionPlanner.synthesize(
            *values,
            tuple(
                reversed(
                    directives()
                )
            ),
        )

        self.assertEqual(
            a.plan_id,
            b.plan_id,
        )

        self.assertEqual(
            a.nodes,
            b.nodes,
        )

        self.assertFalse(
            a.execution_authorized
        )

    def test_03_plan_contains_council_resource_acceptance_retry_effect_and_recovery(self):
        *_, value = plan()

        self.assertEqual(
            len(value.nodes),
            2,
        )

        by_capability = {
            node.capability_id: node
            for node in value.nodes
        }

        implementation = by_capability[
            "SOFTWARE_IMPLEMENTATION"
        ]

        security = by_capability[
            "SECURITY_REVIEW"
        ]

        self.assertEqual(
            implementation.council_id,
            "IT",
        )

        self.assertEqual(
            implementation.resource_id,
            "RESOURCE-IT",
        )

        self.assertTrue(
            implementation
            .acceptance_evidence
        )

        self.assertGreaterEqual(
            implementation
            .retry_policy
            .max_attempts,
            1,
        )

        self.assertTrue(
            implementation
            .effects
            .sandbox_required
        )

        self.assertEqual(
            security.council_id,
            "SC",
        )

        self.assertTrue(
            security.dependency_node_ids
        )

        self.assertIsNotNone(
            security
            .recovery
            .recovery_reference
        )

    def test_04_unknown_dependency_and_cycle_fail_closed(self):
        values = foundation()

        bad_dependency = list(
            directives()
        )

        bad_dependency[0] = (
            CapabilityPlanDirective(
                capability_id=(
                    "SOFTWARE_IMPLEMENTATION"
                ),
                depends_on_capabilities=(
                    "UNKNOWN_CAPABILITY",
                ),
                acceptance_evidence=(
                    "Implementation evidence",
                ),
                retry_policy=RetryPolicy(
                    1,
                    "bounded",
                ),
                effects=effect(),
                recovery=RecoveryBoundary(
                    "ROLLBACK",
                    "checkpoint://x",
                ),
            )
        )

        with self.assertRaises(
            MissionPlanInvariantError
        ):
            GovernedMissionPlanner.synthesize(
                *values,
                tuple(bad_dependency),
            )

        cyclic = (
            CapabilityPlanDirective(
                capability_id=(
                    "SOFTWARE_IMPLEMENTATION"
                ),
                depends_on_capabilities=(
                    "SECURITY_REVIEW",
                ),
                acceptance_evidence=(
                    "Implementation evidence",
                ),
                retry_policy=RetryPolicy(
                    1,
                    "bounded",
                ),
                effects=effect(),
                recovery=RecoveryBoundary(
                    "ROLLBACK",
                    "checkpoint://a",
                ),
            ),
            CapabilityPlanDirective(
                capability_id=(
                    "SECURITY_REVIEW"
                ),
                depends_on_capabilities=(
                    "SOFTWARE_IMPLEMENTATION",
                ),
                acceptance_evidence=(
                    "Security evidence",
                ),
                retry_policy=RetryPolicy(
                    1,
                    "bounded",
                ),
                effects=effect(),
                recovery=RecoveryBoundary(
                    "RECOVERY",
                    "checkpoint://b",
                ),
            ),
        )

        with self.assertRaises(
            MissionPlanInvariantError
        ):
            GovernedMissionPlanner.synthesize(
                *values,
                cyclic,
            )

    def test_05_incomplete_capability_directives_fail_closed(self):
        values = foundation()

        with self.assertRaises(
            MissionPlanIncompleteError
        ):
            GovernedMissionPlanner.synthesize(
                *values,
                (
                    directives()[0],
                ),
            )

    def test_06_external_effects_require_permissions_and_sandbox(self):
        with self.assertRaises(
            MissionPlanInvariantError
        ):
            EffectBudgetDeclaration(
                effects=("WEB_FETCH",),
                permissions=("LOCAL_COMPUTE",),
                max_tool_calls=1,
                max_cost_units=1,
                max_latency_ms=1,
                sandbox_required=True,
                network_allowed=True,
            )

        with self.assertRaises(
            MissionPlanInvariantError
        ):
            EffectBudgetDeclaration(
                effects=("FILE_WRITE",),
                permissions=(
                    "FILESYSTEM_WRITE",
                ),
                max_tool_calls=1,
                max_cost_units=1,
                max_latency_ms=1,
                sandbox_required=False,
                filesystem_write_allowed=True,
            )

    def test_07_complete_validation_yields_eligibility_not_authority(self):
        *_, value = plan()

        councils = tuple(
            sorted(
                {
                    node.council_id
                    for node in value.nodes
                }
            )
        )

        evidence = PlanValidationEvidence(
            plan_id=value.plan_id,
            ay_validation=E.PASS,
            plan_invariants=E.PASS,
            council_validations=tuple(
                CouncilPlanValidation(
                    council,
                    E.PASS,
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
        )

        result = (
            GovernedMissionPlanner
            .validate(
                value,
                evidence,
            )
        )

        self.assertIs(
            result.state,
            PlanValidationState.ELIGIBLE,
        )

        self.assertTrue(
            result.execution_eligible
        )

        self.assertFalse(
            result.execution_authorized
        )
        self.assertFalse(
            result.effects_authorized
        )
        self.assertFalse(
            result.network_authorized
        )

    def test_08_missing_unknown_and_failed_validation_fail_closed(self):
        *_, value = plan()

        council = (
            value.nodes[0].council_id
        )

        unknown = (
            GovernedMissionPlanner
            .validate(
                value,
                PlanValidationEvidence(
                    value.plan_id,
                    E.UNKNOWN,
                    E.PASS,
                    (
                        CouncilPlanValidation(
                            council,
                            E.PASS,
                            "test://partial",
                        ),
                    ),
                    (),
                    "test://unknown",
                ),
            )
        )

        self.assertIs(
            unknown.state,
            PlanValidationState.UNKNOWN,
        )

        failed = (
            GovernedMissionPlanner
            .validate(
                value,
                PlanValidationEvidence(
                    value.plan_id,
                    E.FAIL,
                    E.PASS,
                    (),
                    (),
                    "test://failed",
                ),
            )
        )

        self.assertIs(
            failed.state,
            PlanValidationState.REJECTED,
        )

    def test_09_validation_authority_escalation_fails_closed(self):
        *_, value = plan()

        councils = tuple(
            sorted(
                {
                    node.council_id
                    for node in value.nodes
                }
            )
        )

        result = (
            GovernedMissionPlanner
            .validate(
                value,
                PlanValidationEvidence(
                    value.plan_id,
                    E.PASS,
                    E.PASS,
                    tuple(
                        CouncilPlanValidation(
                            council,
                            E.PASS,
                            f"test://{council}",
                        )
                        for council in councils
                    ),
                    value
                    .mission_acceptance_criteria,
                    "test://authority",
                ),
            )
        )

        for field_name in (
            "execution_authorized",
            "effects_authorized",
            "network_authorized",
            "filesystem_write_authorized",
            "system_truth_asserted",
        ):
            with self.assertRaises(
                MissionPlanInvariantError
            ):
                replace(
                    result,
                    **{
                        field_name: True
                    },
                )

    def test_10_module_is_passive_and_runtime_is_downstream(self):
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
            "maestro.autonomous.sandbox",
            "maestro.resilience.effects",
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
            "start_node",
            "dispatch",
            "prepare",
            "commit",
            "activate",
            "authorize",
            "write_text",
            "write_bytes",
        }

        self.assertEqual(
            calls & forbidden_calls,
            set(),
        )


if __name__ == "__main__":
    unittest.main()
