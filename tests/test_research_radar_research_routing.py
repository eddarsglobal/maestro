from __future__ import annotations

import ast
import unittest

from dataclasses import replace
from pathlib import Path

from maestro.research import (
    ContentDigest,
    ExternalArtifact,
    GovernedRadarDecisionEnvelope,
    GovernedRadarEvidenceFollowUp,
    GovernedRadarEvaluationPipeline,
    GovernedRadarFollowUpCandidateBuilder,
    GovernedRadarPortfolio,
    GovernedRadarResearchDraftAdmissionGate,
    GovernedRadarResearchRequestDraftBuilder,
    GovernedRadarResearchRequestMaterializer,
    GovernedRadarResearchRouter,
    GovernedRadarResearchTaskBinder,
    GovernedRadarReviewHandoff,
    GovernedRadarReviewPacket,
    GovernedRadarReviewResponse,
    GovernedResearchRuntime,
    RadarDecisionPolicy,
    RadarPortfolioEntry,
    RadarResearchDraftAdmissionStatus,
    RadarResearchRequestMaterialization,
    RadarReviewResponseValue,
    RadarReviewTarget,
    ResearchCapability,
    ResearchClaim,
    ResearchEvidenceBridge,
    ResearchProviderDescriptor,
    ResearchProviderRegistry,
    ResearchProviderStatus,
    ResearchRequest,
    ResearchRoutingDecision,
    ResearchSource,
    SourceProvenance,
)

from maestro.tools.registry import (
    ToolRegistry,
)


