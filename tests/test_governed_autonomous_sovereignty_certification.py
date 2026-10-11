from __future__ import annotations

import ast
import json
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.autonomous.executor import (
    CouncilExecutor,
    ExecutionRequest,
    ExecutionResult,
)
from maestro.enums import CouncilId
from maestro.intelligence_market.governed_capability_resource_market import (
    GovernedCapabilityResourceMarket,
    IntelligenceResourceCandidate,
    ResourceEvidenceState,
    ResourceLocality,
    ResourceSelectionPolicy,
)
from maestro.learning.governed_experience_learning_promotion import (
    EvidenceState,
    ExperienceOutcome,
    GovernedExperienceLearningPromotion,
    ResourcePerformanceEvidence,
)
from maestro.orchestration.governed_adaptive_mission_closure import (
    ClosureEvidenceState,
    CouncilMissionVerdictEvidence,
    GovernedAdaptiveMissionClosure,
    MissionVerdictEvidence,
    MissionVerdictState,
    NodeExecutionClosureEvidence,
)
from maestro.orchestration.governed_autonomous_sovereignty_certification import (
    AutonomousSovereigntyCertificationError,
    CouncilExecutionWitness,
    GovernedAutonomousSovereigntyCertification,
)
from maestro.orchestration.governed_durable_mission_recovery import (
    DurableCouncilState,
    DurableRecoveryInformation,
    DurableRetryRecord,
    GovernedDurableMission,
)
from maestro.orchestration.governed_execution_routing import (
    DistributedWorkerEvidence,
    ExecutionAuthorizationEvidence,
    GovernedExecutionRouter,
    RoutingEvidenceState,
    WorkerLocality,
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
    PlanValidationEvidence,
    RecoveryBoundary,
    RetryPolicy,
    ValidationEvidenceState,
)


SOURCE = Path(
    "src/maestro/orchestration/"
    "governed_autonomous_sovereignty_certification.py"
)

DOC = Path(
    "docs/"
    "GOVERNED_AUTONOMOUS_SOVEREIGNTY_CERTIFICATION_CONSTITUTION.md"
)


class DeterministicCouncilAdapter:
    def __init__(
        self,
        council: CouncilId,
    ) -> None:
        self.council = council

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        return ExecutionResult(
            request.task_id,
            request.council,
            True,
            {
                "ok": True,
                "action": request.action,
            },
        )


def _council_id(
    value: str,
) -> CouncilId:
    try:
        return CouncilId(
            value
        )
    except ValueError:
        return CouncilId[
            value
        ]