class RadarResearchRoutingTests(
    unittest.TestCase
):
    NOW = "2026-01-01T00:00:00+00:00"

    TASK_A = "TASK-A1B2C3D4E5F6"
    TASK_B = "TASK-B1C2D3E4F5A6"
    TASK_C = "TASK-C1D2E3F4A5B6"

    def provider(
        self,
        provider_id: str,
        *,
        local: bool = False,
        status: ResearchProviderStatus = (
            ResearchProviderStatus.AVAILABLE
        ),
        quality: float = 0.5,
        cost: float = 0.0,
        latency: float = 0.0,
    ):
        return ResearchProviderDescriptor(
            provider_id=provider_id,
            capabilities=frozenset(
                {
                    ResearchCapability.SEARCH,
                }
            ),
            tool_names={
                ResearchCapability.SEARCH: (
                    f"{provider_id}.search"
                ),
            },
            local=local,
            status=status,
            quality_score=quality,
            cost_score=cost,
            latency_score=latency,
        )

    def runtime(
        self,
        *providers,
    ):
        registry = ResearchProviderRegistry()

        for descriptor in providers:
            registry.register(
                descriptor
            )

        runtime = GovernedResearchRuntime(
            registry,
            ToolRegistry(),
        )

        return runtime, registry

    def evidence(
        self,
        suffix: str,
    ):
        statement = (
            "GPU reasoning improves "
            "MAESTRO research"
        )

        source = ResearchSource(
            (
                "https://example.com/"
                f"adel020-{suffix}"
            ),
            label=f"ADEL0.20 {suffix}",
        )

        provenance = SourceProvenance(
            source_id=source.source_id,
            retrieved_at=self.NOW,
            digest=ContentDigest.from_bytes(
                statement.encode("utf-8")
            ),
            author="Researcher",
            license="MIT",
            version="1.0",
        )

        artifact = ExternalArtifact(
            source=source,
            provenance=provenance,
            artifact_kind="DOCUMENT",
            media_type="text/html",
        )

        claim = ResearchClaim(
            statement=statement,
            artifact_ids=(
                artifact.artifact_id,
            ),
            created_at=self.NOW,
        )

        return ResearchEvidenceBridge.to_evidence(
            task_id=self.TASK_A,
            claim=claim,
            artifacts=[artifact],
        )

    def context(
        self,
    ):
        return GovernedRadarEvaluationPipeline.context(
            known_claims=["legacy baseline"],
            relevance_terms=[
                "MAESTRO",
                "research",
            ],
            capability_terms=[
                "GPU",
                "reasoning",
            ],
            existing_capabilities=(),
            integration_requirements=[
                "python"
            ],
            available_integration_support=[
                "python"
            ],
            independent_sources=[
                "source-a",
                "source-b",
            ],
            reproduction_requirements=[
                "code"
            ],
            reproduction_support=[
                "code"
            ],
            risk_signals=["network"],
            mitigations=["network"],
        )

    def drafts(
        self,
        count=1,
    ):
        portfolio = (
            GovernedRadarPortfolio()
            .evaluate(
                tuple(
                    RadarPortfolioEntry(
                        evidence=self.evidence(
                            str(index)
                        ),
                        context=self.context(),
                    )
                    for index in range(count)
                )
            )
        )

        policy = RadarDecisionPolicy(
            investigate_min_priority=0.0,
            review_min_priority=0.0,
        )

        envelope = (
            GovernedRadarDecisionEnvelope
            .evaluate(
                portfolio,
                policy=policy,
            )
        )

        packet = (
            GovernedRadarReviewPacket
            .build(
                portfolio,
                envelope,
                policy=policy,
            )
        )

        handoff = (
            GovernedRadarReviewHandoff
            .build(
                packet,
                assignments={
                    entry.evidence_id: (
                        RadarReviewTarget
                        .HUMAN_REVIEW
                    )
                    for entry
                    in packet.entries
                },
            )
        )

        response = (
            GovernedRadarReviewResponse
            .build(
                handoff,
                responses={
                    entry.evidence_id: (
                        RadarReviewResponseValue
                        .REQUEST_MORE_EVIDENCE
                    )
                    for entry
                    in handoff.entries
                },
            )
        )

        followup = (
            GovernedRadarEvidenceFollowUp
            .build(
                response
            )
        )

        candidates = (
            GovernedRadarFollowUpCandidateBuilder
            .build(
                followup
            )
        )

        return (
            GovernedRadarResearchRequestDraftBuilder
            .build(
                candidates
            )
        )

    def materialization(
        self,
        count=1,
    ):
        admission = (
            GovernedRadarResearchDraftAdmissionGate
            .evaluate(
                self.drafts(count)
            )
        )

        task_values = (
            self.TASK_A,
            self.TASK_B,
            self.TASK_C,
        )

        task_ids = {
            entry.evidence_id: (
                task_values[index]
            )
            for index, entry
            in enumerate(
                admission.entries
            )
            if (
                entry.status
                is RadarResearchDraftAdmissionStatus
                .ADMISSIBLE
            )
        }

        binding = (
            GovernedRadarResearchTaskBinder
            .bind(
                admission,
                task_ids=task_ids,
            )
        )

        return (
            GovernedRadarResearchRequestMaterializer
            .materialize(
                binding
            )
        )

    def with_request(
        self,
        materialization,
        request,
    ):
        entry = replace(
            materialization.entries[0],
            request=request,
        )

        return RadarResearchRequestMaterialization(
            entries=(entry,)
        )

    def test_empty_materialization_routes_nothing(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        result = GovernedRadarResearchRouter.route(
            self.materialization(0),
            runtime=runtime,
        )

        self.assertEqual(
            result.size,
            0,
        )

    def test_materialized_request_is_routed(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        result = GovernedRadarResearchRouter.route(
            self.materialization(),
            runtime=runtime,
        )

        self.assertEqual(
            result.size,
            1,
        )
        self.assertTrue(
            result.entries[0]
            .routing_decision_created
        )

    def test_decision_is_real_routing_decision(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        row = GovernedRadarResearchRouter.route(
            self.materialization(),
            runtime=runtime,
        ).entries[0]

        self.assertIsInstance(
            row.decision,
            ResearchRoutingDecision,
        )

    def test_available_provider_beats_degraded(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider(
                "degraded-local",
                local=True,
                status=(
                    ResearchProviderStatus
                    .DEGRADED
                ),
                quality=1.0,
            ),
            self.provider(
                "available-remote",
                quality=0.1,
            ),
        )

        row = GovernedRadarResearchRouter.route(
            self.materialization(),
            runtime=runtime,
        ).entries[0]

        self.assertEqual(
            row.decision.provider_id,
            "available-remote",
        )

    def test_local_provider_is_preferred(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider(
                "remote",
                quality=1.0,
            ),
            self.provider(
                "local",
                local=True,
                quality=0.1,
            ),
        )

        row = GovernedRadarResearchRouter.route(
            self.materialization(),
            runtime=runtime,
        ).entries[0]

        self.assertEqual(
            row.decision.provider_id,
            "local",
        )

    def test_quality_cost_latency_and_id_are_deterministic(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider(
                "zeta",
                local=True,
                quality=0.8,
                cost=1.0,
                latency=1.0,
            ),
            self.provider(
                "beta",
                local=True,
                quality=0.9,
                cost=5.0,
                latency=5.0,
            ),
            self.provider(
                "alpha",
                local=True,
                quality=0.9,
                cost=1.0,
                latency=1.0,
            ),
        )

        row = GovernedRadarResearchRouter.route(
            self.materialization(),
            runtime=runtime,
        ).entries[0]

        self.assertEqual(
            row.decision.provider_id,
            "alpha",
        )

        self.assertEqual(
            row.decision.candidates,
            (
                "alpha",
                "beta",
                "zeta",
            ),
        )

    def test_forbidden_provider_is_excluded(
        self,
    ):
        materialization = (
            self.materialization()
        )

        original = (
            materialization.entries[0]
            .request
        )

        request = ResearchRequest(
            task_id=original.task_id,
            capability=original.capability,
            arguments=original.arguments,
            preferred_local=(
                original.preferred_local
            ),
            forbidden_provider_ids=(
                frozenset(
                    {"best"}
                )
            ),
        )

        materialization = self.with_request(
            materialization,
            request,
        )

        runtime, _ = self.runtime(
            self.provider(
                "best",
                local=True,
                quality=1.0,
            ),
            self.provider(
                "second",
                local=True,
                quality=0.5,
            ),
        )

        row = GovernedRadarResearchRouter.route(
            materialization,
            runtime=runtime,
        ).entries[0]

        self.assertEqual(
            row.decision.provider_id,
            "second",
        )

        self.assertNotIn(
            "best",
            row.decision.candidates,
        )

    def test_no_eligible_provider_fails_closed(
        self,
    ):
        runtime, _ = self.runtime()

        with self.assertRaises(
            LookupError
        ):
            GovernedRadarResearchRouter.route(
                self.materialization(),
                runtime=runtime,
            )

    def test_request_identity_is_preserved(
        self,
    ):
        materialization = (
            self.materialization()
        )

        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        row = GovernedRadarResearchRouter.route(
            materialization,
            runtime=runtime,
        ).entries[0]

        self.assertIs(
            row.request,
            materialization.entries[0]
            .request,
        )

    def test_order_and_payload_are_preserved(
        self,
    ):
        materialization = (
            self.materialization(3)
        )

        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        result = GovernedRadarResearchRouter.route(
            materialization,
            runtime=runtime,
        )

        self.assertEqual(
            result.evidence_ids,
            materialization.evidence_ids,
        )

        self.assertEqual(
            result.task_ids,
            materialization.task_ids,
        )

        for before, after in zip(
            materialization.entries,
            result.entries,
        ):
            self.assertEqual(
                after.rank,
                before.rank,
            )
            self.assertEqual(
                after.evidence_id,
                before.evidence_id,
            )
            self.assertEqual(
                after.source_ref,
                before.source_ref,
            )
            self.assertEqual(
                after.claim,
                before.claim,
            )
            self.assertEqual(
                after.priority_score,
                before.priority_score,
            )
            self.assertEqual(
                after.factors,
                before.factors,
            )
            self.assertEqual(
                after.rationale,
                before.rationale,
            )
            self.assertEqual(
                after.target,
                before.target,
            )

    def test_admission_provenance_is_preserved(
        self,
    ):
        materialization = (
            self.materialization()
        )

        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        row = GovernedRadarResearchRouter.route(
            materialization,
            runtime=runtime,
        ).entries[0]

        before = materialization.entries[0]

        self.assertEqual(
            row.admission_status,
            before.admission_status,
        )
        self.assertEqual(
            row.admission_reason,
            before.admission_reason,
        )

    def test_unverified_boundary_is_preserved(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        row = GovernedRadarResearchRouter.route(
            self.materialization(),
            runtime=runtime,
        ).entries[0]

        self.assertEqual(
            row.verification_status,
            "UNVERIFIED_EXTERNAL",
        )
        self.assertFalse(
            row.system_truth_asserted
        )

    def test_routing_flags_are_exact(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        row = GovernedRadarResearchRouter.route(
            self.materialization(),
            runtime=runtime,
        ).entries[0]

        self.assertTrue(
            row.task_id_bound
        )
        self.assertTrue(
            row.research_request_created
        )
        self.assertTrue(
            row.provider_selected
        )
        self.assertTrue(
            row.routing_decision_created
        )

    def test_routing_does_not_validate_or_execute_tool(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        row = GovernedRadarResearchRouter.route(
            self.materialization(),
            runtime=runtime,
        ).entries[0]

        self.assertFalse(
            row.tool_validated
        )
        self.assertFalse(
            row.tool_execution_requested
        )

    def test_routing_has_no_active_side_effects(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        row = GovernedRadarResearchRouter.route(
            self.materialization(),
            runtime=runtime,
        ).entries[0]

        self.assertFalse(
            row.network_requested
        )
        self.assertFalse(
            row.mission_transition_requested
        )
        self.assertFalse(
            row.persistence_requested
        )
        self.assertFalse(
            row.execution_asserted
        )

    def test_routing_asserts_no_authority(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        row = GovernedRadarResearchRouter.route(
            self.materialization(),
            runtime=runtime,
        ).entries[0]

        self.assertFalse(
            row.authorization_asserted
        )
        self.assertFalse(
            row.promotion_asserted
        )
        self.assertFalse(
            row.activation_asserted
        )
        self.assertFalse(
            row.system_truth_asserted
        )

    def test_route_is_deterministic_and_registry_unchanged(
        self,
    ):
        runtime, registry = self.runtime(
            self.provider(
                "alpha",
                local=True,
                quality=0.9,
            ),
            self.provider(
                "beta",
                local=True,
                quality=0.8,
            ),
        )

        before = tuple(
            descriptor.to_dict()
            for descriptor
            in registry.all()
        )

        materialization = (
            self.materialization(2)
        )

        first = GovernedRadarResearchRouter.route(
            materialization,
            runtime=runtime,
        )

        second = GovernedRadarResearchRouter.route(
            materialization,
            runtime=runtime,
        )

        after = tuple(
            descriptor.to_dict()
            for descriptor
            in registry.all()
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertEqual(
            before,
            after,
        )

    def test_wrong_inputs_and_active_boundary_fail_closed(
        self,
    ):
        runtime, _ = self.runtime(
            self.provider("alpha")
        )

        with self.assertRaises(
            TypeError
        ):
            GovernedRadarResearchRouter.route(
                object(),
                runtime=runtime,
            )

        with self.assertRaises(
            TypeError
        ):
            GovernedRadarResearchRouter.route(
                self.materialization(),
                runtime=object(),
            )

        path = Path(
            "src/maestro/research/"
            "radar_research_routing.py"
        )

        source = path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source
        )

        called = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                ast.Call,
            ):
                try:
                    called.add(
                        ast.unparse(
                            node.func
                        )
                    )
                except Exception:
                    pass

        self.assertIn(
            "runtime.route",
            called,
        )

        forbidden_calls = {
            "runtime.execute",
            "runtime._validate_tool",
            "runtime.tools.invoke",
            "runtime.providers.register",
            "runtime.providers.unregister",
            "runtime.providers.set_status",
        }

        self.assertTrue(
            called.isdisjoint(
                forbidden_calls
            )
        )



if __name__ == "__main__":
    unittest.main()