def build_loop(
    *,
    provider_ref: str = "PROVIDER-DATA",
    model_ref: str = "MODEL-DATA",
    runtime_ref: str = "RUNTIME-DATA",
    zero_model: bool = True,
):
    contract = MissionContract(
        objective=(
            "Build a local application under "
            "governed autonomous execution"
        ),
        scope=(
            "Council-native autonomous mission"
        ),
        requested_output=(
            "Verified local artifact"
        ),
        constraints=(
            "local execution",
            "evidence required",
            "no authority transfer",
        ),
        acceptance_criteria=(
            "MISSION ACCEPTED",
        ),
        authority_requirements=(
            "AY validation",
            "EX authorization",
        ),
        evidence_obligations=(
            "NODE-EVIDENCE",
        ),
    )

    demand = (
        GovernedMissionFoundation
        .analyze(
            contract,
            (
                CapabilityRule(
                    "RULE-SOFTWARE",
                    "SOFTWARE_IMPLEMENTATION",
                    (
                        "application",
                    ),
                    (
                        "Software implementation "
                        "is required."
                    ),
                ),
            ),
        )
    )

    council_graph = (
        GovernedMissionFoundation
        .synthesize_council_graph(
            contract,
            demand,
            (
                CouncilCapabilityBinding(
                    "IT",
                    (
                        "SOFTWARE_IMPLEMENTATION",
                    ),
                ),
            ),
        )
    )

    market = (
        GovernedCapabilityResourceMarket()
    )

    capability_graph = (
        market.synthesize_capability_graph(
            demand
        )
    )

    candidate = IntelligenceResourceCandidate(
        resource_id="RESOURCE-END2END",
        capabilities=(
            "SOFTWARE_IMPLEMENTATION",
        ),
        availability=(
            ResourceEvidenceState.PASS
        ),
        evidence_quality=0.99,
        reliability=0.99,
        privacy_score=0.99,
        cost_units=10,
        latency_ms=100,
        locality=(
            ResourceLocality.LOCAL
        ),
        provider_ref=provider_ref,
        model_ref=model_ref,
        runtime_ref=runtime_ref,
    )

    selection_policy = ResourceSelectionPolicy(
        mission_contract_id=(
            contract.contract_id
        ),
        constraint_refs=(
            "mission://local-private",
        ),
        min_evidence_quality=0.90,
        min_reliability=0.90,
        min_privacy_score=0.90,
        max_cost_units=100,
        max_latency_ms=1000,
        require_local=True,
    )

    selection = market.select(
        capability_graph,
        (
            candidate,
        ),
        selection_policy,
    )

    planner = (
        GovernedMissionPlanner()
    )

    plan = planner.synthesize(
        contract,
        council_graph,
        capability_graph,
        selection,
        (
            CapabilityPlanDirective(
                capability_id=(
                    "SOFTWARE_IMPLEMENTATION"
                ),
                depends_on_capabilities=(),
                acceptance_evidence=(
                    "NODE-EVIDENCE",
                ),
                retry_policy=RetryPolicy(
                    2,
                    "bounded",
                ),
                effects=EffectBudgetDeclaration(
                    (
                        "LOCAL_COMPUTE",
                    ),
                    (
                        "LOCAL_COMPUTE",
                    ),
                    2,
                    100,
                    1000,
                    True,
                ),
                recovery=RecoveryBoundary(
                    "RECOVERY",
                    "checkpoint://end2end",
                ),
            ),
        ),
    )

    council_validations = tuple(
        CouncilPlanValidation(
            node.council_id,
            ValidationEvidenceState.PASS,
            (
                "evidence://council/"
                + node.council_id
            ),
        )
        for node in plan.nodes
    )

    validation_evidence = (
        PlanValidationEvidence(
            plan_id=(
                plan.plan_id
            ),
            ay_validation=(
                ValidationEvidenceState.PASS
            ),
            plan_invariants=(
                ValidationEvidenceState.PASS
            ),
            council_validations=(
                council_validations
            ),
            acceptance_criteria_validated=(
                plan
                .mission_acceptance_criteria
            ),
            evidence_source_ref=(
                "evidence://ay/"
                "plan-validation"
            ),
        )
    )

    validation = planner.validate(
        plan,
        validation_evidence,
    )

    authorization = (
        ExecutionAuthorizationEvidence(
            plan_id=(
                plan.plan_id
            ),
            validation_id=(
                validation.validation_id
            ),
            ex_authorization=(
                RoutingEvidenceState.PASS
            ),
            effect_authorization=(
                RoutingEvidenceState.PASS
            ),
            evidence_source_ref=(
                "evidence://ex/"
                "execution-authorization"
            ),
        )
    )

    worker = DistributedWorkerEvidence(
        worker_id="WORKER-END2END",
        node_id="FABRIC-LOCAL",
        councils=tuple(
            sorted(
                {
                    node.council_id
                    for node
                    in plan.nodes
                }
            )
        ),
        capabilities=tuple(
            sorted(
                {
                    node.capability_id
                    for node
                    in plan.nodes
                }
            )
        ),
        locality=(
            WorkerLocality.LOCAL
        ),
        online=(
            RoutingEvidenceState.PASS
        ),
        lease_valid=(
            RoutingEvidenceState.PASS
        ),
        duplicate_guard=(
            RoutingEvidenceState.PASS
        ),
        recovery_ready=(
            RoutingEvidenceState.PASS
        ),
        leased_plan_id=(
            plan.plan_id
        ),
        leased_node_ids=tuple(
            sorted(
                node.node_id
                for node in plan.nodes
            )
        ),
        load_milli=0,
        max_active_routes=8,
        current_active_routes=0,
        evidence_source_ref=(
            "evidence://worker/end2end"
        ),
    )

    routing = (
        GovernedExecutionRouter
        .build(
            plan,
            validation,
            authorization,
            (
                worker,
            ),
            max_parallelism=4,
        )
    )

    executor = CouncilExecutor()

    registered = set()

    for route in routing.routes:
        council = _council_id(
            route.council_id
        )

        if council not in registered:
            executor.register(
                DeterministicCouncilAdapter(
                    council
                )
            )

            registered.add(
                council
            )

    witnesses = []
    execution_evidence = []
    closures = []

    for route in routing.routes:
        council = _council_id(
            route.council_id
        )

        result = executor.execute(
            ExecutionRequest(
                task_id=(
                    "MISSION-END2END"
                ),
                council=council,
                action=(
                    route.capability_id
                ),
                context={
                    "plan_id": (
                        plan.plan_id
                    ),
                    "routing_plan_id": (
                        routing
                        .routing_plan_id
                    ),
                    "route_id": (
                        route.route_id
                    ),
                },
            )
        )

        output_ref = (
            "object://result/"
            + route.node_id
        )

        witnesses.append(
            CouncilExecutionWitness(
                task_id=(
                    result.task_id
                ),
                route_id=(
                    route.route_id
                ),
                node_id=(
                    route.node_id
                ),
                council_id=(
                    result.council.value
                ),
                ex_authorization_ref=(
                    authorization
                    .evidence_source_ref
                ),
                success=(
                    result.success
                ),
                output_ref=(
                    output_ref
                ),
                evidence_refs=(
                    "execution://"
                    + route.route_id,
                ),
            )
        )

        node = next(
            item
            for item in plan.nodes
            if (
                item.node_id
                == route.node_id
            )
        )

        evidence = (
            NodeExecutionClosureEvidence(
                plan_id=(
                    plan.plan_id
                ),
                routing_plan_id=(
                    routing
                    .routing_plan_id
                ),
                route_id=(
                    route.route_id
                ),
                node_id=(
                    route.node_id
                ),
                idempotency_key=(
                    route
                    .idempotency_key
                ),
                execution_state=(
                    ClosureEvidenceState
                    .PASS
                ),
                output_ref=(
                    output_ref
                ),
                provenance_refs=(
                    "provenance://"
                    + route.route_id,
                ),
                execution_evidence_refs=(
                    "execution://"
                    + route.route_id,
                ),
                council_verdict_state=(
                    ClosureEvidenceState
                    .PASS
                ),
                council_verdict_ref=(
                    "verdict://"
                    + route.council_id
                    + "/"
                    + route.route_id
                ),
                acceptance_evidence_keys=(
                    node
                    .acceptance_evidence
                ),
                evidence_source_ref=(
                    "evidence://closure/"
                    + route.route_id
                ),
            )
        )

        execution_evidence.append(
            evidence
        )

        closures.append(
            GovernedAdaptiveMissionClosure
            .close_node(
                plan,
                routing,
                evidence,
            )
        )

    council_ids = tuple(
        sorted(
            {
                route.council_id
                for route
                in routing.routes
            }
        )
    )

    verdict_evidence = (
        MissionVerdictEvidence(
            plan_id=(
                plan.plan_id
            ),
            node_closures=tuple(
                closures
            ),
            acceptance_criteria_validated=(
                plan
                .mission_acceptance_criteria
            ),
            council_verdicts=tuple(
                CouncilMissionVerdictEvidence(
                    council_id,
                    ClosureEvidenceState.PASS,
                    (
                        "verdict://"
                        + council_id
                        + "/mission"
                    ),
                )
                for council_id
                in council_ids
            ),
            ay_system_verdict_state=(
                ClosureEvidenceState.PASS
            ),
            ay_system_verdict_ref=(
                "verdict://AY/system"
            ),
            evidence_source_ref=(
                "evidence://"
                "mission-verdict"
            ),
        )
    )

    verdict = (
        GovernedAdaptiveMissionClosure
        .verdict(
            plan,
            verdict_evidence,
        )
    )

    if (
        verdict.state
        is not MissionVerdictState
        .ACCEPTED
    ):
        raise AssertionError(
            verdict.state
        )

    retries = tuple(
        DurableRetryRecord(
            node.node_id,
            1,
            node.retry_policy.max_attempts,
            (
                "failure://recovered/"
                + node.node_id
            ),
        )
        for node in plan.nodes
    )

    councils = tuple(
        DurableCouncilState(
            council_id,
            "READY",
            (
                "council://"
                + council_id
                + "/end2end"
            ),
            (
                "evidence://"
                + council_id
                + "/runtime",
            ),
        )
        for council_id
        in council_ids
    )

    recovery = (
        DurableRecoveryInformation(
            "checkpoint://stable/end2end",
            1,
            "checkpoint://rollback/end2end",
            "checkpoint://recovery/end2end",
            (
                "recovery://end2end",
            ),
        )
    )

    checkpoint = (
        GovernedDurableMission
        .checkpoint(
            canonical_mission={
                "task_id": (
                    "MISSION-END2END"
                ),
                "objective": (
                    contract.objective
                ),
                "state": (
                    "VERIFIED"
                ),
            },
            contract=contract,
            plan=plan,
            routing=routing,
            node_execution_evidence=tuple(
                execution_evidence
            ),
            node_closures=tuple(
                closures
            ),
            mission_verdict_evidence=(
                verdict_evidence
            ),
            mission_verdict=(
                verdict
            ),
            retries=retries,
            councils=councils,
            recovery=recovery,
            runtime_checkpoint_schema=(
                "maestro.checkpoint.v0.2"
            ),
            runtime_checkpoint_sha256=(
                "a" * 64
            ),
            generation=2,
        )
    )

    performance = tuple(
        ResourcePerformanceEvidence(
            route.resource_id,
            route.capability_id,
            EvidenceState.PASS,
            0.99,
            0.99,
            10,
            100,
            (
                "resource://"
                + route.resource_id
                + "/performance",
            ),
        )
        for route in routing.routes
    )

    experience = (
        GovernedExperienceLearningPromotion
        .capture(
            checkpoint,
            verdict,
            outcome=(
                ExperienceOutcome.SUCCESS
            ),
            verified_result_ref=(
                "verified://mission/"
                "end2end"
            ),
            failure_refs=(),
            retry_evidence_refs=tuple(
                "retry://"
                + node.node_id
                for node in plan.nodes
            ),
            routing_quality_score=0.99,
            resource_performance=(
                performance
            ),
            human_correction_refs=(),
            evidence_refs=(
                "experience://end2end",
            ),
            cost_units=10,
            latency_ms=100,
        )
    )

    certificate = (
        GovernedAutonomousSovereigntyCertification
        .certify(
            contract=contract,
            council_graph=(
                council_graph
            ),
            capability_graph=(
                capability_graph
            ),
            resource_selection=(
                selection
            ),
            plan=plan,
            validation=validation,
            routing=routing,
            execution_witnesses=tuple(
                witnesses
            ),
            node_execution_evidence=tuple(
                execution_evidence
            ),
            node_closures=tuple(
                closures
            ),
            verdict=verdict,
            checkpoint=checkpoint,
            experience=experience,
            zero_model_core_certified=(
                zero_model
            ),
        )
    )

    return {
        "contract": contract,
        "demand": demand,
        "council_graph": (
            council_graph
        ),
        "capability_graph": (
            capability_graph
        ),
        "selection": selection,
        "plan": plan,
        "validation": validation,
        "authorization": (
            authorization
        ),
        "routing": routing,
        "witnesses": tuple(
            witnesses
        ),
        "execution_evidence": tuple(
            execution_evidence
        ),
        "closures": tuple(
            closures
        ),
        "verdict": verdict,
        "checkpoint": checkpoint,
        "experience": experience,
        "certificate": certificate,
    }


class GovernedAutonomousSovereigntyCertificationTests(
    unittest.TestCase
):
    def test_01_constitution_contains_final_laws_and_separations(
        self,
    ):
        text = DOC.read_text(
            encoding="utf-8"
        )

        for number in range(
            1,
            11,
        ):
            self.assertIn(
                f"ASC-{number:02d}",
                text,
            )

        for invariant in (
            "AUTONOMY != AUTHORITY",
            "MODEL SELECTED != MODEL AUTHORITY",
            "PROVIDER SELECTED != PROVIDER AUTHORITY",
            "EXECUTION_ELIGIBLE != EXECUTION_AUTHORIZED",
            "ROUTING PLAN != EXECUTION",
            "EXECUTION COMPLETE != EVIDENCE COMPLETE",
            "EVIDENCE COMPLETE != MISSION ACCEPTED",
            "MISSION ACCEPTED != SYSTEM TRUTH",
            "ZERO MODEL != ZERO GOVERNANCE",
            "PROJECT_COMPLETE != RELEASE AUTHORIZED",
        ):
            self.assertIn(
                invariant,
                text,
            )

    def test_02_real_end_to_end_autonomous_loop_certifies(
        self,
    ):
        result = build_loop()

        certificate = result[
            "certificate"
        ]

        self.assertTrue(
            certificate
            .autonomous_loop_complete
        )

        self.assertTrue(
            certificate
            .council_governed
        )

        self.assertTrue(
            certificate
            .evidence_bound
        )

        self.assertTrue(
            certificate
            .recoverable
        )

        self.assertEqual(
            result[
                "experience"
            ].plan_id,
            result[
                "plan"
            ].plan_id,
        )

    def test_03_real_council_execution_is_bound_to_routes(
        self,
    ):
        result = build_loop()

        route_ids = {
            route.route_id
            for route
            in result[
                "routing"
            ].routes
        }

        witness_ids = {
            witness.route_id
            for witness
            in result[
                "witnesses"
            ]
        }

        self.assertEqual(
            route_ids,
            witness_ids,
        )

        self.assertTrue(
            all(
                witness.success
                for witness
                in result[
                    "witnesses"
                ]
            )
        )

    def test_04_contract_to_plan_lineage_is_exact(
        self,
    ):
        result = build_loop()

        contract = result[
            "contract"
        ]

        council_graph = result[
            "council_graph"
        ]

        capability_graph = result[
            "capability_graph"
        ]

        selection = result[
            "selection"
        ]

        plan = result[
            "plan"
        ]

        self.assertEqual(
            council_graph.contract_id,
            contract.contract_id,
        )

        self.assertEqual(
            capability_graph
            .mission_contract_id,
            contract.contract_id,
        )

        self.assertEqual(
            capability_graph
            .demand_id,
            council_graph.demand_id,
        )

        self.assertEqual(
            selection
            .capability_graph_id,
            capability_graph.graph_id,
        )

        self.assertEqual(
            plan
            .resource_selection_id,
            selection.selection_id,
        )

    def test_05_execution_to_experience_lineage_is_exact(
        self,
    ):
        result = build_loop()

        plan = result[
            "plan"
        ]

        routing = result[
            "routing"
        ]

        verdict = result[
            "verdict"
        ]

        checkpoint = result[
            "checkpoint"
        ]

        experience = result[
            "experience"
        ]

        for evidence in result[
            "execution_evidence"
        ]:
            self.assertEqual(
                evidence.plan_id,
                plan.plan_id,
            )

            self.assertEqual(
                evidence
                .routing_plan_id,
                routing.routing_plan_id,
            )

        self.assertEqual(
            verdict.plan_id,
            plan.plan_id,
        )

        self.assertEqual(
            checkpoint.plan_id,
            plan.plan_id,
        )

        self.assertEqual(
            experience
            .checkpoint_id,
            checkpoint.checkpoint_id,
        )

        self.assertEqual(
            experience
            .mission_verdict_id,
            verdict.verdict_id,
        )

    def test_06_recovery_and_durable_experience_are_present(
        self,
    ):
        result = build_loop()

        payload = json.loads(
            result[
                "checkpoint"
            ].payload_json
        )

        self.assertIn(
            "recovery_information",
            payload,
        )

        self.assertTrue(
            payload[
                "recovery_information"
            ]
        )

        self.assertTrue(
            result[
                "experience"
            ].retry_evidence_refs
        )

        self.assertTrue(
            result[
                "certificate"
            ].recoverable
        )

    def test_07_provider_model_runtime_metadata_never_becomes_authority(
        self,
    ):
        result = build_loop(
            provider_ref=(
                "PROVIDER-X"
            ),
            model_ref=(
                "MODEL-X"
            ),
            runtime_ref=(
                "RUNTIME-X"
            ),
        )

        capability_graph = result[
            "capability_graph"
        ]

        selection = result[
            "selection"
        ]

        routing = result[
            "routing"
        ]

        self.assertFalse(
            capability_graph
            .provider_bound
        )

        self.assertFalse(
            capability_graph
            .model_bound
        )

        self.assertFalse(
            capability_graph
            .runtime_bound
        )

        self.assertFalse(
            selection
            .provider_authority_granted
        )

        self.assertFalse(
            selection
            .model_authority_granted
        )

        self.assertFalse(
            selection
            .runtime_authority_granted
        )

        self.assertFalse(
            routing
            .provider_authority_granted
        )

        self.assertFalse(
            routing
            .model_authority_granted
        )

    def test_08_zero_model_sovereignty_is_required_fail_closed(
        self,
    ):
        with self.assertRaises(
            AutonomousSovereigntyCertificationError
        ):
            build_loop(
                zero_model=False
            )

    def test_09_forged_lineage_fails_closed_and_certificate_is_deterministic(
        self,
    ):
        first = build_loop()
        second = build_loop()

        self.assertEqual(
            first[
                "certificate"
            ].certification_id,
            second[
                "certificate"
            ].certification_id,
        )

        forged_experience = replace(
            first[
                "experience"
            ],
            plan_id=(
                "GMP-"
                + "f" * 24
            ),
        )

        with self.assertRaises(
            AutonomousSovereigntyCertificationError
        ):
            (
                GovernedAutonomousSovereigntyCertification
                .certify(
                    contract=first[
                        "contract"
                    ],
                    council_graph=first[
                        "council_graph"
                    ],
                    capability_graph=first[
                        "capability_graph"
                    ],
                    resource_selection=first[
                        "selection"
                    ],
                    plan=first[
                        "plan"
                    ],
                    validation=first[
                        "validation"
                    ],
                    routing=first[
                        "routing"
                    ],
                    execution_witnesses=first[
                        "witnesses"
                    ],
                    node_execution_evidence=first[
                        "execution_evidence"
                    ],
                    node_closures=first[
                        "closures"
                    ],
                    verdict=first[
                        "verdict"
                    ],
                    checkpoint=first[
                        "checkpoint"
                    ],
                    experience=(
                        forged_experience
                    ),
                    zero_model_core_certified=True,
                )
            )

    def test_10_certification_module_is_passive_and_grants_no_release_authority(
        self,
    ):
        tree = ast.parse(
            SOURCE.read_text(
                encoding="utf-8"
            )
        )

        imports = set()
        calls = set()

        for node in ast.walk(
            tree
        ):
            if isinstance(
                node,
                ast.Import,
            ):
                imports.update(
                    alias.name
                    for alias
                    in node.names
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
            "subprocess",
            "socket",
            "requests",
            "urllib",
            "httpx",
            "maestro.autonomous.executor",
            "maestro.runtime.kernel",
            "maestro.governed_activation",
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
            "activate",
            "authorize",
            "dispatch",
            "promote",
            "install",
            "download",
            "request",
            "urlopen",
            "commit",
            "tag",
            "push",
            "write_text",
            "write_bytes",
        }

        self.assertEqual(
            calls
            & forbidden_calls,
            set(),
        )

        certificate = (
            build_loop()[
                "certificate"
            ]
        )

        self.assertFalse(
            certificate
            .authority_expanded
        )

        self.assertFalse(
            certificate
            .system_truth_asserted
        )

        self.assertFalse(
            certificate
            .production_release_authorized
        )


if __name__ == "__main__":
    unittest.main()
